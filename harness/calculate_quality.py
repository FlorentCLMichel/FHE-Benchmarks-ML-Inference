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

    test_set_label = params.dataset_intermediate_dir() / "test_labels.txt"
    reference_model_predictions = params.dataset_intermediate_dir() / "reference_model_predictions.txt"
    result_file   = params.iodir() / "result_labels.txt"

    try:
        # Read expected labels (one per line)
        expected_labels = test_set_label.read_text().strip().split('\n')
        expected_labels = [label.strip() for label in expected_labels if label.strip()]
        
        # Read result labels (one per line)
        result_labels = result_file.read_text().strip().split('\n')
        result_labels = [label.strip() for label in result_labels if label.strip()]

        reference_model_preds = reference_model_predictions.read_text().strip().split('\n')
        reference_model_preds = [label.strip() for label in reference_model_preds if label.strip()]

    except Exception as e:
        print(f"[harness] failed to read files: {e}")
        sys.exit(1)

    num_samples = len(expected_labels)

    correct_encrypted_predictions = sum(1 for exp, res in zip(expected_labels, result_labels) if exp == res)
    encrypted_model_accuracy = correct_encrypted_predictions / num_samples
    print(f"[harness] Encrypted Model Accuracy: {encrypted_model_accuracy:.4f} ({correct_encrypted_predictions}/{num_samples} correct)")
    utils.log_quality(correct_encrypted_predictions, num_samples, "encrypted model quality")

    correct_ref_model_predictions = sum(1 for exp, res in zip(expected_labels, reference_model_preds) if exp == res)
    reference_model_accuracy = correct_ref_model_predictions / num_samples
    print(f"[harness] Reference Model Accuracy: {reference_model_accuracy:.4f} ({correct_ref_model_predictions}/{num_samples} correct)")
    utils.log_quality(correct_ref_model_predictions, num_samples, "reference model quality")

    OUT_PATH = params.measuredir() / f"encrypted_model_quality.json"
    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    utils.save_quality(OUT_PATH)


if __name__ == "__main__":
    main()