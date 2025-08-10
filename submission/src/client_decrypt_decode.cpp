#include "openfhe.h"
// header files needed for de/serialization
#include "ciphertext-ser.h"
#include "cryptocontext-ser.h"
#include "key/key-ser.h"
#include "scheme/ckksrns/ckksrns-ser.h"
#include "params.h"
#include "iomanip"
#include "limits"

using namespace lbcrypto;
using CiphertextT = ConstCiphertext<DCRTPoly>;
using CCParamsT = CCParams<CryptoContextCKKSRNS>;
using CryptoContextT = CryptoContext<DCRTPoly>;
using EvalKeyT = EvalKey<DCRTPoly>;
using PlaintextT = Plaintext;
using PrivateKeyT = PrivateKey<DCRTPoly>;
using PublicKeyT = PublicKey<DCRTPoly>;

std::vector<float> mlp_decrypt(CryptoContextT v11343, CiphertextT v11344, PrivateKeyT v11345);
template <int N>
int argmax(float *A) {
  int max_idx = 0;
  for (int i = 1; i < N; i++) {
    if (A[i] > A[max_idx]) {
      max_idx = i;
    }
  }
  return max_idx;
}

int main(int argc, char* argv[]) {
    if (argc < 2 || !std::isdigit(argv[1][0])) {
        std::cout << "Usage: " << argv[0] << " instance-size [--count_only]\n";
        std::cout << "  Instance-size: 0-SINGLE, 1-SMALL, 2-MEDIUM, 3-LARGE\n";
        return 0;
    }
    auto size = static_cast<InstanceSize>(std::stoi(argv[1]));
    InstanceParams prms(size);

    CryptoContext<DCRTPoly> cc;
    if (!Serial::DeserializeFromFile(prms.pubkeydir()/"cc.bin", cc,
                                    SerType::BINARY)) {
        throw std::runtime_error("Failed to get CryptoContext from  " + prms.pubkeydir().string());
    }
    PrivateKey<DCRTPoly> sk;
    if (!Serial::DeserializeFromFile(prms.seckeydir()/"sk.bin", sk,
                                    SerType::BINARY)) {
        throw std::runtime_error("Failed to get secret key from  " + prms.seckeydir().string());
    }
    Ciphertext<DCRTPoly> ctxt;     
    if (!Serial::DeserializeFromFile(prms.ctxtdowndir()/"cipher_result.bin", ctxt, SerType::BINARY)) {
      throw std::runtime_error("Failed to get ciphertext from " + prms.ctxtdowndir().string());
    }

    std::vector<float> output = mlp_decrypt(cc, ctxt, sk);

    auto max_id = argmax<1024>(output.data());
    std::ofstream out(prms.iodir() / "result.txt");
    out << max_id << '\n';

    return 0;
}

std::vector<float> mlp_decrypt(CryptoContextT v11343, CiphertextT v11344, PrivateKeyT v11345) {
  PlaintextT v11346;
  v11343->Decrypt(v11345, v11344, &v11346);
  v11346->SetLength(1024);
  const auto& v11347_cast = v11346->GetCKKSPackedValue();
  std::vector<float> v11347(v11347_cast.size());
  std::transform(std::begin(v11347_cast), std::end(v11347_cast), std::begin(v11347), [](const std::complex<double>& c) { return c.real(); });
  return v11347;
}