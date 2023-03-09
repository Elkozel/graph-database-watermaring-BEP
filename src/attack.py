import database as db
import pseudo as ps
from random import choices, choice, randint
from main import resultLog, get_visible_watermark_ids
import logging
import numpy as np
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
    all_ids = session.execute_read(db.get_all_ids)
    while True:
        if not verify(session):
            break
        try:
            ids_to_delete = []
            for s in range(step):
                id_to_delete = choice(range(len(all_ids)))
                ids_to_delete.append(all_ids.pop(id_to_delete))
            result = session.execute_write(db.delete_documents, ids=ids_to_delete)
            iteration += 1
            if iteration % 20 == 0:
                logging.info("Deleted {num}/{total} nodes ({result})".format(num=iteration*step, total=len(all_ids), result=result.single()))
        except Exception as err:
            iteration += 1
            logging.error("Error: {err} encountered after modification attack".format(err=err))
            error = True
            break
    nodes_after = session.execute_read(db.all_ids_count)
    attack_summary = {
        "action": "deletion_attack",
        "iteration": iteration,
        "step": step,
        "nodes_before": nodes_before,
        "nodes_after": nodes_after,
        "nodes_deleted": nodes_before - nodes_after,
        "num_watermarked_nodes": len(nodes_watermarked[0])
    }
    resultLog.write(json.dumps(attack_summary) + "\n")
    resultLog.flush()
    logging.info("The {action} attack concluded with {deleted_nodes} nodes deleted and {nodes_after} remaining".format(
        action=attack_summary["action"],
        deleted_nodes=attack_summary["nodes_deleted"],
        nodes_after=attack_summary["nodes_after"]
    ))
    return iteration

def modification_attack(session, step, verify):
    """
    Perform a modification attack on the database

    :param step: the amount of fields that need to be modified
    :param verify: the function used for verification of the watermark
    """
    logging.debug("Modification attack started with step {step}".format(step=step))
    nodes_before = session.execute_read(db.all_ids_count)
    nodes_watermarked = session.execute_read(get_visible_watermark_ids)
    iteration = 0
    error = False
    all_ids = np.array(session.execute_read(db.get_all_ids_with_fields))
    while True:
        if not verify(session):
            break
        try:
            all_choices = np.where(all_ids[:, 1] > 0)[0]
            ids_to_modify = choices(all_choices, k=step)
            for id in ids_to_modify:
                try:
                    fields = session.execute_read(db.get_fields, id=id.item())
                    if len(fields) == 0:
                        continue
                    field_to_delete = choice(fields)
                    result = session.execute_write(db.delete_field, id=id.item(), field=field_to_delete)
                    iteration += 1
                    all_ids[np.where(all_ids[:,0]==id)[0][0]][1] -= 1
                except Exception as err:
                    logging.error("Error: {err} encountered after modification attack(inner loop)".format(err=err))
            if iteration % 100 == 0:
                logging.info("Deleted {num} fields".format(num=iteration))
        except Exception as err:
            logging.error("Error: {err} encountered after modification attack".format(err=err))
            error = True
            break
    nodes_after = session.execute_read(db.all_ids_count)
    attack_summary = {
        "action": "modification_attack",
        "iteration": iteration,
        "step": step,
        "nodes_before": nodes_before,
        "nodes_after": nodes_after,
        "fields_deleted": iteration,
        "num_watermarked_nodes": len(nodes_watermarked[0]),
        "ended_with_error": error
    }
    resultLog.write(json.dumps(attack_summary) + "\n")
    resultLog.flush()
    logging.info("The {action} attack concluded with {fields_nodes} nodes deleted and {nodes_after} remaining".format(
        action=attack_summary["action"],
        fields_nodes=attack_summary["fields_deleted"],
        nodes_after=attack_summary["nodes_after"]
    ))
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

def intersection(lst1, lst2):
    lst3 = [value for value in lst1 if value in lst2]
    return lst3

# percentages = [0.1, 0.3, 0.5, 0.6, 0.75, 0.8, 0.9, 0.95, 0.98]
# iterations = 5
def deletion_attack_short(session, percentages, iterations):
    """
    Perform a fast deletion attack on the database (without deleting anything from the database)

    :param percentages: the percentages of nodes to be deleted
    """
    logging.debug("Short deletion attack started")
    nodes_all_ids = session.execute_read(db.get_all_ids)
    nodes_watermarked = session.execute_read(get_visible_watermark_ids)
    percentage_nodes = [len(nodes_all_ids)*p for p in percentages]
    results = {}
    for s in range(iterations):
        for index, deletions in enumerate(percentage_nodes):
            deleted_nodes = choices(nodes_all_ids, k=deletions)
            nodes_deleted = intersection(deleted_nodes, nodes_watermarked[0])
            percentage_str = str(percentages[index])
            results[percentage_str] = len(nodes_deleted)

        attack_summary = {
               "action": "deletion_attack_fast",
               "results": results,
                "nodes_before": len(nodes_all_ids),
                "num_watermarked_nodes": len(nodes_watermarked[0])
            }
        resultLog.write(json.dumps(attack_summary) + "\n")
        resultLog.flush()
    logging.info("Short deletion attack ended")
    return results
