import json
import requests
import itertools
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize


def pp_json(json_thing, sort=True, indents=4):
    if type(json_thing) is str:
        print(json.dumps(json.loads(json_thing), sort_keys=sort, indent=indents))
    else:
        print(json.dumps(json_thing, sort_keys=sort, indent=indents))
    return None


def clamp(x, minValue=0, maxValue=1):
    return min(maxValue, max(minValue, x))


def invLerp(minValue, maxValue, x):
    if (minValue == maxValue):
        return 1
    return clamp((x - minValue) / (maxValue - minValue))

# Converts to snake case, with letters in lower case, except for the first one


def format_field(field):
    return field.replace(' ', '_').lower().capitalize()


# Converts 'Category:X' to X
def clear_category_name(name):
    x = name.split(':')
    if (len(x) > 1):
        return x[1]
    else:
        return x[0]


def query_subcategories(field, max):
    params = {
        "action": "query",
        "cmtitle": "Category:" + format_field(field),
        "cmtype": "subcat",
        "list": "categorymembers",
        "format": "json",
        "cmlimit": max
    }

    session = requests.Session()
    return session.get(url='https://en.wikipedia.org/w/api.php', params=params)


def cleanTerm(string):
    # Taken from https://stackabuse.com/removing-stop-words-from-strings-in-python/
    tokens = word_tokenize(string)
    dirty = stopwords.words()
    dirty += ['.', ',', '\'', '!', '?', '-', '(', ')']
    return [(word.lower()) for word in tokens if not word in dirty]


def parse_args(argv):
    argv = argv[1:]
    argc = len(argv)
    if argc == 4:
        queryParameter = argv[0]
        specificParameter = argv[1]
        queryLevel = int(argv[2])
        if (argv[3].isdigit()):
            queryCMLimit = int(argv[3])
        elif (argv[3].lower() == 'max'):
            queryCMLimit = 'max'
        else:
            raise Exception(
                'Invalid max value!. Please use: [0-9]+|\'max\' (limited to 500)')
    else:
        raise Exception('Invalid parameters!')

    return (queryParameter, specificParameter, queryLevel, queryCMLimit)


def list_subcategories(field, max):
    raw_info = query_subcategories(field, max).json()

    return list(
        map(lambda x: clear_category_name(x['title']),  raw_info['query']['categorymembers']))
