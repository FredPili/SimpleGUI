from tkinter import *
from tkinter import ttk
from PIL import Image, ImageTk
import numpy as np
import matplotlib.pyplot as plt
from enum import IntEnum

class Events(IntEnum) :
    PARAM_CHANGE = 1
    DISPLAY_CHANGE = 2


class EventBus :
    # Simple event bus class, no payload in the publish, only for triggering callbacks
    def __init__(self) :
        self.subscribers = {}

    def subscribe(self, event, handler) :
        if event not in self.subscribers :
            self.subscribers[event] = []
        self.subscribers[event].append(handler)

    def publish(self, event) :
        for handler in self.subscribers.get(event, []) :
            handler()


class EntryBundle(ttk.Frame) :
    def __init__(
            self, 
            root, 
            name, 
            width=10, 
            type=None, 
            default_value=None, 
            uniform=None, 
            add_scale=False, 
            from_=None, 
            to=None, 
            callback=None
            ) :
        super().__init__(root)

        self.grid_columnconfigure(0, weight=1, uniform=uniform)
        self.grid_columnconfigure(1, weight=1, uniform=uniform)
        self.grid_rowconfigure(1, weight=1, uniform=uniform)
        self.grid_rowconfigure(1, weight=1, uniform=uniform)
       
        label = ttk.Label(self, text=name)
        label.grid(column=0, row=0, sticky="e")

        if type is None :
            # Default at double
            self.value = DoubleVar(value=default_value)
        elif type == "double" :
            self.value = DoubleVar(value=default_value)
        elif type == "int" :
            self.value = IntVar(value=default_value)

        entry_frame = ttk.Frame(self)
        entry_frame.grid(column=1, row=0, sticky="ew")
        entry_frame.columnconfigure(0, weight=0)
        entry = ttk.Entry(entry_frame, textvariable=self.value, width=width)
        entry.grid(column=0, row=0, sticky="ew")

        if add_scale :
            def scale_update(val) :
                self.value.set(val)
                if callback :
                    callback()

            if type is None :
                # Default to Double
                num = DoubleVar()
            elif type == "double" :
                num = DoubleVar()
            elif type == "int" :
                num = IntVar()
            scale = ttk.Scale(self, orient="horizontal", from_=from_, to=to, variable=num, command=scale_update)
            scale.grid(column=0, columnspan=2, row=1, sticky="ew")

        for child in self.winfo_children():
            child.grid_configure(padx=2, pady=1)

    def get(self) : 
        return self.value.get()

class FrequencyFrame(ttk.Frame) :
    def __init__(
            self,
            root,
            name,
            callback
    ) :
        super().__init__(root)

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)
        self.grid_rowconfigure(2, weight=1)

        frame = ttk.Frame(self, border=1, relief="solid", padding=(5, 5, 5, 5))
        frame.grid(column=0, row=0, sticky="news")

        # Create a label (frequency name)
        freq_label = ttk.Label(frame, text=name)
        freq_label.grid(column=0, row=0, sticky="nw")

        # Create entries
        # Uniform to align the entries
        uniform = "FreqGroup"

        params = {
            "frequency": ("Frequency (Hz)", 1.0, 0.1, 100.0),
            "amplitude": ("Amplitude", 1.0, 0.1, 10),
            "phase": ("Phase", 0.0, 0.0, 360.0),
            "angle": ("Angle", 0.0, 0.0, 360.0),
        }
        positions = [(0,1), (1,1), (0,2), (1,2)]
        
        # Build the widgets
        for (bundle_name, (name, default_value, from_, to)), (column, row) in zip(params.items(), positions) :
            bundle = EntryBundle(
                root=frame,
                name=name,
                default_value=default_value,
                add_scale=True,
                from_=from_,
                to=to,
                uniform=uniform,
                callback=callback,
            )
            bundle.grid(column=column, row=row, sticky="news")
            setattr(self, f"{bundle_name}_bundle", bundle)

    def get(self, param) :
        param_mapping = {
            "frequency" : self.frequency_bundle,
            "amplitude" : self.amplitude_bundle,
            "phase" : self.phase_bundle,
            "angle" : self.angle_bundle,
        }
        return param_mapping[param].get()


