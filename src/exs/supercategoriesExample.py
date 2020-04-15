import requests
from util import pp_json, clear_category_name, format_field, list_subcategories


def query_supercategories(field):
    params = {
        "action": "query",
        "generator": "categorymembers",
        "gcmtitle": "Category:" + format_field(field),
        "prop": "info",
        "format": "json",
    }

    session = requests.Session()
    return session.get(url='https://en.wikipedia.org/w/api.php', params=params)


def list_supercategories(field):
    return query_supercategories(field).json()


def pretty_print_supercategories(field):
    items = list(list_supercategories(field)['query']['pages'].values())
    items.sort(reverse=True, key=lambda x: x['length'])
    subs = list(map(lambda x: clear_category_name(x['title']), items))
    pp_json(subs)


field = 'Mathematics'
pretty_print_supercategories(field)
pp_json(list_subcategories(field))
