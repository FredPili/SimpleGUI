from tkinter import *
from tkinter import ttk
from widgets.frequency_frame import FrequencyFrame
from widgets.scrolled_frame import ScrolledFrame
from core.model import load_frequencies_dict, save_frequencies_dict
import json

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

        scrolled_canvas = ScrolledFrame(self, vertical=True, horizontal=False)
        scrolled_canvas.grid(column=0, row=0, sticky="news")

        self.frame = ttk.Frame(scrolled_canvas)
        scrolled_canvas.add(self.frame)
        self.frame.grid_columnconfigure(0, weight=1)

        # Initialize widgets and button
        self.frequencies_widgets = {}
        self.add_button = None

        # Initialize the first frequency
        self.frequencies = [1]
        
        # Build the editor
        self.build()

    def add_frequency(self) :
        new_freq = max(self.frequencies) + 1
        self.frequencies.append(new_freq)
        self.build()
        self.callback()

    def delete_frequency(self, freq) :
        self.frequencies.remove(freq)
        self.build()
        self.callback()

    def build(self, freq_dict=None) : # If freq dict passed, will build according to this dict
        if freq_dict :
            self.frequencies = list(freq_dict.keys())

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
        if freq_dict :
            # If freq dict passed, reload every entries
            to_add = self.frequencies
        else :
            to_add = set(self.frequencies) - set(displayed_frequencies)
        if len(to_add) > 0:
            for freq in to_add :
                entry_frame = ttk.Frame(self.frame)
                entry_frame.grid_columnconfigure(0, weight=0)
                entry_frame.grid_columnconfigure(1, weight=1)
                if freq_dict :
                    freq_frame = FrequencyFrame(root=entry_frame, name="Frequency " + str(freq), callback=self.callback, params_dict=freq_dict[freq])
                else :
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
            self.frequencies_widgets[freq]["entry_frame"].grid(column=0, row=idx, sticky="ew")

        # Add button after the entries
        if self.add_button is not None :
            self.add_button.destroy()
        self.add_button = ttk.Button(self.frame, text="Add", command=self.add_frequency)
        _, nb_row = self.frame.grid_size()
        self.add_button.grid(column=0, row=nb_row, sticky="ew")

        # Add y padding to every children of the editor frame
        for child in self.frame.winfo_children() :
            child.grid_configure(pady=8)

    def get_frequencies_param(self) :
        freq_params = {}
        for freq in self.frequencies :
            freq_params[freq] = {}
            freq_frame = self.frequencies_widgets[freq]["freq_frame"]
            for param in ["frequency", "amplitude", "phase", "angle"] :
                freq_params[freq][param] = freq_frame.get(param)
        return freq_params
    
    def load_frequencies(self, filename) :
        freq_dict = load_frequencies_dict(filename)
        self.build(freq_dict)
        self.callback()

    def save_frequencies(self, filename) :
        freq_params = self.get_frequencies_param()
        save_frequencies_dict(filename, freq_params)


if __name__ == "__main__" :
    root = Tk()
    root.title("FrequencyEditor Test")

    def on_change(widget) :
        print("Change !")
        print(widget.get_frequencies_param())

    frequency_editor = FrequencyEditor(
        root,
        callback=lambda: on_change(frequency_editor)
    )

    frequency_editor.grid(column=0, row=0, sticky="news")

    root.grid_columnconfigure(0, weight=1)
    root.grid_rowconfigure(0, weight=1)

    root.mainloop()