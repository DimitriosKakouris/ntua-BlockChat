# ntua-blockchain 2023-24

<!-- <p align="center">
  <img src="./images/logo.png" max-width="50%" />
</p> -->

#### BlockChat

#### Build and Run Your Docker Containers:

1. In the [docker-compose.yml](https://github.com/tomkosm/ntua-blockchain/blob/docker/docker-compose.yml) file, comment out the nodes you don't need according to the number of clients you want to test.

2. From home directory (where docker-compose.yml and Dockerfile reside) run:

```
docker build -t ntua-blockchain .
```

2. Create the containers, this will create a network for them with subnet 172.18.0.0/16:

```
docker compose up
```

3. To enter a node (client) and enter the network, for example first node:

```
docker-compose exec node0 bash entrypoint.sh TOTAL_NODES BLOCK_CAPACITY
```
Substitute TOTAL_NODES with the number of the clients in which you want to run the application, and BLOCK_CAPACITY with the capacity of the blocks.

4. To run the tests (files available for either 5 or 10 clients), run:
```
docker-compose exec nodeX bash test_entrypoint.sh TOTAL_NODES BLOCK_CAPACITY [COMPUTE_JUSTICE]
```
The 'COMPUTE_JUSTICE' parameter is boolean. When set to 'False', each node in the tests starts with staking of 10 BCCs. When set to 'True', the bootstrap node will stake 100 BCCs, and all the others 10 BCCs. Defining this parameter is optional and it defaults to 'False'.

5. To close the service and down the containers:

``` 
docker compose down
```
