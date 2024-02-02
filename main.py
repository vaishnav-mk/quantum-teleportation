from qiskit import QuantumCircuit, BasicAer, execute
import time
from tqdm import tqdm


class QuantumDataTeleporter:
    def __init__(self, separator=",", shots=1, file_path=None, text_to_send=None):
        if not file_path and not text_to_send:
            raise ValueError("Either file_path or text_to_send must be provided.")
        self.shots = shots
        self.separator = self.convert_text_to_binary(separator)
        self.text_to_send = (
            self.text_from_file(file_path)
            if file_path
            else text_to_send
        )
        self.binary_text = self.convert_text_to_binary(",".join(self.text_to_send))
        self.circuits = [QuantumCircuit(3, 3) for _ in range(len(self.binary_text))]
        self.create_circuits()

    def text_from_file(self, file_path):
        try:
            with open(file_path, "r") as file:
                text_content = file.read()
                return text_content
        except FileNotFoundError:
            print(f"File '{file_path}' not found.")
            return None

    def convert_text_to_binary(self, text):
        binary_result = "".join(format(ord(char), "08b") for char in text)
        return binary_result

    def convert_binary_to_text(self, binary_str):
        binary_chunks = [binary_str[i : i + 8] for i in range(0, len(binary_str), 8)]
        text = "".join(chr(int(chunk, 2)) for chunk in binary_chunks)
        return text

    def bit_flipper(self, bits):
        return "".join(["1" if x == "0" else "0" for x in bits])

    def handle_flipped_results(self, flipped_results):
        merged_binary = "".join(flipped_results)
        binary_chunks = merged_binary.split(self.separator)

        for i in range(1, len(binary_chunks)):
            if binary_chunks[i - 1] == "" and binary_chunks[i] == "":
                binary_chunks[i - 1] = self.separator
                binary_chunks[i] = ""
        binary_chunks = [chunk for chunk in binary_chunks if chunk != ""]

        return binary_chunks

    def create_circuits(self):
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

    def run_simulation(self):
        total_characters = len(self.circuits)
        start_time = time.time()

        print(f"Processing {total_characters} characters...")
        flipped_results = []

        with tqdm(total=total_characters, desc="Processing characters", unit="char") as pbar:
            simulator = BasicAer.get_backend("qasm_simulator")

            for circuit in self.circuits:
                result = execute(circuit, backend=simulator, shots=self.shots).result()
                flipped_result = self.bit_flipper(list(result.get_counts())[0][0])
                flipped_results.append(flipped_result)
                pbar.update(1)

        end_time = time.time()
        print(f"\nTime taken: {end_time - start_time} seconds.")
        binary_chunks = self.handle_flipped_results(flipped_results)
        converted_chunks = "".join(
            [self.convert_binary_to_text(chunk) for chunk in binary_chunks]
        )

        return converted_chunks, converted_chunks == self.text_to_send


# Example usage with a file

file_path = "text.txt"
quantum_communication = QuantumDataTeleporter(file_path=file_path, shots=1)
received_data, is_data_match = quantum_communication.run_simulation()

print(f"Received Data: {received_data}")
print(f"Sent Data == Received Data: {is_data_match}")

# Example usage with a string

text = "Hello, World!"
quantum_communication = QuantumDataTeleporter(text_to_send=text, shots=1)
received_data, is_data_match = quantum_communication.run_simulation()

print(f"Received Data: {received_data}")
print(f"Sent Data == Received Data: {is_data_match}")