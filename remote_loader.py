"""AScript 在线更新加载器。

用户首次导入的 AScript 工程会永久保留这个模块。每次启动时，本模块按以下顺序
选择业务代码：

1. 从 GitHub 发布分支读取清单，下载并校验对应的运行时 ZIP；
2. 在线检查失败时，加载设备上一次已经验证成功的远程缓存；
3. 设备还没有缓存时，加载用户最初导入工程中自带的业务代码。

下载包只有在大小、SHA-256、ZIP 路径和必要入口均验证通过，并且 Python 模块
能够成功导入后，才会写入 ``active.json`` 成为新的活动版本。这样网络中断、
CDN 旧缓存、下载损坏或发布包结构错误都不会替换设备上最后一个可运行版本。
"""

import hashlib
import importlib
import json
import os
import shutil
import sys
import time
import zipfile

import requests
from ascript.android.system import R


# 在线更新固定读取公开仓库的 runtime 分支。用户设备不保存 GitHub Token、
# SSH 私钥等账号凭据，因此仓库必须允许匿名读取。
REPOSITORY = "qingushan/as-erchong"
RELEASE_BRANCH = "runtime"
MANIFEST_PATH = "dist/latest.json"

# ZIP 解压后的顶层 Python 包名。构建工具必须生成同名目录，并在目录内放置
# runtime_entry.py；加载器使用这个稳定包名导入远程业务入口。
RUNTIME_PACKAGE = "erchong_runtime"
# 当前 Android AScript 中，向 R.sd 传入多个参数会返回多个独立路径组成的列表，
# 而不是拼接后的单一路径；这里传入一个相对路径，确保缓存根目录始终是可供
# os.path 使用的字符串。
# 缓存位于公共存储目录，按 release_id 分目录保存，允许旧版本与新版本共存，
# 便于断网回退和手动排查。这里不存放 GitHub 账号凭据。
CACHE_ROOT = R.sd("AScript/erchong_runtime")

# 同时限制清单声明值、HTTP 响应头和实际读取字节数，避免异常服务器或错误地址
# 把过大的文件写满设备存储。当前完整运行时不足 1 MiB，20 MiB 留有充足余量。
MAX_PACKAGE_BYTES = 20 * 1024 * 1024

# 国内云手机实测 GitHub Raw 可能无法连接，因此优先使用 jsDelivr；若首选源的
# 清单或 ZIP 请求失败，再尝试 GitHub Raw。发布后仍需主动清理 latest.json 的
# jsDelivr 缓存，否则首选源可能暂时返回旧的、但仍合法的清单。
SOURCE_BASES = (
    "https://cdn.jsdelivr.net/gh/{repo}@{branch}/".format(
        repo=REPOSITORY,
        branch=RELEASE_BRANCH,
    ),
    "https://raw.githubusercontent.com/{repo}/{branch}/".format(
        repo=REPOSITORY,
        branch=RELEASE_BRANCH,
    ),
)


class RuntimeUpdateError(Exception):
    """表示远程清单、下载内容或缓存结构不满足加载器约束。"""

    pass


def _read_json(path):
    """按 UTF-8 读取设备上的 JSON 文件并返回反序列化结果。"""
    with open(path, "r", encoding="utf-8") as file_obj:
        return json.load(file_obj)


def _write_json_atomic(path, value):
    """以“临时文件 + 原子替换”方式写入 JSON。

    ``active.json`` 决定下次断网时加载哪个缓存版本。如果脚本在普通写入过程中
    被停止，文件可能只写入一半；先在同目录完成临时文件，再用 ``os.replace``
    一次替换目标，可避免留下半截 JSON。
    """
    os.makedirs(os.path.dirname(path), exist_ok=True)
    temporary_path = path + ".tmp"
    with open(temporary_path, "w", encoding="utf-8") as file_obj:
        json.dump(value, file_obj, ensure_ascii=False, indent=2)
    os.replace(temporary_path, path)


