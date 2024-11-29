from abc import ABC, abstractmethod
from enum import Enum


# TODO: Put into separate file
class NoiseModelType(Enum):
    BIT_FLIP = "bit_flip"
    PHASE_FLIP = "phase_flip"
    PHASE_DAMPING = "phase_damping"
    THERMAL_RELAXATION = "thermal_relaxation"
    AMPLITUDE_DAMPING = "amplitude_damping"
    DEPOLARIZING = "depolarizing"
    READOUT_ERROR = "readout_error"


class Gate:
    def __init__(self, name: str, description: str, noise_models: list, num_qubits: int):
        self.display_name = name
        self.description = description
        self.noise_models = noise_models
        self.num_qubits = num_qubits

    def __repr__(self):
        return f"Gate(name={self.display_name}, description={self.description}, num_qubits={self.num_qubits})"


class BaseSimulator(ABC):
    @abstractmethod
    def load_circuit(self, qasm_str: str):
        """Load a quantum circuit into the simulator."""
        pass

    @abstractmethod
    def simulate(self, shots: int, noise_params: dict):
        """Run the simulation with the given noise parameters."""
        pass

    @abstractmethod
    def supported_gates(self) -> list[Gate]:
        """Return a list of supported gates."""
        pass

    @abstractmethod
    def used_gates(self):
        """Return a list of used gates in the current circuit."""
        pass