class ScrolledCanvas(Frame):

    def __init__(self, parent, vertical=True, horizontal=False):
        super().__init__(parent)
        
        # create canvas
        self._canvas = Canvas(self)
        self._canvas.grid(row=0, column=0, sticky='nwes') # changed   

        # create right scrollbar and connect to canvas Y
        self._vertical_bar = Scrollbar(parent, orient='vertical', command=self._canvas.yview)
        if vertical:
            self._vertical_bar.grid(row=0, column=1, sticky='ns')
        self._canvas.configure(yscrollcommand=self._vertical_bar.set)

        # create bottom scrollbar and connect to canvas X
        self._horizontal_bar = Scrollbar(self, orient='horizontal', command=self._canvas.xview)
        if horizontal:
            self._horizontal_bar.grid(row=1, column=0, sticky='we')
        self._canvas.configure(xscrollcommand=self._horizontal_bar.set)

        self.inner = None
        
        # autoresize inner frame
        self.columnconfigure(0, weight=1) # changed
        self.rowconfigure(0, weight=1) # changed
        

    def resize(self, event=None): 
        self._canvas.configure(scrollregion=self._canvas.bbox('all'))
        self._canvas.itemconfig(self._window, width=self._canvas.winfo_width())


    def add(self, widget):
        self.inner = widget
        self._window = self._canvas.create_window((0, 0), window=self.inner, anchor='nw')
        self.inner.bind('<Configure>', self.resize)
        self._canvas.bind('<Configure>', self.resize)


class FrequencyEditor(ttk.Frame) :
    def __init__(
            self,
            root,
            callback,
    ) :
        super().__init__(root)
        self.callback = callback
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)


        scrolled_canvas = ScrolledCanvas(self, vertical=True, horizontal=False)

        self.frame = ttk.Frame(scrolled_canvas)
        scrolled_canvas.add(self.frame)
        scrolled_canvas.grid(column=0, row=0, sticky="news")

        # Initialize widgets and button
        self.frequencies_widgets = {}
        self.add_button = None

        # Initialize the first frequency
        self.frequencies = [1]
        
        # Build the editor
        self.build()

        # Add y padding to every children of the editor frame
        for child in self.frame.winfo_children() :
            child.grid_configure(pady=8)
        
        # Configure row and colums priorities in the frame
        nb_col, nb_row = self.frame.grid_size()
        for col in range(nb_col) :
            self.frame.grid_columnconfigure(col, weight=1)
        for row in range(nb_row) :
            self.frame.grid_rowconfigure(row, weight=1)

    def add_frequency(self) :
        new_freq = max(self.frequencies) + 1
        self.frequencies.append(new_freq)
        self.build()

    def delete_frequency(self, freq) :
        self.frequencies.remove(freq)
        self.build()

    def build(self) :
        # Clear the frame
        displayed_frequencies = self.frequencies_widgets.keys()
        to_remove = set(displayed_frequencies) - set(self.frequencies)
        if len(to_remove) > 0:
            for freq in to_remove :
                self.frequencies_widgets[freq]["entry_frame"].destroy()
        # Remove element from dict
        for freq in to_remove :
            del self.frequencies_widgets[freq]

        # Build every Frequency entries
        to_add = set(self.frequencies) - set(displayed_frequencies)
        if len(to_add) > 0:
            for freq in to_add :
                entry_frame = ttk.Frame(self.frame)
                freq_frame = FrequencyFrame(root=entry_frame, name="Frequency " + str(freq), callback=self.callback)
                freq_frame.grid(column=0, row=0, sticky="news")
                del_button = ttk.Button(
                    entry_frame, 
                    text="Delete", 
                    command=lambda i=freq: self.delete_frequency(i)) # Pass parameter to identify the button pressed
                del_button.grid(column=1, row=0, sticky="news")
                self.frequencies_widgets[freq] = {"entry_frame":entry_frame, "freq_frame":freq_frame}

        # Position every entries :
        for idx, freq in enumerate(sorted(self.frequencies)) :
            self.frequencies_widgets[freq]["entry_frame"].grid(column=0, row=idx, sticky="news")

        # Add button after the entries
        if self.add_button is not None :
            self.add_button.destroy()
        self.add_button = ttk.Button(self.frame, text="Add", command=self.add_frequency)
        _, nb_row = self.frame.grid_size()
        self.add_button.grid(column=0, row=nb_row, sticky="news")

    def get_frequencies_param(self) :
        freq_params = {}
        for freq in self.frequencies :
            freq_params[freq] = {}
            freq_frame = self.frequencies_widgets[freq]["freq_frame"]
            for param in ["frequency", "amplitude", "phase", "angle"] :
                freq_params[freq][param] = freq_frame.get(param)
        return freq_params


