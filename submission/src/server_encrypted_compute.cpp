
#include "utils.h"
#include "params.h"
#include "mlp_openfhe.h"
#include "mlp_encryption_utils.h"
#include <chrono>

using namespace lbcrypto;


int main(int argc, char* argv[]){

    if (argc < 2 || !std::isdigit(argv[1][0])) {
        std::cout << "Usage: " << argv[0] << " instance-size \n";
        std::cout << "  Instance-size: 0-SINGLE, 1-SMALL, 2-MEDIUM, 3-LARGE\n";
        return 0;
    }
    auto size = static_cast<InstanceSize>(std::stoi(argv[1]));
    InstanceParams prms(size);

    CryptoContext<DCRTPoly> cc = read_crypto_context(prms);
    read_eval_keys(prms, cc);
    PublicKey<DCRTPoly> pk = read_public_key(prms);
    
    std::cout << "         [server] Loading keys" << std::endl;

    Ciphertext<DCRTPoly> ctxt;
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
