import os
import uuid
from PIL import Image
import base64
import logging
import colorlog
from datetime import datetime
import brotli


def text_from_file(file_path: str) -> str:
    """
    Reads text data from a file.

    Args:
        file_path (str): Path to the file.

    Returns:
        str: Text content of the file.

    Raises:
        FileNotFoundError: If the file is not found.
    """
    try:
        with open(file_path, "r") as file:
            return file.read()
    except FileNotFoundError:
        print(f"File '{file_path}' not found.")
        return None


# After modification
def convert_text_to_binary(text):
    """
    Converts text to binary.
    Args:
        text (str): Input text.
    Returns:
        str: Binary representation of the input text.
    """
    if not isinstance(text, str):
        text = str(text)  # Convert to string if not already a string
    binary_result = "".join(format(byte, "08b") for byte in bytearray(text, "utf8"))
    return binary_result


def convert_text_to_binary_with_filter(text: str) -> tuple[str, str]:
    """
    Converts text to binary, excluding characters that are out of ASCII bounds.

    Args:
        text (str): Input text.

    Returns:
        Tuple[str, str]: Binary representation of the filtered text and the new filtered text.
    """
    filtered_text = []
    binary_result = []

    for char in text:
        if ord(char) < 256:
            binary_char = format(ord(char), "08b")
            binary_result.append(binary_char)
            filtered_text.append(char)
        else:
            print(f"Character {char} is out of ASCII bounds and will be excluded.")

    binary_result_str = "".join(binary_result)
    filtered_text_str = "".join(filtered_text)

    return binary_result_str, filtered_text_str


def convert_binary_to_text(binary_list) -> str:
    """
    Converts an array of binary strings to text.

    Args:
        binary_list (List[str]): List of binary strings.

    Returns:
        str: Text representation of the binary input.
    """
    try:
        text = bytearray(int(binary, 2) for binary in binary_list).decode("utf-8")
        return text
    except Exception as e:
        raise Exception(f"Error converting binary to text: {e} | Perhaps the key is incorrect? Eve is eveing")


def bit_flipper(bits: str) -> str:
    """
    Flips bits in the input.

    Args:
        bits (str): Input bit string.

    Returns:
        str: Flipped bit string.
    """
    return "".join(["1" if x == "0" else "0" for x in bits])


def convert_time(time_seconds):
    """
    Convert time in seconds to minutes or hours if necessary.

    Args:
        time_seconds (float): Time in seconds.

    Returns:
        str: Time in seconds, minutes, or hours.
    """
    if time_seconds >= 60:
        time_minutes = time_seconds / 60
        if time_minutes >= 60:
            time_hours = time_minutes / 60
            return f"{time_hours:.2f} hours"
        else:
            return f"{time_minutes:.2f} minutes"
    else:
        return f"{time_seconds:.2f} seconds"


def compare_strings(string1: str, string2: str) -> dict:
    """
    Compare two strings and provide information about their similarity.

    Args:
        string1 (str): The first string.
        string2 (str): The second string.

    Returns:
        dict: A dictionary containing information about the comparison.
    """
    common_chars = sum(c1 == c2 for c1, c2 in zip(string1, string2))
    total_chars = max(len(string1), len(string2))
    percentage_match = round(
        common_chars / total_chars * 100 if total_chars != 0 else 100, 2
    )

    differences = []
    marked_string1 = ""
    marked_string2 = ""
    for i, (c1, c2) in enumerate(zip(string1, string2)):
        if c1 != c2:
            differences.append((i, c1, c2))
            marked_string1 += f"\033[91m{c1}\033[0m"
            marked_string2 += f"\033[91m{c2}\033[0m"
        else:
            marked_string1 += c1
            marked_string2 += c2

    return {
        "percentage_match": percentage_match,
        "differences": differences,
        "marked_string1": marked_string1,
        "marked_string2": marked_string2,
        "total_chars": total_chars,
        "common_chars": common_chars,
        "string1_length": len(string1),
        "string2_length": len(string2),
    }


def xor_encode(binary: str, key: str) -> str:
    """
    Encodes a binary string using XOR with a key.

    Args:
        binary (str): Binary string to encode.
        key (str): Key for XOR encoding.

    Returns:
        str: Encoded binary string.
    """
    encoded_binary = ""
    for bit1, bit2 in zip(binary, key):
        if bit1 != bit2:
            encoded_binary += "1"
        else:
            encoded_binary += "0"
    return encoded_binary


def xor_decode(encoded_binary: str, key: str) -> str:
    """
    Decodes a binary string using XOR with a key.

    Args:
        encoded_binary (str): Encoded binary string to decode.
        key (str): Key for XOR decoding.

    Returns:
        str: Decoded binary string.
    """
    decoded_binary = ""
    for bit1, bit2 in zip(encoded_binary, key):
        if bit1 != bit2:
            decoded_binary += "1"
        else:
            decoded_binary += "0"
    return decoded_binary


