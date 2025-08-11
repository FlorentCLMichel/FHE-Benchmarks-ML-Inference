
#include "openfhe/pke/openfhe.h" 
// header files needed for de/serialization
#include "ciphertext-ser.h"
#include "cryptocontext-ser.h"
#include "key/key-ser.h"
#include "scheme/ckksrns/ckksrns-ser.h"
#include "params.h"
#include <chrono>

#include "mlp_openfhe.h"
#include "mlp_encryption_utils.h"

using namespace lbcrypto;


int main(int argc, char* argv[]){

    if (argc < 2 || !std::isdigit(argv[1][0])) {
        std::cout << "Usage: " << argv[0] << " instance-size \n";
        std::cout << "  Instance-size: 0-SINGLE, 1-SMALL, 2-MEDIUM, 3-LARGE\n";
        return 0;
    }
    auto size = static_cast<InstanceSize>(std::stoi(argv[1]));
    InstanceParams prms(size);

    int batch_size = 10;
    if (size == 0) {
        batch_size = 10; // Run on 10 samples for SINGLE instance
    } else if (size == 1) {
        batch_size = 100; // Run on 100 samples for SMALL instance
    } else if (size == 2) {
        batch_size = 1000; // Run on 1000 samples for MEDIUM instance
    } else if (size == 3) {
        batch_size = 10000; // Run on 10000 samples for LARGE instance
    }
    
    CryptoContextT cc;

    if (!Serial::DeserializeFromFile(prms.pubkeydir()/"cc.bin", cc,
                                    SerType::BINARY)) {
        throw std::runtime_error("Failed to get CryptoContext from  " + prms.pubkeydir().string());
    }
    PublicKeyT pk;
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

    PrivateKeyT secretKey;
    if (!Serial::DeserializeFromFile(prms.seckeydir()/"sk.bin", secretKey,
                                    SerType::BINARY)) {
        throw std::runtime_error("Failed to get secret key from " + prms.seckeydir().string());
    }

    std::cout << "         [server] Loading keys" << std::endl;

    std::vector<Sample> dataset;
    std::string dataset_path = prms.datadir() / "dataset.txt";
    load_dataset(dataset, dataset_path.c_str());

    int accurate = 0;

    for (int i = 0; i < batch_size; ++i) {
        auto *input = dataset[i].image;
        std::cout << "         [server] Processing input: " << i+1 << "/" << batch_size << std::endl;

        std::vector<float> input_vector(input, input + NORMALIZED_DIM);

        auto input_encrypted =
            encrypt_input(cc, input_vector, pk);
        auto start = std::chrono::high_resolution_clock::now();
        auto output_encrypted = mlp(cc, input_encrypted);
        auto end = std::chrono::high_resolution_clock::now();
        auto duration = std::chrono::duration_cast<std::chrono::seconds>(end - start);
        std::cout << "         [server]     Encrypted inference time: " << duration.count() << " seconds" << std::endl;

        std::vector<float> output =
            mlp_decrypt(cc, output_encrypted, secretKey);

        auto result = argmax(output.data(), 1024);
        auto expected = dataset[i].label;

        std::cout << "         [server]     Result: " << result << ", Expected: " << expected << std::endl;

        if (result == expected) {
            accurate++;
        }
    }

    
    fs::create_directories(prms.iodir());
    std::ofstream out(prms.iodir() / "quality.txt");
    out << "batch_size: " << batch_size << '\n';
    out << "accuracy: " << static_cast<float>(accurate) / batch_size << '\n';


    return 0;
}
