# QNEX

Quantum computing offers the potential to solve problems beyond the capabilities of classical systems. However, the
presence of quantum noise stemming from environmental factors, hardware imperfections, and decoherence remains a
significant challenge to the reliability and performance of quantum systems. Despite advancements like Microsoft's
improvements in logical error rates, quantum noise continues to hinder progress.

This paper introduces QNEX, an interactive quantum noise visualization dashboard designed to help students, educators,
and researchers better understand quantum noise. QNEX enables users to configure noise parameters and observe their
effects in real-time.

## Getting Started

Follow these steps to set up and run the project locally.

### Prerequisites

Ensure you have the following installed:
- Python (>= 3.11)
- [Poetry](https://python-poetry.org/) (>= 2.0)

### Installation

1. Clone the repository:
    ```bash
    git clone https://github.com/Typiqally/qnex.git
    cd qnex
    ```

2. Install project dependencies using Poetry:
    ```bash
    poetry install
    ```

3. (Optional) If you wish to activate the virtual environment, use:
    ```bash
    poetry shell
    ```

### Running the Application

1. Start the Dash application:
    ```bash
    poetry run python qnex/dashboard/app.py
    ```

2. Open your browser and navigate to:
    ```
    http://127.0.0.1:8050
    ```