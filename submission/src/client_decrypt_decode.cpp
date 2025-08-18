#include "utils.h"
#include "iomanip"
#include "limits"

#include "mlp_encryption_utils.h"

using namespace lbcrypto;


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

    std::vector<float> output;
    for (size_t i = 0; i < prms.getBatchSize(); ++i) {
        output = mlp_decrypt(cc, ctxt, sk);

        auto max_id = argmax(output.data(), 1024);
        auto result_path = prms.iodir()/("result_" + std::to_string(i) + ".txt");
        std::ofstream out(result_path);
        out << max_id << '\n';
    }

    return 0;
}