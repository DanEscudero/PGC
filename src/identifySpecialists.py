import sys, csv, json, collections
import pandas as pd
from Node import Node
from util import parse_args, pp_json
from google_trans_new import google_translator

def getRelevantTerms(state):
    filepath = '../out/extraction-short/' + Node.getFileName(state)

    fp = open(filepath)
    lines = fp.readlines()
    fp.close()
    return [x.strip() for x in lines]

def translateTerms(terms):
    translator = google_translator()
    # terms list is interpreted and translated as a single string. That's why, we use eval here :(
    return eval(translator.translate(terms, lang_src='en', lang_tgt='pt'))

def getRelatedTerms(title, terms):
    relevant = []
    for term in terms:
        if not isinstance(title, str):
            continue

        
        term, title = term.lower(), title.lower()
        if term in title:
            relevant.append((term, title))
    
    return relevant

def getRelevantPublicationsFrom(path, relevantTerms):
    data = pd.read_csv(
        path,
        sep='\t',
        header=0,
        names=['id_lattes','titulo','autores'],
        warn_bad_lines=False,
        error_bad_lines=False,
        engine='python'
    )

    data['terms'] = data.apply(lambda x: getRelatedTerms(x['titulo'], relevantTerms), axis=1)
    data = data[data['terms'].map(len) != 0]
    data.reset_index(inplace=True, drop=True)
    return data

def getRelevantPublications(relevantTerms):
    relevant = pd.concat([
        getRelevantPublicationsFrom('../out/base-cv/Publicacoes-cap_livros.tsv', relevantTerms),
        # getRelevantPublicationsFrom('../out/base-cv/Publicacoes-livros.tsv', relevantTerms),
        # getRelevantPublicationsFrom('../out/base-cv/Publicacoes-periodicos.tsv', relevantTerms),
        # getRelevantPublicationsFrom('../out/base-cv/Publicacoes-eventos.tsv', relevantTerms)
    ])
    
    relevant.reset_index(inplace=True, drop=True)

    return relevant


def toFile(publications, filepath):
    f = open(filepath, 'w')
    for (index, publication) in publications.iterrows():
        f.write(str(publication.id_lattes) + '\t' + publication.titulo + '\n')

def getSpecialists(counts, big_area):
    ids = counts.keys()
    researchers_keys = ['id_lattes', 'nome', 'primeira_a']

    researchers = pd.read_csv(
        '../out/base-cv/Info-pesquisadores.tsv', 
        sep='\t',
        header=0,
        names=['id_lattes', 'nome', 'nome_citacoes', 'primeira_ga', 'primeira_a'],
        error_bad_lines=False,
        engine='python'
    )

    specialists = researchers[
        (researchers['id_lattes'].isin(ids))
        & (researchers['primeira_a'] == big_area)
    ][researchers_keys]

    return list(
        map(lambda specialist:
            {
                'nome': specialist['nome'],
                'id_lattes': specialist['id_lattes'],
                'count': counts[specialist['id_lattes']],
            },
            specialists.to_dict('records')
        )
    )


def orderSpecialists(specialists):
    return sorted(specialists, reverse=True, key=lambda x: x['count'])

def dictToTsvFile(data, name):
    f = open(name, 'w')
    output = csv.writer(f)

    output.writerow(data[0].keys())
    for row in data:
        output.writerow(row.values())

def translateArea(big_area):
    f = open('./map.json', 'r')
    d = json.load(f)

    if (big_area in d):
        return d[big_area]
    raise Exception('Invalid big area! Please check map.json to see a list of valid areas.')

def main():
    state = parse_args(sys.argv)
    big_area = state[0]
    big_area = translateArea(big_area)

    relevantTerms = translateTerms(getRelevantTerms(state))

    publications = getRelevantPublications(relevantTerms)
    name = Node.getFileName(state)
    toFile(publications, '../out/specialists/publications/' + name + '.tsv')

    lattes_ids = collections.Counter(list(map(lambda x: x[1].id_lattes, publications.iterrows())))

    specialists = orderSpecialists(getSpecialists(lattes_ids, big_area))

    dictToTsvFile(specialists, '../out/specialists/researchers/' + name + '.tsv')

    print('Specialists saved to:\n', '../out/specialists/researchers/' + name + '.tsv')
    print()
    print('Relevant publications saved to:\n', '../out/specialists/publications/' + name + '.tsv')


if __name__ == "__main__":
    main()
