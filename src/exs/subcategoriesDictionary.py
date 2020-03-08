from util import format_field, pp_json, list_subcategories


# Returns subcategories as dictionary.
# TODO: add count of subcategories as a state, passed along with accumulated
def r_subs(field, parent, accumulated, level):
    global queries
    # Base case
    if (level == 0):
        # create entry as list (if it's not created yet)
        if (not (parent in accumulated)):
            accumulated[parent] = []

        # Push field to list full dictionary
        accumulated[parent] += [field]
        return accumulated

    # Setup for recursive step
    # Create entry as a new dictionary
    if (not (parent in accumulated)):
        accumulated[parent] = dict()

    # Recursive step
    subcategories = list_subcategories(field)
    queries += 1

    for subcategory in subcategories:
        search(subcategory, field, state, level-1)

    if (len(subcategories)):
        for subcategory in subcategories:
            next = r_subs(subcategory,
                          field, accumulated[parent], level-1)
            accumulated[parent] = next
    else:
        r_subs('', field, state, 0)

    return accumulated


# Number of queries q:
# q <= Sum of i = 1 up to n of (i-1) ^ l = O(n^l)
# where n is number of levels, and l is the maximum length of the list

# Parameters
queries = 0
field = 'Neuroscience'
entryName = 'Subcategories for ' + field
levels = 2  # 5 takes way too long to answer

subcategories = r_subs(field, entryName, dict(), levels)
print('Number of queries:', queries)
pp_json(subcategories)
