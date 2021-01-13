import sys
import math
import collections
import pandas as pd
from Node import Node
from util import parse_args
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
        f.write(str(publication.id_lattes) + '\t' + publication.titulo)


def main():
    state = parse_args(sys.argv)
    relevantTerms = getRelevantTerms(state)
    relevantTerms = translateTerms(relevantTerms)

    publications = getRelevantPublications(relevantTerms)

    name = Node.getFileName(state)
    toFile(publications, '../out/specialists/' + name + '.tsv')
    ids = collections.Counter(list(map(lambda x: x[1].id_lattes, publications.iterrows())))
    print(ids)

if __name__ == "__main__":
    main()
