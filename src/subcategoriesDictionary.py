from util import format_field, pp_json, clear_category_name, list_subcategories


# Returns subcategories as dictionary.
# TODO: add count of subcategories as a state, passed along with accumulated
def recursive_subcategories(field, parent, accumulated, level):
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
    for subcategory in subcategories:
        accumulated[parent] = recursive_subcategories(subcategory,
                                                      field, accumulated[parent], level-1)

    return accumulated


# Parameters
field = 'Neuroscience'
entryName = 'Subcategories for ' + field
levels = 2  # 5 takes way too long to answer

subcategories = recursive_subcategories(field, entryName, dict(), levels)
pp_json(subcategories)
