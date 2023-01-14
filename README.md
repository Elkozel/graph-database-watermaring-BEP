

# Install
To install the project you just need to install all the requirements:
```shell
pip install -r requirements.txt
```

# Run


# I simply want to see what this does

## 1. Install Neo4j

### Install in docker
To install the neo4j docker image, simply follow the [following guide](https://neo4j.com/developer/docker-run-neo4j/) or run:
```shell
docker run -p7474:7474 -p7687:7687 -p7473:7473 -d --env NEO4J_AUTH=neo4j/test_password --name Neo4j neo4j:latest
```

### Install normally 
Follow [this guide](https://neo4j.com/docs/operations-manual/current/installation/windows/)

## 2. Install this project
```shell
pip install -r requirements.txt
```

## 3. Modify the .env file (if needed)
Usually, after installing the database, you should configure the credentials for access, however for the docker container they are already prefilled

## 4. Run the python script
```shell
python .\src\main.py
```
then, choose option `Populate database` to insert fake data inside the database and then `Watermark database` to actually insert the watermark.