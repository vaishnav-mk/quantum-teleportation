import base64
import brotli

def adaptive_compression(text: str, threshold = 128) -> tuple[str, str, float]:
    """
    Compresses the given text using Brotli if the size exceeds a threshold,
    otherwise uses no compression.

    Args:
        text (str): Text to compress.

    Returns:
        tuple: Compressed data, compression method, and compression percentage.
    """
    if len(text) <= threshold:
        return text
    else:
        compressed_data, compressed_percentage = brotli_compression(text)
        return compressed_data, "brotli", compressed_percentage

def brotli_compression(data: str) -> tuple[str, float]:
    """
    Compresses data using Brotli compression algorithm, encodes the compressed data in Base64,
    and calculates the compression percentage.

    Args:
        data (str): The data to be compressed.

    Returns:
        tuple[str, float]: A tuple containing the Base64 encoded compressed data
        and the compression percentage.
    """
    original_length = len(data)
    compressed_data = brotli.compress(data.encode())
    base64_encoded_data = base64.b64encode(compressed_data).decode()
    compressed_length = len(base64_encoded_data)
    compression_percentage = (
        (original_length - compressed_length) / original_length
    ) * 100

    # Ensure both the encoded compressed data and the compression percentage are returned
    print(f"Original length: {original_length} bytes")
    print(f"Compressed length: {compressed_length} bytes")
    print(f"Compression percentage: {compression_percentage:.2f}")
    return base64_encoded_data



def brotli_decompression(compressed_data: str) -> str:
    """
    Decompresses Base64 encoded compressed data using Brotli decompression algorithm.

    Args:
        compressed_data (str): The Base64 encoded compressed data.

    Returns:
        str: The decompressed data.
    """
    compressed_data_bytes = base64.b64decode(compressed_data.encode())
    decompressed_data = brotli.decompress(compressed_data_bytes).decode()
    return decompressed_data


def adaptive_decompression(data: str) -> str:
    """
    Decompresses data using the adaptive compression algorithm.

    Args:
        data (str): Compressed data to decompress.

    Returns:
        str: Decompressed data.
    """
    try:
        decoded_data = base64.b64decode(data, validate=True)
        decompressed_data = brotli.decompress(decoded_data).decode()
        return decompressed_data
    except Exception:
        return data

def decompress_data(data: str, algorithm: str, logs: bool = True) -> str:
    """
    Decompresses the given data based on the specified algorithm.

    Args:
        data (str): Compressed data to decompress.
        algorithm (str): Compression algorithm used.
        logs (bool, optional): Whether to print logs. Defaults to True.

    Returns:
        str: Decompressed data.
    """
    if algorithm == "brotli":
        decompressed_data = brotli_decompression(data)
        if logs:
            print("Decompressed using Brotli.")
    elif algorithm == "adaptive":
        decompressed_data = adaptive_decompression(data)
        if logs:
            print("Decompressed using Adaptive compression.")
    elif not algorithm:
        decompressed_data = data
        if logs:
            print("No compression applied.")
    else:
        raise ValueError("Unsupported compression algorithm.")

    return decompressed_data