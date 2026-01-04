"""Build script for creating standalone executables.

Run this script on the platform you want to target. It requires
PyInstaller to be installed (``pip install pyinstaller``). The resulting
artifacts will appear in ``dist/``.
"""

from __future__ import annotations

import platform
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).parent
APP_ENTRY = ROOT / "app" / "main.py"
BUILD_DIR = ROOT / "build"
DIST_DIR = ROOT / "dist"
SPEC_FILE = ROOT / "home_student_extractor.spec"


def ensure_pyinstaller() -> None:
    try:
        import pyinstaller  # type: ignore  # noqa: F401
    except ImportError:
        print("PyInstaller is not installed. Installing now...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "pyinstaller"])


def build() -> None:
    ensure_pyinstaller()
    if SPEC_FILE.exists():
        SPEC_FILE.unlink()
    if BUILD_DIR.exists():
        shutil.rmtree(BUILD_DIR)

    name_suffix = "win" if platform.system() == "Windows" else "mac"
    executable_name = f"HomeStudentExtractor-{name_suffix}"

    cmd = [
        sys.executable,
        "-m",
        "PyInstaller",
        "--name",
        executable_name,
        "--windowed",
        "--noconfirm",
        "--clean",
        "--add-data",
        f"{APP_ENTRY}{platform_delimiter()}.",
        str(APP_ENTRY),
    ]
    print("Running:", " ".join(cmd))
    subprocess.check_call(cmd)

    archive_base = DIST_DIR / executable_name
    archive_path = archive_base.with_suffix(".zip")
    if archive_path.exists():
        archive_path.unlink()
    shutil.make_archive(str(archive_base), "zip", root_dir=DIST_DIR, base_dir=executable_name)

    print(f"Build complete. Executable located in: {DIST_DIR / executable_name}")
    print(f"Zipped bundle created at: {archive_path}")


def platform_delimiter() -> str:
    return ";" if platform.system() == "Windows" else ":"


if __name__ == "__main__":
    build()
