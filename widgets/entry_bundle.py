from tkinter import *
from tkinter import ttk


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
        self.grid_rowconfigure(0, weight=1, uniform=uniform)
        self.grid_rowconfigure(1, weight=1, uniform=uniform)

        self.name = name
       
        label = ttk.Label(self, text=name)
        label.grid(column=0, row=0, sticky="ew")

        if type is None :
            # Default at double
            self.value = DoubleVar(value=default_value)
        elif type == "double" :
            self.value = DoubleVar(value=default_value)
        elif type == "int" :
            self.value = IntVar(value=default_value)

        entry_frame = ttk.Frame(self)
        entry_frame.grid(column=1, row=0, sticky="news")
        entry_frame.columnconfigure(0, weight=1)
        entry = ttk.Entry(entry_frame, textvariable=self.value, width=width)
        entry.grid(column=0, row=0, sticky="ew")

        if add_scale :
            def scale_update(val) :
                if isinstance(self.value, IntVar) :
                    self.value.set(int(round(float(val))))
                else :
                    self.value.set(val)

            scale = ttk.Scale(self, orient="horizontal", from_=from_, to=to, variable=self.value, command=scale_update)
            scale.grid(column=0, columnspan=2, row=1, sticky="ew")

        def trace(*args) :
            if callback :
                callback()
        self.value.trace_add("write", trace)

        for child in self.winfo_children():
            child.grid_configure(padx=2, pady=1)

    def get(self) : 
        return self.value.get()
    
    def set(self, val) :
        self.value.set(val)
    

if __name__ == "__main__" :
    root = Tk()
    root.title("Entry bundle test")

    def on_change(bundle) :
        print(f"{bundle.name} changed value ! : {bundle.get()}")

    uniform="Group"
    entry_bundle_double = EntryBundle(
        root,
        name="Entry Bundle Double",
        add_scale=True,
        type="double",
        from_=0.0,
        to=10.0,
        callback=lambda: on_change(entry_bundle_double),
        uniform=uniform
    )
    entry_bundle_double.grid(column=0, row=0, sticky="nwes")
    entry_bundle_int = EntryBundle(
        root,
        name="Entry Bundle Int",
        add_scale=True,
        type="int",
        from_=0.0,
        to=10.0,
        callback=lambda: on_change(entry_bundle_int),
        uniform=uniform
    )
    entry_bundle_int.grid(column=0, row=1, sticky="nwes")
    entry_bundle_double_noscale = EntryBundle(
        root,
        name="Entry Bundle Double No scale",
        type="double",
        callback=lambda: on_change(entry_bundle_double_noscale),
        uniform=uniform
    )
    entry_bundle_double_noscale.grid(column=1, row=0, sticky="nwes")
    entry_bundle_int_noscale = EntryBundle(
        root,
        name="Entry Bundle Int No scale",
        type="int",
        callback=lambda: on_change(entry_bundle_int_noscale),
        uniform=uniform
    )
    entry_bundle_int_noscale.grid(column=1, row=1, sticky="nwes")

    root.grid_columnconfigure((0,1), weight=1)
    root.grid_rowconfigure((0,1), weight=1)
    root.mainloop()