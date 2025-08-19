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
    size, params, seed, __, __ = parse_submission_arguments('Generate input for FHE benchmark.')
    PIXELS_PATH = params.get_test_input_file()
    LABELS_PATH = params.get_ground_truth_labels_file()
    PIXELS_PATH.parent.mkdir(parents=True, exist_ok=True)
    num_samples = params.get_batch_size()
    mnist.export_test_pixels_labels(
            data_dir = params.datadir(), 
            pixels_file=PIXELS_PATH, 
            labels_file=LABELS_PATH, 
            num_samples=num_samples, 
            seed=seed)
    
    

    


if __name__ == "__main__":
    main()
