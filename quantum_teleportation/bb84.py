import random
import quantum_teleportation.utils as utils

def generate_random_bits(length):
    return ''.join(str(random.randint(0, 1)) for _ in range(length))

def bb84_protocol(data):
    binary_data = utils.convert_text_to_binary(data)
    data_length = len(binary_data)

    # Generate random bits for the key and bases
    key_bits = generate_random_bits(data_length)
    base_bits = generate_random_bits(data_length)

    # Encode the data using the key and bases
    encoded_data = ''.join(str(int(bit) ^ int(base_bits[i]) ^ int(key_bits[i])) for i, bit in enumerate(binary_data))

    return encoded_data, key_bits, base_bits

def decode_bb84(encoded_data, key_bits, base_bits):
    decoded_binary = ''.join(str(int(bit) ^ int(base_bits[i]) ^ int(key_bits[i])) for i, bit in enumerate(encoded_data))
    decoded_text = utils.convert_binary_to_text([decoded_binary[i:i+8] for i in range(0, len(decoded_binary), 8)])
    return decoded_text