def _sha256(path):
    """分块计算文件 SHA-256，避免一次性把整个 ZIP 读入内存。"""
    digest = hashlib.sha256()
    with open(path, "rb") as file_obj:
        for chunk in iter(lambda: file_obj.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _safe_name(value, field_name):
    """校验会参与本地路径拼接的清单字段。

    ``release_id`` 最终会成为缓存目录名，只允许字母、数字、点、下划线和短横线，
    防止远程清单通过斜杠或 ``..`` 把文件写到缓存目录之外。
    """
    if not isinstance(value, str) or not value:
        raise RuntimeUpdateError("{} 不能为空".format(field_name))
    allowed = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789-_."
    if any(char not in allowed for char in value):
        raise RuntimeUpdateError("{} 包含非法字符".format(field_name))
    return value


def _validate_manifest(manifest):
    """校验远程发布清单，并返回下载所需的标准字段。

    清单必须使用当前支持的 schema=1；ZIP 必须位于 ``dist/releases``，文件名
    以 ``.zip`` 结尾；SHA-256 必须是 64 位十六进制字符串；声明大小必须为正数
    且不超过全局上限。任何一项不符合要求都禁止下载或加载。
    """
    if not isinstance(manifest, dict) or manifest.get("schema") != 1:
        raise RuntimeUpdateError("不支持的远程清单格式")

    release_id = _safe_name(manifest.get("release_id"), "release_id")
    package = manifest.get("package")
    if not isinstance(package, dict):
        raise RuntimeUpdateError("远程清单缺少 package")

    package_path = package.get("path")
    if (
        not isinstance(package_path, str)
        or not package_path.startswith("dist/releases/")
        or ".." in package_path
        or not package_path.endswith(".zip")
    ):
        raise RuntimeUpdateError("远程包路径不合法")

    expected_sha256 = package.get("sha256", "").lower()
    if len(expected_sha256) != 64 or any(
        char not in "0123456789abcdef" for char in expected_sha256
    ):
        raise RuntimeUpdateError("远程包 SHA-256 不合法")

    package_size = package.get("size")
    if not isinstance(package_size, int) or not 0 < package_size <= MAX_PACKAGE_BYTES:
        raise RuntimeUpdateError("远程包大小不合法")

    return release_id, package_path, expected_sha256, package_size


def _download(url, destination, expected_size=None):
    """以流式方式下载单个文件，并执行双重大小限制。

    连接超时和读取超时分开设置，避免网络异常时长期卡住脚本启动。响应头中的
    ``content-length`` 只能作为提前拒绝依据，不能完全信任，所以读取每个分块后
    还会累计真实字节数。运行时 ZIP 另外要求真实大小与清单声明值完全一致。
    """
    response = requests.get(url, timeout=(4, 12), stream=True)
    response.raise_for_status()

    content_length = response.headers.get("content-length")
    if content_length and int(content_length) > MAX_PACKAGE_BYTES:
        response.close()
        raise RuntimeUpdateError("远程文件超过大小限制")

    received = 0
    with open(destination, "wb") as file_obj:
        for chunk in response.iter_content(64 * 1024):
            if not chunk:
                continue
            received += len(chunk)
            if received > MAX_PACKAGE_BYTES:
                response.close()
                raise RuntimeUpdateError("远程文件超过大小限制")
            file_obj.write(chunk)
    response.close()

    if expected_size is not None and received != expected_size:
        raise RuntimeUpdateError(
            "远程包大小不匹配：期望 {}，实际 {}".format(expected_size, received)
        )


def _fetch_manifest():
    """按源优先级获取并验证 ``latest.json``。

    查询参数每 5 分钟变化一次，用于区分普通 HTTP 缓存请求；它不能保证刷新
    jsDelivr 的分支缓存，发布流程仍必须调用官方 purge 地址。某个源请求失败、
    返回非 2xx、JSON 损坏或清单校验失败时，会记录原因并继续尝试下一个源。
    """
    errors = []
    cache_buster = int(time.time() // 300)
    for source_base in SOURCE_BASES:
        manifest_url = source_base + MANIFEST_PATH + "?v={}".format(cache_buster)
        try:
            response = requests.get(manifest_url, timeout=(4, 8))
            response.raise_for_status()
            manifest = response.json()
            _validate_manifest(manifest)
            return manifest, source_base
        except Exception as exc:
            errors.append("{}: {}".format(source_base, exc))
    raise RuntimeUpdateError("无法获取远程清单；{}".format(" | ".join(errors)))


def _download_package(package_path, expected_sha256, expected_size, preferred_base):
    """下载发布 ZIP，并同时验证精确大小和 SHA-256。

    优先从成功提供清单的源下载，保证清单和 ZIP 尽量来自同一 CDN 视图；失败后
    再尝试另一个源。每次重试前删除旧临时文件，所有源都失败时也会清理残留，
    未通过哈希校验的内容绝不会进入 releases 目录。
    """
    os.makedirs(CACHE_ROOT, exist_ok=True)
    temporary_path = os.path.join(CACHE_ROOT, "runtime-download.tmp")
    errors = []

    bases = [preferred_base]
    bases.extend(base for base in SOURCE_BASES if base != preferred_base)
    for source_base in bases:
        try:
            if os.path.exists(temporary_path):
                os.remove(temporary_path)
            _download(source_base + package_path, temporary_path, expected_size)
            actual_sha256 = _sha256(temporary_path)
            if actual_sha256 != expected_sha256:
                raise RuntimeUpdateError(
                    "远程包校验失败：期望 {}，实际 {}".format(
                        expected_sha256,
                        actual_sha256,
                    )
                )
            return temporary_path
        except Exception as exc:
            errors.append("{}: {}".format(source_base, exc))

    if os.path.exists(temporary_path):
        os.remove(temporary_path)
    raise RuntimeUpdateError("无法下载远程包；{}".format(" | ".join(errors)))


def _extract_package(archive_path, release_id):
    """把验证过的 ZIP 安全解压到内容标识对应的缓存目录。

    解压先写入 ``.staging`` 临时目录，并检查 ZIP 每个成员解析后的真实路径都在
    临时目录内部，阻止 ``../`` 或绝对路径造成目录穿越。全部解压完成后还必须
    找到 ``erchong_runtime/runtime_entry.py``，最后才整体替换正式发布目录。
    已存在且含入口的同一 release_id 会直接复用，不重复解压。
    """
    releases_root = os.path.join(CACHE_ROOT, "releases")
    release_root = os.path.join(releases_root, release_id)
    runtime_entry = os.path.join(release_root, RUNTIME_PACKAGE, "runtime_entry.py")
    if os.path.isfile(runtime_entry):
        return release_root

    staging_root = release_root + ".staging"
    shutil.rmtree(staging_root, ignore_errors=True)
    os.makedirs(staging_root, exist_ok=True)

    staging_real = os.path.realpath(staging_root)
    try:
        with zipfile.ZipFile(archive_path, "r") as archive:
            for member in archive.infolist():
                target_path = os.path.realpath(os.path.join(staging_root, member.filename))
                if target_path != staging_real and not target_path.startswith(
                    staging_real + os.sep
                ):
                    raise RuntimeUpdateError("远程包包含越界路径")
                archive.extract(member, staging_root)

        staged_entry = os.path.join(
            staging_root,
            RUNTIME_PACKAGE,
            "runtime_entry.py",
        )
        if not os.path.isfile(staged_entry):
            raise RuntimeUpdateError("远程包缺少 runtime_entry.py")

        shutil.rmtree(release_root, ignore_errors=True)
        os.replace(staging_root, release_root)
        return release_root
    except Exception:
        shutil.rmtree(staging_root, ignore_errors=True)
        raise


def _import_runtime(release_root):
    """从指定发布目录重新导入远程业务入口。

    发布目录加入 ``sys.path`` 后，先删除同名远程包及其子模块的旧缓存，避免脚本
    在同一 Python 进程内重启时混用新旧模块对象，然后再导入稳定入口模块。
    """
    if release_root not in sys.path:
        sys.path.insert(0, release_root)

    for module_name in list(sys.modules):
        if module_name == RUNTIME_PACKAGE or module_name.startswith(
            RUNTIME_PACKAGE + "."
        ):
            del sys.modules[module_name]

    return importlib.import_module(RUNTIME_PACKAGE + ".runtime_entry")


def _active_release_root():
    """读取上次成功版本，返回可用的发布根目录。

    只有 ``active.json`` 格式正确、release_id 安全且运行时入口仍存在时才返回；
    文件缺失、缓存被手动删除或 JSON 损坏均视为没有可用缓存，由上层继续回退。
    """
    active_path = os.path.join(CACHE_ROOT, "active.json")
    if not os.path.isfile(active_path):
        return None
    try:
        active = _read_json(active_path)
        release_id = _safe_name(active.get("release_id"), "release_id")
        release_root = os.path.join(CACHE_ROOT, "releases", release_id)
        runtime_entry = os.path.join(
            release_root,
            RUNTIME_PACKAGE,
            "runtime_entry.py",
        )
        if os.path.isfile(runtime_entry):
            return release_root
    except Exception as exc:
        print("读取远程运行时缓存失败：{}".format(exc))
    return None


def _load_remote_runtime():
    """检查在线清单，准备对应缓存并导入远程运行时。

    若 release_id 已完整缓存则跳过下载；否则依次执行下载、哈希校验和安全解压。
    ``active.json`` 特意放在 ``_import_runtime`` 成功之后写入，确保导入阶段发生的
    语法错误、缺少依赖或包结构错误不会把坏版本标记为活动版本。
    """
    manifest, preferred_base = _fetch_manifest()
    release_id, package_path, expected_sha256, expected_size = _validate_manifest(
        manifest
    )
    release_root = os.path.join(CACHE_ROOT, "releases", release_id)
    runtime_entry = os.path.join(release_root, RUNTIME_PACKAGE, "runtime_entry.py")

    # 用入口文件是否已经存在区分“本次下载”与“已有远程缓存”。两种情况都
    # 属于在线清单对应的远程版本，但日志应明确告诉维护者是否实际发生了下载。
    is_cached = os.path.isfile(runtime_entry)
    if not is_cached:
        archive_path = _download_package(
            package_path,
            expected_sha256,
            expected_size,
            preferred_base,
        )
        try:
            release_root = _extract_package(archive_path, release_id)
        finally:
            if os.path.exists(archive_path):
                os.remove(archive_path)

    runtime = _import_runtime(release_root)
    _write_json_atomic(
        os.path.join(CACHE_ROOT, "active.json"),
        {
            "release_id": release_id,
            "app_version": manifest.get("app_version", ""),
            "sha256": expected_sha256,
        },
    )
    if is_cached:
        print("已加载已缓存的远程运行时：{}".format(release_id))
    else:
        print("已下载并加载远程运行时：{}".format(release_id))
    return runtime


def _load_cached_runtime():
    """在线更新失败时，导入 ``active.json`` 指向的最后成功缓存。"""
    release_root = _active_release_root()
    if release_root is None:
        return None
    runtime = _import_runtime(release_root)
    print("已加载上次缓存的远程运行时：{}".format(os.path.basename(release_root)))
    return runtime


def _load_bundled_runtime():
    """设备没有可用远程缓存时，加载最初导入工程中自带的业务入口。"""
    print("远程运行时不可用，使用 AScript 工程内置版本")
    return importlib.import_module(__package__ + ".runtime_entry")


def start():
    """按照“在线版本 -> 上次缓存 -> 工程内置版本”的顺序启动业务入口。

    每层都独立捕获异常并输出原因，保证单次网络故障或缓存损坏不会直接导致脚本
    无法打开。最终选定的运行时统一调用 ``runtime.start()`` 展示配置界面。
    """
    runtime = None
    try:
        runtime = _load_remote_runtime()
    except Exception as exc:
        print("远程更新检查失败：{}".format(exc))

    if runtime is None:
        try:
            runtime = _load_cached_runtime()
        except Exception as exc:
            print("缓存运行时加载失败：{}".format(exc))

    if runtime is None:
        runtime = _load_bundled_runtime()

    runtime.start()
