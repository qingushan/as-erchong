"""构建内容可复现的 AScript 运行时 ZIP 及 ``latest.json``。

构建结果使用“版本号 + ZIP 内容哈希前 12 位”作为 release_id。只要打包内容相同，
ZIP 字节和文件名就保持相同；源码、UI 或注释发生变化时会生成新文件名，避免
GitHub/jsDelivr 把新内容与旧 ZIP 缓存混淆。工具只读取 ``VERSION``，不会替维护者
修改版本号。
"""

import ast
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
import sys
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen
import zipfile


# 所有路径都从脚本所在位置反推项目根目录，避免发布结果依赖执行命令时的当前
# 工作目录。dist 只保存发布清单和内容寻址 ZIP，不参与 AScript 本地业务导入。
PROJECT_ROOT = Path(__file__).resolve().parents[1]
DIST_ROOT = PROJECT_ROOT / "dist"
RELEASES_ROOT = DIST_ROOT / "releases"
RUNTIME_PACKAGE = "erchong_runtime"
INCLUDED_ROOT_FILES = ("runtime_entry.py",)
EXCLUDED_PARTS = {"__pycache__"}
EXCLUDED_SUFFIXES = {".pyc", ".pyo"}
# ZIP 默认记录源文件修改时间，同一份源码在不同电脑上会得到不同哈希。固定成员
# 时间戳并统一权限，确保相同文件内容生成完全相同的 ZIP 字节。
ZIP_TIMESTAMP = (2020, 1, 1, 0, 0, 0)

# 清单地址固定不变，jsDelivr 会按 URL 缓存它。该地址只应在 runtime 分支完成
# git push 后调用；如果在推送前调用，CDN 只会重新缓存旧清单。
JSDLIVR_PURGE_URL = (
    "https://purge.jsdelivr.net/gh/qingushan/as-erchong@runtime/"
    "dist/latest.json"
)


def read_version():
    """使用 AST 安全读取配置中的 VERSION 常量。

    不直接导入 ``res.config``，因为它属于 Android AScript 工程，本机发布环境不应
    加载设备端依赖或执行配置模块中的其他代码。
    """
    config_path = PROJECT_ROOT / "res" / "config.py"
    module = ast.parse(config_path.read_text(encoding="utf-8"))
    for node in module.body:
        if isinstance(node, ast.Assign):
            for target in node.targets:
                if isinstance(target, ast.Name) and target.id == "VERSION":
                    return ast.literal_eval(node.value)
    raise RuntimeError("未在 res/config.py 中找到 VERSION")


def runtime_files():
    """按稳定顺序枚举需要进入远程运行时的文件。

    远程包包含业务入口和整个 res 目录，因此 Python、UI、更新日志、字库和图片
    可以同步升级；稳定加载器、构建脚本、Git 元数据、字节码缓存不会进入 ZIP。
    """
    for root_file in INCLUDED_ROOT_FILES:
        source_path = PROJECT_ROOT / root_file
        yield source_path, Path(RUNTIME_PACKAGE) / root_file

    resource_root = PROJECT_ROOT / "res"
    for source_path in sorted(path for path in resource_root.rglob("*") if path.is_file()):
        relative_path = source_path.relative_to(PROJECT_ROOT)
        if EXCLUDED_PARTS.intersection(relative_path.parts):
            continue
        if source_path.suffix.lower() in EXCLUDED_SUFFIXES:
            continue
        yield source_path, Path(RUNTIME_PACKAGE) / relative_path


def zip_info(archive_path):
    """为 ZIP 成员创建固定时间、固定权限和固定压缩方式的元数据。"""
    info = zipfile.ZipInfo(archive_path.as_posix(), ZIP_TIMESTAMP)
    info.compress_type = zipfile.ZIP_DEFLATED
    info.external_attr = 0o644 << 16
    return info


