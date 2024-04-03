import random
import os
import logging
import time
from tqdm import tqdm
from dotenv import load_dotenv

import quantum_teleportation.utils as utils
import quantum_teleportation.compression_utils as c_utils
import quantum_teleportation.qiskit_utils as q_utils

from qiskit import QuantumCircuit, BasicAer, execute
from qiskit_aer import AerSimulator
from qiskit.providers.fake_provider import FakeVigo

# Setup logger
logger = utils.setup_logger("bb84_protocol", level=logging.DEBUG)

# Load environment variables
load_dotenv()
PRIVATE_KEY = os.getenv("PRIVATE_KEY")

class BB84Protocol:
    def __init__(self, data: str, compression: str = "brotli", noise_model=False, shots: int = 1, output_path: str = None) -> None:
        """
        Initializes the BB84Protocol object.

        Args:
            data (str): The text data to be sent.
            compression (str): Compression method to use: "adaptive", "brotli", or False.
            noise_model (bool): Whether to use a noise model in the simulation.
            shots (int): Number of shots for the quantum simulation.
            output_path (str): Path to save the output data.
        """
        self.data = data
        self.compression = compression
        self.noise_model = noise_model
        self.shots = shots
        self.output_path = output_path
        self.device_backend = FakeVigo()

        self.binary_data = utils.convert_text_to_binary(data)
        self.data_length = len(self.binary_data)
        self.key_bits = self.generate_random_bits(self.data_length)
        self.base_bits = self.generate_random_bits(self.data_length)

        if compression == "brotli":
            compressed_data = c_utils.brotli_compression(self.binary_data)
            self.binary_data = utils.convert_text_to_binary(compressed_data)
        elif compression == "adaptive":
            compressed_data = c_utils.adaptive_compression(self.binary_data)
            self.binary_data = utils.convert_text_to_binary(compressed_data[0])

        # Ensure all strings are of equal length
        max_length = max(len(self.binary_data), len(self.key_bits), len(self.base_bits))
        self.binary_data = self.binary_data.zfill(max_length)
        self.key_bits = self.key_bits.zfill(max_length)
        self.base_bits = self.base_bits.zfill(max_length)

    def generate_random_bits(self, length: int) -> str:
        """
        Generates a string of random bits of a given length.

        Args:
            length (int): The length of the string of bits to generate.

        Returns:
            str: A string of random bits.
        """
        return ''.join(str(random.randint(0, 1)) for _ in range(length))

    def run_protocol(self) -> tuple[str, bool]:
        """
        Runs the BB84 protocol simulation.

        Returns:
            tuple: Tuple containing received data and a boolean indicating data match.
        """
        print(f"Data to send: {self.data}")
        print(f"Binary data: {self.binary_data}")
        encoded_data = self.binary_data # ''.join(str(int(bit) ^ int(self.base_bits[i]) ^ int(self.key_bits[i])) for i, bit in enumerate(self.binary_data))
        total_bits = len(encoded_data)
        start_time = time.time()

        logger.info(f"Running simulation with {total_bits} bits...")

        flipped_results = []

        with tqdm(total=total_bits, desc="Processing bits", unit="bit") as pbar:
            simulator = AerSimulator.from_backend(self.device_backend) if self.noise_model else BasicAer.get_backend("qasm_simulator")

            print(f"Data to send: {self.data}")
            print(f"Encoded data: {encoded_data}")

            for bit in encoded_data:
                circuit = QuantumCircuit(1, 1)
                circuit.x(0) if bit == '1' else circuit.id(0)
                circuit.barrier()
                circuit.measure(0, 0)

                result = simulator.run(circuit, shots=self.shots).result() if self.noise_model else execute(circuit, backend=simulator, shots=self.shots).result()
                res = max(result.get_counts().keys(), key=result.get_counts().get)

                print(f"Bit: {bit}, Result: {res}")

                flipped_result = res #utils.bit_flipper(res[0])
                flipped_results.append(flipped_result)
                pbar.update(1)

        end_time = time.time()
        logger.info(f"Time taken: {utils.convert_time(end_time - start_time)}")

        print(f"Flipped results: {flipped_results}")
        print(''.join(flipped_results))

        decoded_binary = ''.join(flipped_results) #''.join(str(int(bit) ^ int(self.base_bits[i]) ^ int(self.key_bits[i])) for i, bit in enumerate(flipped_results))
        print(f"Decoded binary: {decoded_binary}")
        decoded_text = c_utils.decompress_data(utils.convert_binary_to_text([decoded_binary[i:i+8] for i in range(0, len(decoded_binary), 8)]), self.compression, logs=True)
        print(f"Decoded text: {decoded_text}")

        logger.info(f"Received data: {decoded_text}")

        if self.output_path:
            utils.save_data(
                converted_chunks=decoded_text,
                output_path=self.output_path,
                data={
                    "time_taken": utils.convert_time(end_time - start_time),
                    "text": self.data,
                    "data_match": decoded_text == self.data,
                    "binary_text": self.binary_data,
                    "flipped_results": flipped_results,
                    "compression": self.compression,
                    "shots": self.shots,
                    "noise_model": self.noise_model,
                },
            )
            logger.info(f"Data saved to {self.output_path}")

        return decoded_text, decoded_text == self.data