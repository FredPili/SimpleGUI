from tkinter import *
from tkinter import ttk
from widgets.entry_bundle import EntryBundle

class FrequencyFrame(ttk.Frame) :
    def __init__(
            self,
            root,
            name,
            callback,
            params_dict=None
    ) :
        super().__init__(root)

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)

        frame = ttk.Frame(self, border=1, relief="solid", padding=(5, 5, 5, 5))
        frame.grid(column=0, row=0, sticky="news")
        frame.grid_columnconfigure((0, 1), weight=1)
        frame.grid_rowconfigure((1, 2), weight=1)

        # Create a label (frequency name)
        self.name = name
        freq_label = ttk.Label(frame, text=name)
        freq_label.grid(column=0, columnspan=2, row=0, sticky="news")

        # Create entries
        # Uniform to align the entries
        uniform = "FreqGroup"
        
        if params_dict :
            params = {
                "frequency": ("Frequency (Hz)", params_dict["frequency"], 0.1, 100.0),
                "amplitude": ("Amplitude", params_dict["amplitude"], 0.1, 10),
                "phase": ("Phase", params_dict["phase"], 0.0, 360.0),
                "angle": ("Angle", params_dict["angle"], 0.0, 360.0),
            }
        else :
            # Default params
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
    
    def set(self, param_dict) :
        param_mapping = {
            "frequency" : self.frequency_bundle,
            "amplitude" : self.amplitude_bundle,
            "phase" : self.phase_bundle,
            "angle" : self.angle_bundle,
        }
        for param, value in param_dict.items() :
            if param in param_mapping.keys() :
                if param in ["angle", "phase"] :
                    value = value % 360.0
                param_mapping[param].set(value)
    

if __name__ == "__main__" :
    root = Tk()
    root.title("FrequencyFrame Test")

    def on_change(frequency_frame) :
        print(f"{frequency_frame.name} changed values !")
        for param in ["frequency", "amplitude", "phase", "angle"] :
            print(f"{param} : {frequency_frame.get(param)} ")
        print("\n")

    frequency_frame = FrequencyFrame(
        root,
        name="1",
        callback=lambda: on_change(frequency_frame)
    )
    frequency_frame.grid(column=0, row=0, sticky="news")

    root.grid_columnconfigure(0, weight=1)
    root.grid_rowconfigure(0, weight=1)

    root.mainloop()