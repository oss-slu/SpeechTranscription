import os
import sys
import shutil

def get_base_path():
    if getattr(sys, "frozen", False):
        return os.path.dirname(sys.executable)
    return os.path.dirname(os.path.abspath(__file__))


def configure_bundled_java():
    base_path = get_base_path()
    java_home = os.path.join(base_path, "jre")
    java_exe = os.path.join(java_home, "bin", "java.exe")

    print("Looking for Java at:", java_exe)

    if os.path.exists(java_exe):
        os.environ["JAVA_HOME"] = java_home
        os.environ["PATH"] = os.path.join(java_home, "bin") + os.pathsep + os.environ.get("PATH", "")

        print("Using Java from:", shutil.which("java"))
        print("Looking for Java at:", java_exe)
        return java_exe

    print("Bundled Java NOT found")
    
    return None