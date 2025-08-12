
#include "openfhe.h" 
// header files needed for de/serialization
#include "ciphertext-ser.h"
#include "cryptocontext-ser.h"
#include "key/key-ser.h"
#include "scheme/ckksrns/ckksrns-ser.h"
#include "params.h"
#include <chrono>

#include "mlp_openfhe.h"

using namespace lbcrypto;


int main(int argc, char* argv[]){

    if (argc < 2 || !std::isdigit(argv[1][0])) {
        std::cout << "Usage: " << argv[0] << " instance-size \n";
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
    PublicKey<DCRTPoly> pk;
    if (!Serial::DeserializeFromFile(prms.pubkeydir()/"pk.bin", pk,
                                    SerType::BINARY)) {
        throw std::runtime_error("Failed to get public key from  " + prms.pubkeydir().string());
    }

    std::ifstream emult_file(prms.pubkeydir()/"mk.bin", std::ios::in | std::ios::binary);
    if (!emult_file.is_open() ||
        !cc->DeserializeEvalMultKey(emult_file, SerType::BINARY)) {
      throw std::runtime_error(
        "Failed to get re-linearization key from " +prms.pubkeydir().string());
    }

    std::ifstream erot_file(prms.pubkeydir()/"rk.bin", std::ios::in | std::ios::binary);
    if (!erot_file.is_open() ||
        !cc->DeserializeEvalAutomorphismKey(erot_file, SerType::BINARY)) {
      throw std::runtime_error(
        "Failed to get rotation keys from " + prms.pubkeydir().string());
    }
    std::cout << "         [server] Loading keys" << std::endl;

    CiphertextT ctxt;
    if (!Serial::DeserializeFromFile(prms.ctxtupdir()/"cipher_input.bin", ctxt, SerType::BINARY)) {
        throw std::runtime_error("Failed to get ciphertexts from " + prms.ctxtupdir().string());
    }

    std::cout << "         [server] run encrypted MNIST inference" << std::endl;
    auto start = std::chrono::high_resolution_clock::now();
    auto ctxtResult = mlp(cc, ctxt);
    auto end = std::chrono::high_resolution_clock::now();
    auto duration = std::chrono::duration_cast<std::chrono::seconds>(end - start);
    std::cout << "         [server] Execution time: " << duration.count() << " seconds" << std::endl;

    
    fs::create_directories(prms.ctxtdowndir());
    Serial::SerializeToFile(prms.ctxtdowndir()/"cipher_result.bin", ctxtResult, SerType::BINARY);

    return 0;
}
