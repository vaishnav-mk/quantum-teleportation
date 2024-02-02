import quantum_communication.utils as utils
from qiskit import QuantumCircuit, BasicAer, execute
from tqdm import tqdm
import time


class QuantumDataTeleporter:
    def __init__(
        self,
        separator: str = ",",
        shots: int = 1,
        file_path: str = None,
        text_to_send: str = None,
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
        self.separator = utils.convert_text_to_binary(separator)
        self.text_to_send = (
            utils.text_from_file(file_path) if file_path else text_to_send
        )
        self.binary_text = utils.convert_text_to_binary(",".join(self.text_to_send))
        self.circuits = [QuantumCircuit(3, 3) for _ in range(len(self.binary_text))]
        self.create_circuits()

    def handle_flipped_results(self, flipped_results: list[str]) -> list[str]:
        """
        Handles flipped results by merging and splitting binary chunks.

        Args:
            flipped_results (list): List of flipped results.

        Returns:
            list: Binary chunks after processing.
        """
        merged_binary = "".join(flipped_results)
        binary_chunks = merged_binary.split(self.separator)

        for i in range(1, len(binary_chunks)):
            if binary_chunks[i - 1] == "" and binary_chunks[i] == "":
                binary_chunks[i - 1] = self.separator
                binary_chunks[i] = ""
        binary_chunks = [chunk for chunk in binary_chunks if chunk != ""]

        return binary_chunks

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

    def run_simulation(self) -> tuple[str, bool]:
        """
        Runs the quantum simulation.

        Returns:
            tuple: Tuple containing received data and a boolean indicating data match.
        """
        total_characters = len(self.circuits)
        start_time = time.time()

        print(f"Processing {total_characters} characters...")
        flipped_results = []

        with tqdm(
            total=total_characters, desc="Processing characters", unit="char"
        ) as pbar:
            simulator = BasicAer.get_backend("qasm_simulator")

            for circuit in self.circuits:
                result = execute(circuit, backend=simulator, shots=self.shots).result()
                flipped_result = utils.bit_flipper(list(result.get_counts())[0][0])
                flipped_results.append(flipped_result)
                pbar.update(1)

        end_time = time.time()
        print(f"\nTime taken: {end_time - start_time} seconds.")
        binary_chunks = self.handle_flipped_results(flipped_results)
        converted_chunks = "".join(
            [utils.convert_binary_to_text(chunk) for chunk in binary_chunks]
        )

        return converted_chunks, converted_chunks == self.text_to_send
