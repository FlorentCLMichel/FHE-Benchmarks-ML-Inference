
#include "utils.h"
#include "mlp_encryption_utils.h"

using namespace lbcrypto;


int main(int argc, char* argv[]){

    if (argc < 2 || !std::isdigit(argv[1][0])) {
        std::cout << "Usage: " << argv[0] << " instance-size [--count_only]\n";
        std::cout << "  Instance-size: 0-SINGLE, 1-SMALL, 2-MEDIUM, 3-LARGE\n";
        return 0;
    }
    auto size = static_cast<InstanceSize>(std::stoi(argv[1]));
    InstanceParams prms(size);

    CryptoContext<DCRTPoly> cc = read_crypto_context(prms);

    // Step 2: Read public key
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
