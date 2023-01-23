import database as db
import pseudo as ps
from random import choices, choice, randint
from main import resultLog, get_visible_watermark_ids
import logging
import json

def deletion_attack(session, step, verify):
    """
    Perform a deletion attack on the database

    :param step: the amount of documents that need to be deleted
    :param verify: the function used for verification of the watermark
    """
    logging.debug("Deletion attack started with step {step}".format(step=step))
    nodes_before = session.execute_read(db.all_ids_count)
    nodes_watermarked = session.execute_read(get_visible_watermark_ids)
    iteration = 0
    while True:
        if not verify(session):
            break
        id_to_delete = choices(session.execute_read(db.get_all_ids), k=step)
        session.execute_write(db.delete_documents, ids=id_to_delete)
        iteration += 1
    nodes_after = session.execute_read(db.all_ids_count)
    attack_summary = {
        "action": "modification_attack",
        "iteration": iteration,
        "step": step,
        "nodes_before": nodes_before,
        "nodes_after": nodes_after,
        "num_watermarked_nodes": len(nodes_watermarked)
    }
    resultLog.write(json.dumps(attack_summary) + "\n")
    return iteration

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