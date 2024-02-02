# Quantum Teleportation

Quantum Data Teleportation using Qiskit, Quantum Gates and the principles of Superposition and Entanglement.

## Installation

1. Clone the repository

```bash
$ git clone https://github.com/vaishnav-mk/quantum-teleportation.git
$ cd quantum-teleportation
```

2. Create and activate a conda virtual environment

```bash
$ conda env create -f environment.yml
$ conda activate panorama
```

## Usage
### With a File
```python
file_path = "data/text.txt"
quantum_communication = QuantumDataTeleporter(file_path=file_path, shots=1)
received_data, is_data_match = quantum_communication.run_simulation()

print(f"Received Data: {received_data}")
print(f"Sent Data == Received Data: {is_data_match}")
```

### With a String
```python
text = "Hello, World!"
quantum_communication = QuantumDataTeleporter(text_to_send=text, shots=1)
received_data, is_data_match = quantum_communication.run_simulation()

print(f"Received Data: {received_data}")
print(f"Sent Data == Received Data: {is_data_match}")
```

## Documentation
### [`QuantumDataTeleporter`](https://github.com/vaishnav-mk/quantum-teleportation/blob/main/quantum_communication/quantum_data_teleporter.py#L7) Class
#### Initialization
The class is initialized with the following parameters:

* `separator`: The separator used for binary encoding.
* `shots`: The number of shots for the quantum simulation.
* `file_path`: The path to the file for reading text data.
* `text_to_send`: The text data to be sent if file_path is not provided.

### Superposition and Entanglement

The system utilizes the principles of superposition and entanglement in quantum mechanics. Superposition allows a qubit to exist in multiple states simultaneously, and entanglement establishes correlations between qubits, even when separated by large distances.

### Quantum Gates and Circuits
#### Controlled-X gate (CX) on Qubit 1
```
     ┌───┐ ░            ░      ┌───┐ ░ ┌─┐              
q_0: ┤ X ├─░────────────░───■──┤ H ├─░─┤M├─────────■────
     └───┘ ░ ┌───┐      ░ ┌─┴─┐└───┘ ░ └╥┘┌─┐      │    
q_1: ──────░─┤ H ├──■───░─┤ X ├──────░──╫─┤M├──■───┼────
           ░ └───┘┌─┴─┐ ░ └───┘      ░  ║ └╥┘┌─┴─┐ │ ┌─┐
q_2: ──────░──────┤ X ├─░────────────░──╫──╫─┤ X ├─■─┤M├
           ░      └───┘ ░            ░  ║  ║ └───┘   └╥┘
c: 3/═══════════════════════════════════╩══╩══════════╩═
                                        0  1          2
```

![0](https://github.com/vaishnav-mk/quantum-teleportation/assets/84540554/01403cc1-864b-4770-be45-bba8fdfde9ce)

The quantum circuits created by the Quantum Data Teleporter employ various quantum gates, such as the Hadamard gate (H), controlled-X gate (CX), controlled-Z gate (CZ), and Pauli-X gate (X). These gates manipulate qubits to perform encoding, transmission, and decoding operations.

The protocol that allows the transfer of quantum information from one qubit to another works as follows:

1. The sender and receiver share an entangled pair of qubits.
2. The sender encodes the classical data into a qubit using the Pauli-X gate and the Hadamard gate.
3. The sender applies a controlled-X gate and a controlled-Z gate to the qubit and the entangled qubit, respectively.
4. The sender measures the qubit and the entangled qubit and sends the measurement results to the receiver.
5. The receiver applies the appropriate gates to the entangled qubit based on the measurement results to obtain the original qubit.

#### Controlled-X gate (CX) on Qubit 1
```
           ░            ░      ┌───┐ ░ ┌─┐              
q_0: ──────░────────────░───■──┤ H ├─░─┤M├─────────■────
     ┌───┐ ░ ┌───┐      ░ ┌─┴─┐└───┘ ░ └╥┘┌─┐      │    
q_1: ┤ X ├─░─┤ H ├──■───░─┤ X ├──────░──╫─┤M├──■───┼────
     └───┘ ░ └───┘┌─┴─┐ ░ └───┘      ░  ║ └╥┘┌─┴─┐ │ ┌─┐
q_2: ──────░──────┤ X ├─░────────────░──╫──╫─┤ X ├─■─┤M├
           ░      └───┘ ░            ░  ║  ║ └───┘   └╥┘
c: 3/═══════════════════════════════════╩══╩══════════╩═
                                        0  1          2
```

![1](https://github.com/vaishnav-mk/quantum-teleportation/assets/84540554/23172977-0349-4c08-9e25-b7122e4f19b8)

```python
circuit.x(1 if self.binary_text[i] == "1" else 0)
```
This gate (`X` gate) flips the qubit from the |0⟩ state to the |1⟩ state if the bit is 1.

* If the X gate is on Qubit 0, the teleported data on `Qubit 0` becomes `1`
```
{'100': 252, '111': 259, '110': 263, '101': 250}
```

![image](https://github.com/vaishnav-mk/quantum-teleportation/assets/84540554/16392e5d-f4f4-4e7c-812c-13d17e07fc1e)

* The same applies to Qubit 1 as well; if the X gate is on Qubit 1, the probability of `0`, increases
```
{'000': 255, '001': 304, '010': 238, '011': 227}
```
![image](https://github.com/vaishnav-mk/quantum-teleportation/assets/84540554/026aa739-2221-44d7-8999-4bc7c5f38629)


```python
circuit.barrier()
```
This adds a barrier to the circuit, visually separating the encoding and transmission stages.

```python
circuit.h(1)
circuit.cx(1, 2)
```
The Hadamard gate (`H` gate) creates a superposition of the |0⟩ and |1⟩ states, and the controlled-X gate (`CX` gate) entangles the qubits by flipping the target qubit if the control qubit is in the |1⟩ state.

```python
circuit.barrier()
```
Another barrier for visual separation.

```python
circuit.cx(0, 1)
circuit.h(0)
```
Another controlled-X gate between qubits 0 and 1 and a Hadamard gate to qubit 0 are applied to the qubit to prepare it for measurement.

```python
circuit.barrier()
```
Yet another barrier.

```python
circuit.measure([0, 1], [0, 1])
```
Measurement of the qubits 0 and 1 is performed, and the results are stored in classical bits 0 and 1, respectively.

```python
circuit.cx(1, 2)
circuit.cz(0, 2)
```
CX gate and CZ gate are applied, transforming the state of qubit 2 based on the measurement results of qubits 0 and 1. This is a crucial step in the teleportation process as it allows the receiver to obtain the original qubit.

```python
circuit.measure([2], [2])
```
The final measurement is performed on qubit 2, and the result is stored in classical bit 2. This measurement completes the teleportation.

