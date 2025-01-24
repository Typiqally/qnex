from enum import Enum
from dataclasses import dataclass
import numpy as np


class NoiseParameterType(Enum):
    BIT_FLIP = (
        "bit_flip",
        "Bit Flip",
        "A bit-flip error occurs when a qubit's state unexpectedly flips from |0⟩ to |1⟩ or vice versa."
    )
    PHASE_FLIP = (
        "phase_flip",
        "Phase Flip",
        "A phase flip occurs when the relative phase of the |1⟩ state in a qubit is inverted, impacting interference patterns."
    )
    PHASE_DAMPING = (
        "phase_damping",
        "Phase Damping",
        "Phase damping describes the loss of phase coherence caused by interaction with the surrounding environment."
    )
    THERMAL_RELAXATION = (
        "thermal_relaxation",
        "Thermal Relaxation",
        "Thermal relaxation describes how a qubit loses its excited state and settles into its ground state due to energy exchange with the environment."
    )
    AMPLITUDE_DAMPING = (
        "amplitude_damping",
        "Amplitude Damping",
        "Amplitude damping models energy loss in a qubit, where the qubit transitions from the |1⟩ state to the |0⟩ state as energy dissipates."
    )
    DEPOLARIZING = (
        "depolarizing",
        "Depolarizing",
        "Depolarizing noise simulates a qubit becoming a mixed state, losing quantum information with an equal probability of flipping to any state."
    )
    READOUT_ERROR = (
        "readout_error",
        "Readout Error",
        "Readout error models inaccuracies during the measurement process, where the observed qubit state may differ from the actual state."
    )

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
    ideal_counts: list[np.ndarray]
    noisy_counts: list[np.ndarray]
