from dbpedia_sparql_simplify import sparql_query
import sys
import unicodecsv as csv


def example_search(my_query):
    print("Select the index of the property of {} that you want to find something about:"
          .format(my_query.query_description))
    my_properties = my_query.find_properties()

    if len(my_properties) == 0:
        print('{} has no property. Exporting current results to excel...')
        export_results_to_excel(my_query.run_query(),"results.csv")
        sys.exit(0)

    i = 0
    for my_property in my_properties:
        print('{} - {}'.format(i, my_property['label']))
        i += 1

    selected_property_index = int(input('Selection: '))
    if selected_property_index < 0 or selected_property_index >= len(my_properties):
        print("Selection should've been between {} and {}".format(0, len(my_properties) - 1))
        sys.exit(-1)

    my_query.add_property_to_query(my_properties[selected_property_index])

    selected_path = int(input(
        "1 - I want to find the items which have same {0}\n"
        "2 - I want to find something related to {0}\n"
        "3 - I want to see {0}\n"
        "Selection: ".format(my_query.query_description)))

    if selected_path == 1:
        export_results_to_excel(my_query.find_objects_with_same_property(), 'results.csv')
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
        row=[]
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


my_query = sparql_query.SparqlQuery(input('Enter the name of the object that you want to search: '))
print('Searching for {}'.format(my_query.query_description))
example_search(my_query)

