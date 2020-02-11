import json
import requests


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


# TODO: think about piping fields, in order to save request.
# https://www.mediawiki.org/wiki/API:Etiquette#Request_limit
# Could speed execution up to 10 times (?)
def query_subcategories(field):
    params = {
        "action": "query",
        "cmtitle": "Category:" + format_field(field),
        "cmtype": "subcat",
        "list": "categorymembers",
        "format": "json"
    }

    session = requests.Session()
    return session.get(url='https://en.wikipedia.org/w/api.php', params=params)


def list_subcategories(field):
    raw_info = query_subcategories(field).json()

    return list(
        map(lambda x: clear_category_name(x['title']),  raw_info['query']['categorymembers']))
