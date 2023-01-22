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
import time
import json
import fake
import argparse
import logging

# Configure logger
resultLog = open("log/results.json", 'a')
logging.basicConfig(filename='basic.log', encoding='utf-8', level=logging.DEBUG)

# Load Environment Variables
load_dotenv()
# Load settings
settings = {}
with open("settings.json") as settingsFile:
    settings = json.load(settingsFile)
logging.debug("Settings loaded: {settings}".format(settings=json.dumps()))

# CONSTANTS
URI = os.getenv("DB_URL")
AUTH = (os.getenv("DB_USER"), os.getenv("DB_PASSWORD"))
ids = []


def get_all_non_company_ids(link):
    result = link.run("match (n)"
                      "where not \"Company\" in labels(n)"
                      "return id(n), labels(n)[0]")
    return result.values()


def get_all_company_ids(link):
    result = link.run("match (n:Company)"
                      "return id(n), labels(n)[0]")
    return result.values()


def get_visible_watermark_ids(link):
    result1 = link.run("match (n:CompanyW) "
                       "return id(n)")
    result2 = link.run("match (n:PropertyW) "
                       "return id(n)")
    return [result1.value(), result2.value()]


def watermark_uk_companies(session, watermark_key: int, watermark_identity: str, watermark_visibility: bool = False):
    """
    Watermark the UK companies database

    :param session: the session for connection to the database
    """
    # Retrieve all IDs from the database
    logging.debug("Watermarking UK Companies dataset")
    id_count = session.execute_read(db.all_ids_count)
    all_company_ids = session.execute_read(get_all_company_ids)
    all_non_company_ids = session.execute_read(get_all_non_company_ids)
    logging.debug("Fetching all document ids: Done")
    start_time = time.time()
    watermarked = wk.watermark_database(session,
                                        ids=all_company_ids,
                                        min_group_size=10,
                                        max_group_size=1000,
                                        watermarked_document_type="Company",
                                        watermark_cover_field="companyNumber",
                                        watermarked_document_fields=[
                                            "countryOfOrigin", "name", "status"],
                                        watermarked_document_optional_fields=[
                                            "mortgagesOutstanding", "SIC", "category"],
                                        watermark_key=watermark_key,
                                        watermark_identity=watermark_identity,
                                        watermark_visibility=watermark_visibility)
    end_time = time.time()
    performance = {
        "duration": end_time-start_time,
        "number_company_ids": len(all_company_ids),
        "number_non_company_ids": len(all_non_company_ids),
        "number_nodes_before": id_count,
        "documents_introduced": len(watermarked)
    }
    resultLog.write(json.loads(performance))
    logging.debug("Database was watermarked in {time} seconds".format(time=end_time-start_time))
    logging.info("{number} pseudo nodes introduced".format(number=sum(len(watermarked))))
    return [watermarked, []]


def verify_uk_companies(session, watermarked_ids: tuple[List[int], List[int]], key: int, watermark_identity: str, fast_check: bool = True):
    result = verify_watermark(
        session=session,
        watermarked_ids=watermarked_ids[0],
        key=key,
        watermark_identity=watermark_identity,
        watermark_fields=[
            "countryOfOrigin", "name", "status"],
        watermark_cover_field="companyNumber",
        fast_check=fast_check
    )
    logging.info("Watermark verification with result {result}".format(result=result))
    return result


def verify_watermark(session, watermarked_ids: List[int], key: int, watermark_identity: str, watermark_fields: List[str], watermark_cover_field: str, fast_check: bool = True):
    documents = session.execute_read(db.get_documents, ids=watermarked_ids)
    logging.debug("Verifying {number} documents for watermark".format(number=len(documents)))
    for document in documents:
        result = wk.detect_watermark(document, key=key, identity=watermark_identity,
                                     field=watermark_cover_field, fields=watermark_fields)
        if result:
            return True
    return False


parser = argparse.ArgumentParser(description='Watermark a Neo4j database')
parser.add_argument("-i", '--interactive', action='store_true',
                    help='Show the interactive menu')
parser.add_argument("-w", '--watermark', action='store_true',
                    help='Watermark UK database without asking')
parser.add_argument('--verify', action='store_true',
                    help='Verify the watermark (exit with error if not verified)')
# parser.add_argument('--reset', metavar='N', type=int,
#                     help='Watermark UK database')

args = parser.parse_args()
print(args.watermark)
# MAIN MENU
main_menu = [
    inquirer.List('Main menu',
                  message="What would you like me to do?",
                  choices=["Watermark UK database",
                           "Verify watermark", "Populate database", "Reset --hard", "Exit"],
                  ),
]


def show_menu():
    # Present the user with the main menu
    answer = inquirer.prompt(main_menu)
    match answer["Main menu"]:
        case "Watermark UK database":
            with driver.session(database="neo4j") as session:
                watermark_uk_companies(
                    session, settings["key"], settings["watermark_identity"], settings["watermark_visible"])
        case "Verify watermark":
            with driver.session(database="neo4j") as session:
                res = verify_uk_companies(
                    session, ids, settings["key"], settings["watermark_identity"])
                print(res)
        case "Populate database":
            with driver.session(database="neo4j") as session:
                fake.populate_fake_data(session)
        case "Reset --hard":
            with driver.session(database="neo4j") as session:
                db.delete_everythong(session)
        case "Exit":
            sys.exit(0)


if __name__ == "__main__":
    with GraphDatabase.driver(URI, auth=AUTH) as driver:
        # Verify connection to the database
        driver.verify_connectivity()

    with driver.session(database="neo4j") as session:
        ids = session.execute_read(get_visible_watermark_ids)

    if args.interactive:
        while True:
            show_menu()
    elif args.watermark:
        with driver.session(database="neo4j") as session:
            ids = watermark_uk_companies(session)
    elif args.verify:
        with driver.session(database="neo4j") as session:
            res = verify_uk_companies(
                session, ids, settings["key"], settings["watermark_identity"])
            print(res)
    else:
        while True:
            show_menu()
