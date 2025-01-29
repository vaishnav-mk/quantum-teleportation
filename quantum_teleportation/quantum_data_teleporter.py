import quantum_teleportation.utils as utils
import quantum_teleportation.qiskit_utils as q_utils
import quantum_teleportation.compression_utils as c_utils

from quantum_teleportation.bb84_utils import run_bb84_protocol  # <-- NEW: Import BB84
from qiskit import QuantumCircuit, BasicAer, execute
from qiskit_aer import AerSimulator
from qiskit.providers.fake_provider import FakeVigo
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
PRIVATE_KEY = os.getenv("PRIVATE_KEY")  # may or may not exist

if not PRIVATE_KEY:
    num = random.randint(2000, 2500)
    logger.warning(
        f"No private key found in the environment variables. Generating a random key with length: {num}..."
    )
    PRIVATE_KEY = q_utils.qrng(num)
    os.environ["PRIVATE_KEY"] = PRIVATE_KEY

    with open(".env", "a") as f:
        f.write(f"PRIVATE_KEY={PRIVATE_KEY}")

device_backend = FakeVigo()


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
        use_bb84: bool = False,      # <-- NEW parameter
        num_bb84_qubits: int = 64    # <-- NEW parameter
    ) -> None:
        """
        Initializes the QuantumDataTeleporter object.

        Args:
            shots (int): Number of shots for the quantum simulation.
            file_path (str): Path to a text file to be read.
            image_path (str): Path to an image to be read (converted to base64).
            text_to_send (str): Text data to be sent if file_path is not provided.
            compression (str): Compression method: "adaptive", "brotli", or False.
            output_path (str): Where to save results, if desired.
            noise_model (bool): Whether to use a noise model.
            logs (bool): Whether to log debug information.
            use_bb84 (bool): If True, generate a shared key via BB84 instead of using PRIVATE_KEY.
            num_bb84_qubits (int): Number of qubits for BB84 key generation.
        """
        if not file_path and not text_to_send and not image_path:
            raise ValueError(
                "Either file_path or text_to_send or image_path must be provided."
            )

        self.shots = shots
        self.logs = logs
        self.compression = compression
        self.output_path = output_path
        self.noise_model = noise_model

        # 1) Determine what text to send
        text_to_send = (
            utils.text_from_file(file_path)
            if file_path
            else utils.image_to_base64(image_path) if image_path else text_to_send
        )

        self.initial_text = text_to_send

        # 2) Compress if needed
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

        # 3) Convert to binary
        _binary_text = utils.convert_text_to_binary(self.text_to_send)

        # 4) Private key setup
        if use_bb84:
            # Use BB84 to generate the key
            logger.info("Generating a key via BB84 protocol...")
            alice_key, bob_key = run_bb84_protocol(num_qubits=num_bb84_qubits)
            # In real usage, Alice would have 'alice_key' and Bob 'bob_key',
            # but here we unify them for demonstration (they should match).
            # We'll use alice_key as our "private key".
            if alice_key != bob_key:
                logger.warning("BB84 keys differ => potential eavesdropping or error.")
            self.private_key = alice_key
            logger.info(f"BB84 key length: {len(self.private_key)} bits")
        else:
            # Original environment-based or random approach
            self.private_key = PRIVATE_KEY

        # 5) Possibly adjust if private_key length != message length
        if self.private_key:
            if len(self.private_key) != len(_binary_text):
                logger.warning(
                    "Private key length does not match binary text length. Adjusting..."
                )
                if len(self.private_key) < len(_binary_text):
                    logger.warning("Private key length is less than the text length.")
                    # Increase the private key length to match the binary text length
                    while len(self.private_key) < len(_binary_text):
                        self.private_key += self.private_key
                    # Truncate to exact length
                    self.private_key = self.private_key[: len(_binary_text)]
                else:
                    # Truncate the private key if it's longer than the binary text
                    self.private_key = self.private_key[: len(_binary_text)]

        self.binary_text = _binary_text

        # 6) Build your circuits
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
                f"Complexity: {circuit_complexity}, Text Length: {text_length}, "
                f"Confidence Level: {confidence_level}, Base Shots: {base_shots}, Max Shots: {max_shots}"
            )
            logger.debug(f"Additional shots: {additional_shots}")
            logger.info(f"Total shots: {base_shots + additional_shots}")

        return base_shots + additional_shots

    def create_circuits(self) -> None:
        """
        Creates quantum circuits based on the binary text.
        """
        if self.logs:
            logger.debug(f"Creating circuits for {len(self.binary_text)} bits...")

        for i in range(len(self.binary_text)):
            bit = self.binary_text[i]
            # Prepare qubit based on bit 0/1
            if bit == "1":
                self.circuits[i].x(1)
            else:
                # If "0", do nothing special
                pass

            self.circuits[i].barrier()
            self.circuits[i].h(1)
            self.circuits[i].cx(1, 2)
            self.circuits[i].barrier()
            self.circuits[i].cx(0, 1)
            self.circuits[i].h(0)
            self.circuits[i].barrier()
            self.circuits[i].measure([0, 1], [0, 1])
            self.circuits[i].cx(1, 2)
            self.circuits[i].cz(0, 2)
            self.circuits[i].measure([2], [2])

            # Some error correction code? (Your original code snippet)
            self.circuits[i].barrier()
            self.circuits[i].measure([0, 1, 2], [3, 4, 5])
            self.circuits[i].cx(3, 4)
            self.circuits[i].cx(3, 5)
            self.circuits[i].cx(4, 5)
            self.circuits[i].barrier()
            self.circuits[i].ccx(3, 4, 5)
            self.circuits[i].measure([5], [0])

    def run_simulation(self) -> tuple[str, bool]:
        """
        Runs the quantum simulation and returns (received_data, is_data_match).
        """
        total_characters = len(self.circuits)
        start_time = time.time()

        if self.logs:
            logger.info(f"Running simulation with {total_characters} characters...")

        # Shots
        if self.shots == -1 and self.circuits:
            # Maybe you want to do adaptive shots
            circuit_complexity = len(self.circuits[0])  # or a more refined measure
            self.shots = self.calculate_adaptive_shots(
                circuit_complexity,
                text_length=len(self.text_to_send),
            )

        logger.info(
            f"Processing {len(self.text_to_send)} characters "
            f"({total_characters} bits)... with {self.shots} shot(s). "
            f"| Noise Model: {self.noise_model}"
        )

        flipped_results = []

        with tqdm(total=total_characters, desc="Processing characters", unit="char") as pbar:
            if self.noise_model:
                # Use a noise model from the FakeVigo device
                noise_backend = NoiseModel.from_backend(device_backend)
                simulator = AerSimulator(noise_model=noise_backend)
            else:
                simulator = BasicAer.get_backend("qasm_simulator")

            for circuit in self.circuits:
                if self.noise_model:
                    result = simulator.run(circuit).result()
                else:
                    result = execute(circuit, backend=simulator, shots=1).result()

                counts_dict = result.get_counts()
                # The measurement result is the key with the highest count
                best_key = max(counts_dict, key=counts_dict.get)
                # bit_flipper uses only the first character?
                flipped_bit = utils.bit_flipper(best_key[0])
                flipped_results.append(flipped_bit)
                pbar.update(1)

        end_time = time.time()
        logger.info(f"Time taken: {utils.convert_time(end_time - start_time)}")

        # Convert those bits to text
        binary_chunks = utils.handle_flipped_results(
            flipped_results=flipped_results, logs=self.logs
        )
        converted_chunks = utils.convert_binary_to_text(binary_chunks)

        # Decompress if needed
        converted_chunks = c_utils.adaptive_decompression(data=converted_chunks)

        logger.info(f"Received data: {converted_chunks}")

        # Compare
        if converted_chunks != self.initial_text:
            logger.warning("Data mismatch.")
            comparison_result = utils.compare_strings(self.initial_text, converted_chunks)
            logger.warning("Percentage of similarity: %s", comparison_result["percentage_match"])
            logger.warning("Sent data:\n%s", comparison_result["marked_string1"])
            logger.warning("Received data:\n%s", comparison_result["marked_string2"])
        else:
            logger.info("Data match.")
            # Save if requested
            if self.output_path:
                utils.save_data(
                    converted_chunks=converted_chunks,
                    output_path=self.output_path,
                    image_path=self.image_path,
                    data={
                        "time_taken": utils.convert_time(end_time - start_time),
                        "text": self.initial_text,
                        "data_match": converted_chunks == self.initial_text,
                        "private_key": self.private_key,
                        "binary_text": self.binary_text,
                        "flipped_results": flipped_results,
                        "compression": self.compression,
                        "shots": self.shots,
                        "noise_model": self.noise_model,
                    },
                )
                logger.info(f"Data saved to {self.output_path}")

        return converted_chunks, (converted_chunks == self.initial_text)