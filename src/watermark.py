from typing import Any, List
from random import randint, randrange
import database as db
import pseudo as ps
import sys

def embed_watermark(document, key: int, identity: str, field: str, fields: List[str]):
    """
    Embed the watermark inside the document

    :param document the document, where the watermark should be embedded
    :param str key the key used for the embedding process
    :param str indetity the indetity, which the watermark will carry
    :param str field the field, into which the watermark will be embedded
    :param List[str] fields the fields, which will be used to generate the watermark
    """
    concatinated_fields = [str(document[field]) for field in fields]
    watermark = hash(identity + "".join(concatinated_fields) + str(key)) % 11706361
    document[field] = watermark
    return watermark

def detect_watermark(document, key: int, identity: str, field: str, fields: List[str]):
    """
    Detect if a watermark is present inside the document

    :param document the document, where the watermark should be embedded
    :param str key the key used for the embedding process
    :param str indetity the indetity, which the watermark will carry
    :param str field the field, into which the watermark will be embedded
    :param List[str] fields the fields, which will be used to generate the watermark
    """
    concatinated_fields = [str(document[field]) for field in fields]
    watermark = hash(identity + "".join(concatinated_fields) + str(key)) % 11706361
    return document[field] == watermark


def get_random_set(target_sum: int, lower_range: int, upper_range: int, max_tries: int):
    """
    Generate a set of random numbers, all summing up to a target sum

    :param int target_sum the target sum when you sum up all the numbers from the list
    :param int lower_range the lower bound (inclusive) of the range
    :param int upper_range the upper bound (excluside) of the range
    :param int max_tries the number of tries it takes before the algorithm gives up
    """
    # While the algorithm has not exeeded the maximum tries
    if max_tries <= 0:
        print("No groups were found satisfying the bounds {lower} and {upper} after {tries} tries"
            .format(upper=upper_range, lower=lower_range, tries=max_tries))
        sys.exit(1)

    random_list = []
    # Fill the list with random ints, untill you hit the upper bound of the range
    while target_sum - sum(random_list) > upper_range:
        random_list.append(randint(lower_range, upper_range))
    # Then check if the number is in the range
    remainder = target_sum - sum(random_list)
    if remainder < lower_range:
        # If the number is not in the range, run the algorithm again
        return get_random_set(target_sum, upper_range, lower_range, max_tries - 1)
    # else append the remainder and return the array
    else:
        random_list.append(remainder)
        return random_list

def divide_groups(group: List[Any], group_sizes: List[int]):
    """
    Divide a list of objects into groups with a given size

    :param List[Any] group the whole group of objects
    :param List[int] group_sizes a list of sizes for each group
    """
    # Check if the sum of group_sizes is equal to the size of group
    assert len(group) == sum(group_sizes)
    # Create a new list
    new_groups = []
    # for each size
    for group_size in group_sizes:
        # pick random elements from the list and create a new array from them
        new_group = [group.pop(randrange(len(group))) for _ in range(group_size)]
        # append the new array to the return of the function
        new_groups.append(new_group)

    return new_groups


RELATIONS = {
    "Recipient": {"type": "DONATED", "dir": "out"},
    "Property": {"type": "OWNS", "dir": "out"},
    "Person": {"type": "HAS_CONTROL", "dir": "in"},
    "Company": {"type": "HAS_CONTROL", "dir": "out"}
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
    group_sizes = get_random_set(
        len(ids), min_group_size, max_group_size, group_find_max_tries)
    # Pick the groups, based on the predetermined size
    groups = divide_groups(ids, group_sizes)
    # Generate pseudo document for each group
    document_ids = []
    for group in groups:
        pseudo_document = session.execute_read(
            ps.create_pseudo_document,
            type=watermarked_document_type,
            fields=watermarked_document_fields,
            optional_fields=watermarked_document_optional_fields)
        # Embed watermark in each pseudo document
        embed_watermark(pseudo_document, key=watermark_key, identity=watermark_identity,
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
