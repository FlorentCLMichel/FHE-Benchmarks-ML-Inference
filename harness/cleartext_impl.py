#!/usr/bin/env python3
"""
Cleartext reference for the “add” workload.
For each test case:
    - Reads the dataset
    - Computes the sum between the two 
    - Writes the result to expected_XXX.txt for each test case (# datasets/expected.txt)
"""
import random
from pathlib import Path
from utils import parse_submission_arguments

def get_first_char_as_int(file_path):
    """
    Read the first character from the first line of a file and return it as an integer.
    
    Args:
        file_path (Path): Path to the file
        
    Returns:
        int: First character as integer, or None if file doesn't exist/is empty/not a digit
    """
    if file_path.exists():
        with open(file_path, 'r') as f:
            first_line = f.readline()
            if first_line and first_line[0].isdigit():
                return int(first_line[0])
            elif first_line:
                print(f"First character '{first_line[0]}' is not a digit")
                return None
            else:
                print("File is empty")
                return None
    else:
        print(f"File {file_path} does not exist")
        return None

def main():

    __, params, __, __, __ = parse_submission_arguments('Generate dataset for FHE benchmark.')
    DATASET_Q_PATH = params.dataset_intermediate_dir() / f"plain_input.bin"
    # Get reference result
    result = get_first_char_as_int(DATASET_Q_PATH)
    
    # Write to expected.txt (overwrites if it already exists)
    OUT_PATH = params.dataset_intermediate_dir() / f"expected.txt"
    OUT_PATH.write_text(f"{result}\n", encoding="utf-8")

if __name__ == "__main__":
    main()