def write_runtime_zip(destination):
    """把业务代码和资源写入目标 ZIP。

    AScript 工程源码目录未必都带 ``__init__.py``，远程运行时却需要作为标准 Python
    包动态导入，因此构建时为各级代码目录补充空的包标记文件。
    """
    package_directories = {
        Path(RUNTIME_PACKAGE),
        Path(RUNTIME_PACKAGE) / "res",
        Path(RUNTIME_PACKAGE) / "res" / "assets",
        Path(RUNTIME_PACKAGE) / "res" / "cloud_task",
        Path(RUNTIME_PACKAGE) / "res" / "task",
        Path(RUNTIME_PACKAGE) / "res" / "test",
        Path(RUNTIME_PACKAGE) / "res" / "ui",
        Path(RUNTIME_PACKAGE) / "res" / "util",
    }

    with zipfile.ZipFile(destination, "w") as archive:
        for directory in sorted(package_directories):
            init_path = directory / "__init__.py"
            archive.writestr(zip_info(init_path), b"")
        for source_path, archive_path in runtime_files():
            archive.writestr(zip_info(archive_path), source_path.read_bytes())


def sha256(path):
    """分块计算发布包 SHA-256，供 release_id 和远程清单共同使用。"""
    digest = hashlib.sha256()
    with path.open("rb") as file_obj:
        for chunk in iter(lambda: file_obj.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def purge_jsdelivr_cache():
    """请求 jsDelivr 删除 runtime 分支的最新清单缓存。

    该动作不会删除 GitHub 文件，也不会修改仓库；它只让 jsDelivr 下一次重新
    从 GitHub 获取 ``dist/latest.json``。函数单独提供为 ``--purge`` 模式，避免
    默认构建流程在 git push 之前清理缓存并重新缓存旧内容。

    清理接口返回 HTTP 200 且 JSON 中 ``status`` 为 ``finished`` 或 ``processing``
    才视为请求已被接受。网络错误和非预期响应会抛出异常，让发布流程明确失败。
    """
    request = Request(
        JSDLIVR_PURGE_URL,
        headers={"User-Agent": "erchong-runtime-release"},
    )
    try:
        with urlopen(request, timeout=30) as response:
            if response.status != 200:
                raise RuntimeError("jsDelivr 清理接口返回 HTTP {}".format(response.status))
            result = json.loads(response.read().decode("utf-8"))
    except (HTTPError, URLError) as exc:
        raise RuntimeError("jsDelivr 清理请求失败：{}".format(exc))

    status = result.get("status") if isinstance(result, dict) else None
    if status not in ("finished", "processing"):
        raise RuntimeError("jsDelivr 清理接口返回未知状态：{}".format(status))
    print("jsDelivr 清单缓存清理请求已接受：{}".format(status))
    return result


def main():
    """生成内容寻址 ZIP，并用其真实哈希和大小覆盖最新发布清单。

    ZIP 先写入临时文件，哈希确定后再移动到最终文件名；``latest.json`` 始终指向
    这次完整构建的结果。旧发布 ZIP 不删除，以便清单回滚到已验证版本。
    """
    # 清理模式不重新构建、不修改本地文件，只用于 git push 完成后的最后一步。
    if "--purge" in sys.argv[1:]:
        purge_jsdelivr_cache()
        return

    version = read_version()
    RELEASES_ROOT.mkdir(parents=True, exist_ok=True)

    temporary_path = RELEASES_ROOT / ".runtime-release.tmp"
    write_runtime_zip(temporary_path)
    package_sha256 = sha256(temporary_path)
    release_id = "v{}-{}".format(version, package_sha256[:12])
    package_name = "erchong-runtime-{}.zip".format(release_id)
    package_path = RELEASES_ROOT / package_name
    temporary_path.replace(package_path)

    manifest = {
        "schema": 1,
        "release_id": release_id,
        "app_version": version,
        "created_at": datetime.now(timezone.utc).replace(microsecond=0).isoformat(),
        "package": {
            "path": "dist/releases/{}".format(package_name),
            "sha256": package_sha256,
            "size": package_path.stat().st_size,
        },
    }
    manifest_path = DIST_ROOT / "latest.json"
    manifest_path.write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )

    print("运行时发布包构建完成")
    print("  发布标识: {}".format(release_id))
    print("  发布包: {}".format(package_path.relative_to(PROJECT_ROOT)))
    print("  SHA-256: {}".format(package_sha256))
    print("  清单: {}".format(manifest_path.relative_to(PROJECT_ROOT)))


if __name__ == "__main__":
    main()
