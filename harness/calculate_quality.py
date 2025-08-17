#!/usr/bin/env python3
"""
calculate_quality.py - Quality calculator for ML Inference workload.
"""

import sys
from pathlib import Path
import utils
from utils import parse_submission_arguments

def main():

    """
    Calculates accuracy by comparing labels line by line.
    Each file should contain one label per line.
    Returns accuracy metric and prints results.
    """
    __, params, __, __, __, __ = parse_submission_arguments('Generate query for FHE benchmark.')

    expected_file = params.dataset_intermediate_dir() / "test_labels.txt"
    result_file   = params.iodir() / "result_labels.txt"

    try:
        # Read expected labels (one per line)
        expected_labels = expected_file.read_text().strip().split('\n')
        expected_labels = [label.strip() for label in expected_labels if label.strip()]
        
        # Read result labels (one per line)
        result_labels = result_file.read_text().strip().split('\n')
        result_labels = [label.strip() for label in result_labels if label.strip()]
        
    except Exception as e:
        print(f"[harness] failed to read files: {e}")
        sys.exit(1)

    num_samples = len(expected_labels)

    correct_predictions = sum(1 for exp, res in zip(expected_labels, result_labels) if exp == res)
    accuracy = correct_predictions / num_samples

    print(f"[harness] Accuracy: {accuracy:.4f} ({correct_predictions}/{num_samples} correct)")

    quality_json = {"accuracy": accuracy, "correct": correct_predictions, "total": num_samples}

    OUT_PATH = params.measuredir() / f"encrypted_model_quality.json"
    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    utils.save_quality(OUT_PATH, correct_predictions, num_samples, "encrypted model quality")


if __name__ == "__main__":
    main()