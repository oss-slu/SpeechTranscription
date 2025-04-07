from customtkinter import *
from PIL import Image
import matplotlib.pyplot as plt
import sys
import os

def resource_path(relative_path):
    if hasattr(sys, '_MEIPASS'):
        return os.path.join(sys._MEIPASS, relative_path)
    return os.path.join(os.path.abspath("."), relative_path)

def scale_image(image_path, size=(30, 30)):
    image = Image.open(resource_path(image_path))
    return CTkImage(light_image=image.resize(size), dark_image=image.resize(size), size=size)

LOCK_ICON = scale_image("images/locked_icon.png")
UNLOCK_ICON = scale_image("images/unlocked_icon.png")
CLEAR_ICON = scale_image("images/clear_icon.png")

def createButton(master, text, row, column, command=None, **kwargs):
    btn = CTkButton(
        master=master,
        text=text,
        command=command,
        height=kwargs.get('height', 60),
        width=kwargs.get('width', 100),
        font=kwargs.get('font', ("Arial", 14))
    )
    if row is not None and column is not None:
        btn.grid(
            row=row,
            column=column,
            padx=kwargs.get('padx', 10),
            pady=kwargs.get('pady', 10),
            rowspan=kwargs.get('rowspan', 1),
            columnspan=kwargs.get('columnspan', 1),
            sticky=NSEW
        )
    if kwargs.get('lock', True):
        lockItem(btn)
    return btn

def unlockItem(item):
    item.configure(state="normal")

def lockItem(item):
    item.configure(state="disabled")

def plotAudio(time, signal):
    plt.figure(1)
    plt.title("Audio Wave")
    plt.xlabel("Time")
    plt.plot(time, signal)
    plt.show()