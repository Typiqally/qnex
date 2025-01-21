import numpy as np


def compute_quantum_fidelity(sv1, sv2):
    # Ensure both state vectors are normalized
    sv1 = sv1 / np.linalg.norm(sv1)
    sv2 = sv2 / np.linalg.norm(sv2)

    # Compute the inner product and then square its magnitude to get fidelity
    fidelity = np.abs(np.vdot(sv1, sv2)) ** 2

    return fidelity
