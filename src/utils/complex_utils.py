import numpy as np


def serialize_complex_array(complex_array):
    real_parts = np.real(complex_array).tolist()
    imag_parts = np.imag(complex_array).tolist()

    return [(r, i) for r, i in zip(real_parts, imag_parts)]


def deserialize_complex_array(array):
    return [complex(r, i) for r, i in array]
