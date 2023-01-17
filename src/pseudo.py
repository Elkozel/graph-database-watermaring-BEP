from random import choice, choices, randint
from typing import List


def create_pseudo_document(link, type: str, fields: List[str], optional_fields: List[str]):
    """
    Create a pseudo (fake) document, given the document type and its fields
    
    :param List[str] fields: the fields, which the resulting pseudo document should have
    :param str type: the type of the resulting document
    :param List[str] optional_fields: fields, which are optional and might not be present in the end result
    """
    # For each of the fields
    new_object = {}
    for field in fields:
        # Retrieve all values
        values = link.run("Match (n:{type}) return collect(distinct n.{field})".format(field=field, type=type)).value()[0]
        # Pick a random value for the field
        new_object[field] = choice(values)
    
    # Return if no optional fields were specified
    if len(optional_fields) == 0:
        return new_object
    
    # Add optional fields
    op_fields_chosen = choices(optional_fields, k=randint(0, len(optional_fields)))
    for op_field in op_fields_chosen:
        # Retrieve all values
        values = link.run("Match (n:{type}) return collect(distinct n.{field})".format(field=op_field, type=type)).value()[0]
        # Pick a random value for the field
        new_object[op_field] = choice(values)

    return new_object