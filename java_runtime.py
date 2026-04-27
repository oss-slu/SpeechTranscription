import os
import sys
import shutil
import platform

def get_base_path():
    if getattr(sys, "frozen", False):
        return getattr(sys, "_MEIPASS", os.path.dirname(sys.executable))
    return os.path.dirname(os.path.abspath(__file__))

def configure_bundled_java():
    base_path = get_base_path()

    # Define possible relative paths to the 'java' executable
    if platform.system() == "Windows":
        candidates = [
            os.path.join("jre", "bin", "java.exe"),
            os.path.join("bin", "java.exe"),
        ]
    elif platform.system() == "Darwin":
        candidates = [
            os.path.join("jre", "Contents", "Home", "bin", "java"),
            os.path.join("jre", "bin", "java"),
            os.path.join("bin", "java"),
        ]
    else:
        candidates = [
            os.path.join("jre", "bin", "java"),
            os.path.join("bin", "java"),
        ]

    print("sys.frozen:", getattr(sys, "frozen", False))
    print("sys.executable:", sys.executable)

    for rel_path in candidates:
        # Check both the bundle root and the executable root
        for root in [base_path, os.path.dirname(sys.executable)]:
            java_exe = os.path.abspath(os.path.join(root, rel_path))
            print("Looking for Java at:", java_exe)

            if os.path.exists(java_exe):
                # For macOS, JAVA_HOME is usually the directory containing 'bin'
                # or the 'Contents/Home' directory.
                if "Contents/Home" in java_exe:
                    java_home = java_exe.split("/bin/java")[0]
                else:
                    java_home = os.path.dirname(os.path.dirname(java_exe))
                
                os.environ["JAVA_HOME"] = java_home
                bin_dir = os.path.dirname(java_exe)
                os.environ["PATH"] = bin_dir + os.pathsep + os.environ.get("PATH", "")

                print("Using Java from:", java_exe)
                print("JAVA_HOME set to:", java_home)
                return java_exe

    print("Bundled Java NOT found")
    return None