#!/bin/bash
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"
BASE_DIR="$SCRIPT_DIR/.."

cd "$BASE_DIR"

# Download JRE if not present
if [ ! -d "bundled_jre" ]; then
    echo "Downloading Temurin JRE 17 for local build..."
    curl -L "https://github.com/adoptium/temurin17-binaries/releases/download/jdk-17.0.12%2B7/OpenJDK17U-jre_x64_mac_hotspot_17.0.12_7.tar.gz" -o jre.tar.gz
    mkdir -p bundled_jre
    tar -xzf jre.tar.gz -C bundled_jre --strip-components 1
    rm jre.tar.gz
fi

# Set JAVA_HOME to bundled JRE for the build process (if needed by any scripts)
export JAVA_HOME="$BASE_DIR/bundled_jre/Contents/Home"
export PATH="$JAVA_HOME/bin:$PATH"

echo "Building with PyInstaller..."
pyinstaller --noconfirm Saltify.spec