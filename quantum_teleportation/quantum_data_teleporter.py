import quantum_teleportation.utils as utils
import quantum_teleportation.qiskit_utils as q_utils
import quantum_teleportation.compression_utils as c_utils

from qiskit.circuit import QuantumCircuit
from qiskit_aer import AerSimulator
from qiskit.providers.fake_provider import GenericBackendV2
from qiskit_aer.noise import NoiseModel

from dotenv import load_dotenv
import matplotlib.pyplot as plt
from tqdm import tqdm
import random
import time
import os
import logging

logger = utils.setup_logger("quantum_data_teleporter", level=logging.DEBUG)

load_dotenv()
PRIVATE_KEY = os.getenv("PRIVATE_KEY")

if not PRIVATE_KEY:
    num = random.randint(2000, 2500)
    logger.warning(
        f"No private key found in the environment variables. Generating a random key with length: {num}..."
    )
    PRIVATE_KEY = q_utils.qrng(num)
    os.environ["PRIVATE_KEY"] = PRIVATE_KEY

    with open(".env", "a") as f:
        f.write(f"PRIVATE_KEY={PRIVATE_KEY}")

device_backend = GenericBackendV2(num_qubits=6)


class QuantumDataTeleporter:
    def __init__(
        self,
        shots: int = 1,
        file_path: str = None,
        image_path: str = None,
        text_to_send: str = None,
        compression: str = "brotli",
        output_path: str = None,
        noise_model=False,
        logs: bool = True,
    ) -> None:
        """
        Initializes the QuantumDataTeleporter object.

        Args:
            shots (int): Number of shots for the quantum simulation.
            file_path (str): Path to the file for reading text data.
            image_path (str): Path to the image for reading text data.
            text_to_send (str): Text data to be sent if file_path is not provided.
            compression (str): Compression method to use: "adaptive", "brotli", or False.
        """
        if not file_path and not text_to_send and not image_path:
            raise ValueError(
                "Either file_path or text_to_send or image_path must be provided."
            )

        self.shots = shots
        self.logs = logs
        self.compression = compression
        self.output_path = output_path

        text_to_send = (
            utils.text_from_file(file_path)
            if file_path
            else utils.image_to_base64(image_path) if image_path else text_to_send
        )

        self.initial_text = text_to_send
        if compression == "adaptive":
            self.text_to_send = c_utils.adaptive_compression(text_to_send)
        elif compression == "brotli":
            self.text_to_send = c_utils.brotli_compression(text_to_send)
        elif not compression:
            self.text_to_send = text_to_send
        else:
            raise ValueError(
                "Invalid compression method. Use 'adaptive', 'brotli', or False."
            )

        self.image_path = image_path
        self.noise_model = noise_model

        _binary_text = utils.convert_text_to_binary(self.text_to_send)
        self.private_key = PRIVATE_KEY

        if self.private_key:
            if len(self.private_key) != len(_binary_text):
                logger.warning(
                    "Private key length does not match binary text length. Adjusting..."
                )
                if len(self.private_key) < len(_binary_text):
                    logger.warning("Private key length is less than binary text length.")
                    # Increase the private key length to match the binary text length
                    while len(self.private_key) < len(_binary_text):
                        self.private_key += self.private_key
                    self.private_key = self.private_key[: len(_binary_text)]
                else:
                    # Truncate the private key if it's longer than the binary text length
                    self.private_key = self.private_key[: len(_binary_text)]

            self.binary_text = _binary_text
            self.circuits = [QuantumCircuit(6, 6) for _ in range(len(self.binary_text))]

            self.create_circuits()

            if self.logs and not self.image_path:
                logger.info(f"Text to send: {self.initial_text}")
                logger.info(f"Binary text: {self.binary_text}")
                logger.debug(f"Circuit count: {len(self.circuits)}")

    def calculate_adaptive_shots(
        self,
        circuit_complexity: int,
        text_length: int,
        confidence_level: float = 0.90,
        base_shots: int = 250,
        max_shots: int = 4096,
    ) -> int:
        """
        Calculates the number of shots required based on the circuit complexity, text length, and confidence level.

        Args:
            text_length (int): Length of the text to be encoded.
            circuit_complexity (int): Complexity of the quantum circuit.
            confidence_level (float): Confidence level for the simulation.
            base_shots (int): Base number of shots for the simulation.
            max_shots (int): Maximum number of shots for the simulation.

        Returns:
            int: Number of shots required for the simulation.
        """
        additional_shots_complexity = min(
            circuit_complexity * 5, max_shots - base_shots
        )
        additional_shots_length = min(text_length * 0.1, max_shots - base_shots)

        additional_shots = round(
            (additional_shots_complexity + additional_shots_length) / 2
        )

        if confidence_level > 0.90:
            additional_shots = min(circuit_complexity * 1.5, max_shots - base_shots)

        if self.logs:
            logger.debug(
                f"Complexity: {circuit_complexity}, Text Length: {text_length}, Confidence Level: {confidence_level}, Base Shots: {base_shots}, Max Shots: {max_shots}"
            )
            logger.debug(f"Additional shots: {additional_shots}")
            logger.info(f"Total shots: {base_shots + additional_shots}")

        return base_shots + additional_shots

    def create_circuits(self):
        """
        Creates quantum circuits for the BB84 protocol.
        """
        import numpy as np

        if self.logs:
            logger.debug(f"Creating BB84 circuits for {len(self.binary_text)} bits...")

        # Randomly generate Alice's and Bob's bases
        alice_bases = np.random.choice(["Z", "X"], size=len(self.binary_text))
        bob_bases = np.random.choice(["Z", "X"], size=len(self.binary_text))

        self.alice_bases = alice_bases
        self.bob_bases = bob_bases
        self.circuits = []

        for i, bit in enumerate(self.binary_text):
            qc = QuantumCircuit(1, 1)

            # Step 1: Alice prepares the qubit
            if bit == "1":  # Encode bit 1 by applying X gate first
                qc.x(0)
            if self.alice_bases[i] == "X":  # Rotate to X basis if chosen
                qc.h(0)
            qc.barrier()

            # Step 2: Transmission (Eve can interfere here)
            # This barrier marks where Eve might interact

            # Step 3: Bob measures the qubit
            if self.bob_bases[i] == "X":  # Rotate to X basis for measurement
                qc.h(0)
            qc.measure(0, 0)

            self.circuits.append(qc)

        if self.logs:
            logger.debug(f"BB84 circuits created: {len(self.circuits)}")

    def run_simulation(self) -> tuple[list[int], list[int]]:
        if self.logs:
            logger.info("Running BB84 simulation...")

        simulator = AerSimulator()
        job = simulator.run(self.circuits, shots=self.shots)
        result = job.result()

        # Initialize Bob's results list
        bob_results = []

        # Iterate over each circuit's result
        for idx, circuit in enumerate(self.circuits):
            # Retrieve counts for the circuit (explicitly reference the circuit or its index)
            counts = result.get_counts(circuit)
            # Assume one shot per circuit; get the measured bit
            measured_bit = max(counts, key=counts.get)
            bob_results.append(int(measured_bit))

        # Sift keys based on matching bases
        alice_key = []
        bob_key = []
        for i in range(len(self.binary_text)):
            if self.alice_bases[i] == self.bob_bases[i]:  # Bases match
                alice_key.append(int(self.binary_text[i]))
                bob_key.append(bob_results[i])

        if self.logs:
            logger.info(f"Alice's bases: {self.alice_bases}")
            logger.info(f"Bob's bases: {self.bob_bases}")
            logger.info(f"Sifted Alice key: {alice_key}")
            logger.info(f"Sifted Bob key: {bob_key}")

        key_match = alice_key == bob_key
        if key_match:
            logger.info("Key exchange successful.")
        else:
            logger.warning("Key mismatch detected. Possible eavesdropper.")

        return alice_key, bob_key