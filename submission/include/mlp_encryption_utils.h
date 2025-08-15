#ifndef MLP_ENCRYPTION_UTILS_H_
#define MLP_ENCRYPTION_UTILS_H_

#include "openfhe.h"
#include "params.h"

using namespace lbcrypto;
using CiphertextT = ConstCiphertext<DCRTPoly>;
using CCParamsT = CCParams<CryptoContextCKKSRNS>;
using CryptoContextT = CryptoContext<DCRTPoly>;
using EvalKeyT = EvalKey<DCRTPoly>;
using PlaintextT = Plaintext;
using PrivateKeyT = PrivateKey<DCRTPoly>;
using PublicKeyT = PublicKey<DCRTPoly>;

#define MNIST_DIM 784
#define NORMALIZED_DIM 1024

struct Sample {
  float image[NORMALIZED_DIM];
};

ConstCiphertext<DCRTPoly> encrypt_input(CryptoContext<DCRTPoly> cc, std::vector<float> input, PublicKey<DCRTPoly> pk);
std::vector<float> mlp_decrypt(CryptoContextT v11343, CiphertextT v11344, PrivateKeyT v11345);
PublicKey<DCRTPoly> read_public_key(const InstanceParams& prms);
PrivateKey<DCRTPoly> read_secret_key(const InstanceParams& prms);
CryptoContext<DCRTPoly> read_crypto_context(const InstanceParams& prms);
void read_eval_keys(const InstanceParams& prms, CryptoContextT cc);
void load_dataset(std::vector<Sample> &dataset, const char *filename);
int argmax(float *A, int N);

#endif  // ifndef MLP_ENCRYPTION_UTILS_H_