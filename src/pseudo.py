from random import choice
from typing import List


def create_pseudo_document(link, fields: List[str], type: str = "Person"):
    """
    Create a pseudo (fake) document, given the document type and its fields
    
    :param List[str] fields the fields, which the resulting pseudo document should have
    :param str type the type of the resulting document
    """
    # For each of the fields
    new_object = {}
    for field in fields:
        # Retrieve all values
        values = link.run("Match (n:{type}) return collect( distinct n.{field})".format(field=field, type=type)).value()[0]
        # Pick a random value for the field
        new_object[field] = choice(values)
    
    return new_object