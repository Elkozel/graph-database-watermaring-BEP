import os
from typing import List
from neo4j import GraphDatabase
from dotenv import load_dotenv
import inquirer
import database as db
import pseudo as ps
import watermark as wk

# Load Environment Variables
load_dotenv()

# CONSTANTS 
URI = os.getenv("DB_URL")
AUTH = (os.getenv("DB_USER"), os.getenv("DB_PASSWORD"))

def watermark_database(session, min_group_size: int, max_group_size: int, watermarked_document_type: str, watermarked_document_field: str, watermarked_document_fields: List[str], watermark_key:int, watermark_identity: str):
    # Retrieve all IDs from the database
    all_ids = session.execute_read(db.get_all_ids)
    # Determine the size of each group
    group_sizes = wk.get_random_set(len(all_ids), min_group_size, max_group_size)
    # Pick the groups, based on the predetermined size
    groups = wk.divide_groups(all_ids, group_sizes)
    # Generate pseudo document for each group
    for group in groups:
        pseudo_document = session.execute_read(ps.create_pseudo_document, type=watermarked_document_type, fields=watermarked_document_fields)
        # Embed watermark in each pseudo document
        wk.embed_watermark(pseudo_document, key=watermark_key, identity=watermark_identity, field=watermarked_document_field, fields=watermarked_document_fields)
        # Insert the pseudo documents inside the database
        session.execute_write(db.add_document, 
            First_name = pseudo_document["First_name"],
            Last_name = pseudo_document["Last_name"],
            Age = pseudo_document["Age"], 
            connections = group,
            randomized_directions = True)

def watermark_fake_database(session):
    """
    Watermark a database populated with fake information

    :param session the session for connection to the database
    """
    # Create groups
    all_ids = session.execute_read(db.get_all_ids)
    group_sizes = wk.get_random_set(len(all_ids), 3, 12)
    groups = wk.divide_groups(all_ids, group_sizes)
    # Generate pseudo document for each group
    for group in groups:
        pseudo_document = session.execute_read(ps.create_pseudo_document, type="Person", fields=["First_name", "Last_name", "Age"])
        # Embed watermark in each pseudo document
        wk.embed_watermark(pseudo_document, key="")
        # Insert the pseudo documents inside the database
        session.execute_write(db.add_document, 
            First_name = pseudo_document["First_name"],
            Last_name = pseudo_document["Last_name"],
            Age = pseudo_document["Age"], 
            connections = group,
            randomized_directions = True)

def watermark_uk_companies(session):
    """
    Watermark the UK companies database

    :param session the session for connection to the database
    """


# MAIN MENU
main_menu = [
  inquirer.List('Main menu',
                message="What would you like me to do?",
                choices=["Watermark database", "Populate database", "Reset --hard", "Exit"],
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
                case "Watermark database":
                    with driver.session(database="neo4j") as session:
                        watermark_fake_database(session)
                case "Populate database":
                    with driver.session(database="neo4j") as session:
                        db.populate_fake_data(session)
                case "Reset --hard":
                    with driver.session(database="neo4j") as session:
                        db.delete_everythong(session)
                        db.populate_fake_data(session)
                case "Exit":
                    sys.exit(0)