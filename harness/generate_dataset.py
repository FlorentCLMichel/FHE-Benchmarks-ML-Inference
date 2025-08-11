#!/usr/bin/env python3
"""
If the datasets are too large to include, generate them here or pull them 
from a storage source.
"""
import numpy as np
from pathlib import Path
from utils import parse_submission_arguments
from mnist import mnist

def main():
    """
    Generate random value representing the database in the workload.
    """
    __, params, __, __, __ = parse_submission_arguments('Generate dataset for FHE benchmark.')
    DATASET_PATH = params.datadir() / f"dataset.txt"
    DATASET_PATH.parent.mkdir(parents=True, exist_ok=True)

    mnist.export_test_data(data_dir = params.datadir(), output_file=DATASET_PATH, num_samples=10000)

if __name__ == "__main__":
    main()
