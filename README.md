# FHE Benchmarking Suite - ML Inference
This repository contains the harness for the ML-inference workload of the FHE benchmarking suite of [HomomorphicEncrypption.org].
The harness currently supports mnist model benchmarking as specified in `harness/mnist` directory.
The `main` branch contains a reference implementation of this workload, under the `submission` subdirectory.

Submitters need to clone this reposiroty, create a new branch with a name in the format `<submitter>-<date>`, replace the content of the `submission` subdirectory by their own implementation, and push the new branch to this repository.
They also may need to changes or replace the script `scripts/build_task.sh` to account for dependencies and build environment for their submission.
Submitters are expected to document any changes made to the model architecture `harness/mnist/mnist.py` in the `submission/README.md` file. 

## Running the ML-inference workload
The build environment depends on OpenFHE being installed as specificied in `scripts/get_openfhe.sh` and `submission/CMakeLists.txt`
See https://github.com/openfheorg/openfhe-development#installation.

To run the workload, clone and install dependencies:
```console
git clone https://github.com/code-perspective/FHE-Benchmarks-ML-Inference.git
cd FHE-Benchmarks-ML-Inference

python -m venv bmenv
source ./bmenv/bin/activate
pip install -r requirements.txt

python3 harness/run_submission.py -h  # Information about command-line options
```

The harness script `harness/run_submission.py` will attempt to build the submission itself, if it is not already built. If already built, it will use the same project without re-building it (unless the code has changed). An example run is provided below.


```console
$ python3 harness/run_submission.py -h
usage: run_submission.py [-h] [--num_runs NUM_RUNS] [--seed SEED] [--clrtxt CLRTXT]
                         [--run_quality_check RUN_QUALITY_CHECK]
                         {0,1,2,3}

Run ML Inference FHE benchmark.

positional arguments:
  {0,1,2,3}             Instance size (0-single/1-small/2-medium/3-large)

options:
  -h, --help            show this help message and exit
  --num_runs NUM_RUNS   Number of times to run steps 4-9 (default: 1)
  --seed SEED           Random seed for dataset and query generation
  --clrtxt CLRTXT       Specify with 1 if to rerun the cleartext computation
  --run_quality_check RUN_QUALITY_CHECK
                        Specify this flag to run the quality check. instance
                        size 0 runs on 10 samples, small on 100, medium on
                        1000, large on 10000 samples

$ python3 ./harness/run_submission.py 0 --seed 3 --num_runs 2
 
[harness] Running submission for single inference
[get-openfhe] Found OpenFHE at /usr/local/google/home/gshruthi/projects/FHE-Benchmarks-ML-Inference/third_party/openfhe (use --force to rebuild).
-- FOUND PACKAGE OpenFHE
-- OpenFHE Version: 1.3.1
-- OpenFHE installed as shared libraries: ON
-- OpenFHE include files location: /usr/local/google/home/gshruthi/projects/FHE-Benchmarks-ML-Inference/third_party/openfhe/include/openfhe
-- OpenFHE lib files location: /usr/local/google/home/gshruthi/projects/FHE-Benchmarks-ML-Inference/third_party/openfhe/lib
-- OpenFHE Native Backend size: 64
-- Configuring done (0.0s)
-- Generating done (0.0s)
-- Build files have been written to: /usr/local/google/home/gshruthi/projects/FHE-Benchmarks-ML-Inference/submission/build
[ 27%] Built target server_preprocess_model
[ 27%] Built target client_preprocess_input
[ 33%] Built target client_postprocess
[ 44%] Built target mlp_encryption_utils
[ 55%] Built target client_key_generation
[ 66%] Built target client_encode_encrypt_input
[ 77%] Built target server_encrypted_compute
[ 88%] Built target client_decrypt_decode
[100%] Built target server_encrypted_model_quality
17:44:41 [harness] 1: Harness: MNIST Test dataset generation completed (elapsed: 7.3106s)
17:44:44 [harness] 2: Client: Key Generation completed (elapsed: 2.7355s)
         [harness] Client: Public and evaluation keys size: 1.4G
17:44:44 [harness] 3: Server: (Encrypted) model preprocessing completed (elapsed: 0.008s)

         [harness] Run 1 of 2
17:44:48 [harness] 4: Harness: Input generation for Single Encrypted Inference completed (elapsed: 3.7404s)
17:44:48 [harness] 5: Client: Input preprocessing completed (elapsed: 0.0061s)
17:44:48 [harness] 6: Client: Input encryption completed (elapsed: 0.0179s)
         [harness] Client: Encrypted input size: 354.8K
         [server] Loading keys
         [server] run encrypted MNIST inference
         [server] Execution time: 12 seconds
17:45:03 [harness] 7: Server: Encrypted ML Inference computation completed (elapsed: 14.9282s)
         [harness] Client: Encrypted results size: 65.6K
17:45:03 [harness] 8: Client: Result decryption completed (elapsed: 0.0199s)
17:45:03 [harness] 9: Client: Result postprocessing completed (elapsed: 0.0052s)
         [harness] Wrote expected result to:  /usr/local/google/home/gshruthi/projects/FHE-Benchmarks-ML-Inference/datasets/single/intermediate/expected.txt
[harness] PASS  (expected=7, got=7)
[total latency] 28.7717s

         [harness] Run 2 of 2
17:45:06 [harness] 4: Harness: Input generation for Single Encrypted Inference completed (elapsed: 3.3445s)
17:45:06 [harness] 5: Client: Input preprocessing completed (elapsed: 0.0056s)
17:45:06 [harness] 6: Client: Input encryption completed (elapsed: 0.0177s)
         [harness] Client: Encrypted input size: 354.8K
         [server] Loading keys
         [server] run encrypted MNIST inference
         [server] Execution time: 12 seconds
17:45:20 [harness] 7: Server: Encrypted ML Inference computation completed (elapsed: 14.1896s)
         [harness] Client: Encrypted results size: 65.6K
17:45:20 [harness] 8: Client: Result decryption completed (elapsed: 0.0196s)
17:45:20 [harness] 9: Client: Result postprocessing completed (elapsed: 0.0052s)
         [harness] Wrote expected result to:  /usr/local/google/home/gshruthi/projects/FHE-Benchmarks-ML-Inference/datasets/single/intermediate/expected.txt
[harness] PASS  (expected=7, got=7)
[total latency] 27.6363s

All steps completed for the single inference!
```

