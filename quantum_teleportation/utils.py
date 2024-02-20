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


def convert_text_to_binary(text: str) -> str:
    """
    Converts text to binary.

    Args:
        text (str): Input text.

    Returns:
        str: Binary representation of the input text.
    """
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
    text = bytearray(int(binary, 2) for binary in binary_list).decode("utf-8")
    return text


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
