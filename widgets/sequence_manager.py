from tkinter import *
from tkinter import ttk
from widgets.save_manager import SaveManager
from core.sequence import SequencePlayer, load_sequence_config, make_sequence
import os

class SequenceManager(ttk.Frame) :
    def __init__(self, root, initialdir, sequence=None, callback=None) :
        super().__init__(root)

        self.sequence=sequence
        if sequence is not None :
            self.timestep = len(sequence)
        else :
            self.timestep = None

        # Mainframe
        mainframe = ttk.Frame(self)
        mainframe.grid(column=0, row=0, sticky="news")
        mainframe.grid_columnconfigure((0,1,2,3,4), weight=1)
        mainframe.grid_rowconfigure((0,1), weight=1)

        # Load button
        self.save_manager = SaveManager(mainframe, initialdir, self.load_sequence, load=True, save=False)
        self.save_manager.grid(column=0, row=0, sticky="news")

        # SequencePlayer
        self.player = SequencePlayer(sequence=sequence, callback=callback)
        Button(mainframe, text="Start", command=self.player.start).grid(column=1, row=0, sticky="news")
        Button(mainframe, text="Pause", command=self.player.pause).grid(column=2, row=0, sticky="news")
        Button(mainframe, text="Resume", command=self.player.resume).grid(column=3, row=0, sticky="news")
        Button(mainframe, text="Stop", command=self.player.stop).grid(column=4, row=0, sticky="news")

        # Label to display informations
        self.label = ttk.Label(mainframe, text="SequenceManager infos")
        self.label.grid(column=0, columnspan=4, row=1, sticky="news")

        # Padding
        for child in mainframe.winfo_children() :
            child.grid_configure(padx=2)

    def set_load_command(self, load_command) :
        self.save_manager.set_load_command(load_command)

    def load_sequence(self, filename) :
        self.player.stop()
        sequence_config = load_sequence_config(filename)
        self.timestep = sequence_config["timestep"]
        self.sequence = make_sequence(sequence_config)
        self.player.set_timestep(self.timestep)
        self.player.set_sequence(self.sequence)
        nb_steps = len(self.sequence)
        total_time = nb_steps * self.timestep
        self.label.config(text=f"Loaded sequence : {nb_steps} steps - {total_time:.2f} seconds")


if __name__ == "__main__" :
    root = Tk()
    root.title("SequenceManager Test")

    def on_step(step) :
        print("Step:", step)
        nb_steps = len(sequence_manager.player.sequence)

    import os
    sequence_manager = SequenceManager(
        root, 
        initialdir=os.path.abspath(os.path.dirname(__file__)),
        callback=on_step
        )
    sequence_manager.grid(column=0, row=0, sticky="news")

    root.mainloop()