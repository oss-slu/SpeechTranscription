# components/constants.py
from customtkinter import *
from PIL import Image
import sys
import os

WIDTH = 1500
HEIGHT = 740
SETTINGS_FILE = "user_settings.txt"

def resource_path(relative_path):
    if hasattr(sys, '_MEIPASS'):
        return os.path.join(sys._MEIPASS, relative_path)
    return os.path.join(os.path.abspath("."), relative_path)

def scale_image(image_path, size=(30, 30)):
    image = Image.open(resource_path(image_path))
    image = image.resize(size)
    return CTkImage(light_image=image, dark_image=image, size=size)

LOCK_ICON = scale_image("images/locked_icon.png", size=(30, 30))
UNLOCK_ICON = scale_image("images/unlocked_icon.png", size=(30, 30))
CLEAR_ICON = scale_image("images/clear_icon.png", size=(30, 30))