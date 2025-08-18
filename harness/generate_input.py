#!/usr/bin/env python3
"""
Generate a new input for each run.
"""
import numpy as np
from pathlib import Path
import utils
from utils import parse_submission_arguments
from mnist import mnist


def main():
    """
    Generate random value representing the query in the workload.
    """
    size, params, seed, __, __, quality_check = parse_submission_arguments('Generate input for FHE benchmark.')
    PIXELS_PATH = params.dataset_intermediate_dir() / f"plain_input.bin"
    LABELS_PATH = params.dataset_intermediate_dir() / f"plain_output.bin"
    PIXELS_PATH.parent.mkdir(parents=True, exist_ok=True)
    num_samples = 1

    if quality_check:
        PIXELS_PATH = params.dataset_intermediate_dir() / f"test_pixels.txt"
        LABELS_PATH = params.dataset_intermediate_dir() / f"test_labels.txt"
        # Andreea: changed SMALL to 10 for debugging purposes
        if size == utils.SINGLE:
            num_samples = 1
        elif size == utils.SMALL:
            num_samples = 10
        elif size == utils.MEDIUM:
            num_samples = 1000
        elif size == utils.LARGE:
            num_samples = 10000
    
    mnist.export_test_pixels_labels(
            data_dir = params.datadir(), 
            pixels_file=PIXELS_PATH, 
            labels_file=LABELS_PATH, 
            num_samples=num_samples, 
            seed=seed)
    
    

    


if __name__ == "__main__":
    main()
