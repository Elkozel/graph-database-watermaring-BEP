#!/bin/bash
echo "Please specify the number of times to run: "
read runs

for (( s=0; s<$runs; s++ ))
do
    echo "Run $s"
    echo "Resetting data"
    sudo rm -rf ./.db-data
    sudo tar -xzvf ./db/uk_companies.tar.gz -C .
    echo "Composing docker container"
    sudo docker compose up --abort-on-container-exit # start the containers and wait until complete
    echo "Disposing docker container"
    sudo docker compose down # burn everything
done