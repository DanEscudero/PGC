from util import list_subcategories, pp_json


def pretty_print_subcategories(field):
    subcategories = list_subcategories(field)

    print('===================')
    print(str(len(subcategories)) + ' subcategories of ' + field + ':')
    print('===================')

    pp_json(subcategories)


field = 'Mathematics'
pretty_print_subcategories(field)
