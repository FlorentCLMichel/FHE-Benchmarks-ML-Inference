
#include "openfhe.h"
// header files needed for de/serialization
#include "ciphertext-ser.h"
#include "cryptocontext-ser.h"
#include "key/key-ser.h"
#include "scheme/ckksrns/ckksrns-ser.h"
#include "params.h"

using namespace lbcrypto;
#define MNIST_DIM 784
#define NORMALIZED_DIM 1024

struct Sample {
  int label;
  float image[NORMALIZED_DIM];
};

ConstCiphertext<DCRTPoly> encrypt_input(CryptoContext<DCRTPoly> cc, std::vector<float> input, PublicKey<DCRTPoly> pk);
PublicKey<DCRTPoly> read_public_key(const InstanceParams& prms);
CryptoContext<DCRTPoly> read_crypto_context(const InstanceParams& prms);
void load_dataset(std::vector<Sample> &dataset, const char *filename);




int main(int argc, char* argv[]){

    if (argc < 2 || !std::isdigit(argv[1][0])) {
        std::cout << "Usage: " << argv[0] << " instance-size [--count_only]\n";
        std::cout << "  Instance-size: 0-SINGLE, 1-SMALL, 2-MEDIUM, 3-LARGE\n";
        return 0;
    }
    auto size = static_cast<InstanceSize>(std::stoi(argv[1]));
    InstanceParams prms(size);

    CryptoContext<DCRTPoly> cc = read_crypto_context(prms);
    PublicKey<DCRTPoly> pk = read_public_key(prms);

    std::vector<Sample> dataset;
    std::string q_path = prms.dataintermdir()/"plain_input.bin";
    load_dataset(dataset, q_path.c_str());
    if (dataset.empty()) {
        throw std::runtime_error("No data found in " + q_path);
    }
    auto *input = dataset[0].image;
    std::vector<float> input_vector(input, input + NORMALIZED_DIM);

    auto ctxt = encrypt_input(cc, input_vector, pk);
    fs::create_directories(prms.ctxtupdir());
    Serial::SerializeToFile(prms.ctxtupdir()/"cipher_input.bin", ctxt, SerType::BINARY);

    return 0;
}

PublicKey<DCRTPoly> read_public_key(const InstanceParams& prms) {
    PublicKey<DCRTPoly> pk;
    if (!Serial::DeserializeFromFile(prms.pubkeydir()/"pk.bin", pk,
                                    SerType::BINARY)) {
        throw std::runtime_error("Failed to get public key from  " + prms.pubkeydir().string());
    }
    return pk;
}

CryptoContext<DCRTPoly> read_crypto_context(const InstanceParams& prms) {
    CryptoContext<DCRTPoly> cc;
    if (!Serial::DeserializeFromFile(prms.pubkeydir()/"cc.bin", cc, SerType::BINARY)) {
        throw std::runtime_error("Failed to get CryptoContext from " + prms.pubkeydir().string());
    }
    return cc;
}


ConstCiphertext<DCRTPoly> encrypt_input(CryptoContext<DCRTPoly> cc, std::vector<float> input, PublicKey<DCRTPoly> pk) {
  std::vector<double> v11340(std::begin(input), std::end(input));
  uint32_t v11340_filled_n = cc->GetCryptoParameters()->GetElementParams()->GetRingDimension() / 2;
  auto v11340_filled = v11340;
  v11340_filled.clear();
  v11340_filled.reserve(v11340_filled_n);
  for (uint32_t i = 0; i < v11340_filled_n; ++i) {
    v11340_filled.push_back(v11340[i % v11340.size()]);
  }
  const auto& v11341 = cc->MakeCKKSPackedPlaintext(v11340_filled);
  const auto& v11342 = cc->Encrypt(pk, v11341);
  return v11342;
}


void load_dataset(std::vector<Sample> &dataset, const char *filename) {
  std::ifstream file(filename);
  Sample sample;
  while (file >> sample.label) {
    // Read MNIST_DIM values from file
    for (int i = 0; i < MNIST_DIM; i++) {
      file >> sample.image[i];
    }
    // Pad remaining values with 0.0 if NORMALIZED_DIM > MNIST_DIM
    for (int i = MNIST_DIM; i < NORMALIZED_DIM; i++) {
      sample.image[i] = 0.0f;
    }

    dataset.push_back(sample);
  }
}
