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
python -m venv bmenv
source ./bmenv/bin/activate
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
[get-openfhe] Found OpenFHE installed at /usr/local/lib/ (use --force to rebuild).
-- FOUND PACKAGE OpenFHE
-- OpenFHE Version: 1.3.1
-- OpenFHE installed as shared libraries: ON
-- OpenFHE include files location: /usr/local/include/openfhe
-- OpenFHE lib files location: /usr/local/lib
-- OpenFHE Native Backend size: 64
-- Configuring done (0.0s)
-- Generating done (0.0s)
-- Build files have been written to: /usr/local/google/home/gshruthi/projects/FHE-Benchmarks-ML-Inference/submission/build
[ 40%] Built target server_preprocess_model
[ 40%] Built target client_postprocess
[ 40%] Built target client_preprocess_input
[ 66%] Built target client_decrypt_decode
[ 66%] Built target client_encode_encrypt_input
[ 80%] Built target client_key_generation
[100%] Built target server_encrypted_compute
00:44:42 [harness] 1: Test dataset generation completed (elapsed: 11.9646s)
00:44:42 [harness] 2: Test dataset preprocessing completed (elapsed: 0.0029s)
00:44:45 [harness] 3: Key Generation completed (elapsed: 3.0766s)
         [harness] Public and evaluation keys size: 1.4G
00:44:45 [harness] 4: (Encrypted) model preprocessing completed (elapsed: 0.0049s)

         [harness] Run 1 of 2
00:44:50 [harness] 5: Input generation completed (elapsed: 5.0768s)
00:44:50 [harness] 6: Input preprocessing completed (elapsed: 0.0021s)
00:44:50 [harness] 7: Input encryption completed (elapsed: 0.0339s)
         [harness] Encrypted input size: 354.8K
         [server] Loading keys
         [server] run encrypted MNIST inference
         [server] Execution time: 18 seconds
00:45:11 [harness] 8: Encrypted ML Inference computation completed (elapsed: 20.9319s)
         [harness] Encrypted results size: 65.6K
00:45:11 [harness] 9: Result decryption completed (elapsed: 0.0391s)
00:45:11 [harness] 10: Result postprocessing completed (elapsed: 0.002s)
         [harness] Wrote expected result to:  /usr/local/google/home/gshruthi/projects/FHE-Benchmarks-ML-Inference/datasets/single/intermediate/expected.txt
[harness] PASS  (expected=2, got=2)
[total latency] 41.1349s

         [harness] Run 2 of 2
00:45:16 [harness] 5: Input generation completed (elapsed: 5.2668s)
00:45:16 [harness] 6: Input preprocessing completed (elapsed: 0.0023s)
00:45:16 [harness] 7: Input encryption completed (elapsed: 0.0359s)
         [harness] Encrypted input size: 354.8K
         [server] Loading keys
         [server] run encrypted MNIST inference
         [server] Execution time: 18 seconds
00:45:37 [harness] 8: Encrypted ML Inference computation completed (elapsed: 21.2919s)
         [harness] Encrypted results size: 65.6K
00:45:37 [harness] 9: Result decryption completed (elapsed: 0.038s)
00:45:37 [harness] 10: Result postprocessing completed (elapsed: 0.002s)
         [harness] Wrote expected result to:  /usr/local/google/home/gshruthi/projects/FHE-Benchmarks-ML-Inference/datasets/single/intermediate/expected.txt
[harness] PASS  (expected=2, got=2)
[total latency] 41.6859s

All steps completed for the single inference!
```


Sample benchmark measurements
```
{
  "total_latency_ms": 41.1349,
  "per_stage": {
    "Test dataset generation": "11.9646s",
    "Test dataset preprocessing": "0.0029s",
    "Key Generation": "3.0766s",
    "(Encrypted) model preprocessing": "0.0049s",
    "Input generation": "5.0768s",
    "Input preprocessing": "0.0021s",
    "Input encryption": "0.0339s",
    "Encrypted ML Inference computation": "20.9319s",
    "Result decryption": "0.0391s",
    "Result postprocessing": "0.002s"
  },
  "bandwidth": {
    "Public and evaluation keys": "1.4G",
    "Encrypted input": "354.8K",
    "Encrypted results": "65.6K"
  }
}
```
