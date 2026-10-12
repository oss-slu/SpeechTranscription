"""Download the NLTK data the app needs into a folder for PyInstaller to bundle.

Usage: python scripts/bundle_nltk_data.py <target_dir>

Exits non-zero if any package fails to download or the app's NLTK calls fail
when NLTK is restricted to <target_dir>, so CI cannot ship a bundle that is
missing data (the packaged app never downloads NLTK data at runtime).
"""

import os
import sys

import nltk

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import nltk_resources  # noqa: E402


def main():
    if len(sys.argv) != 2:
        sys.exit("usage: python scripts/bundle_nltk_data.py <target_dir>")
    target_dir = os.path.abspath(sys.argv[1])
    # NLTK refuses to download into group- or world-writable directories.
    os.makedirs(target_dir, mode=0o755, exist_ok=True)
    os.chmod(target_dir, 0o755)

    for package in nltk_resources.PACKAGES:
        print(f"Downloading {package}")
        nltk.download(package, download_dir=target_dir, quiet=True, raise_on_error=True)

    nltk_resources.verify(target_dir)
    print(f"NLTK data verified in {target_dir}")


if __name__ == "__main__":
    main()
