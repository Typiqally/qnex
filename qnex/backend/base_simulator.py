from abc import ABC, abstractmethod
from typing import Optional

from qnex.backend.types import Gate, SimulationResult


class BaseSimulator(ABC):
    @abstractmethod
    def load_circuit(self, qasm_str: str):
        """Load a quantum circuit into the simulator."""
        pass

    @abstractmethod
    def simulate(self, qasm_str: str, shots: int, seed: Optional[int], noise_params: dict) -> SimulationResult:
        """Run the simulation with the given noise parameters."""
        pass

    @abstractmethod
    def supported_operations(self) -> list[Gate]:
        """Return a list of supported gates."""
        pass

    @abstractmethod
    def used_operations(self, qasm_str: str) -> list[Gate]:
        """Return a list of used gates in the current circuit."""
        pass
