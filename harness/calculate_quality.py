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
    Usage:  python3 calculate_quality.py  <expected_file>  <result_file> <num_samples>
    Calculates accuracy by comparing labels line by line.
    Each file should contain one label per line.
    Returns accuracy metric and prints results.
    """
    __, params, __, __, __, __ = parse_submission_arguments('Generate query for FHE benchmark.')

    expected_file = params.datadir() / "dataset_labels.txt"
    result_file   = params.iodir() / "quality_result.txt"
    num_samples   = 10 if params.size == utils.SINGLE else 10000


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

    # Check if we have enough labels in both files
    if len(expected_labels) < num_samples:
        print(f"[harness] FAIL - Not enough expected labels: have {len(expected_labels)}, need {num_samples}")
        sys.exit(1)
    
    if len(result_labels) < num_samples:
        print(f"[harness] FAIL - Not enough result labels: have {len(result_labels)}, need {num_samples}")
        sys.exit(1)

    # Calculate accuracy for the first num_samples only
    expected_subset = expected_labels[:num_samples]
    result_subset = result_labels[:num_samples]
    
    correct_predictions = sum(1 for exp, res in zip(expected_subset, result_subset) if exp == res)
    accuracy = correct_predictions / num_samples 

    print(f"[harness] Accuracy: {accuracy:.4f} ({correct_predictions}/{num_samples} correct)")

    OUT_PATH = params.measuredir() / f"quality.txt"
    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUT_PATH.write_text(f"{accuracy:.4f}\n({correct_predictions}/{num_samples} correct)\n", encoding="utf-8")


if __name__ == "__main__":
    main()