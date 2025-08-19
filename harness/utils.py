#!/usr/bin/env python3
"""
utils.py - Scaffolding code for running the submission.
"""

import sys
import subprocess
import argparse
import json
from datetime import datetime
from pathlib import Path
from params import InstanceParams, SINGLE, LARGE
from typing import Tuple

# Global variable to track the last timestamp
_last_timestamp: datetime = None
# Global variable to store measured times
_timestamps = {}
_timestampsStr = {}
# Global variable to store measured sizes
_bandwidth = {}
# Global variable to store model quality metrics
_model_quality = {}

def parse_submission_arguments(workload: str) -> Tuple[int, InstanceParams, int, int, int, bool]:
    """
    Get the arguments of the submission. Populate arguments as needed for the workload.
    """
    # Parse arguments using argparse
    parser = argparse.ArgumentParser(description=workload)
    parser.add_argument('size', type=int, choices=range(SINGLE, LARGE+1),
                        help='Instance size (0-single/1-small/2-medium/3-large)')
    parser.add_argument('--num_runs', type=int, default=1,
                        help='Number of times to run steps 4-9 (default: 1)')
    parser.add_argument('--seed', type=int,
                        help='Random seed for dataset and query generation')
    parser.add_argument('--clrtxt', type=int,
                        help='Specify with 1 if to rerun the cleartext computation')

    args = parser.parse_args()
    size = args.size
    seed = args.seed
    num_runs = args.num_runs
    clrtxt = args.clrtxt

    # Use params.py to get instance parameters
    params = InstanceParams(size)
    return size, params, seed, num_runs, clrtxt

def ensure_directories(rootdir: Path):
    """ Check that the current directory has sub-directories
    'harness', 'scripts', and 'submission' """
    required_dirs = ['harness', 'scripts', 'submission']
    for dir_name in required_dirs:
        if not (rootdir / dir_name).exists():
            print(f"Error: Required directory '{dir_name}'",
                  f"not found in {rootdir}")
            sys.exit(1)

def build_submission(script_dir: Path):
    """
    Build the submission, including pulling dependencies as neeed
    """
    # Clone and build OpenFHE if needed
    subprocess.run([script_dir/"get_openfhe.sh"], check=True)
    # CMake build of the submission itself
    subprocess.run([script_dir/"build_task.sh", "./submission"], check=True)

def log_step(step_num: int, step_name: str, start: bool = False):
    """ 
    Helper function to print timestamp after each step with second precision 
    """
    global _last_timestamp
    global _timestamps
    global _timestampsStr
    now = datetime.now()
    # Format with milliseconds precision
    timestamp = now.strftime("%H:%M:%S")

    # Calculate elapsed time if this isn't the first call
    elapsed_str = ""
    elapsed_seconds = 0
    if _last_timestamp is not None:
        elapsed_seconds = (now - _last_timestamp).total_seconds()
        elapsed_str = f" (elapsed: {round(elapsed_seconds, 4)}s)"

    # Update the last timestamp for the next call
    _last_timestamp = now

    if (not start):
        print(f"{timestamp} [harness] {step_num}: {step_name} completed{elapsed_str}")
        _timestampsStr[step_name] = f"{round(elapsed_seconds, 4)}s"
        _timestamps[step_name] = elapsed_seconds

def log_size(path: Path, object_name: str, flag: bool = False, previous: int = 0):
    global _bandwidth
    
    # Check if the path exists before trying to calculate size
    if not path.exists():
        print(f"         [harness] Warning: {object_name} path does not exist: {path}")
        _bandwidth[object_name] = "0B"
        return 0
    
    size = int(subprocess.run(["du", "-sb", path], check=True,
                           capture_output=True, text=True).stdout.split()[0])
    if(flag):
        size -= previous
    
    print("         [harness]", object_name, "size:", human_readable_size(size))

    _bandwidth[object_name] = human_readable_size(size)
    return size

def human_readable_size(n: int):
    for unit in ["B","K","M","G","T"]:
        if n < 1024:
            return f"{n:.1f}{unit}"
        n /= 1024
    return f"{n:.1f}P"

def save_run(path: Path, size: int = 0):
    global _timestamps
    global _timestampsStr
    global _bandwidth
    global _model_quality

    if size == 0:
        json.dump({
            "total_latency_ms": round(sum(_timestamps.values()), 4),
            "per_stage": _timestampsStr,
            "bandwidth": _bandwidth,
        }, open(path,"w"), indent=2)
    else:
        json.dump({
            "total_latency_ms": round(sum(_timestamps.values()), 4),
            "per_stage": _timestampsStr,
            "bandwidth": _bandwidth,
            "mnist_model_quality" : _model_quality,
        }, open(path,"w"), indent=2)

    print("[total latency]", f"{round(sum(_timestamps.values()), 4)}s")

def calculate_quality():
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
    log_quality(correct_enc_pred, num_samples, "Encrypted model quality")

    correct_harness_model_pred = sum(1 for exp, res in zip(test_set_labels, harness_model_pred) if exp == res)
    harness_model_accuracy = correct_harness_model_pred / num_samples
    print(f"[harness] Harness Model Accuracy: {harness_model_accuracy:.4f} ({correct_harness_model_pred}/{num_samples} correct)")
    log_quality(correct_harness_model_pred, num_samples, "Harness plaintext model quality")

def log_quality(correct_predictions, total_samples, tag):
    global _model_quality
    _model_quality[tag] = {
        "correct_predictions": correct_predictions,
        "total_samples": total_samples,
        "accuracy": correct_predictions / total_samples if total_samples > 0 else 0
    }