import json

input_file = "../text_input.txt"


def convert_asm_to_json(input_file, output_file):

    try:
        with open(input_file, "r") as f:
            data = {i: line for i, line in enumerate(f.read().splitlines(), start=1)}

        with open(output_file, "w") as json_f:
            json.dump(data, json_f, indent=4)

        print(f"Successfully converted {input_file} to {output_file}")

    except FileNotFoundError:
        print("Error: The input file was not found.")


# Usage
convert_asm_to_json(input_file, "../json_input.json")
