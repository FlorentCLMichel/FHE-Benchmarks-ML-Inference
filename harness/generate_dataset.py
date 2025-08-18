#!/usr/bin/env python3
"""
If the datasets are too large to include, generate them here or pull them 
from a storage source.
"""

import sys
from pathlib import Path
from mnist import mnist

def main():
    """
    Usage:  python3 generate_dataset.py  <output_file>
    """

    if len(sys.argv) != 2:
        sys.exit("Usage: generate_dataset.py <output_file>")

    DATASET_PATH = Path(sys.argv[1])
    DATASET_PATH.parent.mkdir(parents=True, exist_ok=True)

    mnist.export_test_data(output_file=DATASET_PATH, num_samples=10000, seed=None)


if __name__ == "__main__":
    main()
