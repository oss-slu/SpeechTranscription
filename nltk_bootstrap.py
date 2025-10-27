import os
import sys
import nltk

# Detect if running in PyInstaller bundle
if getattr(sys, 'frozen', False):
    base_path = sys._MEIPASS
else:
    base_path = os.path.dirname(__file__)

nltk_data_path = os.path.join(base_path, "nltk_data")

if os.path.exists(nltk_data_path):
    nltk.data.path.insert(0, nltk_data_path)
    print(f"[INFO] Using bundled NLTK data at: {nltk_data_path}")
else:
    print(f"[WARN] nltk_data directory not found at {nltk_data_path}")
