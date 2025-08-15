
#include "utils.h"

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
    } else {
        batch_size = 10000; // Run on 10000 samples for LARGE instance
    }
    
    CryptoContext<DCRTPoly> cc = read_crypto_context(prms);
    read_eval_keys(prms, cc);
    PublicKey<DCRTPoly> pk = read_public_key(prms);

    PrivateKeyT secretKey = read_secret_key(prms);

    std::cout << "         [server] Loading keys" << std::endl;

    std::vector<Sample> dataset;
    std::string dataset_path = prms.datadir() / "dataset_pixels.txt";
    load_dataset(dataset, dataset_path.c_str());

    fs::create_directories(prms.iodir());
    std::ofstream out(prms.iodir() / "quality_result.txt");
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

        std::vector<float> output = mlp_decrypt(cc, output_encrypted, secretKey);

        auto result = argmax(output.data(), 1024);
        std::cout << "         [server]     Result: " << result << std::endl;
        out << result << '\n';
    }
    return 0;
}
