#!/usr/bin/env python3
"""
Cleartext reference for the “ML Inference” workload.
For each test case:
    - Reads the input pixels from the dataset intermediate directory
    - Writes the predicted labels to output_labels path.
"""

import sys
from pathlib import Path
from utils import parse_submission_arguments
from mnist import mnist

def main():
    """
    Usage:  python3 cleartext_impl.py  <input_pixels_path>  <output_labels_path>
    """

    if len(sys.argv) != 3:
        sys.exit("Usage: cleartext_impl.py <input_pixels_path> <output_labels_path>")

    INPUT_PATH = Path(sys.argv[1])
    OUTPUT_PATH = Path(sys.argv[2])
    model_path = "harness/mnist/mnist_ffnn_model.pth"

    mnist.run_predict(model_path=model_path, pixels_file=INPUT_PATH, predictions_file=OUTPUT_PATH)

if __name__ == "__main__":
    main()