class WaveViewer :
    def __init__(self, root) :
        # Setup the event bus
        self.event_bus = EventBus()
        self.event_bus.subscribe(Events.PARAM_CHANGE, self.on_param_change)
        self.event_bus.subscribe(Events.DISPLAY_CHANGE, self.on_display_change)

        root.title("Wave Viewer")
        mainframe = ttk.Frame(root)
        mainframe.grid(column=0, row=0, sticky=(N, W, E, S))
        root.columnconfigure(0, weight=1)
        root.rowconfigure(0, weight=1)

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
        
        #-----------------Bottom Frame-----------------------
        bottom_frame = ttk.Frame(mainframe)
        bottom_frame.grid(column=0, row=1, sticky="news")

        #----------------Frequency Editor---------------------
        self.freq_editor = FrequencyEditor(bottom_frame, callback=lambda: self.event_bus.publish(Events.PARAM_CHANGE))
        self.freq_editor.grid(column=0, row=0, sticky="nesw")

        #--------------Visualiazation Frame--------------------
        visu_frame = ttk.Frame(bottom_frame)
        visu_frame.grid(column=1, row=0, sticky=(E, W))

        # PLaceholder self.image to confirm the widhets positions
        self.width, self.height = 500, 500
        self.image = Image.open("placeholder.jpeg").resize((self.width, self.height))
        display = ImageTk.PhotoImage(self.image)
        display = display
        self.canvas = Canvas(visu_frame, width=self.width, height=self.height)
        self.canvas.grid(column=0, row=0, rowspan=2, sticky=(N, W, E, S))
        self.canvas.create_image(0, 0, image=display, anchor="nw")
        self.canvas.image = display

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
        # Hepler functions 
        deg2rad = lambda deg : np.pi * deg / 180.0
        # Get general parameters 
        nb_samples = self.sample_bundle.get()
        length = self.length_bundle.get()
        # Get frequencies parameters
        freq_params = self.freq_editor.get_frequencies_param()
        # Generate wave
        x = np.linspace(0, length, nb_samples)
        X, Y = np.meshgrid(x, x)
        self.image = np.zeros_like(X)
        for params in freq_params.values() :
            freq = params["frequency"]
            angle = params["angle"]
            amplitude = params["amplitude"]
            phase = params["phase"]
            angle = deg2rad(angle)
            phase = deg2rad(phase) + 0.001
            self.image += amplitude * np.sin(2 * np.pi * freq * (np.cos(angle) * X + np.sin(angle) * Y) + phase)
        # Fourier transform
        if self.fourier_checkval.get() :
            transform = np.fft.fft2(self.image)
            shifted_transorm = np.fft.fftshift(transform)
            if self.ftype_var.get() == "mag" :
                self.image = np.abs(shifted_transorm)
            elif self.ftype_var.get() == "phase" :
                self.image = np.angle(shifted_transorm)
                self.image = (self.image + np.pi) / (2 * np.pi)


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

if __name__=="__main__" :
    root = Tk()
    wv = WaveViewer(root)
    root.bind("<Return>", lambda event: wv.update())
    root.mainloop()
