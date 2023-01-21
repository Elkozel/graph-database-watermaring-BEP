import database as db
import pseudo as ps
from random import choices, choice, randint

def deletion_attack(session, step):
    """
    Perform a deletion attack on the database

    :param step: the amount of documents that need to be deleted
    """
    id_to_delete = choices(session.execute_read(db.get_all_ids), k=step)

    session.execute_write(db.delete_documents, ids=id_to_delete)

def insertion_attack(session, step, connections_min=0, connections_max=20):
    """
    Perform an insertion attack

    :param step: the amount of documents, which should be added
    :param connections_min: the minimum amount of connections per document
    :param connections_max: the maximum amount of connections per document
    """
    node_type = "Company"
    fields = []
    opt_fields = []

    for s in step:
        all_ids = session.execute_read(db.get_all_ids)
        doc = session.execute_read(ps.create_pseudo_document,
            type=node_type,
            fields=fields,
            optional_fields=opt_fields
        )
        doc_id = session.execute_write(db.create_node,
            document=doc,
            node_type=node_type
        )
        connections = list(set(choices(all_ids, k=randint(connections_min, connections_max))))
        for connection in connections:
            # skip if connection is to itself
            if connection == doc_id:
                continue
            # Create a connection 
            session.execute_write(db.create_relation, source_id=doc_id, dest_id=connection, type="Connection")