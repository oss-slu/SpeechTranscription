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
    app_path = os.path.dirname(sys.executable)
    system = platform.system()

    if system == "Windows":
        possible_java_paths = [
            os.path.join(base_path, "jre", "bin", "java.exe"),
            os.path.join(app_path, "jre", "bin", "java.exe"),
        ]

    elif system == "Darwin":  # macOS
        possible_java_paths = [
            os.path.join(base_path, "jre", "Contents", "Home", "bin", "java"),
            os.path.join(app_path, "jre", "Contents", "Home", "bin", "java"),
            os.path.join(app_path, "..", "Resources", "jre", "Contents", "Home", "bin", "java"),
        ]

    else:
        possible_java_paths = [
            os.path.join(base_path, "jre", "bin", "java"),
            os.path.join(app_path, "jre", "bin", "java"),
        ]

    print("sys.frozen:", getattr(sys, "frozen", False))
    print("sys._MEIPASS:", getattr(sys, "_MEIPASS", "NOT SET"))
    print("sys.executable:", sys.executable)
    print("System:", system)

    for java_exe in possible_java_paths:
        java_exe = os.path.abspath(java_exe)
        print("Looking for Java at:", java_exe)

        if os.path.exists(java_exe):
            java_home = os.path.dirname(os.path.dirname(java_exe))

            os.environ["JAVA_HOME"] = java_home
            os.environ["PATH"] = os.path.join(java_home, "bin") + os.pathsep + os.environ.get("PATH", "")

            print("Using Java from:", shutil.which("java"))
            print("JAVA_HOME set to:", java_home)
            return java_exe

    print("Bundled Java NOT found")
    return None