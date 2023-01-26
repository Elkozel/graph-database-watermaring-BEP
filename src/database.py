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
    source_id = create_node(link, document=document,
                            visible=visible, node_type=document_type)
    # Create all the edges from the newly created node to the connection nodes
    for connection in connections:
        if randomized_directions:
            result = create_relation(link, source_id, connection, edge_type="Watermark",
                                     visible=visible, reversed=choice([True, False]))
        else:
            result = create_relation(
                link, source_id, connection, edge_type="Watermark", visible=visible, reversed=reversed_direction)
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
    fields = ["{name}: $document.{field}".format(
        name=key, field=key) for key in document.keys()]
    query = "create (n:" + node_type + \
        " {" + ', '.join(fields) + "}) return id(n)"
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

def all_ids_count(link):
    result = link.run("match (n) return count(n)")
    return result.single()[0]


def get_all_ids(link):
    result = link.run("match (n) return id(n)")
    return result.value()


def get_all_ids_with_labels(link):
    result = link.run("match (n) return id(n), labels(n)[0]")
    return result.value()


def get_document(link, id):
    return link.run("match (m) "
                    "where id(m) = $id "
                    "return m", id=id
                    ).single()


def get_documents(link, ids):
    return link.run("match (m) "
                    "where id(m) in $ids "
                    "return m", ids=ids
                    ).value()


def dublicate_documents(link, ids):
    return link.run("match (n)"
                    "where id(n) in $ids"
                    "with collect(n) AS c_nodes"
                    "call apoc.refactor.cloneNodes(c_nodes)"
                    "YIELD input, output"
                    "Return id(output)", ids=ids
                    )


def delete_document(link, id):
    result = link.run("match (m)-[r]-() "
                      "where id(m) = $id "
                      "delete r, m", id=id
                      )


def delete_documents(link, ids):
    result = link.run("match (m)-[r]-() "
                      "where id(m) in $ids "
                      "delete r, m", ids=ids
                      )
    return result

def delete_field(link, id, field):
    result = link.run("match (m) "
                      "where id(m) = $id "
                      "remove m.$field ", id=id, field=field
                      )
    return result


def delete_everythong(link):
    link.run("match (m)-[r]-(n) delete r, m, n")
    link.run("match (m) delete m")

def populate_uk_companies(session):
    session.execute_write(uk_companies_contraints)
    session.execute_write(load_uk_companies)
    session.execute_write(uk_companies_index)

def uk_companies_contraints(link):
    link.run("CREATE CONSTRAINT FOR (c:Company) REQUIRE c.companyNumber IS UNIQUE")
    link.run("CREATE CONSTRAINT FOR (p:Property) REQUIRE p.titleNumber IS UNIQUE")

def load_uk_companies(link):
    link.run("LOAD CSV WITH HEADERS FROM \"https://guides.neo4j.com/ukcompanies/data/PSCAmericans.csv\" AS row1 MERGE (c:Company {companyNumber: row1.company_number})")
    link.run("LOAD CSV WITH HEADERS FROM \"https://guides.neo4j.com/ukcompanies/data/PSCAmericans.csv\" AS row2 MERGE (p:Person {name: row2.`data.name`, birthYear: row2.`data.date_of_birth.year`, birthMonth: row2.`data.date_of_birth.month`}) ON CREATE SET p.nationality = row2.`data.nationality`, p.countryOfResidence = row2.`data.country_of_residence`")
    link.run("LOAD CSV WITH HEADERS FROM \"https://guides.neo4j.com/ukcompanies/data/PSCAmericans.csv\" AS row3 MATCH (c:Company {companyNumber: row3.company_number}) MATCH (p:Person {name: row3.`data.name`, birthYear: row3.`data.date_of_birth.year`, birthMonth: row3.`data.date_of_birth.month`}) MERGE (p)-[r:HAS_CONTROL]->(c) SET r.nature = split(replace(replace(replace(row3.`data.natures_of_control`, \"[\",\"\"),\"]\",\"\"),  '\"', \"\"), \",\")")
    link.run("LOAD CSV WITH HEADERS FROM \"https://guides.neo4j.com/ukcompanies/data/CompanyDataAmericans.csv\" AS row4 MATCH (c:Company {companyNumber: row4.` CompanyNumber`}) SET c.name = row4.CompanyName, c.mortgagesOutstanding = toInteger(row4.`Mortgages.NumMortOutstanding`), c.incorporationDate = Date(Datetime({epochSeconds: apoc.date.parse(row4.IncorporationDate,'s','dd/MM/yyyy')})),    c.SIC = row4.`SICCode.SicText_1`,    c.countryOfOrigin = row4.CountryOfOrigin,    c.status = row4.CompanyStatus,    c.category = row4.CompanyCategory")
    link.run("LOAD CSV WITH HEADERS FROM \"https://guides.neo4j.com/ukcompanies/data/ElectionDonationsAmericans.csv\" AS row5 MATCH (c:Company) WHERE c.companyNumber = row5.CompanyRegistrationNumber MERGE (p:Recipient {name: row5.RegulatedEntityName}) SET p.entityType = row5.RegulatedEntityTypeMERGE (c)-[r:DONATED {ref: row5.ECRef}]->(p) SET r.date  = Date(Datetime({epochSeconds: apoc.date.parse(row5.ReceivedDate,'s','dd/MM/yyyy')})),    r.value = toFloat(replace(replace(row5.Value, \"£\", \"\"), \",\", \"\"))")
    link.run("LOAD CSV WITH HEADERS FROM \"https://guides.neo4j.com/ukcompanies/data/LandOwnershipAmericans.csv\" AS row6 MATCH (c:Company {companyNumber: row6.`Company Registration No. (1)`}) MERGE (p:Property {titleNumber: row6.`Title Number`}) SET p.address = row6.`Property Address`, p.county  = row6.County,    p.price   = toInteger(row6.`Price Paid`),    p.district = row6.DistrictMERGE (c)-[r:OWNS]->(p)WITH row6, c,r,p WHERE row6.`Date Proprietor Added` IS NOT NULLSET r.date = Date(Datetime({epochSeconds: apoc.date.parse(row6.`Date Proprietor Added`,'s','dd-MM-yyyy')}))")


def uk_companies_index(link):
    link.run("CREATE INDEX CompanyIndex FOR (n:Company) ON (n.incorporationDate)")