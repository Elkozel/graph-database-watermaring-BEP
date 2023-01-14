from typing import List
import names
from random import randrange, choices, choice

def add_document(link, First_name: str, Last_name:str, Age: float, connections: List[int], randomized_directions: bool = False):
    """
    Add a document to the database

    :param link the database session
    :param document the document, which should be added
    :param connections the connections which the document should have
    """

    # Create the node
    source_id = create_node(link, First_name, Last_name, Age, True)
    # Create all the edges from the newly created node to the connection nodes
    for connection in connections:
        if randomized_directions:
            result = create_relation(link, source_id, connection, True, reversed = choice([True, False]))
        else:
            result = create_relation(link, source_id, connection, True)
            
    
def create_node(link, First_name: str, Last_name: str, Age: float, pseudo: bool = False, node_type: str = "Person",):
    """
    Creates a node inside the database and returns its ID

    :param link the database session
    :param str first_name the first name of the new person
    :param str last_name the last name of the new person
    :param float Age the age of the person
    :param str node_type the type of the newly created node
    :param bool pseudo determines if the document is a pseudo document or not
    """
    # Check if the node should be pseudo
    if pseudo:
        node_type += "W"
    # Insert the node inside the database
    query = "create (n:"+ node_type +" {First_name: $first_name, Last_name: $last_name, Age: $age}) return id(n)"
    result = link.run(query, first_name=First_name, last_name=Last_name, age=Age)
    return result.single()[0]

def create_relation(link, source_id: int, dest_id: int, pseudo: bool = False, type: str = "Friends", reversed: bool = False) -> int:
    """
    Create a relation between two documents inside the database

    :param int source_id the id of the source node
    :param int dest_id the id of the destination node
    :param str type the type of the relation
    :param bool pseudo whether the relation should be indicated as watermark (for visualization purposes)
    :param bool reversed whether the relation is reversed or not
    """
    # If the relation is of a pseudo document, the suffix of W is added
    if pseudo:
        type += "W"
    # If reverse is True, swap the IDs of source and dest
    if reversed:
        temp = source_id
        source_id = dest_id
        dest_id = temp

    # Create the relation
    result = link.run("match (dest), (source) "
        "where id(source) = $source_id and id(dest) = $dest_id "
        "create (source)-[r:{type}]->(dest)"
        "return id(r)".format(type=type), 
        source_id=source_id, dest_id=dest_id)
    return result.single()[0]

def get_all_ids(link):
    result = link.run("match (n:Person) return id(n)")
    return result.value()

def delete_everythong(link):
    link.run("match (m)-[r]-(n) delete r, m, n")
    link.run("match (m) delete m")

def populate_fake_data(session, records: int = 25, relations:int = randrange(10)):
    """
    Populate the dataset with fake data
    
    :param int records the number of records to be added to the database
    :param int relations the number of random relations per record
    """
    arr = []
    for s in range(records):
        # create an array of pseudo documents
        arr.append(session.execute_write(create_node, First_name=names.get_first_name(), Last_name=names.get_last_name(), Age=randrange(85)))
    for s in arr:
        # generate a random array of nodes, to which the pseudo document will be connected
        connections = list(set(choices(range(records), k=relations)))
        for connection in connections:
            # skip if connection is to itself
            if arr[connection] == s:
                continue
            # Create a connection 
            session.execute_write(create_relation, source_id=s, dest_id=arr[connection])

def populate_uk_companies(link):
    """
    Populate the database with the uk_companies dataset

    :param link 
    """
    link.run("CREATE CONSTRAINT ON (c:Company) ASSERT c.companyNumber IS UNIQUE;"
             "CREATE CONSTRAINT ON (p:Property) ASSERT p.titleNumber IS UNIQUE;")
    link.run()