def image_to_binary(image_path, grayscale=True, threshold=None):
    """
    Convert an image to binary.

    Args:
        image_path (str): Path to the image file.
        grayscale (bool, optional): Whether to convert the image to grayscale. Default is True.
        threshold (int, optional): Threshold value for binarization. Pixels above this value will be set to 1,
                                   and pixels below or equal to this value will be set to 0. Default is None.

    Returns:
        str: Binary representation of the image.
    """
    img = Image.open(image_path)

    if grayscale:
        img = img.convert("L")

    if threshold is not None:
        img = img.point(lambda p: p > threshold and 255)

    pixels = list(img.getdata())

    binary_data = [format(pixel, "08b") for pixel in pixels]

    binary_string = "".join(binary_data)

    return binary_string


def image_to_base64(image_path: str) -> str:
    """
    Encodes an image file to Base64 format.

    Args:
        image_path (str): Path to the image file.

    Returns:
        str: Base64 encoded string representing the image.
    """
    with open(image_path, "rb") as image_file:
        encoded_image = base64.b64encode(image_file.read()).decode("utf-8")
    print(f"Encoded image: {encoded_image}")
    return encoded_image


def base64_to_image(base64_string, output_path):
    """
    Convert a base64 encoded image string to an image file.

    Args:
        base64_string (str): Base64 encoded image string.
        output_path (str): Path to save the image file.

    Returns:
        str: Path to the saved image file.
    """
    image_data = base64.b64decode(base64_string)

    with open(output_path, "wb") as image_file:
        image_file.write(image_data)

    return output_path


def handle_flipped_results(flipped_results: list[str], logs: bool = False) -> list[str]:
    """Handles flipped results by merging and splitting binary chunks into bytes.
    Args:
        flipped_results (list): List of flipped results.
    Returns:
        list: List of bytes (8-bit chunks).
    """
    merged_binary = "".join(flipped_results)
    bytes_list = []
    for i in range(0, len(merged_binary), 8):
        byte = merged_binary[i : i + 8]
        bytes_list.append(byte)
    if logs:
        print(f"Merged binary: {merged_binary}")
        print(f"Bytes list: {bytes_list}")
    return bytes_list


def save_data(converted_chunks, output_path, image_path=None, data=None):
    """
    Save received data to a file.

    Args:
        converted_chunks (str): Received data to be saved.
        output_path (str): Path to the directory where the data will be saved.
        image_path (str, optional): Path to the original image file if applicable. Defaults to None.
    """
    print(f"Output path: {output_path} | Image path: {image_path}")
    if output_path is None:
        print("No output path provided. Data will not be saved.")
        return

    if not "/" in output_path and not "\\" in output_path:
        output_path = output_path + "/"

    if not os.path.isdir(output_path):
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        print(f"Created directory: {os.path.dirname(output_path)}")

    if os.path.isdir(output_path):
        if image_path:
            filename = os.path.basename(image_path)
        else:
            filename = f"output_{uuid.uuid4().hex[:8]}.txt"
        output_file_path = os.path.join(output_path, filename)
        print(f"Output file path: {output_file_path}")
    else:
        output_file_path = output_path
        print(f"Output file path: {output_file_path}")

    if image_path:
        print(f"Image path: {image_path}")
        output_file_path = output_file_path.replace(
            ".txt", os.path.splitext(image_path)[1]
        )
        print(f"Output file path after extension: {output_file_path}")
        base64_to_image(converted_chunks, output_file_path)
        print(f"Saved image to: {output_file_path}")
    else:
        if isinstance(converted_chunks, str):
            with open(output_file_path, "w") as f:
                f.write(f"time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} IST\n")
                if data:
                    for key, value in data.items():
                        f.write(f"{key}: {value}\n")
                    f.write("--------------------\n\n")
                f.write(converted_chunks)
                print(f"Saved text data to: {output_file_path}")
        else:
            with open(output_file_path, "wb") as f:
                f.write(converted_chunks)
                print(f"Saved binary data to: {output_file_path}")

    return output_file_path


class ColoredFormatter(colorlog.ColoredFormatter):
    def format(self, record):
        log_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        record.log_time = log_time
        return super().format(record)


def setup_logger(name, level=logging.DEBUG):
    logger = logging.getLogger(name)
    logger.setLevel(level)

    formatter = ColoredFormatter(
        "%(log_color)s[%(log_time)s] [%(levelname)s]: %(message)s",
        datefmt=None,
        reset=True,
        log_colors={
            "DEBUG": "cyan",
            "INFO": "green",
            "WARNING": "yellow",
            "ERROR": "red",
            "CRITICAL": "red,bg_white",
        },
        secondary_log_colors={},
        style="%",
    )

    stream_handler = logging.StreamHandler()
    stream_handler.setFormatter(formatter)

    logger.addHandler(stream_handler)

    return logger
