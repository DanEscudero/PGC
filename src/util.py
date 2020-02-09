import json


def pp_json(json_thing, sort=True, indents=4):
    if type(json_thing) is str:
        print(json.dumps(json.loads(json_thing), sort_keys=sort, indent=indents))
    else:
        print(json.dumps(json_thing, sort_keys=sort, indent=indents))
    return None


# Converts to snake case, with letters in lower case, except for the first one
def format_field(field):
    return field.replace(' ', '_').lower().capitalize()


# Converts 'Category:X' to X
def clear_category_name(name):
    return name.split(':')[1]
