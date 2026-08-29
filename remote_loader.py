"""下载、校验、缓存并加载当前业务运行时。"""

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


REPOSITORY = "qingushan/as-erchong"
RELEASE_BRANCH = "runtime"
MANIFEST_PATH = "dist/latest.json"
RUNTIME_PACKAGE = "erchong_runtime"
# 当前 Android AScript 中，向 R.sd 传入多个参数会返回多个独立路径组成的列表，
# 而不是拼接后的单一路径；这里传入一个相对路径，确保缓存根目录始终是可供
# os.path 使用的字符串。
CACHE_ROOT = R.sd("AScript/erchong_runtime")
MAX_PACKAGE_BYTES = 20 * 1024 * 1024

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
    pass


def _read_json(path):
    with open(path, "r", encoding="utf-8") as file_obj:
        return json.load(file_obj)


def _write_json_atomic(path, value):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    temporary_path = path + ".tmp"
    with open(temporary_path, "w", encoding="utf-8") as file_obj:
        json.dump(value, file_obj, ensure_ascii=False, indent=2)
    os.replace(temporary_path, path)


def _sha256(path):
    digest = hashlib.sha256()
    with open(path, "rb") as file_obj:
        for chunk in iter(lambda: file_obj.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _safe_name(value, field_name):
    if not isinstance(value, str) or not value:
        raise RuntimeUpdateError("{} 不能为空".format(field_name))
    allowed = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789-_."
    if any(char not in allowed for char in value):
        raise RuntimeUpdateError("{} 包含非法字符".format(field_name))
    return value


def _validate_manifest(manifest):
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
    if release_root not in sys.path:
        sys.path.insert(0, release_root)

    for module_name in list(sys.modules):
        if module_name == RUNTIME_PACKAGE or module_name.startswith(
            RUNTIME_PACKAGE + "."
        ):
            del sys.modules[module_name]

    return importlib.import_module(RUNTIME_PACKAGE + ".runtime_entry")


def _active_release_root():
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
    manifest, preferred_base = _fetch_manifest()
    release_id, package_path, expected_sha256, expected_size = _validate_manifest(
        manifest
    )
    release_root = os.path.join(CACHE_ROOT, "releases", release_id)
    runtime_entry = os.path.join(release_root, RUNTIME_PACKAGE, "runtime_entry.py")

    if not os.path.isfile(runtime_entry):
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
    print("已加载远程运行时：{}".format(release_id))
    return runtime


def _load_cached_runtime():
    release_root = _active_release_root()
    if release_root is None:
        return None
    runtime = _import_runtime(release_root)
    print("已加载上次缓存的远程运行时：{}".format(os.path.basename(release_root)))
    return runtime


def _load_bundled_runtime():
    print("远程运行时不可用，使用 AScript 工程内置版本")
    return importlib.import_module(__package__ + ".runtime_entry")


def start():
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
