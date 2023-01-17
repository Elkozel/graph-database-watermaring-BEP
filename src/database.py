from typing import List
from random import choice

def add_document(link, document: dict, connections: List[int], document_type: str, reversed_direction: bool = False, randomized_directions: bool = False, visible: bool = False):
    """
    Add a document to the database

    :param link: the database session
    :param dict document: the document to be addeed to the database
    :param connections: the connections which the document should have
    :param bool reversed_direction: whether or not to reverse the direction of edge (mutually excludable with randomized_directions)
    :param bool randomized_directions: whether or not the edge directions should be randomized (mutually excludable with reversed_direction)
    :param bool visible: If selected, the letter W will be added on  the back of the type of the watermark document and edges, indicating that it is watermarked.
    """

    # Create the node
    source_id = create_node(link, document=document, visible=visible, node_type=document_type)
    # Create all the edges from the newly created node to the connection nodes
    for connection in connections:
        if randomized_directions:
            result = create_relation(link, source_id, connection, edge_type="Watermark",visible=visible, reversed = choice([True, False]))
        else:
            result = create_relation(link, source_id, connection, edge_type="Watermark" ,visible=visible, reversed=reversed_direction)
    return source_id
            
    
def create_node(link, document: dict, node_type: str, visible: bool = False):
    """
    Creates a node inside the database and returns its ID

    :param link the database session
    :param dict document: the document to be addeed to the database
    :param str node_type: the type of the newly created node
    :param bool visible: If selected, the letter W will be added on  the back of the type of the watermark document, indicating that it is watermarked.
    """
    # Check if the node should be pseudo
    if visible:
        node_type += "W"
    # Insert the node inside the database
    fields = ["{name}: $document.{field}".format(name=key, field=key) for key in document.keys()]
    query = "create (n:"+ node_type +" {" + ', '.join(fields) +"}) return id(n)"
    result = link.run(query, document=document)
    return result.single()[0]

def create_relation(link, source_id: int, dest_id: int, edge_type: str, visible: bool = False, reversed: bool = False) -> int:
    """
    Create a relation between two documents inside the database

    :param int source_id: the id of the source node
    :param int dest_id: the id of the destination node
    :param str edge_type: the type of the relation
    :param bool visible: If selected, the letter W will be added on  the back of the type of the watermark edge, indicating that it is watermarked.
    :param bool reversed: whether the relation is reversed or not
    """
    # If the relation is of a pseudo document, the suffix of W is added
    if visible:
        edge_type += "W"
    # If reverse is True, swap the IDs of source and dest
    if reversed:
        temp = source_id
        source_id = dest_id
        dest_id = temp

    # Create the relation
    result = link.run("match (dest), (source) "
        "where id(source) = $source_id and id(dest) = $dest_id "
        "create (source)-[r:{type}]->(dest) "
        "return id(r)".format(type=edge_type), 
        source_id=source_id, dest_id=dest_id)
    return result.single()[0]

def get_all_ids(link):
    result = link.run("match (n) return id(n)")
    return result.value()

def delete_everythong(link):
    link.run("match (m)-[r]-(n) delete r, m, n")
    link.run("match (m) delete m")
