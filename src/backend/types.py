from enum import Enum


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


class Gate:
    def __init__(self, short_name: str, long_name: str, description: str, supported_noise_params: list, num_qubits: int):
        self.short_name = short_name
        self.long_name = long_name
        self.description = description
        self.supported_noise_params = supported_noise_params
        self.num_qubits = num_qubits

    def __repr__(self):
        return f"Gate(short_name={self.short_name}, long_name={self.long_name}, description={self.description}, num_qubits={self.num_qubits})"