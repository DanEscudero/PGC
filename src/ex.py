from util import format_field, pp_json, clear_category_name, list_subcategories


# Returns subcategories as dictionary.
# TODO: add count of subcategories as a state, passed along with accumulated
def search(field, parent, state, level):
    (accumulated, queries) = state
    # Base case
    if (level == 0):
        # create entry as list (if it's not created yet)
        if (not (parent in accumulated)):
            accumulated[parent] = []

        if (field != ''):
            # Push field to list full dictionary
            accumulated[parent] += [field]

        return (accumulated, queries)

    # Setup for recursive step
    # Create entry as a new dictionary
    if (not (parent in accumulated)):
        accumulated[parent] = dict()

    # Recursive step
    subcategories = list_subcategories(field)
    queries = queries + 1
    # print('q', field)

    state = (accumulated[parent], queries)
    if (len(subcategories)):
        for subcategory in subcategories:
            search(subcategory, field, state, level-1)
    else:
        search('', field, state, 0)

    return (accumulated, queries)


# Parameters
field = 'Neuroscience'
entryName = 'Subcategories for ' + field
levels = 2  # 5 takes way too long to answer

state = (dict(), 0)
(subcategories, q) = search(field, entryName, state, levels)

pp_json(subcategories)
print(q)
