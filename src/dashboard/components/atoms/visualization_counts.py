import dash_mantine_components as dmc
import numpy as np
from dash import Input, Output

from src.utils.qiskit_utils import deserialize_statevector


def create_visualization_shots(app):
    @app.callback(
        Output('visualization-shots', 'data'),
        Input('simulation-results', 'data'),
        Input('select-state-vector', 'value'),
        prevent_initial_call=True
    )
    def update_data(simulation_results, state_vector):
        # Return an empty list if no state vector is selected
        if state_vector is None:
            return []

        # Extract ideal and noisy state vectors
        state_vectors_ideal = simulation_results['ideal'][state_vector]
        state_vectors_noisy = simulation_results['noisy'][state_vector]

        # Calculate probabilities from state vectors
        def calculate_totals(state_vectors):
            return (np.abs([deserialize_statevector(s) for s in state_vectors]) ** 2).sum(axis=0)

        totals_ideal = calculate_totals(state_vectors_ideal)
        totals_noisy = calculate_totals(state_vectors_noisy)

        # Determine the number of qubits
        num_results = len(state_vectors_ideal[0])  # Assuming state_vectors_ideal[0] exists and has correct size
        num_qubits = int(np.log2(num_results))

        # Generate binary combinations for results
        basis_states = [format(i, f'0{num_qubits}b') for i in range(num_results)]

        # Format results for output
        formatted_results = [
            {
                "basis_state": basis_states[i],
                "Ideal": totals_ideal[i],
                "Noisy": totals_noisy[i]
            }
            for i in range(len(basis_states))
        ]

        return formatted_results

    return dmc.Stack(
        [
            dmc.Title('Shots', order=4),
            dmc.BarChart(
                id='visualization-shots',
                h=256,
                data=[],
                dataKey="basis_state",
                xAxisLabel="Computational basis states",
                yAxisLabel="Counts",
                barProps={"isAnimationActive": True},
                series=[
                    {"name": "Ideal", "color": "blue"},
                    {"name": "Noisy", "color": "red"}
                ]
            )
        ]
    )
