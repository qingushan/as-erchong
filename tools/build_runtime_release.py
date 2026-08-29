"""构建内容可复现的 AScript 运行时包及其发布清单。"""

import ast
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
import zipfile


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DIST_ROOT = PROJECT_ROOT / "dist"
RELEASES_ROOT = DIST_ROOT / "releases"
RUNTIME_PACKAGE = "erchong_runtime"
INCLUDED_ROOT_FILES = ("runtime_entry.py",)
EXCLUDED_PARTS = {"__pycache__"}
EXCLUDED_SUFFIXES = {".pyc", ".pyo"}
ZIP_TIMESTAMP = (2020, 1, 1, 0, 0, 0)


def read_version():
    config_path = PROJECT_ROOT / "res" / "config.py"
    module = ast.parse(config_path.read_text(encoding="utf-8"))
    for node in module.body:
        if isinstance(node, ast.Assign):
            for target in node.targets:
                if isinstance(target, ast.Name) and target.id == "VERSION":
                    return ast.literal_eval(node.value)
    raise RuntimeError("未在 res/config.py 中找到 VERSION")


def runtime_files():
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
    info = zipfile.ZipInfo(archive_path.as_posix(), ZIP_TIMESTAMP)
    info.compress_type = zipfile.ZIP_DEFLATED
    info.external_attr = 0o644 << 16
    return info


def write_runtime_zip(destination):
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
    digest = hashlib.sha256()
    with path.open("rb") as file_obj:
        for chunk in iter(lambda: file_obj.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def main():
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
