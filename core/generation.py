import numpy as np

def generate_wave(freq_params, length, nb_samples) :
    # Hepler functions 
    deg2rad = lambda deg : np.pi * deg / 180.0
    # Generate wave
    x = np.linspace(0, length, nb_samples)
    X, Y = np.meshgrid(x, x)
    image = np.zeros_like(X)
    for params in freq_params.values() :
        freq = params["frequency"]
        angle = params["angle"]
        amplitude = params["amplitude"]
        phase = params["phase"]
        angle = deg2rad(angle)
        phase = deg2rad(phase) + 0.001
        image += amplitude * np.sin(2 * np.pi * freq * (np.cos(angle) * X + np.sin(angle) * Y) + phase)
    return image

def apply_fourier_transform(image, phase=False) :
    transform = np.fft.fft2(image)
    shifted_transorm = np.fft.fftshift(transform)
    if not phase :
        image = np.abs(shifted_transorm)
    else :
        image = np.angle(shifted_transorm)
        image = (image + np.pi) / (2 * np.pi)
    return image