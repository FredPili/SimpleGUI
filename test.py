from tkinter import *
from PIL import Image, ImageTk
from tkinter import ttk

class ImageApp:
    def __init__(self, root):
        root.title("Image Viewer")
        mainframe = ttk.Frame(root)
        mainframe.pack()

        # Load image and force into memory
        image = Image.open("placeholder.jpeg").convert("RGB")
        photo = ImageTk.PhotoImage(image)

        # Store image as instance attributes (to avoid GC)
        # self.image = image
        self.photo = photo

        # Create and pack canvas
        self.canvas = Canvas(mainframe, width=image.width, height=image.height)
        self.canvas.grid(column=0, row=0)

        # Draw image on canvas
        self.canvas.create_image(0, 0, image=self.photo, anchor="nw")
        # self.canvas.image = self.photo  # extra reference on widget

# Run the GUI
if __name__ == "__main__":
    root = Tk()
    app = ImageApp(root)
    root.mainloop()
