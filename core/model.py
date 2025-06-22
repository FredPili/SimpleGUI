import json

def load_frequencies_dict( filename) :
    with open(filename, "r") as file :
        freq_dict = json.load(file)
        file.close()
    # Convert keys
    return {int(k):v for k, v in freq_dict.items()}

def save_frequencies_dict(filename, freq_params) :
    # Convert keys
    freq_params_convert = {str(k):v for k, v in freq_params.items()}
    with open(filename, "w") as file :
        json.dump(freq_params_convert, file)
        file.close()
    