# MNIST circuit built with HEIR
See details of compilation here: https://github.com/google/heir/issues/1232


clang++ -std=c++17 -o mlp_openfhe mlp_openfhe_main.cpp mlp_openfhe.cpp -I. -lOPENFHEcore -lOPENFHEpke -lOPENFHEbinfhe -I /usr/local/include/openfhe/core -I /usr/local/include/openfhe/pke -I /usr/local/include/openfhe/binfhe/ -I /usr/local/include/openfhe/

ulimit -s unlimited

./mlp_openfhe