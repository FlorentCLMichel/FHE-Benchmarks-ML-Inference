#!/usr/bin/env python3
"""
run_submission.py - run the entire submission process, from build to verify
"""

# TODO: Add license and copyright

import subprocess
import pathlib
import sys
import numpy as np
import utils
from params import instance_name

def main():
    """
    Run the entire submission process, from build to verify
    """
    
    # 0. Prepare running
    # Get the arguments
    size, params, seed, num_runs, clrtxt = utils.parse_submission_arguments('Run ML Inference FHE benchmark.')
    if size > utils.SINGLE:
        print(f"Currently single inference is the only supported size for this benchmark.")
        sys.exit(1)
    test = instance_name(size)
    print(f"\n[harness] Running submission for {test} inference")

    # Ensure the required directories exist
    utils.ensure_directories(params.rootdir)

    # Build the submission if not built already
    utils.build_submission(params.rootdir/"scripts")

    # The harness scripts are in the 'harness' directory,
    # the executables are in the directory submission/build
    harness_dir = params.rootdir/"harness"
    exec_dir = params.rootdir/"submission"/"build"

    # Remove and re-create IO directory
    io_dir = params.iodir()
    if io_dir.exists():
        subprocess.run(["rm", "-rf", str(io_dir)], check=True)
    io_dir.mkdir(parents=True)
    utils.log_step(0, "Init", True)

    # 1. Client-side: Generate the test datasets
    cmd = ["python3", harness_dir/"generate_dataset.py", str(size)]
    subprocess.run(cmd, check=True)
    utils.log_step(1, "Test dataset generation")

    # 2. Client-side: Preprocess the dataset using exec_dir/client_preprocess_dataset
    subprocess.run([exec_dir/"client_preprocess_dataset", str(size)], check=True)
    utils.log_step(2, "Test dataset preprocessing")

    # 3. Client-side: Generate the cryptographic keys 
    # Note: this does not use the rng seed above, it lets the implementation
    #   handle its own prg needs. It means that even if called with the same
    #   seed multiple times, the keys and ciphertexts will still be different.
    subprocess.run([exec_dir/"client_key_generation", str(size)], check=True)
    utils.log_step(3, "Key Generation")
    # Report size of keys and encrypted data
    utils.log_size(io_dir / "public_keys", "Public and evaluation keys")

    # 4. Server-side: Preprocess the (encrypted) dataset using exec_dir/server_preprocess_model
    subprocess.run(exec_dir/"server_preprocess_model", check=True)
    utils.log_step(4, "(Encrypted) model preprocessing")    

    # Run steps 5-11 multiple times if requested
    for run in range(num_runs):
        if num_runs > 1:
            print(f"\n         [harness] Run {run+1} of {num_runs}")

        # 5. Client-side: Generate a new random input using harness/generate_input.py
        cmd = ["python3", harness_dir/"generate_input.py", str(size)]
        if seed is not None:
            # Use a different seed for each run but derived from the base seed
            genqry_seed = rng.integers(0,0x7fffffff)
            cmd.extend(["--seed", str(genqry_seed)])
        subprocess.run(cmd, check=True)
        utils.log_step(5, "Input generation")

        # 6. Client-side: Preprocess input using exec_dir/client_preprocess_input
        subprocess.run([exec_dir/"client_preprocess_input", str(size)], check=True)
        utils.log_step(6, "Input preprocessing")

        # 7. Client-side: Encrypt the input
        subprocess.run([exec_dir/"client_encode_encrypt_input", str(size)], check=True)
        utils.log_step(7, "Input encryption")
        utils.log_size(io_dir / "ciphertexts_upload", "Encrypted input")

        # 8. Server side: Run the encrypted processing run exec_dir/server_encrypted_compute
        subprocess.run([exec_dir/"server_encrypted_compute", str(size)], check=True)
        utils.log_step(8, "Encrypted computation")
        utils.log_size(io_dir / "ciphertexts_download", "Encrypted results")

        # 9. Client-side: decrypt
        subprocess.run([exec_dir/"client_decrypt_decode", str(size)], check=True)
        utils.log_step(9, "Result decryption")

        # 10. Client-side: post-process
        subprocess.run([exec_dir/"client_postprocess", str(size)], check=True)
        utils.log_step(10, "Result postprocessing")

        # 11.1 Run the cleartext computation in cleartext_impl.py
        # If the cleartext computation takes too long, compute it once for a given state and skip this step.
        # One can store the results for multiple runs; currently, storing expected.txt works only with num_runs = 1.
        if clrtxt is None:
            subprocess.run(["python3", harness_dir/"cleartext_impl.py", str(size)], check=True)
            print("         [harness] Wrote expected result to: ", params.dataset_intermediate_dir() / "expected.txt")

        # 11.2 Verify the result
        expected_file = params.dataset_intermediate_dir() / "expected.txt"
        result_file = io_dir / "result.txt"

        if not result_file.exists():
            print(f"Error: Result file {result_file} not found")
            sys.exit(1)

        subprocess.run(["python3", harness_dir/"verify_result.py",
               str(expected_file), str(result_file)], check=False)

        # 12. Store measurements
        run_path = params.measuredir() / f"results-{run+1}.json"
        run_path.parent.mkdir(parents=True, exist_ok=True)
        utils.save_run(run_path)

    print(f"\nAll steps completed for the {instance_name(size)} inference!")

if __name__ == "__main__":
    main()