from typing import Any, List
from random import randint, randrange
from base64 import b64encode
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
