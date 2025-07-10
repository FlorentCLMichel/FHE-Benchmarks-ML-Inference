# MNIST circuit built with HEIR
See details of compilation here: https://github.com/google/heir/issues/1232


# Build mlp_openfhe_main
It is assumed that openfhe is installed. Run the following command from  submissions/MNIST_heir
```
clang++ -std=c++17 -o mlp_openfhe mlp_openfhe_main.cpp mlp_openfhe.cpp -I. -lOPENFHEcore -lOPENFHEpke -lOPENFHEbinfhe -I /usr/local/include/openfhe/core -I /usr/local/include/openfhe/pke -I /usr/local/include/openfhe/binfhe/ -I /usr/local/include/openfhe/
```

Set stack size to be unlimited as weights are part of the function argument
```
ulimit -s unlimited
```

Run the benchmark
```
./mlp_openfhe
```