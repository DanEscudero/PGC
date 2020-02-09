import requests

from util import format_field, pp_json, clear_category_name


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


def pretty_print_subcategories(field):
    subcategories = list_subcategories(field)

    print('===================')
    print(str(len(subcategories)) + ' subcategories of ' + field + ':')
    print('===================')

    pp_json(subcategories)


def recursive_subcategories(field, parent, accumulated, level):
    if (level == 0):
        # if (not (parent in accumulated)):
        #     accumulated[parent] = []

        # return accumulated[parent] = accumulated[parent] + [field]
        return accumulated + [(parent, field)]
        return accumulated + [field]

    subs = []
    subcategories = list_subcategories(field)
    for subcategory in subcategories:
        subs += recursive_subcategories(subcategory,
                                        field, accumulated, level-1)

    return accumulated + subs


list = recursive_subcategories(
    'Mathematics', '', [], 2)
pp_json(list)
print('Number of Results:', len(list))

# pretty_print_subcategories('Subfields of Computer Science')
