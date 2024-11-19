import dash_mantine_components as dmc
import numpy as np
from dash import Input, Output

from src.utils.qiskit_utils import deserialize_statevector


def create_visualization_probabilities(app):
    @app.callback(
        Output('visualization-probabilities', 'data'),
        Input('simulation-results', 'data'),
        Input('input-visualize-shot', 'value'),
        Input('select-state-vector', 'value'),
        prevent_initial_call=True
    )
    def update_data(simulation_results, selected_shot, state_vector):
        # Return an empty list if no state vector is selected
        if state_vector is None:
            return []

        # Extract ideal and noisy state vectors
        state_vectors_ideal = simulation_results['ideal'][state_vector]
        state_vectors_noisy = simulation_results['noisy'][state_vector]
        probabilities_ideal = deserialize_statevector(state_vectors_ideal[selected_shot]).probabilities() * 100
        probabilities_noisy = deserialize_statevector(state_vectors_noisy[selected_shot]).probabilities() * 100

        # Determine the number of qubits
        num_results = len(state_vectors_ideal[0])  # Assuming state_vectors_ideal[0] exists and has correct size
        num_qubits = int(np.log2(num_results))

        # Generate binary combinations for results
        basis_states = [format(i, f'0{num_qubits}b') for i in range(num_results)]

        # Format results for output
        formatted_results = [
            {
                "basis_state": basis_states[i],
                "Ideal": probabilities_ideal[i],
                "Noisy": probabilities_noisy[i]
            }
            for i in range(len(basis_states))
        ]

        return formatted_results

    return dmc.Stack(
        [
            dmc.Title('Probabilities', order=4),
            dmc.BarChart(
                id='visualization-probabilities',
                h=256,
                data=[],
                dataKey="basis_state",
                xAxisLabel="Computational basis states",
                yAxisLabel="Probability (%)",
                barProps={"isAnimationActive": True},
                series=[
                    {"name": "Ideal", "color": "blue"},
                    {"name": "Noisy", "color": "red"}
                ],
                yAxisProps={
                    'domain': [0, 100]
                }
            )
        ]
    )
