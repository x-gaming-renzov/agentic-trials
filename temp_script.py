import json
import os

def extract_and_save_elements(input_filename, output_filename, num_elements):
    base_path = os.getcwd()
    input_file_path = os.path.join(base_path, input_filename)
    output_file_path = os.path.join(base_path, output_filename)

    with open(input_file_path, 'r') as file:
        data = json.load(file)

    extracted_elements = data[:num_elements]

    with open(output_file_path, 'w') as file:
        json.dump(extracted_elements, file, indent=4)

extract_and_save_elements('data.json', 'elements.json', 5)