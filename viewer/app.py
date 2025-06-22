from tkinter import *
from tkinter import ttk
from core.events import EventBus, Events
from widgets.entry_bundle import EntryBundle
from widgets.frequency_editor import FrequencyEditor
from widgets.save_manager import SaveManager
from widgets.sequence_manager import SequenceManager
from core.generation import generate_wave, apply_fourier_transform
import matplotlib.pyplot as plt
import numpy as np
from PIL import Image, ImageTk


class WaveViewer(ttk.Frame) :
    def __init__(self, root, initialdir) :
        super().__init__(root)
        # Setup the event bus
        self.event_bus = EventBus()
        self.event_bus.subscribe(Events.PARAM_CHANGE, self.on_param_change)
        self.event_bus.subscribe(Events.DISPLAY_CHANGE, self.on_display_change)
        self.event_bus.subscribe(Events.PLAYER_STEP, self.on_step)

        self.root = root
        mainframe = ttk.Frame(self.root)
        mainframe.grid(column=0, row=0, sticky=(N, W, E, S))

        # ----------TOP Frame----------------------------
        top_frame = ttk.Frame(mainframe)
        top_frame.grid(column=0, row=0, sticky="news")
        #-----------Param Frame--------------------------
        param_frame = ttk.Frame(top_frame)
        param_frame.grid(column=0, row=0, sticky=(E, W))

        self.sample_bundle = EntryBundle(
            param_frame, 
            name="Nb samples", 
            default_value=500,
            type="int",            
            add_scale=True, 
            from_=2,
            to=500,
            callback=lambda: self.event_bus.publish(Events.PARAM_CHANGE),
            uniform="params"
            )
        self.sample_bundle.grid(column=0, row=0, sticky="nsew")


        self.length_bundle = EntryBundle(
            param_frame, 
            name="Length (s)", 
            default_value=1, 
            type="double",
            add_scale=True,
            from_=1,
            to=10,
            callback=lambda: self.event_bus.publish(Events.PARAM_CHANGE), 
            uniform="params"
            )
        self.length_bundle.grid(column=1, row=0, sticky="nsew")

        col_count, row_count = param_frame.grid_size()
        for col in range(col_count) :
            param_frame.grid_columnconfigure(col, weight=1, minsize=0)
        
        for row in range(row_count) :
            param_frame.grid_rowconfigure(row, weight=1, minsize=0)

        for child in param_frame.winfo_children() :
            child.grid_configure(padx=2, pady=2)

        #----------------SaveManager------------------------
        self.save_manager = SaveManager(top_frame, initialdir=initialdir)
        self.save_manager.grid(column=1, row=0, sticky="news")

        #---------------Sequence Manager--------------------
        self.sequence_manager = SequenceManager(top_frame, initialdir=initialdir, callback=self.on_step)
        self.sequence_manager.grid(column=2, row=0, sticky="news")

        #-------------TopFrame grid configure-----------------
        for child in top_frame.winfo_children() :
            child.grid_configure(padx=20)
        
        #-----------------Bottom Frame-----------------------
        bottom_frame = ttk.Frame(mainframe)
        bottom_frame.grid(column=0, row=1, sticky="news")

        #----------------Frequency Editor---------------------
        self.freq_editor = FrequencyEditor(bottom_frame, callback=lambda: self.event_bus.publish(Events.PARAM_CHANGE))
        self.freq_editor.grid(column=0, row=0, sticky="nesw")
        # Set the load command in the save manager
        self.save_manager.set_load_command(self.freq_editor.load_frequencies)
        self.save_manager.set_save_command(self.freq_editor.save_frequencies)

        #--------------Visualiazation Frame--------------------
        visu_frame = ttk.Frame(bottom_frame)
        visu_frame.grid(column=1, row=0, sticky=(E, W))

        # PLaceholder self.image to confirm the widhets positions
        self.width, self.height = 500, 500
        self.canvas = Canvas(visu_frame, width=self.width, height=self.height)
        self.canvas.grid(column=0, row=0, rowspan=2, sticky=(N, W, E, S))

        fourier_frame = ttk.Frame(visu_frame)
        fourier_frame.grid(column=1, row=0, sticky="news")
        self.fourier_checkval = IntVar()
        fourier_checkbox = ttk.Checkbutton(fourier_frame, text="Fourier Transform", variable=self.fourier_checkval, onvalue=1, offvalue=0, command=lambda: self.event_bus.publish(Events.PARAM_CHANGE))
        fourier_checkbox.grid(column=0, columnspan=2, row=0, sticky="new")
        self.ftype_var = StringVar(value="mag")
        ftype_mag_button = ttk.Radiobutton(fourier_frame, text="Magnitude", variable=self.ftype_var, value="mag", command=lambda: self.event_bus.publish(Events.PARAM_CHANGE))
        ftype_mag_button.grid(column=0, row=1, sticky="new")
        ftype_phase_button = ttk.Radiobutton(fourier_frame, text="Phase", variable=self.ftype_var, value="phase", command=lambda: self.event_bus.publish(Events.PARAM_CHANGE))
        ftype_phase_button.grid(column=1, row=1, sticky="new")

        for child in fourier_frame.winfo_children() :
            child.grid_configure(padx=2, pady=5)


        self.choices = ["gray", "viridis", "magma", "inferno", "managua", "ocean", "plasma", "jet", "coolwarm", "hsv"]
        self.cmap = plt.get_cmap("gray")
        choicesvar = StringVar(value=self.choices)
        self.listbox = Listbox(visu_frame, height=min(len(self.choices), 15), selectmode="browse", listvariable=choicesvar)
        self.listbox.grid(column=2, row=0, sticky="n")
        from functools import partial
        self.listbox.bind("<<ListboxSelect>>", lambda event: self.event_bus.publish(Events.DISPLAY_CHANGE))

        generate_button = ttk.Button(visu_frame, text="Generate Image", command=self.update)
        generate_button.grid(column=1, row=1, sticky="se")

        for child in visu_frame.winfo_children():
            child.grid_configure(padx=2, pady=2)

        for child in mainframe.winfo_children():
            child.grid_configure(padx=5, pady=5)

        self.update()

    def update(self) :
        self.generate_image()
        self.display_image()

    def generate_image(self, *args) :
        # Get general parameters 
        nb_samples = self.sample_bundle.get()
        length = self.length_bundle.get()
        # Get frequencies parameters
        freq_params = self.freq_editor.get_frequencies_param()
        # Generate wave
        self.image = generate_wave(freq_params, length, nb_samples)
        # Fourier transform
        if self.fourier_checkval.get() :
            phase = self.ftype_var.get() == "phase"
            self.image = apply_fourier_transform(self.image, phase)

    def display_image(self) :
        # Select cmap 
        if len(self.listbox.curselection()) == 0 :
            cmap = self.cmap
        else :
            cmap = plt.get_cmap(self.choices[self.listbox.curselection()[0]])
            self.cmap = cmap
        # Normalize image
        self.image = (self.image - np.min(self.image)) / (np.max(self.image) - np.min(self.image))
        # Apply cmap
        colored_image = cmap(self.image)
        # Convert image for Tkinter
        PIL_image = Image.fromarray((colored_image[:,:,:3]*255).astype(np.uint8)).resize((self.width, self.height), resample=Image.Resampling.NEAREST)
        display = ImageTk.PhotoImage(PIL_image)
        # Update display
        self.canvas.delete("all")
        self.canvas.create_image(0, 0, image=display, anchor="nw")
        self.canvas.image = display

    def on_param_change(self) :
        self.generate_image()
        self.display_image()

    def on_display_change(self) :
        self.display_image()

    def on_step(self, step) :
        step["phase"] = step["phase"] % 360
        step["angle"] = step["angle"] % 360
        self.root.after_idle(lambda: self.freq_editor.frequencies_widgets[1]["freq_frame"].set(step))

if __name__ == "__main__" :
    import os
    initialdir = os.path.abspath(os.path.dirname(__file__))
    root = Tk()
    root.title("WaveViewer Test")
    wave_viewer = WaveViewer(root, initialdir)
    root.mainloop()