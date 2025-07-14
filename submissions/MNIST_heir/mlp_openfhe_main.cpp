#include <cerrno>
#include <fstream>
#include <iostream>
#include <vector>
#include <chrono>

#include "mlp_openfhe.h"

#define DIM 1024

struct Sample {
  int label;
  float image[DIM];
};

using Dataset = std::vector<Sample>;

void load_dataset(Dataset &dataset, const char *filename) {
  std::ifstream file(filename);
  Sample sample;
  while (file >> sample.label) {
    for (int i = 0; i < DIM; i++) {
      file >> sample.image[i];
    }
    dataset.push_back(sample);
  }
  std::cout << "Found " << dataset.size() << " samples" << std::endl;
}

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

int main(int argc, char *argv[]) {
  auto dataset = Dataset();
  std::cout << "Loading dataset" << std::endl;
  load_dataset(dataset, "mnist_test.txt");
  std::cout << "Done loading dataset" << std::endl;

  int accurate = 0;
  int batch_size = 1;  // Default value
  
  // Read total from command line argument if provided
  if (argc > 1) {
    batch_size = std::atoi(argv[1]);
    if (batch_size <= 0) {
      std::cerr << "Error: batch size must be a positive integer" << std::endl;
      return 1;
    }
  } else {
    std::cout << "Batch size not provided, defaulting to 1" << std::endl;
  }
  
  std::cout << "Processing " << batch_size << " samples" << std::endl;

  auto cryptoContext = mlp__generate_crypto_context();
  auto keyPair = cryptoContext->KeyGen();
  auto publicKey = keyPair.publicKey;
  auto secretKey = keyPair.secretKey;
  cryptoContext = mlp__configure_crypto_context(cryptoContext, secretKey);

  std::cout << *cryptoContext->GetCryptoParameters() << std::endl;

  for (int i = 0; i < batch_size; ++i) {
    auto *input = dataset[i].image;
    std::cout << "Done extracting first image" << std::endl;

    std::vector<float> input_vector(input, input + DIM);

    auto input_encrypted =
        mlp__encrypt__arg0(cryptoContext, input_vector, publicKey);
    std::cout << "Encryption done" << std::endl;


    std::cout << "Run MNIST inference" << std::endl;
    auto start = std::chrono::high_resolution_clock::now();
    auto output_encrypted = mlp(cryptoContext, input_encrypted);
    auto end = std::chrono::high_resolution_clock::now();
    auto duration = std::chrono::duration_cast<std::chrono::seconds>(end - start);
    std::cout << "Execution time: " << duration.count() << " seconds" << std::endl;
    
    std::vector<float> output =
        mlp__decrypt__result0(cryptoContext, output_encrypted, secretKey);
    std::cout << "Decryption done" << std::endl;

    auto max_id = argmax<1024>(output.data());
    auto label = dataset[i].label;

    std::cout << "max_id: " << max_id << ", label: " << label << std::endl;

    if (max_id == label) {
      accurate++;
    }
  }

  if (batch_size > 1 ) {
    std::cout << "accuracy: " << accurate << "/" << batch_size << std::endl;
  } else {
    std::cout << "Omitting accuracy for batch size less than 1" << std::endl;
  }
  return 0;
}
