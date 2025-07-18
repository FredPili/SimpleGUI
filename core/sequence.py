import time
import threading
import json
import numpy as np

def load_sequence_config(filename) :
    with open(filename, "r") as file :
        sequence_config = json.load(file)
        file.close()
    # Convert the string keys to int
    sequence_config_convert = {int(k):v for k, v in sequence_config.items() if k not in ["timestep"]}
    sequence_config_convert["timestep"] = sequence_config["timestep"]
    return sequence_config_convert

def make_sequence(sequence_config) :
    # retireve step time and remove it from the config
    timestep = sequence_config["timestep"]
    del sequence_config["timestep"]

    temp = {}

    # Interpolate each wave
    for freq_label, config in sequence_config.items() :
        interpolated = {}
        for param, keypoints in config.items() :
            values = []
            for idx in range(len(keypoints)-1) :
                t1, v1 = keypoints[idx]["time"], keypoints[idx]["value"]
                t2, v2 = keypoints[idx + 1]["time"], keypoints[idx + 1]["value"]
                nb_steps = int(round((t2 - t1) / timestep))
                interp = np.linspace(v1, v2, nb_steps, endpoint=False)
                values.append(interp)
            values.append([keypoints[-1]["value"]]) # Add final value
            interpolated[param] = np.concatenate(values)
        temp[freq_label] = interpolated

    # Compute gloabal max length
    max_len = max(len(arr) for wave in temp.values() for arr in wave.values())

    # Pad to all same length
    for interpolated in temp.values() :
        for param, arr in interpolated.items() :
            if len(arr) < max_len :
                padded = np.pad(arr, (0, max_len - len(arr)), mode="constant", constant_values=arr[-1])
                interpolated[param] = padded

    # Build the sequence (per step dictionnaries)
    sequence = []
    for i in range(max_len) :
        step = {}
        for freq_label, interpolated in temp.items():
            step[freq_label] = {param: arr[i] for param, arr in interpolated.items()}
        sequence.append(step)
        
    return sequence

def make_sequence_player(sequence_config, callback=None) :
    timestep = sequence_config["timestep"]
    sequence = make_sequence(sequence_config)
    sequence_player = SequencePlayer(sequence, timestep=timestep, callback=callback)
    return sequence_player


class SequencePlayer :
    def __init__(self, sequence=None, timestep=0.1, callback=None) :

        self.sequence = sequence
        self.timestep = timestep
        self.callback = callback

        self.thread = None
        self.running = False
        self.paused = False

        self.time = time.time()

    def start(self):
        if self.thread is None or not self.thread.is_alive() :
            self.running = True
            self.paused = False
            self.thread = threading.Thread(target=self.run, daemon=True)
            self.thread.start()

    def pause(self) :
        self.paused = True

    def resume(self) :
        self.paused = False

    def stop(self) : 
        self.running = False
        self.paused = False

    def run(self) :
        for step in self.sequence :
            self.time = time.time()
            if not self.running :
                break
            while self.paused :
                time.sleep(0.05)
            if self.callback:
                self.callback(step)
            to_sleep = max(0, self.timestep - (time.time() - self.time))
            time.sleep(to_sleep)

    def set_sequence(self, sequence) :
        self.sequence = sequence

    def set_timestep(self, timestep) :
        self.timestep = timestep

if __name__ == "__main__" :
    from tkinter import *
    from tkinter import ttk
    def make_gui() :
        root = Tk()
        root.title("SequencePlayer test")

        def on_step(step) :
            print("Step:", step)
            root.after(0, lambda: label.config(text=f"Step: {step}"))

        sequence_config = {
            "1" : {
                "frequency" : [
                    {"time": 0.0, "value": 1.0},
                    {"time": 2.0, "value": 5.0}
                ],
                "phase" : [
                    {"time": 0.0, "value": 1.0},
                    {"time": 2.0, "value": 4.0},
                    {"time": 3.5, "value": 3.0}
                ],
            },
            "2" : {
                "frequency" : [
                    {"time": 0.0, "value": 1.0},
                    {"time": 2.0, "value": 10.0}
                ],
            },
            "timestep" : 0.2,
        }
        player = make_sequence_player(sequence_config, callback=on_step)

        ttk.Button(root, text="Start", command=player.start).grid(column=0, row=0, sticky="news")
        ttk.Button(root, text="Pause", command=player.pause).grid(column=1, row=0, sticky="news")
        ttk.Button(root, text="Resume", command=player.resume).grid(column=2, row=0, sticky="news")
        ttk.Button(root, text="Stop", command=player.stop).grid(column=3, row=0, sticky="news")

        label = ttk.Label(root, text="Step: -")
        label.grid(column=0, row=1, rowspan=4, sticky="news")

        root.mainloop()

    make_gui()

