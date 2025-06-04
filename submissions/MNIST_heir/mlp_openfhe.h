
#include "openfhe/pke/openfhe.h"  // use this for clang
// #include "openfhe.h"  // use this for bazel from @openfhe

using namespace lbcrypto;
using CiphertextT = ConstCiphertext<DCRTPoly>;
using CCParamsT = CCParams<CryptoContextCKKSRNS>;
using CryptoContextT = CryptoContext<DCRTPoly>;
using EvalKeyT = EvalKey<DCRTPoly>;
using PlaintextT = Plaintext;
using PrivateKeyT = PrivateKey<DCRTPoly>;
using PublicKeyT = PublicKey<DCRTPoly>;

CiphertextT mlp(CryptoContextT v0, CiphertextT v1);
CiphertextT mlp__encrypt__arg0(CryptoContextT v11337, std::vector<float> v11338, PublicKeyT v11339);
std::vector<float> mlp__decrypt__result0(CryptoContextT v11343, CiphertextT v11344, PrivateKeyT v11345);
CryptoContextT mlp__generate_crypto_context();
CryptoContextT mlp__configure_crypto_context(CryptoContextT v11350, PrivateKeyT v11351);
