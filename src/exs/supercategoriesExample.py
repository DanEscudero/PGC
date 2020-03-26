from util import list_supercategories, pp_json, clear_category_name


def pretty_print_supercategories(field):
    items = list(list_supercategories(field)['query']['pages'].values())
    items.sort(reverse=True, key=lambda x: x['length'])
    subs = list(map(lambda x: clear_category_name(x['title']), items))
    pp_json(subs)


field = 'Algebra'
pretty_print_supercategories(field)
