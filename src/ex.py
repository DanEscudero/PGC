from dbpedia_sparql_simplify import sparql_query
from dbpedia_sparql_simplify import sparql_util

import sys
import json
import requests
import unicodecsv as csv


def example_search(my_query):
    print("Select the index of the property of {} that you want to find something about:"
          .format(my_query.query_description))
    my_properties = my_query.find_properties()

    if len(my_properties) == 0:
        print('{} has no property. Exporting current results to excel...')
        export_results_to_excel(my_query.run_query(), "results.csv")
        sys.exit(0)

    i = 0
    for my_property in my_properties:
        print('{} - {}'.format(i, my_property['label']))
        i += 1

    selected_property_index = int(input('Selection: '))
    if selected_property_index < 0 or selected_property_index >= len(my_properties):
        print("Selection should've been between {} and {}".format(
            0, len(my_properties) - 1))
        sys.exit(-1)

    my_query.add_property_to_query(my_properties[selected_property_index])

    selected_path = int(input(
        "1 - I want to find the items which have same {0}\n"
        "2 - I want to find something related to {0}\n"
        "3 - I want to see {0}\n"
        "Selection: ".format(my_query.query_description)))

    if selected_path == 1:
        export_results_to_excel(
            my_query.find_objects_with_same_property(), 'results.csv')
    elif selected_path == 2:
        example_search(my_query)
    elif selected_path == 3:
        export_results_to_excel(my_query.run_query(), 'results.csv')
    else:
        print("Your selection should've been between 1 and 3.")
        sys.exit(-1)


def export_results_to_excel(results, output_file_path):
    if results is None:
        return

    data = []

    title = []
    #    title.append(item['label'] + ";")
    for key in results[0]:
        title.append(key + ";")

    data.append(title)

    for binding in results:
        row = []
        for key in binding:
            val_raw = binding[key]['value']
            val = format_value(val_raw)
            row.append(val + ";")
        data.append(row)

    with open(output_file_path, 'wb') as csv_file:
        result_writer = csv.writer(csv_file, dialect='excel-tab')
        result_writer.writerows(data)


def format_value(value):
    trim = False
    if value[0: 5] == 'http:' or value[0: 6] == 'https:':
        trim = True

    if trim:
        split = value.split('/')
        new_value = split[-1:][0]
        new_value = new_value.replace('_', ' ')
        return new_value

    return value


def get_page_info(page_id):
    params = {
        "action": "query",
        "cmtitle": "Category:Topology",
        "cmtype": "subcat",
        "list": "categorymembers",
        "format": "json"
    }

    return requests.Session().get(url='https://en.wikipedia.org/w/api.php', params=params)


def pp_json(json_thing, sort=True, indents=4):
    if type(json_thing) is str:
        print(json.dumps(json.loads(json_thing), sort_keys=sort, indent=indents))
    else:
        print(json.dumps(json_thing, sort_keys=sort, indent=indents))
    return None


def print_query(q):
    print('>>> Query_description   ', q.query_description)
    print('>>> Query               ', q.query)
    print('>>> Item_name_indicator ', q.item_name_indicator)
    print('>>> Resource_list       ', q.resource_list)
    print('>>> Select_list         ', q.select_list)

# my_query = sparql_query.SparqlQuery(
#     input('Enter the name of the object that you want to search: '))
# print('Searching for {}'.format(my_query.query_description))
# example_search(my_query)


# query_term = 'Topology'
# q = sparql_query.SparqlQuery(query_term)

# print('_____________')
# print(query_term)
# print('_____________')
# print('PROPERTIES')
# print('_____________')

# properties_labels = list(map(lambda x: x['label'], q.find_properties()))
# print(properties_labels)

# q.add_property_to_query(q.find_properties()[0])
# # for property in q.find_properties():

# print('_____________')
# print('QUERY')
# print('_____________')
# result = q.run_query()
# print(result)

# result_entry = result[0]
# result_key = list(result_entry.keys())[0]
# page_id = result_entry[result_key]['value']

print('_____________')
print('PAGE INFO')
print('_____________')
info = get_page_info(123)
pp_json(info.json())
