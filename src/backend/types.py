from enum import Enum

from dataclasses import dataclass

import numpy as np


class NoiseParameterType(Enum):
    BIT_FLIP = ("bit_flip", "Bit Flip", "Models random bit-flip errors in qubits.")
    PHASE_FLIP = ("phase_flip", "Phase Flip", "Models random phase-flip errors in qubits.")
    PHASE_DAMPING = ("phase_damping", "Phase Damping", "Models phase damping due to environment interaction.")
    THERMAL_RELAXATION = ("thermal_relaxation", "Thermal Relaxation", "Models relaxation due to thermal noise.")
    AMPLITUDE_DAMPING = ("amplitude_damping", "Amplitude Damping", "Models energy loss in qubits.")
    DEPOLARIZING = ("depolarizing", "Depolarizing", "Models depolarizing noise affecting all states equally.")
    READOUT_ERROR = ("readout_error", "Readout Error", "Models errors during qubit measurement.")

    def __init__(self, value, display_name, description):
        self._value_ = value
        self.display_name = display_name
        self.description = description


@dataclass
class Gate:
    short_name: str
    long_name: str
    description: str
    supported_noise_params: list[NoiseParameterType]
    num_qubits: int

    def __repr__(self):
        return f"Gate(short_name={self.short_name}, long_name={self.long_name}, description={self.description}, num_qubits={self.num_qubits})"


@dataclass
class StatevectorResult:
    state_vector: list[complex]
    counts: list[np.ndarray]
    probabilities: list[np.ndarray]


@dataclass
class SimulationResult:
    basis_states: list[str]
    ideal: dict[str, StatevectorResult]
    noisy: dict[str, StatevectorResult]
