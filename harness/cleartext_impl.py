#!/usr/bin/env python3
"""
Cleartext reference for the “ML Inference” workload.
For each test case:
    - Reads the plain_input.bin file from the dataset intermediate directory
    - Writes the result to expected_XXX.txt for each test case (# datasets/expected.txt)
"""

from pathlib import Path
from utils import parse_submission_arguments

def main():
    __, params, __, __, __, __ = parse_submission_arguments('Generate dataset for FHE benchmark.')
    INPUT_PATH = params.dataset_intermediate_dir() / f"plain_output.bin"
    
    # Get reference result by reading from INPUT_PATH
    result = INPUT_PATH.read_text(encoding="utf-8").strip()

    # Write to expected.txt (overwrites if it already exists)
    OUT_PATH = params.dataset_intermediate_dir() / f"expected.txt"
    OUT_PATH.write_text(f"{result}\n", encoding="utf-8")

if __name__ == "__main__":
    main()