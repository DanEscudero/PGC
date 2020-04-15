import requests
from util import format_field, pp_json, clear_category_name, list_subcategories


# Returns subcategories as dictionary.
# TODO: add count of subcategories as a state, passed along with accumulated
def search(field, parent, level):
    global queries, pending, searched

    # Base case
    if (level == 0):
        # create entry as list (if it's not created yet)
        if (not (parent in accumulated)):
            accumulated[parent] = []

        if (field != ''):
            # Push field to list full dictionary
            accumulated[parent] += [field]

        return (accumulated)

    # Setup for recursive step
    # Create entry as a new dictionary
    if (not (parent in accumulated)):
        accumulated[parent] = dict()

    # Recursive step
    subcategories = list_subcategories(field)
    queries = queries + 1

    state = (accumulated[parent])
    if (len(subcategories)):
        for subcategory in subcategories:
            search(subcategory, field, state, level-1)
    else:
        search('', field, state, 0)

    return (accumulated)


# supercategories
super = {
    "action": "query",
    "generator": "categories",
    "titles": "Mathematics",
    "prop": "info",
    "cllimit": "max",
    "format": "json",
}

# Subcategories
sub = {
    "action": "query",
    "gcmtitle": "Category:Mathematics",
    "gcmtype": "subcat",
    "generator": "categorymembers",
    "format": "json",
    "alprop": "title",
    "gcmlimit": "max",
    "list": "alllinks",
    "allimit": "max",
}

session = requests.Session()
result = session.get(
    url='https://en.wikipedia.org/w/api.php', params=sub).json()

pp_json(result)
