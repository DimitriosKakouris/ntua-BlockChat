# ntua-blockchain 2023-24

<!-- <p align="center">
  <img src="./images/logo.png" max-width="50%" />
</p> -->

#### BlockChat


#### Run in VMs:

1. Change your BOOTSTRAP_IP and BOOTSTRAP_PORT in the [.env file](https://github.com/tomkosm/ntua-blockchain/blob/main/src/.env), and the prefix of the private IPs of the nodes in the network in this [line](https://github.com/tomkosm/ntua-blockchain/blob/main/src/wserve.py#L23).

2. For each node, open a terminal, and change to the home directory.

3. To run the client, from each terminal run:

```
bash entrypoint.sh TOTAL_NODES BLOCK_CAPACITY
```

Substitute TOTAL_NODES with the number of the clients in which you want to run the application, and BLOCK_CAPACITY with the capacity of the blocks.

2. To run the tests (files available for either 5 or 10 clients), run:

```
bash test_entrypoint.sh TOTAL_NODES BLOCK_CAPACITY [COMPUTE_JUSTICE]
```

The 'COMPUTE_JUSTICE' parameter is boolean. When set to 'False', each node in the tests starts with staking of 10 BCCs. When set to 'True', the bootstrap node will stake 100 BCCs, and all the others 10 BCCs. Defining this parameter is optional and it defaults to 'False'.


##### To run the code in Docker containers, use the docker branch.
