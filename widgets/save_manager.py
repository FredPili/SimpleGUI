from tkinter import *
from tkinter import ttk
from tkinter import filedialog

class SaveManager(ttk.Frame) :
    def __init__(self, root, initialdir, load_command=None, savecommand=None, load=True, save=True) :
        super().__init__(root)

        self.initialdir = initialdir
        self.load_command = load_command
        self.save_command = savecommand

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # Mainframe container
        frame = ttk.Frame(self)
        frame.grid(column=0, row=0, sticky="news")
        
        # Load button
        if load :
            load_button = ttk.Button(frame, text="Load", command=self.load)
            load_button.grid(column=0, row=0, sticky="ew")
            load_button.grid_configure(padx=2)
            frame.grid_columnconfigure(0, weight=1)
        
        # Save button
        if save :
            save_button = ttk.Button(frame, text="Save", command=self.save)
            save_button.grid(column=1, row=0, sticky="ew")
            save_button.grid_configure(padx=2)
            frame.grid_columnconfigure(1, weight=1)

        # Mainframe grid configure
        frame.grid_rowconfigure(0, weight=1)

    def load(self) :
        filename = filedialog.askopenfilename(
            initialdir=self.initialdir,
            filetypes=[("JSON files", "*.json")],
        )
        if filename and self.load_command :
            self.load_command(filename)

    def save(self) :
        filename = filedialog.asksaveasfilename(
            initialdir=self.initialdir,
            filetypes=[("JSON files", "*.json")],
        )
        if filename and self.save_command :
            self.save_command(filename)

    def set_load_command(self, load_command) :
        self.load_command = load_command

    def set_save_command(self, save_command) :
        self.save_command = save_command


if __name__ == "__main__" :
    root = Tk()
    root.title("SaveManager Test")
    
    import os
    save_manager = SaveManager(
        root,
        initialdir=os.path.abspath(os.path.dirname(__file__))
    )
    save_manager.grid(column=0, row=0, sticky="news")

    def load_command(filename) :
        print("Load command !")
    
    def save_command(filename) :
        print("Save command !")

    save_manager.set_load_command(load_command)
    save_manager.set_save_command(save_command)

    root.grid_columnconfigure(0, weight=1)
    root.grid_rowconfigure(0, weight=1)

    root.mainloop()