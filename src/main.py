import os
import sys
from typing import List
from neo4j import GraphDatabase
from dotenv import load_dotenv
import inquirer
import database as db
import pseudo as ps
import watermark as wk
import attack
import fake
import argparse

# Load Environment Variables
load_dotenv()

# CONSTANTS
URI = os.getenv("DB_URL")
AUTH = (os.getenv("DB_USER"), os.getenv("DB_PASSWORD"))
RELATIONS = {
    "Recipient": {"type": "DONATED", "dir": "out"},
    "Property": {"type": "OWNS", "dir": "out"},
    "Person": {"type": "HAS_CONTROL", "dir": "in"}
}


def watermark_database(session,
                       ids: List[int],
                       min_group_size: int,
                       max_group_size: int,
                       watermarked_document_type: str,
                       watermark_cover_field: str,
                       watermarked_document_fields: List[str],
                       watermark_key: int,
                       group_find_max_tries: int = 50,
                       watermarked_document_optional_fields: List[str] = [],
                       watermark_identity: str = "",
                       watermark_edge_direction_randomized: bool = False,
                       watermark_visibility: bool = False):
    """
    Watermarks a database

    :param ids: The ids of the documents, which need to be watermarked
    :param min_group_size: The minimum size of each group
    :param max_group_size: The maximum size of each group
    :param watermarked_document_type: The type of the document, which contains the watermark
    :param watermark_cover_field: The name of the field, which contains the watermark
    :param watermarked_document_fields: The fields, which are included inside the watermarked document
    :param watermarked_document_optional_fields: The fielDs, which are optionally included inside the watermarked document
    :param watermark_key: The private key for the watermark
    :param group_find_max_tries: The amount of tries it will take for the algorithm to give up on partitioning groups
    :param watermark_identity: An optional identity for the watermark, this can be the name of the person the information was leased or any other identifiable string
    :param watermark_edge_direction_randomized: If the edge direction should be randomized. If true, the algorithm will treat the graph as undirected and not take the direction of the edges into account when creating the watermark.
    :param watermark_visibility: Optional. If selected, the letter W will be added on  the back of the type of the watermark document and edges, indicating that it is watermarked.
    """
    # Determine the size of each group
    group_sizes = wk.get_random_set(len(ids), min_group_size, max_group_size, group_find_max_tries)
    # Pick the groups, based on the predetermined size
    groups = wk.divide_groups(ids, group_sizes)
    # Generate pseudo document for each group
    document_ids = []
    for group in groups:
        pseudo_document = session.execute_read(
            ps.create_pseudo_document, 
            type=watermarked_document_type, 
            fields=watermarked_document_fields,
            optional_fields=watermarked_document_optional_fields)
        # Embed watermark in each pseudo document
        wk.embed_watermark(pseudo_document, key=watermark_key, identity=watermark_identity,
                           field=watermark_cover_field, fields=watermarked_document_fields)
        # Insert the pseudo documents inside the database
        pseudo_node = session.execute_write(db.create_node,
            document=pseudo_document,
            visible=watermark_visibility,
            node_type=watermarked_document_type
        )
            
        document_ids.append(pseudo_node)
        # Create relations
        for (node, label) in group:
            relation = RELATIONS[label]
            session.execute_write(db.create_relation,
                source_id=pseudo_node,
                dest_id=node,
                edge_type=relation["type"],
                reversed=(relation["dir"] == "in"),
                visible=watermark_visibility
            )
    return document_ids


def get_all_company_ids(link):
    result = link.run("match (n)"
                      "where not \"Company\" in labels(n)"
                      "return id(n), labels(n)[0]")
    return result.values()

def watermark_uk_companies(session):
    """
    Watermark the UK companies database

    :param session: the session for connection to the database
    """
    # Retrieve all IDs from the database
    all_ids = session.execute_read(get_all_company_ids)
    watermarked = watermark_database(session,
                       ids=all_ids,
                       min_group_size=10,
                       max_group_size=1000,
                       watermarked_document_type="Company",
                       watermark_cover_field="companyNumber",
                       watermarked_document_fields=["countryOfOrigin", "name", "status"],
                       watermarked_document_optional_fields=["mortgagesOutstanding", "SIC", "category"],
                       watermark_key=1,
                       watermark_identity="RP Project",
                       watermark_visibility=True)
    return watermarked
    

def verify_watermark(session, watermarked_ids: List[int], key: int, watermark_identity: str, watermark_fields: List[str], watermark_cover_field: str, fast_check: bool = True):
    documents = session.execute_read(db.get_documents, ids=watermarked_ids)
    for document in documents:
        result = wk.detect_watermark(document, key=key, identity=watermark_identity, field=watermark_cover_field, fields=watermark_fields)
        if result:
            return True
    return False


# MAIN MENU
main_menu = [
    inquirer.List('Main menu',
                  message="What would you like me to do?",
                  choices=["Watermark UK database",
                           "Populate database", "Reset --hard", "Exit"],
                  ),
]

if __name__ == "__main__":
    with GraphDatabase.driver(URI, auth=AUTH) as driver:
        # Verify connection to the database
        driver.verify_connectivity()
        
        while True:
            # Present the user with the main menu
            answer = inquirer.prompt(main_menu)
            match answer["Main menu"]:
                case "Watermark UK database":
                    with driver.session(database="neo4j") as session:
                        watermark_uk_companies(session)
                case "Populate database":
                    with driver.session(database="neo4j") as session:
                        fake.populate_fake_data(session)
                case "Reset --hard":
                    with driver.session(database="neo4j") as session:
                        db.delete_everythong(session)
                case "Exit":
                    sys.exit(0)
