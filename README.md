# Graph Database Watermarker(BEP)

# Install
To install the project you just need to install all the requirements:
```bash
pip install -r requirements.txt
```

# Run
To run this python script, you need to execute the following shell:
```bash
python ./src/main.py --interactive
```

# Cite
Use the intergrated Github system to easily create a citation for this project. If you have no idea what it is, please follow [this link](https://twitter.com/natfriedman/status/1420122675813441540).

# I simply want to see what this does

## 1. Run the setup script
```bash
chmod +x setup.sh
./setup.sh
```

# I want to install it myself

## 1. Start with a clean installation of Neo4j

### Install in docker
To install the neo4j docker image, simply follow the [following guide](https://neo4j.com/developer/docker-run-neo4j/) or run:
```bash
docker run -p7474:7474 -p7687:7687 -p7473:7473 -d --env NEO4J_AUTH=neo4j/test_password --env 'NEO4JLABS_PLUGINS=["apoc"]' --name Neo4j neo4j:latest
```

### Install normally 
Follow [this guide](https://neo4j.com/docs/operations-manual/current/installation/windows/)

## 2. Install the APOC Plugin
Install the APOC plugin using the [following guide](https://neo4j.com/developer/neo4j-apoc/#installing-apoc) 

## 3. Import the UK Companies dataset
After installing Neo4j and including the plugin, open the browser app using the following link [http://localhost:7474](http://localhost:7474) (assuming the DB instance runs on your local PC).
Then, connect to the database and run the contents of the [uk_companies.txt file](./db/uk_companies.txt)

## 4. Install this project
```bash
pip install -r requirements.txt
```
