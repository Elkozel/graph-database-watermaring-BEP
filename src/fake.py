import names
from random import randrange, choices
import database as db
import pseudo as ps
import watermark as wk
from main import watermark_database


def populate_fake_data(session, records: int = 25, relations:int = randrange(10)):
    """
    Populate the dataset with fake data
    
    :param int records the number of records to be added to the database
    :param int relations the number of random relations per record
    """
    arr = []
    for s in range(records):
        # create an array of pseudo documents
        doc = {
            "First_Name": names.get_first_name(),
            "Last_Name": names.get_last_name(),
            "Age": randrange(85)
        }
        arr.append(session.execute_write(db.create_node, document=doc))
    for s in arr:
        # generate a random array of nodes, to which the pseudo document will be connected
        connections = list(set(choices(range(records), k=relations)))
        for connection in connections:
            # skip if connection is to itself
            if arr[connection] == s:
                continue
            # Create a connection 
            session.execute_write(db.create_relation, source_id=s, dest_id=arr[connection], type="Friends")

def watermark_fake_database(session):
    """
    Watermark a database populated with fake information

    :param session the session for connection to the database
    """
    # Create groups
    all_ids = session.execute_read(db.get_all_ids)
    watermark_database(session, all_ids, 3, 12, "Person", "Salary", ["First_Name", "Last_Name", "Age"], 1, watermark_visibility=True)