# ntua-blockchain 2023-24

<p align="center">
  <img src="./images/logo.png" max-width="50%" />
</p>

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

```  docker build -t ntua-distributed-systems . ```

2. Run each docker container with this command:
``docker run -e PORT=8000 -e IP=127.0.0.1 -p 8000:8000 --rm ntua-distributed-systems``
3. Check status of docker containers:

``` docker-compose ps ``` 

#### Shut down the containers:

``` docker-compose down ```
