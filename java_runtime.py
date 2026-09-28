import os
import sys
import shutil
import stat


def get_base_path():
    if getattr(sys, "frozen", False):
        return getattr(sys, "_MEIPASS", os.path.dirname(sys.executable))
    return os.path.dirname(os.path.abspath(__file__))


def _java_candidates(base_path):
    """Return possible bundled Java executable paths (Windows + macOS/Linux)."""
    roots = [
        base_path,
        os.path.dirname(sys.executable),
    ]
    # Temurin on macOS may keep Contents/Home if not normalized in CI.
    relative_bins = [
        ("jre", "bin", "java"),
        ("jre", "bin", "java.exe"),
        ("jre", "Contents", "Home", "bin", "java"),
        ("jre", "Contents", "Home", "bin", "java.exe"),
    ]
    seen = set()
    candidates = []
    for root in roots:
        for parts in relative_bins:
            path = os.path.join(root, *parts)
            if path not in seen:
                seen.add(path)
                candidates.append(path)
    return candidates


def _java_home_from_bin(java_bin):
    # .../jre/bin/java -> .../jre
    # .../jre/Contents/Home/bin/java -> .../jre/Contents/Home
    return os.path.dirname(os.path.dirname(java_bin))


def configure_bundled_java():
    base_path = get_base_path()

    print("sys.frozen:", getattr(sys, "frozen", False))
    print("sys._MEIPASS:", getattr(sys, "_MEIPASS", "NOT SET"))
    print("sys.executable:", sys.executable)

    for java_bin in _java_candidates(base_path):
        print("Looking for Java at:", java_bin)

        if os.path.exists(java_bin):
            if not java_bin.endswith(".exe"):
                mode = os.stat(java_bin).st_mode
                if not mode & stat.S_IXUSR:
                    os.chmod(java_bin, mode | stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH)
            java_home = _java_home_from_bin(java_bin)
            os.environ["JAVA_HOME"] = java_home
            os.environ["PATH"] = os.path.join(java_home, "bin") + os.pathsep + os.environ.get("PATH", "")

            print("Using Java from:", shutil.which("java"))
            print("JAVA_HOME set to:", java_home)
            return java_bin

    print("Bundled Java NOT found")
    return None
