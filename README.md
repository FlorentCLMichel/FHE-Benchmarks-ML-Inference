# FHE Benchmarking Suite - ML Inference
This repository contains the harness for the ML-inference workload of the FHE benchmarking suite of [HomomorphicEncrypption.org].
The harness currently supports mnist model benchmarking as specified in `harness/mnist` directory.
The `main` branch contains a reference implementation of this workload, under the `submission` subdirectory.

Submitters need to clone this repository, replace the content of the `submission` subdirectory by their own implementation.
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
usage: run_submission.py [-h] [--num_runs NUM_RUNS] [--seed SEED] [--clrtxt CLRTXT] {0,1,2,3}

Run ML Inference FHE benchmark.

positional arguments:
  {0,1,2,3}            Instance size (0-single/1-small/2-medium/3-large)

options:
  -h, --help           show this help message and exit
  --num_runs NUM_RUNS  Number of times to run steps 4-9 (default: 1)
  --seed SEED          Random seed for dataset and query generation
  --clrtxt CLRTXT      Specify with 1 if to rerun the cleartext computation
```

The single instance runs the inference for a single input and verifies the correctness of the obtained label compared to the ground-truth label.

```console
$ python3 ./harness/run_submission.py 0 --seed 3 --num_runs 2
 

[harness] Running submission for single inference
[get-openfhe] Found OpenFHE at .../ml-inference/third_party/openfhe (use --force to rebuild).
-- FOUND PACKAGE OpenFHE
-- OpenFHE Version: 1.3.1
-- OpenFHE installed as shared libraries: ON
-- OpenFHE include files location: .../ml-inference/third_party/openfhe/include/openfhe
-- OpenFHE lib files location: .../ml-inference/third_party/openfhe/lib
-- OpenFHE Native Backend size: 64
-- Configuring done (0.0s)
-- Generating done (0.0s)
-- Build files have been written to: .../ml-inference/submission/build
[ 12%] Built target client_preprocess_input
[ 25%] Built target client_postprocess
[ 37%] Built target server_preprocess_model
[ 62%] Built target client_key_generation
[ 62%] Built target mlp_encryption_utils
[ 75%] Built target client_encode_encrypt_input
[100%] Built target client_decrypt_decode
[100%] Built target server_encrypted_compute
02:01:26 [harness] 1: Harness: MNIST Test dataset generation completed (elapsed: 7.5245s)
02:01:29 [harness] 2: Client: Key Generation completed (elapsed: 2.5987s)
         [harness] Client: Public and evaluation keys size: 1.4G
02:01:29 [harness] 3: Server: (Encrypted) model preprocessing completed (elapsed: 0.0081s)

         [harness] Run 1 of 2
100.0%
100.0%
100.0%
100.0%
02:01:36 [harness] 4: Harness: Input generation for MNIST completed (elapsed: 6.8985s)
02:01:36 [harness] 5: Client: Input preprocessing completed (elapsed: 0.0058s)
02:01:36 [harness] 6: Client: Input encryption completed (elapsed: 0.0185s)
         [harness] Client: Encrypted input size: 354.8K
         [server] Loading keys
         [server] run encrypted MNIST inference
         [server] Execution time for ciphertext 0 : 12 seconds
02:01:50 [harness] 7: Server: Encrypted ML Inference computation completed (elapsed: 14.0882s)
         [harness] Client: Encrypted results size: 65.6K
02:01:50 [harness] 8: Client: Result decryption completed (elapsed: 0.0194s)
02:01:50 [harness] 9: Client: Result postprocessing completed (elapsed: 0.0054s)
[harness] PASS  (expected=7, got=7)
[total latency] 31.1672s

         [harness] Run 2 of 2
02:01:53 [harness] 4: Harness: Input generation for MNIST completed (elapsed: 3.6967s)
02:01:53 [harness] 5: Client: Input preprocessing completed (elapsed: 0.0057s)
02:01:53 [harness] 6: Client: Input encryption completed (elapsed: 0.0171s)
         [harness] Client: Encrypted input size: 354.8K
         [server] Loading keys
         [server] run encrypted MNIST inference
         [server] Execution time for ciphertext 0 : 13 seconds
02:02:09 [harness] 7: Server: Encrypted ML Inference computation completed (elapsed: 15.0818s)
         [harness] Client: Encrypted results size: 65.6K
02:02:09 [harness] 8: Client: Result decryption completed (elapsed: 0.0195s)
02:02:09 [harness] 9: Client: Result postprocessing completed (elapsed: 0.0055s)
[harness] PASS  (expected=7, got=7)
[total latency] 28.9577s

All steps completed for the single inference!
```

The batch inference cases run the inference for a batch of inputs of varying sizes. The accuracy (with respect to the ground truth labels) is compared between the decrypted results and the results obtained using the harness model.

```console
$python3 ./harness/run_submission.py 1 --seed 3 --num_runs 2

[harness] Running submission for small inference
[harness] Running submission for single inference
[get-openfhe] Found OpenFHE at .../ml-inference/third_party/openfhe (use --force to rebuild).
-- FOUND PACKAGE OpenFHE
-- OpenFHE Version: 1.3.1
-- OpenFHE installed as shared libraries: ON
-- OpenFHE include files location: .../ml-inference/third_party/openfhe/include/openfhe
-- OpenFHE lib files location: .../ml-inference/third_party/openfhe/lib
-- OpenFHE Native Backend size: 64
-- Configuring done (0.0s)
-- Generating done (0.0s)
-- Build files have been written to: .../ml-inference/submission/build
[ 12%] Built target client_preprocess_input
[ 25%] Built target client_postprocess
[ 37%] Built target server_preprocess_model
[ 62%] Built target client_key_generation
[ 62%] Built target mlp_encryption_utils
[ 75%] Built target client_encode_encrypt_input
[100%] Built target client_decrypt_decode
[100%] Built target server_encrypted_compute
20:54:08 [harness] 1: Harness: MNIST Test dataset generation completed (elapsed: 9.1386s)
20:54:11 [harness] 2: Client: Key Generation completed (elapsed: 3.6615s)
         [harness] Client: Public and evaluation keys size: 1.4G
