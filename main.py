from tkinter import *
from viewer.app import WaveViewer
import os

if __name__ == "__main__" :
    root = Tk()
    root.title("Wave Viewer")
    initialdir = os.path.abspath(os.path.join(os.path.dirname(__file__), "saves"))
    wave_viewer = WaveViewer(root, initialdir)
    wave_viewer.grid(column=1, row=1, sticky="news")
    root.grid_columnconfigure(0, weight=1)
    root.grid_rowconfigure(0, weight=1)
    root.mainloop()