"""
Module for converting assembly code to JSON format.
"""

import json

input_file = "text_input.txt"


def convert_asm_to_json(input_file, output_file):
    """
    Convert an assembly text file to a JSON file format.

    Reads lines from the input file, ignoring empty lines and comments,
    and writes them out as a dictionary mapped by line numbers to the
    output JSON file.

    Args:
        input_file (str): The path to the input assembly file.
        output_file (str): The path to the output JSON file.
    """

    try:
        data = {}
        i = 1

        with open(input_file, "r") as f:
            for line in f:
                line = line.split("#")[0].strip().replace(",", " ")

                if line == "":
                    continue

                """
                if ":" in line:
                    label = line.split(":")[0]
                    instruction = (
                        line.split(":")[1] if len(line.split(":", 1)) > 1 else ""
                    )

                    data[i] = label + ":"
                    if instruction != "":
                        data[i + 1] = instruction
                        i += 1
                else:
                """
                data[i] = line

                i += 1

        with open(output_file, "w") as json_f:
            json.dump(data, json_f, indent=4)

        print(f"Successfully converted {input_file} to {output_file}")

    except FileNotFoundError:
        print("Error: The input file was not found.")


# Usage
convert_asm_to_json(input_file, "json_input.json")
