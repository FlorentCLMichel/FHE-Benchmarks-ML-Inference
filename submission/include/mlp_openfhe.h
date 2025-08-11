
#ifndef MLP_OPENFHE_H_
#define MLP_OPENFHE_H_

#include "openfhe/pke/openfhe.h"

using namespace lbcrypto;
using CiphertextT = ConstCiphertext<DCRTPoly>;
using CCParamsT = CCParams<CryptoContextCKKSRNS>;
using CryptoContextT = CryptoContext<DCRTPoly>;
using EvalKeyT = EvalKey<DCRTPoly>;
using PlaintextT = Plaintext;
using PrivateKeyT = PrivateKey<DCRTPoly>;
using PublicKeyT = PublicKey<DCRTPoly>;


CiphertextT mlp(CryptoContextT v0, CiphertextT v1);

#endif  // ifndef MLP_OPENFHE_H_