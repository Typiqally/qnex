from enum import Enum


class NoiseParameterType(Enum):
    BIT_FLIP = "bit_flip"
    PHASE_FLIP = "phase_flip"
    PHASE_DAMPING = "phase_damping"
    THERMAL_RELAXATION = "thermal_relaxation"
    AMPLITUDE_DAMPING = "amplitude_damping"
    DEPOLARIZING = "depolarizing"
    READOUT_ERROR = "readout_error"


class Gate:
    def __init__(self, name: str, description: str, supported_noise_model: list, num_qubits: int):
        self.display_name = name
        self.description = description
        self.noise_models = supported_noise_model
        self.num_qubits = num_qubits

    def __repr__(self):
        return f"Gate(name={self.display_name}, description={self.description}, num_qubits={self.num_qubits})"