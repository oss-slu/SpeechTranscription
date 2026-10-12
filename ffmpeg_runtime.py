import os
import shutil
import stat

from java_runtime import get_base_path


def _ensure_executable(path):
    mode = os.stat(path).st_mode
    if not mode & stat.S_IXUSR:
        os.chmod(path, mode | stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH)


def configure_bundled_ffmpeg():
    """Put bundled ffmpeg/ffprobe first on PATH.

    Must run before pydub is imported: pydub resolves the ffmpeg path at import time.
    Whisper shells out to "ffmpeg" at runtime, so PATH covers it too.
    """
    bin_dir = os.path.join(get_base_path(), "ffmpeg_bin")
    ffmpeg = os.path.join(bin_dir, "ffmpeg")
    if not os.path.exists(ffmpeg):
        print("Bundled ffmpeg NOT found")
        return None

    for name in ("ffmpeg", "ffprobe"):
        path = os.path.join(bin_dir, name)
        if os.path.exists(path):
            _ensure_executable(path)

    os.environ["PATH"] = bin_dir + os.pathsep + os.environ.get("PATH", "")
    print("Using ffmpeg from:", shutil.which("ffmpeg"))
    return ffmpeg
