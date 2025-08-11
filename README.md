# FHE-Benchmarks-ML-Inference
Starter repository for benchmarking ML Inference workload.

To run the workload
Clone the repository
```console
git clone https://github.com/code-perspective/FHE-Benchmarks-ML-Inference.git
cd FHE-Benchmarks-ML-Inference
```
Install python requirements
```console
pip install -r requirements.txt
```

Run the workload
```console
python3 harness/run_submission.py -h # Provide information about command-line options
```

The first time you run `harness/run_submission.py`, it will attempt to pull and build OpenFHE if it is not already installed, and will then build the submission itself. 
On subsequent calls it will use the same project without re-building it unless the code has changed. An example run is provided below.


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


$ python3 ./harness/run_submission.py 0 --seed 3 --num_runs 2
[harness] Running submission for single inference
[get-openfhe] Found OpenFHE installed at /usr/local/lib/ (use --force to rebuild).
-- FOUND PACKAGE OpenFHE
-- OpenFHE Version: 1.2.4
-- OpenFHE installed as shared libraries: ON
-- OpenFHE include files location: /usr/local/include/openfhe
-- OpenFHE lib files location: /usr/local/lib
-- OpenFHE Native Backend size: 64
-- Configuring done (0.0s)
-- Generating done (0.0s)
-- Build files have been written to: /usr/local/google/home/gshruthi/projects/FHE-Benchmarks-ML-Inference/submission/build
[ 10%] Built target client_preprocess_dataset
[ 21%] Built target client_encode_encrypt_db
[ 31%] Built target client_preprocess_input
[ 42%] Built target client_postprocess
[ 52%] Built target server_preprocess_dataset
[ 63%] Built target client_encode_encrypt_input
[ 84%] Built target client_key_generation
[ 84%] Built target client_decrypt_decode
[100%] Built target server_encrypted_compute
23:55:00 [harness] 1: Dataset generation completed (elapsed: 12.0112s)
23:55:00 [harness] 2: Dataset preprocessing completed (elapsed: 0.0023s)
23:55:03 [harness] 3: Key Generation completed (elapsed: 3.0246s)
23:55:03 [harness] 4: Dataset encoding and encryption completed (elapsed: 0.0023s)
         [harness] Public and evaluation keys size: 1.4G
23:55:03 [harness] 5: (Encrypted) dataset preprocessing completed (elapsed: 0.0048s)

         [harness] Run 1 of 2
23:55:08 [harness] 6: Input generation completed (elapsed: 4.8747s)
23:55:08 [harness] 7: Input preprocessing completed (elapsed: 0.0023s)
23:55:08 [harness] 8: Input encryption completed (elapsed: 0.0343s)
         [harness] Encrypted input size: 354.8K
         [server] Loading keys
         [server] run encrypted MNIST inference
         [server] Execution time: 17 seconds
23:55:28 [harness] 9: Encrypted computation completed (elapsed: 19.8515s)
         [harness] Encrypted results size: 65.6K
23:55:28 [harness] 10: Result decryption completed (elapsed: 0.0373s)
23:55:28 [harness] 11: Result postprocessing completed (elapsed: 0.0019s)
         [harness] Wrote expected result to:  /usr/local/google/home/gshruthi/projects/FHE-Benchmarks-ML-Inference/datasets/single/intermediate/expected.txt
[harness] PASS  (expected=4, got=4)
[total latency] 39.8471s

         [harness] Run 2 of 2
23:55:33 [harness] 6: Input generation completed (elapsed: 4.9837s)
23:55:33 [harness] 7: Input preprocessing completed (elapsed: 0.0025s)
23:55:33 [harness] 8: Input encryption completed (elapsed: 0.0341s)
         [harness] Encrypted input size: 354.8K
         [server] Loading keys
         [server] run encrypted MNIST inference
         [server] Execution time: 17 seconds
23:55:53 [harness] 9: Encrypted computation completed (elapsed: 20.3411s)
         [harness] Encrypted results size: 65.6K
23:55:53 [harness] 10: Result decryption completed (elapsed: 0.0374s)
23:55:53 [harness] 11: Result postprocessing completed (elapsed: 0.0023s)
         [harness] Wrote expected result to:  /usr/local/google/home/gshruthi/projects/FHE-Benchmarks-ML-Inference/datasets/single/intermediate/expected.txt
[harness] PASS  (expected=5, got=5)
[total latency] 40.4463s

All steps completed for the single dataset!
```


Sample benchmark measurements
```
{
  "total_latency_ms": 39.8471,
  "per_stage": {
    "Dataset generation": "12.0112s",
    "Dataset preprocessing": "0.0023s",
    "Key Generation": "3.0246s",
    "Dataset encoding and encryption": "0.0023s",
    "(Encrypted) dataset preprocessing": "0.0048s",
    "Input generation": "4.8747s",
    "Input preprocessing": "0.0023s",
    "Input encryption": "0.0343s",
    "Encrypted computation": "19.8515s",
    "Result decryption": "0.0373s",
    "Result postprocessing": "0.0019s"
  },
  "bandwidth": {
    "Public and evaluation keys": "1.4G",
    "Encrypted input": "354.8K",
    "Encrypted results": "65.6K"
  }
}
```
