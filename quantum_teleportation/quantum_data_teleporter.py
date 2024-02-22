import quantum_teleportation.utils as utils
import quantum_teleportation.qiskit_utils as q_utils

from qiskit import QuantumCircuit, BasicAer, execute, QuantumRegister, ClassicalRegister
from qiskit_aer import AerSimulator
from qiskit.providers.fake_provider import FakeVigo
from qiskit_aer.noise import NoiseModel

from dotenv import load_dotenv
import matplotlib.pyplot as plt
from tqdm import tqdm
import time
import os

load_dotenv()

PRIVATE_KEY = os.getenv("PRIVATE_KEY")

if not PRIVATE_KEY:
    print(
        "Warning: No private key found in the environment variables. Generating a random key..."
    )
    PRIVATE_KEY = q_utils.qrng(1000)
    os.environ["PRIVATE_KEY"] = PRIVATE_KEY

    with open(".env", "a") as f:
        f.write(f"PRIVATE_KEY={PRIVATE_KEY}")

device_backend = FakeVigo()


class QuantumDataTeleporter:
    def __init__(
        self,
        shots: int = 1,
        file_path: str = None,
        text_to_send: str = None,
        noise_model=False,
    ) -> None:
        """
        Initializes the QuantumDataTeleporter object.

        Args:
            separator (str): Separator used for binary encoding.
            shots (int): Number of shots for the quantum simulation.
            file_path (str): Path to the file for reading text data.
            text_to_send (str): Text data to be sent if file_path is not provided.
        """
        if not file_path and not text_to_send:
            raise ValueError("Either file_path or text_to_send must be provided.")
        self.shots = shots
        self.text_to_send = (
            utils.text_from_file(file_path) if file_path else text_to_send
        )
        self.noise_model = noise_model

        _binary_text = utils.convert_text_to_binary(self.text_to_send)

        self.private_key = PRIVATE_KEY

        if self.private_key:
            if len(self.private_key) != len(self.text_to_send):
                print(
                    "Warning: Private key length does not match text length. Slicing..."
                )
                if len(self.private_key) < len(_binary_text):
                    self.private_key = (
                        self.private_key
                        + self.private_key[: len(_binary_text) - len(self.private_key)]
                    )
                else:
                    self.private_key = self.private_key[: len(_binary_text)]

        self.binary_text = utils.xor_encode(_binary_text, self.private_key)

        self.circuits = []
        self.noise_model = noise_model

        self.circuits = [QuantumCircuit(6, 6) for _ in range(len(self.binary_text))]
        self.create_circuits()

    def calculate_adaptive_shots(
        self,
        circuit_complexity: int,
        text_length: int,
        confidence_level: float = 0.90,
        base_shots: int = 250,
        max_shots: int = 1024
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
        # print(f"Complexity: {circuit_complexity}, Text Length: {text_length}")
        additional_shots_complexity = min(circuit_complexity * 5, max_shots - base_shots)
        additional_shots_length = min(text_length * 0.1, max_shots - base_shots)

        # print(f"Complexity Shots: {additional_shots_complexity}, Length Shots: {additional_shots_length}")
        additional_shots = round((additional_shots_complexity + additional_shots_length) / 2)

        if confidence_level > 0.90:
            additional_shots = min(circuit_complexity * 1.5, max_shots - base_shots)

        return base_shots + additional_shots


    def handle_flipped_results(self, flipped_results: list[str]) -> list[str]:
        """Handles flipped results by merging and splitting binary chunks into bytes.

        Args:
            flipped_results (list): List of flipped results.

        Returns:
            list: List of bytes (8-bit chunks).
        """

        merged_binary = "".join(flipped_results)

        # Separate binary chunks into 8-bit bytes
        bytes_list = []
        for i in range(0, len(merged_binary), 8):
            byte = merged_binary[i : i + 8]
            bytes_list.append(byte)

        return bytes_list

    def create_circuits(self) -> None:
        """
        Creates quantum circuits based on the binary text.
        """
        for i in range(len(self.binary_text)):
            self.circuits[i].x(1 if self.binary_text[i] == "1" else 0)
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

            # ec
            self.circuits[i].barrier()
            self.circuits[i].measure([0, 1, 2], [3, 4, 5])
            self.circuits[i].cx(3, 4)
            self.circuits[i].cx(3, 5)
            self.circuits[i].cx(4, 5)
            self.circuits[i].barrier()
            self.circuits[i].ccx(3, 4, 5)
            self.circuits[i].measure([5], [0])

            # self.circuits[i].draw(output="mpl", filename=f"pics/circuit_{i}.png")

    def plot_histogram(self, counts, save_path=None):
        plt.bar(counts.keys(), counts.values())
        plt.xlabel("Outcome")
        plt.ylabel("Frequency")
        plt.title("Measurement Outcomes Histogram")
        if save_path:
            plt.savefig(save_path)
        plt.show()

    def run_simulation(self) -> tuple[str, bool]:
        """
        Runs the quantum simulation.

        Args:
            noise_model (NoiseModel, optional): The noise model to apply to the simulation. Defaults to None.

        Returns:
            tuple: Tuple containing received data and a boolean indicating data match.
        """
        total_characters = len(self.circuits)
        start_time = time.time()

        self.shots = self.calculate_adaptive_shots(
            len(self.circuits[0] if self.circuits else 0),
            text_length=len(self.text_to_send),
        )

        print(
            f"Processing {len(self.text_to_send)} characters ({total_characters} bits)... with {self.shots} shots. | Noise Model: {self.noise_model}"
        )
        flipped_results = []

        with tqdm(
            total=total_characters, desc="Processing characters", unit="char"
        ) as pbar:
            simulator = None
            if self.noise_model:
                simulator = AerSimulator.from_backend(device_backend)
            else:
                simulator = BasicAer.get_backend("qasm_simulator")

            for circuit in self.circuits:
                if self.noise_model:
                    result = simulator.run(circuit).result()
                else:
                    result = execute(circuit, backend=simulator, shots=1).result()

                res = max(result.get_counts(), key=result.get_counts().get)

                flipped_result = utils.bit_flipper(res[0])
                flipped_results.append(flipped_result)
                pbar.update(1)

        # self.plot_histogram(result.get_counts(), save_path="pics/histogram.png")

        end_time = time.time()
        print(f"\nTime taken: {utils.convert_time(end_time - start_time)}\n")

        flipped_results = utils.xor_decode(flipped_results, self.private_key)

        binary_chunks = self.handle_flipped_results(flipped_results)
        converted_chunks = utils.convert_binary_to_text(binary_chunks)

        if converted_chunks != self.text_to_send:
            print("Data mismatch.")
            comparison_result = utils.compare_strings(
                self.text_to_send, converted_chunks
            )
            print("Percentage of similarity: ", comparison_result["percentage_match"])
            print("Sent data:\n", comparison_result["marked_string1"])
            print("Received data:\n", comparison_result["marked_string2"])
            print("\n")

        return converted_chunks, converted_chunks == self.text_to_send
