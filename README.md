# ntua-blockchain 2023-24

<!-- <p align="center">
  <img src="./images/logo.png" max-width="50%" />
</p> -->

#### BlockChat

# To-Do List
- [ ] Run the code and debug
- [X] Websockets/endpoints
- [X] app.py/main.py file
- [X] client/blockchat.py file

Implement the following functions:
- [x] generate_wallet()
- [x] create_transaction()
- [x] broadcast_transaction()
- [x] broadcast_block()
- [x] validate_chain()
- [x] stake(amount)


#### Build and Run Your Docker Containers:

1. From home directory (where docker-compose.yml and Dockerfile reside) run:

```  docker build -t ntua-blockchain . ```

2. Create the containers, this will create a network for them with subnet 172.18.0.0/16:

``` docker compose up ```

3. To enter a node (client) and enter the network, for example first node:

``` docker-compose exec node1 bash entrypoint.sh ```

4. To close the service and down the containers:

``` docker compose down ```
