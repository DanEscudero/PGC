import requests

from util import format_field, pp_json, clear_category_name, list_subcategories


def recursive_subcategories(field, parent, accumulated, level, track_parents):
    if (level == 0):
        if (track_parents):
            return accumulated + [(parent, field)]
        else:
            return accumulated + [field]

    subs = []
    subcategories = list_subcategories(field)
    for subcategory in subcategories:
        subs += recursive_subcategories(subcategory,
                                        field, accumulated, level-1, track_parents)

    return accumulated + subs


# Parameters
field = 'Mathematics'
parent = ''
accumulated = []
levels = 2
track_parents = False

list = recursive_subcategories(
    field, parent, accumulated, levels, track_parents)

print('Number of Results:', len(list))
pp_json(list)
