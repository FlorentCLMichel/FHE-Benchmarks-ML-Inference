
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
    fs::create_directories(prms.ctxtdowndir());
    std::cout << "         [server] Run encrypted MNIST inference" << std::endl;
    for (size_t i = 0; i < prms.getBatchSize(); ++i) {
        auto input_ctxt_path = prms.ctxtupdir()/("cipher_input_" + std::to_string(i) + ".bin");
        if (!Serial::DeserializeFromFile(input_ctxt_path, ctxt, SerType::BINARY)) {
            throw std::runtime_error("Failed to get ciphertexts from " + input_ctxt_path.string());
        }
        auto start = std::chrono::high_resolution_clock::now();
        auto ctxtResult = mlp(cc, ctxt);
        auto end = std::chrono::high_resolution_clock::now();
        auto duration = std::chrono::duration_cast<std::chrono::seconds>(end - start);
        std::cout << "         [server] Execution time for ciphertext " << i << " : " 
                << duration.count() << " seconds" << std::endl;
        auto result_ctxt_path = prms.ctxtdowndir()/("cipher_result_" + std::to_string(i) + ".bin");
        Serial::SerializeToFile(result_ctxt_path, ctxtResult, SerType::BINARY);
    }

    return 0;
}