20:54:12 [harness] 3: Server: (Encrypted) model preprocessing completed (elapsed: 0.2954s)

         [harness] Run 1 of 2
20:54:18 [harness] 4: Harness: Input generation for MNIST completed (elapsed: 6.4897s)
20:54:18 [harness] 5: Client: Input preprocessing completed (elapsed: 0.0898s)
20:54:19 [harness] 6: Client: Input encryption completed (elapsed: 0.4931s)
         [harness] Client: Encrypted input size: 5.2M
         [server] Loading keys
         [server] run encrypted MNIST inference
         [server] Execution time for ciphertext 0 : 15 seconds
         [server] Execution time for ciphertext 1 : 14 seconds
         [server] Execution time for ciphertext 2 : 11 seconds
         [server] Execution time for ciphertext 3 : 12 seconds
         [server] Execution time for ciphertext 4 : 10 seconds
         [server] Execution time for ciphertext 5 : 9 seconds
         [server] Execution time for ciphertext 6 : 9 seconds
         [server] Execution time for ciphertext 7 : 12 seconds
         [server] Execution time for ciphertext 8 : 11 seconds
         [server] Execution time for ciphertext 9 : 10 seconds
         [server] Execution time for ciphertext 10 : 10 seconds
         [server] Execution time for ciphertext 11 : 11 seconds
         [server] Execution time for ciphertext 12 : 10 seconds
         [server] Execution time for ciphertext 13 : 10 seconds
         [server] Execution time for ciphertext 14 : 11 seconds
20:57:14 [harness] 7: Server: Encrypted ML Inference computation completed (elapsed: 174.8259s)
         [harness] Client: Encrypted results size: 988.6K
20:57:14 [harness] 8: Client: Result decryption completed (elapsed: 0.3275s)
20:57:14 [harness] 9: Client: Result postprocessing completed (elapsed: 0.1225s)
20:57:20 [harness] 10.1: Harness: Run inference for harness plaintext model. completed (elapsed: 6.2491s)
         [harness] Wrote harness model predictions to:  ...ml-inference/io/small/harness_model_predictions.txt
[harness] Encrypted Model Accuracy: 0.9333 (14/15 correct)
[harness] Harness Model Accuracy: 0.9333 (14/15 correct)
20:57:20 [harness] 10.2: Harness: Run encrypted inference. completed (elapsed: 0.1794s)
[total latency] 201.8726s

         [harness] Run 2 of 2
20:57:25 [harness] 4: Harness: Input generation for MNIST completed (elapsed: 4.5939s)
20:57:25 [harness] 5: Client: Input preprocessing completed (elapsed: 0.1698s)
20:57:26 [harness] 6: Client: Input encryption completed (elapsed: 0.5338s)
         [harness] Client: Encrypted input size: 5.2M
         [server] Loading keys
         [server] run encrypted MNIST inference
         [server] Execution time for ciphertext 0 : 13 seconds
         [server] Execution time for ciphertext 1 : 11 seconds
         [server] Execution time for ciphertext 2 : 9 seconds
         [server] Execution time for ciphertext 3 : 11 seconds
         [server] Execution time for ciphertext 4 : 11 seconds
         [server] Execution time for ciphertext 5 : 11 seconds
         [server] Execution time for ciphertext 6 : 11 seconds
         [server] Execution time for ciphertext 7 : 11 seconds
         [server] Execution time for ciphertext 8 : 11 seconds
         [server] Execution time for ciphertext 9 : 11 seconds
         [server] Execution time for ciphertext 10 : 10 seconds
         [server] Execution time for ciphertext 11 : 10 seconds
         [server] Execution time for ciphertext 12 : 11 seconds
         [server] Execution time for ciphertext 13 : 11 seconds
         [server] Execution time for ciphertext 14 : 10 seconds
21:00:15 [harness] 7: Server: Encrypted ML Inference computation completed (elapsed: 169.2421s)
         [harness] Client: Encrypted results size: 988.6K
21:00:16 [harness] 8: Client: Result decryption completed (elapsed: 0.785s)
21:00:16 [harness] 9: Client: Result postprocessing completed (elapsed: 0.1903s)
21:00:22 [harness] 10.1: Harness: Run inference for harness plaintext model. completed (elapsed: 6.0502s)
         [harness] Wrote harness model predictions to:  ...ml-inference/io/small/harness_model_predictions.txt
[harness] Encrypted Model Accuracy: 0.9333 (14/15 correct)
[harness] Harness Model Accuracy: 0.9333 (14/15 correct)
21:00:22 [harness] 10.2: Harness: Run encrypted inference. completed (elapsed: 0.0972s)
[total latency] 194.758s

All steps completed for the small inference!
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
| `client_decrypt_decode`          | Decryption and plaintext decoding of the result at the client.
| `client_postprocess`             | Any in the clear computation that the client wants to apply on the decrypted result.


The outer python script measures the runtime of each stage.
The current stage separation structure requires reading and writing to files more times than minimally necessary.
For a more granular runtime measuring, which would account for the extra overhead described above, we encourage
submitters to separate and print in a log the individual times for reads/writes and computations inside each stage. 
