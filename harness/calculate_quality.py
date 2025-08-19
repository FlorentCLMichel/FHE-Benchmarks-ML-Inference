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
    __, params, __, __, __ = parse_submission_arguments('Generate query for FHE benchmark.')

    test_set_label_file = params.get_ground_truth_labels_file()
    harness_model_pred = params.get_harness_model_predictions_file()
    encrypted_model_pred = params.get_encrypted_model_predictions_file()

    try:
        # Read expected labels (one per line)
        test_set_labels = test_set_label_file.read_text().strip().split('\n')
        test_set_labels = [label.strip() for label in test_set_labels if label.strip()]

        # Read result labels (one per line)
        enc_model_preds = encrypted_model_pred.read_text().strip().split('\n')
        enc_model_preds = [label.strip() for label in enc_model_preds if label.strip()]

        harness_model_pred = harness_model_pred.read_text().strip().split('\n')
        harness_model_pred = [label.strip() for label in harness_model_pred if label.strip()]

    except Exception as e:
        print(f"[harness] failed to read files: {e}")
        sys.exit(1)

    num_samples = len(enc_model_preds)

    correct_enc_pred = sum(1 for exp, res in zip(test_set_labels, enc_model_preds) if exp == res)
    encrypted_model_accuracy = correct_enc_pred / num_samples
    print(f"[harness] Encrypted Model Accuracy: {encrypted_model_accuracy:.4f} ({correct_enc_pred}/{num_samples} correct)")
    utils.log_quality(correct_enc_pred, num_samples, "Encrypted model quality")

    correct_harness_model_pred = sum(1 for exp, res in zip(test_set_labels, harness_model_pred) if exp == res)
    harness_model_accuracy = correct_harness_model_pred / num_samples
    print(f"[harness] Harness Model Accuracy: {harness_model_accuracy:.4f} ({correct_harness_model_pred}/{num_samples} correct)")
    utils.log_quality(correct_harness_model_pred, num_samples, "Harness plaintext model quality")

    run_path = params.measuredir() / f"quality.json"
    run_path.parent.mkdir(parents=True, exist_ok=True)
    utils.save_quality(run_path)



if __name__ == "__main__":
    main()