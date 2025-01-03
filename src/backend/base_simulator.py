from abc import ABC, abstractmethod

from src.backend.types import Gate


class BaseSimulator(ABC):
    @abstractmethod
    def load_circuit(self, qasm_str: str):
        """Load a quantum circuit into the simulator."""
        pass

    @abstractmethod
    def simulate(self, shots: int, noise_model: dict):
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