After finishing the run, deactivate the virtual environment.
```console
deactivate
```

## Directory structure

The directory structure of this reposiroty is as follows:
```
├─ README.md     # This file
├─ LICENSE.md    # Harness software license (Apache v2)
├─ harness/      # Scripts to drive the workload implementation
|   ├─ run_submission.py
|   ├─ verify_result.py
|   ├─ calculate_quality.py
|   └─ [...]
├─ datasets/     # The harness scripts create and populate this directory
├─ docs/         # Optional: additional documentation
├─ io/           # This directory is used for client<->server communication
├─ measurements/ # Holds logs with performance numbers
├─ scripts/      # Helper scripts for dependencies and build system
└─ submission/   # This is where the workload implementation lives
    ├─ README.md   # Submission documentation (mandatory)
    ├─ LICENSE.md  # Optional software license (if different from Apache v2)
    └─ [...]
```
Submitters must overwrite the contents of the `scripts` and `submissions`
subdirectories.

## Description of stages

A submitter can edit any of the `client_*` / `server_*` sources in `/submission`. 
Moreover, for the particular parameters related to a workload, the submitter can modify the params files.
If the current description of the files are inaccurate, the stage names in `run_submission` can be also 
modified.

The current stages are the following, targeted to a client-server scenario.
The order in which they are happening in `run_submission` assumes an initialization step which is 
database-dependent and run only once, and potentially multiple runs for multiple queries.
Each file can take as argument the test case size.


| Stage executables                | Description |
|----------------------------------|-------------|
| `client_key_generation`          | Generate all key material and cryptographic context at the client.           
| `client_preprocess_dataset`      | (Optional) Any in the clear computations the client wants to apply over the dataset/model.
| `client_preprocess_input`        | (Optional) Any in the clear computations the client wants to apply over the input.
| `client_encode_encrypt_query`    | Plaintext encoding and encryption of the input at the client.
| `server_preprocess_model`        | (Optional) Any in the clear or encrypted computations the server wants to apply over the model.
| `server_encrypted_compute`       | The computation the server applies to achieve the workload solution over encrypted data.
| `server_encrypted_compute`       | The computation the server applies on encypted data to measure encrypted model quality.
| `client_decrypt_decode`          | Decryption and plaintext decoding of the result at the client.
| `client_postprocess`             | Any in the clear computation that the client wants to apply on the decrypted result.


The outer python script measures the runtime of each stage.
The current stage separation structure requires reading and writing to files more times than minimally necessary.
For a more granular runtime measuring, which would account for the extra overhead described above, we encourage
submitters to separate and print in a log the individual times for reads/writes and computations inside each stage. 
