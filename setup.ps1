$runs = Read-Host -Prompt "Please specify the number of times to run: "

echo "Building docker image"
docker build -t rp/modification .

for ( $s=0; $s -lt $runs; $s=$s + 1 ) {
    echo "========== Run $s =========="
    echo "Resetting data"
    $db_data_dir = "./.db-data"
    if (Test-Path $db_data_dir) {
        Remove-Item $db_data_dir -Recurse -Force
    }
    
    Expand-Archive -Path "./db/uk_companies.zip" -DestinationPath "."
    echo "Composing docker container"
    docker compose up --abort-on-container-exit # start the containers and wait until complete
    echo "Disposing docker container"
    docker compose down # burn everything
}