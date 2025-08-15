#!/usr/bin/env python3
"""
Generate a new input for each run.
"""
import numpy as np
from pathlib import Path
from utils import parse_submission_arguments
from mnist import mnist

def count_lines_in_file(file_path):
    """
    Count the number of lines in a file.
    
    Args:
        file_path (Path): Path to the file
        
    Returns:
        int: Number of lines in the file, or 0 if file doesn't exist
    """
    if file_path.exists():
        with open(file_path, 'r') as f:
            return sum(1 for line in f)
    else:
        return 0

def main():
    """
    Generate random value representing the query in the workload.
    """
    __, params, seed, __, __, __ = parse_submission_arguments('Generate query for FHE benchmark.')
    DATASET_PIXEL_PATH = params.datadir() / f"dataset_pixels.txt"
    DATASET_LABEL_PATH = params.datadir() / f"dataset_labels.txt"

    DATASET_INPUT_PATH = params.dataset_intermediate_dir() / f"plain_input.bin"
    DATASET_OUTPUT_PATH = params.dataset_intermediate_dir() / f"plain_output.bin"
    DATASET_INPUT_PATH.parent.mkdir(parents=True, exist_ok=True)


    # Set random seed if provided
    if seed is not None:
        np.random.seed(seed)
    
    # Pick a random query from the dataset.
    num_lines = count_lines_in_file(DATASET_PIXEL_PATH)
    random_line = np.random.randint(1, num_lines + 1)
    if DATASET_PIXEL_PATH.exists():
        with open(DATASET_PIXEL_PATH, 'r') as f:
            for i, line in enumerate(f):
                if i == random_line - 1:
                    break
    else:
        print(f"Dataset file {DATASET_PIXEL_PATH} does not exist.")
     # Write the input to a file
    with open(DATASET_INPUT_PATH, 'w') as f:
        # Assuming the line contains space-separated values, we can write it directly
        f.write(line.strip())

    if DATASET_LABEL_PATH.exists():
        with open(DATASET_LABEL_PATH, 'r') as f:
            for i, line in enumerate(f):
                if i == random_line - 1:
                    break
    else:
        print(f"Dataset file {DATASET_LABEL_PATH} does not exist.")

    # Write the label to a file
    with open(DATASET_OUTPUT_PATH, 'w') as f:
        f.write(line.strip())


if __name__ == "__main__":
    main()
