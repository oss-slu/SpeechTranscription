# components/utils.py
from customtkinter import *

def createButton(master, text: str, row: int, column: int, command=None, padx=10, pady=10, 
                rowspan=1, columnspan=1, height=60, width=100, font=("Arial", 14), lock=True):
    button = CTkButton(master, text=text, height=height, width=width, command=command, font=font)
    if row is not None and column is not None:
        button.grid(row=row, column=column, rowspan=rowspan, columnspan=columnspan, 
                  padx=padx, pady=pady, sticky=W + E)
    if lock:
        lockItem(button)
    return button

def unlockItem(item):
    item.configure(state="normal")

def lockItem(item):
    item.configure(state="disabled")

def unlockMultipleItems(items):
    for item in items:
        unlockItem(item)

def lockMultipleItems(items):
    for item in items:
        lockItem(item)