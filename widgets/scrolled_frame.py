from tkinter import *
from tkinter import ttk

class ScrolledFrame(Frame):
    def __init__(self, root, vertical=True, horizontal=False) :
        super().__init__(root)

        self.canvas = Canvas(self)
        self.canvas.grid(column=0, row=0, sticky="news")

        if vertical :
            self.vsbar = Scrollbar(self, orient=VERTICAL, command=self.canvas.yview)
            self.vsbar.grid(column=1, row=0, sticky="ns")
            self.canvas.configure(yscrollcommand=self.vsbar.set)
        
        if horizontal :
            self.hsbar = Scrollbar(self, orient=HORIZONTAL, command=self.canvas.xview)
            self.hsbar.grid(column=0, row=1, sticky="ew")
            self.canvas.configure(xscrollcommand=self.hsbar.set)

        self.inner = None
        
        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)
        self.rowconfigure(1, weight=0)
        self.columnconfigure(1, weight=0)

        self.bind("<Enter>", self._bound_to_mouswheel)
        self.bind("<Leave>", self._unbound_to_mousewheel)

        for child in self.winfo_children() :
            child.grid_configure(padx=2)

    def _bound_to_mouswheel(self, event) :
        self.canvas.bind_all("<MouseWheel>", self._on_mousewheel)

    def _unbound_to_mousewheel(self, event) :
        self.canvas.unbind_all("<MouseWheel>")

    def _on_mousewheel(self, event) :
        self.canvas.yview_scroll(int(-1*(event.delta/120)), "units")

    def resize(self, event=None) :
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        self.canvas.itemconfig(self.window, width=self.canvas.winfo_width())
        
    def add(self, widget) :
        self.inner = widget
        self.window = self.canvas.create_window(0,0, window=self.inner, anchor="nw")
        self.inner.bind("<Configure>", self.resize)
        self.canvas.bind("<Configure>", self.resize)



if __name__ == "__main__" :
    root = Tk()
    root.title("Scrolled Frame Test")

    scrolled_frame = ScrolledFrame(
        root,
        vertical=True,
        horizontal=False
    )

    scrolled_frame.grid(column=0, row=0, sticky="news")

    root.grid_columnconfigure(0, weight=1)
    root.grid_rowconfigure(0, weight=1)

    root.mainloop()