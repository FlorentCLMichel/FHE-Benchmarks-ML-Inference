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
    size, params, seed, num_runs, clrtxt, quality_check = utils.parse_submission_arguments('Run ML Inference FHE benchmark.')
    if size > utils.SINGLE and not quality_check:
        print(f"Currently only single inference is supported for measuring latency.")
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
    dataset_path = params.datadir() / f"dataset.txt"
    cmd = ["python3", harness_dir/"generate_dataset.py", str(dataset_path)]
    subprocess.run(cmd, check=True)
    utils.log_step(1, "Harness: MNIST Test dataset generation")

    # 2. Client-side: Generate the cryptographic keys 
    # Note: this does not use the rng seed above, it lets the implementation
    #   handle its own prg needs. It means that even if called with the same
    #   seed multiple times, the keys and ciphertexts will still be different.
    subprocess.run([exec_dir/"client_key_generation", str(size)], check=True)
    utils.log_step(2 , "Client: Key Generation")
    # Report size of keys and encrypted data
    utils.log_size(io_dir / "public_keys", "Client: Public and evaluation keys")

    # 3. Server-side: Preprocess the (encrypted) dataset using exec_dir/server_preprocess_model
    subprocess.run(exec_dir/"server_preprocess_model", check=True)
    utils.log_step(3, "Server: (Encrypted) model preprocessing")

    # Run steps 4-10 multiple times if requested
    for run in range(num_runs):
        if num_runs > 1:
            print(f"\n         [harness] Run {run+1} of {num_runs}")

        # 4. Client-side: Generate a new random input using harness/generate_input.py
        cmd = ["python3", harness_dir/"generate_input.py", str(size)]
        if seed is not None:
            # Use a different seed for each run but derived from the base seed
            rng = np.random.default_rng(seed)
            genqry_seed = rng.integers(0,0x7fffffff)
            cmd.extend(["--seed", str(genqry_seed)])
        subprocess.run(cmd, check=True)
        utils.log_step(4, "Harness: Input generation for Single Encrypted Inference")

        # 5. Client-side: Preprocess input using exec_dir/client_preprocess_input
        subprocess.run([exec_dir/"client_preprocess_input", str(size)], check=True)
        utils.log_step(5, "Client: Input preprocessing")

        # 6. Client-side: Encrypt the input
        subprocess.run([exec_dir/"client_encode_encrypt_input", str(size)], check=True)
        utils.log_step(6, "Client: Input encryption")
        utils.log_size(io_dir / "ciphertexts_upload", "Client: Encrypted input")

        # 7. Server side: Run the encrypted processing run exec_dir/server_encrypted_compute
        subprocess.run([exec_dir/"server_encrypted_compute", str(size)], check=True)
        utils.log_step(7, "Server: Encrypted ML Inference computation")
        # Report size of encrypted results
        utils.log_size(io_dir / "ciphertexts_download", "Client: Encrypted results")

        # 8. Client-side: decrypt
        subprocess.run([exec_dir/"client_decrypt_decode", str(size)], check=True)
        utils.log_step(8, "Client: Result decryption")

        # 9. Client-side: post-process
        subprocess.run([exec_dir/"client_postprocess", str(size)], check=True)
        utils.log_step(9, "Client: Result postprocessing")

        # 10 Verify the result
        expected_file = params.dataset_intermediate_dir() / "plain_output.bin"\
        # Andreea: In the case of multiple samples, the result file should have the correct number appended (iteration in the for loop)
        result_file = io_dir / "result_0.txt"

        if not result_file.exists():
            print(f"Error: Result file {result_file} not found")
            sys.exit(1)

        subprocess.run(["python3", harness_dir/"verify_result.py",
            str(expected_file), str(result_file)], check=False)

        # 11. Store measurements
        run_path = params.measuredir() / f"results-{run+1}.json"
        run_path.parent.mkdir(parents=True, exist_ok=True)
        utils.save_run(run_path)

    
    if quality_check:
        print("------------------------------------------------------------------")
        print("         [harness] Running quality check for encrypted inference.")
        # 12.1. Client-side: Generate a new random input using harness/generate_input.py
        cmd = ["python3", harness_dir/"generate_input.py", str(size)]
        if seed is not None:
            # Use a different seed for each run but derived from the base seed
            rng = np.random.default_rng(seed)
            genqry_seed = rng.integers(0,0x7fffffff)
            cmd.extend(["--seed", str(genqry_seed)])
        if quality_check:
            cmd.extend(["--run_quality_check", "True"])
        subprocess.run(cmd, check=True)
        utils.log_step(12.1, "Harness: Input generation for Encrypted Model Quality")

        # 12.2 Run the cleartext computation in cleartext_impl.py
        test_pixels = params.dataset_intermediate_dir() / f"test_pixels.txt"
        reference_model_predictions = params.dataset_intermediate_dir() / f"reference_model_predictions.txt"
        subprocess.run(["python3", harness_dir/"cleartext_impl.py", str(test_pixels), str(reference_model_predictions)], check=True)
        print("         [harness] Wrote reference model predictions to: ", reference_model_predictions)

        # 12.3. Run the quality check for encrypted inference.
        cmd = [exec_dir/"server_encrypted_model_quality", str(size)]
        subprocess.run(cmd, check=True)
        utils.log_step(12.3, "Server: Encrypted inference model quality check")

        # 12.4. Calculate and save accuracy.
        subprocess.run(["python3", harness_dir/"calculate_quality.py",
            str(size)], check=True)

    print(f"\nAll steps completed for the {instance_name(size)} inference!")

if __name__ == "__main__":
    main()