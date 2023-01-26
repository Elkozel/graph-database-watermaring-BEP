#!/bin/bash
echo "Please specify the number of times to run: "
read runs

echo "Building docker image"
sudo docker build -t rp/modification .

for (( s=0; s<$runs; s++ ))
do
    echo "========== Run $s =========="
    echo "Resetting data"
    sudo rm -rf ./.db-data
    sudo tar -xzvf ./db/uk_companies.tar.gz -C . >> /dev/null
    echo "Composing docker container"
    sudo docker compose up # start the containers and wait until complete
    echo "Disposing docker container"
done