#!/bin/bash
SERVICES=("node1" "node2" "node3" "node4" "node5") # Names of the services in docker-compose.yml
current_dir=$PWD
SCRIPT_PATH="$current_dir/execute_tests.py"

for SERVICE in "${SERVICES[@]}"
do
    docker-compose exec -T $SERVICE python $SCRIPT_PATH &
done

wait
echo "Scripts started on all nodes."
