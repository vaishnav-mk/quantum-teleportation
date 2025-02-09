import quantum_teleportation.utils as utils
import quantum_teleportation.qiskit_utils as q_utils
import quantum_teleportation.compression_utils as c_utils
import quantum_teleportation.qkd_protocols as qkd
from . import cascade_correction as cc

from qiskit.circuit import QuantumCircuit
from qiskit_aer import AerSimulator
from qiskit.providers.fake_provider import GenericBackendV2

from dotenv import load_dotenv
import random
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

# Instantiate a dummy backend (if needed for other purposes)
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
        noise_model: bool = False,
        protocol: str = "bb84",  # Protocol flag: "bb84", "b92", "e91", etc.
        logs: bool = True,
    ) -> None:
        """
        Initializes the QuantumDataTeleporter object.

        Args:
            shots (int): Number of shots for the quantum simulation.
            file_path (str): Path to a text file.
            image_path (str): Path to an image file.
            text_to_send (str): Raw text to be sent (if no file/image is provided).
            compression (str): Compression method ("adaptive", "brotli", or False).
            output_path (str): Directory or file path to save output data.
            noise_model (bool): If True, simulate noise (and trigger an eavesdropper simulation).
            protocol (str): QKD protocol to use (e.g., "bb84", "b92", "e91").
            logs (bool): Enable or disable logging.
        """
        if not file_path and not text_to_send and not image_path:
            raise ValueError("Either file_path or text_to_send or image_path must be provided.")

        self.shots = shots
        self.logs = logs
        self.noise_model = noise_model
        self.protocol = protocol.lower()
        self.output_path = output_path

        # Read the text from file/image or use the provided text.
        text_to_send = (
            utils.text_from_file(file_path)
            if file_path
            else utils.image_to_base64(image_path) if image_path
            else text_to_send
        )

        self.initial_text = text_to_send
        if compression == "adaptive":
            self.text_to_send = c_utils.adaptive_compression(text_to_send)
        elif compression == "brotli":
            self.text_to_send = c_utils.brotli_compression(text_to_send)
        elif not compression:
            self.text_to_send = text_to_send
        else:
            raise ValueError("Invalid compression method. Use 'adaptive', 'brotli', or False.")

        self.image_path = image_path

        # Convert the text to a binary string.
        _binary_text = utils.convert_text_to_binary(self.text_to_send)
        self.private_key = PRIVATE_KEY

        # Adjust private key length if necessary.
        if self.private_key:
            if len(self.private_key) != len(_binary_text):
                logger.warning("Private key length does not match binary text length. Adjusting...")
                if len(self.private_key) < len(_binary_text):
                    logger.warning("Private key length is less than binary text length.")
                    while len(self.private_key) < len(_binary_text):
                        self.private_key += self.private_key
                    self.private_key = self.private_key[: len(_binary_text)]
                else:
                    self.private_key = self.private_key[: len(_binary_text)]

            self.binary_text = _binary_text
            # Prepare the quantum circuits, along with randomly chosen bases.
            self.alice_bases = []
            self.bob_bases = []
            self.circuits = []
            self.create_circuits()

            if self.logs and not self.image_path:
                logger.info(f"Text to send: {self.initial_text}")
                logger.info(f"Binary text: {self.binary_text}")
                logger.debug(f"Circuit count: {len(self.circuits)}")

    def create_circuits(self):
        """
        Creates quantum circuits for each bit in the binary text according to BB84.
        """
        import numpy as np

        if self.logs:
            logger.debug(f"Creating BB84 circuits for {len(self.binary_text)} bits...")

        self.circuits = []
        # Randomly choose bases for Alice and Bob.
        self.alice_bases = np.random.choice(["Z", "X"], size=len(self.binary_text))
        self.bob_bases = np.random.choice(["Z", "X"], size=len(self.binary_text))

        for i, bit in enumerate(self.binary_text):
            qc = QuantumCircuit(1, 1)
            # Alice encodes the bit.
            if bit == "1":
                qc.x(0)
            if self.alice_bases[i] == "X":
                qc.h(0)
            qc.barrier()
            # Bob's measurement.
            if self.bob_bases[i] == "X":
                qc.h(0)
            qc.measure(0, 0)
            self.circuits.append(qc)

        if self.logs:
            logger.debug(f"BB84 circuits created: {len(self.circuits)}")

    def run_simulation(self) -> tuple:
        if self.logs:
            logger.info("Running BB84 simulation...")

        # Setup simulator with or without noise.
        if self.noise_model:
            from qiskit_aer.noise import NoiseModel, depolarizing_error
            one_qubit_error = depolarizing_error(0.01, 1)
            noise_model = NoiseModel()
            for gate in ["u1", "u2", "u3", "h", "x"]:
                noise_model.add_all_qubit_quantum_error(one_qubit_error, gate)
            simulator = AerSimulator(noise_model=noise_model)
        else:
            simulator = AerSimulator()

        job = simulator.run(self.circuits, shots=self.shots)
        result = job.result()

        # Get measurement results.
        bob_results = []
        for idx, circuit in enumerate(self.circuits):
            counts = result.get_counts(circuit)
            measured_bit = max(counts, key=counts.get)
            bob_results.append(int(measured_bit))

        # Pass complete raw keys (bitwise conversion of self.binary_text) to the Cascade routine.
        raw_alice_key = [int(bit) for bit in self.binary_text]
        raw_bob_key = bob_results

        if self.logs:
            logger.info(f"Raw Alice key: {raw_alice_key}")
            logger.info(f"Raw Bob key: {raw_bob_key}")

        # For protocol "bb84", use our new full Cascade reconciliation.
        if self.protocol == "bb84":
            # Choose an estimated QBER; here we set it to 0.05 (5%), adjust as needed.
            qber_estimate = 0.35
            corrected_bob = cc.cascade_full(raw_alice_key, raw_bob_key, qber_estimate, max_passes=4, confirm_rounds=20)
            final_alice_key = "".join(str(bit) for bit in raw_alice_key)
            final_bob_key = "".join(str(bit) for bit in corrected_bob)
        elif self.protocol == "b92":
            raise NotImplementedError("B92 protocol not yet implemented.")
        elif self.protocol == "e91":
            raise NotImplementedError("E91 protocol not yet implemented.")
        else:
            raise ValueError("Unsupported protocol selected.")

        keys_match = (final_alice_key == final_bob_key)
        if self.logs:
            if keys_match:
                logger.info("Final key exchange successful!")
            else:
                logger.warning("Final keys do not match. Security may be compromised.")

        return final_alice_key, final_bob_key