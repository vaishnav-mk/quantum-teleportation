import random
import quantum_teleportation.utils as utils
import quantum_teleportation.compression_utils as c_utils
import quantum_teleportation.qiskit_utils as q_utils

from qiskit import QuantumCircuit, BasicAer, execute
from qiskit_aer import AerSimulator
from qiskit.providers.fake_provider import FakeVigo
from tqdm import tqdm
import logging
import time

logger = utils.setup_logger("bb84_protocol", level=logging.DEBUG)

device_backend = FakeVigo()

def generate_random_bits(length):
    return ''.join(str(random.randint(0, 1)) for _ in range(length))

def bb84_protocol(data, compression="brotli", noise_model=False, shots=1, output_path=None):
    binary_data = utils.convert_text_to_binary(data)
    data_length = len(binary_data)

    # Generate random bits for the key and bases
    key_bits = generate_random_bits(data_length)
    base_bits = generate_random_bits(data_length)

    # Compress the data if compression is enabled
    if compression == "brotli":
        compressed_data = c_utils.brotli_compression(binary_data)
        binary_data = utils.convert_text_to_binary(compressed_data)
    elif compression == "adaptive":
        compressed_data = c_utils.adaptive_compression(binary_data)
        binary_data = utils.convert_text_to_binary(compressed_data[0])

    # Pad the shorter strings with zeros
    max_length = max(len(binary_data), len(key_bits), len(base_bits))
    binary_data = binary_data.zfill(max_length)
    key_bits = key_bits.zfill(max_length)
    base_bits = base_bits.zfill(max_length)

    # Encode the data using the key and bases
    encoded_data = ''.join(str(int(bit) ^ int(base_bits[i]) ^ int(key_bits[i])) for i, bit in enumerate(binary_data))

    # Simulate the transmission of the encoded data
    total_bits = len(encoded_data)
    start_time = time.time()

    if logger.isEnabledFor(logging.INFO):
        logger.info(f"Running simulation with {total_bits} bits...")

    flipped_results = []

    with tqdm(total=total_bits, desc="Processing bits", unit="bit") as pbar:
        simulator = None
        if noise_model:
            simulator = AerSimulator.from_backend(device_backend)
        else:
            simulator = BasicAer.get_backend("qasm_simulator")

        for bit in encoded_data:
            circuit = QuantumCircuit(1, 1)
            circuit.x(0 if bit == '0' else 0)  # Change this line
            circuit.barrier()
            circuit.measure(0, 0)

            if noise_model:
                result = simulator.run(circuit, shots=shots).result()
            else:
                result = execute(circuit, backend=simulator, shots=shots).result()

            res = max(result.get_counts(), key=result.get_counts().get)
            flipped_result = utils.bit_flipper(res[0])
            flipped_results.append(flipped_result)
            pbar.update(1)

    end_time = time.time()
    logger.info(f"Time taken: {utils.convert_time(end_time - start_time)}")

    decoded_binary = ''.join(str(int(bit) ^ int(base_bits[i]) ^ int(key_bits[i])) for i, bit in enumerate(flipped_results))
    decoded_text = c_utils.decompress_data(utils.convert_binary_to_text([decoded_binary[i:i+8] for i in range(0, len(decoded_binary), 8)]), compression, logs=True)

    logger.info(f"Received data: {decoded_text}")

    if output_path:
        utils.save_data(
            converted_chunks=decoded_text,
            output_path=output_path,
            data={
                "time_taken": utils.convert_time(end_time - start_time),
                "text": data,
                "data_match": decoded_text == data,
                "binary_text": binary_data,
                "flipped_results": flipped_results,
                "compression": compression,
                "shots": shots,
                "noise_model": noise_model,
            },
        )
        logger.info(f"Data saved to {output_path}")

    return decoded_text, decoded_text == data

def decode_bb84(encoded_data, key_bits, base_bits):
    decoded_binary = ''.join(str(int(bit) ^ int(base_bits[i]) ^ int(key_bits[i])) for i, bit in enumerate(encoded_data))
    decoded_text = utils.convert_binary_to_text([decoded_binary[i:i+8] for i in range(0, len(decoded_binary), 8)])
    return decoded_text