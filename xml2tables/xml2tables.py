#!/usr/bin/python3
import xml.etree.ElementTree as ET
import re
import sys
import fileinput
import operator
import locale
import os
import unicodedata
import zipfile
import io

locale.setlocale(locale.LC_ALL, "pt_BR.utf8")

regex = r"[-'a-zA-ZÀ-ÖØ-öø-ÿ0-9][-'a-zA-ZÀ-ÖØ-öø-ÿ0-9]+"   # raw string

xmlDir = "../../tar/"


def remove_accents(input_str):
    nkfd_form = unicodedata.normalize('NFKD', input_str)
    return u"".join([c for c in nkfd_form if not unicodedata.combining(c)])


def agrupaCoautores(lista):
    autores = list()
    for aut in lista:
        aut_nome = aut.get('NOME-PARA-CITACAO').split(";")[0].strip()
        aut_ordem = int(aut.get('ORDEM-DE-AUTORIA'))
        autores.append((aut_nome, aut_ordem))
    autores.sort(key=operator.itemgetter(1))
    nomes = ""
    for (a, _) in autores:
        nomes += a + "; "
    nomes = nomes.rstrip("; ")

    return nomes


def intValidar(ano):
    if ano == None:
        return 0
    else:
        try:
            return int(ano)
        except:
            return 0


def strValidar(objeto, atributo):
    if objeto == None:
        return ""
    else:
        try:
            x = objeto.get(atributo)
            if x == None:
                return ""
            else:
                return x
        except:
            return ""


def getName(root):
    return root.find('DADOS-GERAIS').get('NOME-COMPLETO').replace("\n", " ").replace("\t", " ").strip()


def getCitationNames(root):
    finder = 'DADOS-GERAIS'
    key = 'NOME-EM-CITACOES-BIBLIOGRAFICAS'
    return root.find(finder).get(key).replace("\n", " ").replace("\t", " ").strip()


def getAreas():
    vetorDeGA = 10*[""]
    vetorDeA = 10*[""]

    for areas in root.iter('AREAS-DE-ATUACAO'):
        for area in areas.iter('AREA-DE-ATUACAO'):
            a = strValidar(area, 'NOME-DA-AREA-DO-CONHECIMENTO')
            ga = strValidar(area, 'NOME-GRANDE-AREA-DO-CONHECIMENTO')
            seq = intValidar(strValidar(area, 'SEQUENCIA-AREA-DE-ATUACAO'))-1

            if seq < 10:
                vetorDeA[seq] = a
                vetorDeGA[seq] = ga

    primeiraA = procurarPrimeiro(vetorDeA)
    primeiraGA = procurarPrimeiro(vetorDeGA)

    return (primeiraGA, primeiraA)


def procurarPrimeiro(vetor):
    for v in vetor:
        if v != '':
            return v
    return ""


def getKey(pub, key, finder):
    return strValidar(
        pub.find(finder), key
    ).replace("\n", " ").replace("\t", " ").strip()


def isEventComplete(evento):
    return evento.find('DADOS-BASICOS-DO-TRABALHO').get('NATUREZA') == 'COMPLETO'


def fileIsEmpty(path):
    return os.stat(path).st_size == 0


def scrapBook(livro):
    titulo = getKey(
        livro,
        'TITULO-DO-LIVRO',
        'DADOS-BASICOS-DO-LIVRO'
    )

    autores = agrupaCoautores(livro.findall('AUTORES'))

    return (titulo, autores)


def scrapChapter(capitulo):
    titulo = getKey(
        capitulo,
        'DADOS-BASICOS-DO-CAPITULO',
        'TITULO-DO-CAPITULO-DO-LIVRO'
    )

    tituloLivro = getKey(
        capitulo,
        'TITULO-DO-LIVRO',
        'DETALHAMENTO-DO-CAPITULO'
    )

    autores = agrupaCoautores(capitulo.findall('AUTORES'))

    return (titulo, tituloLivro, autores)


def scrapJournal(jornal):
    titulo = getKey(jornal, 'TITULO-DO-ARTIGO', 'DADOS-BASICOS-DO-ARTIGO')
    autores = agrupaCoautores(jornal.findall('AUTORES'))
    return (titulo, autores)


def scrapEvent(evento):
    titulo = getKey(evento, 'TITULO-DO-TRABALHO', 'DADOS-BASICOS-DO-TRABALHO')
    autores = agrupaCoautores(evento.findall('AUTORES'))
    return (titulo, autores)


def scrapPublications(root, p_periodicos, p_eventos, p_livros, p_cap_livros):
    for jornal in root.iter('ARTIGO-PUBLICADO'):
        p_periodicos[idLattes].append(scrapJournal(jornal))

    for evento in root.iter('TRABALHO-EM-EVENTOS'):
        if isEventComplete(evento):
            p_eventos[idLattes].append(scrapEvent(evento))

    for livro in root.iter('LIVRO-PUBLICADO-OU-ORGANIZADO'):
        p_livros[idLattes].append(scrapBook(livro))

    for capitulo in root.iter('CAPITULO-DE-LIVRO-PUBLICADO'):
        p_cap_livros[idLattes].append(scrapChapter(capitulo))


def scrapResearcher(root, idLattes, dicPesquisadores):
    nome = getName(root)
    nomeEmCitacoes = getCitationNames(root)
    (primeiraGA, primeiraA) = getAreas()

    dicPesquisadores[idLattes] = f'{nome}\t{nomeEmCitacoes}\t{primeiraGA}\t{primeiraA}'


def outputResearchers(path, header, dic):
    def buildLine(idLattes, record):
        return f"{idLattes}\t{record}\n"
    outputToFile(path, header, dic, buildLine)


def outputPublications(path, header, dic):
    def getter(idLattes, record):
        line = "\n".join(
            map(lambda r: f'{idLattes}\t{r}', ['\t'.join(r) for r in record])
        )

        if len(record):
            line = line + "\n"
        return line
    outputToFile(path, header, dic, getter)


def printStatistics(total, success, not_found, bad_format, no_data, key):
    header = f'id\ttotal\tsuccess\tnot_found\tbad_format\tno_data'

    def buildLine(key, value):
        return value

    dic = {
        'data': f'{key}\t{total}\t{success}\t{not_found}\t{bad_format}\t{no_data}\n'
    }
    outputToFile('../out/statisticts.tsv', header, dic, buildLine)


def outputToFile(path, header, dic, buildLine):
    f = open(path, 'a')
    if (header != "" and fileIsEmpty(path)):
        f.write(f"{header}\n")

    for (key, value) in dic.items():
        f.write(buildLine(key, value))

    f.close()


if __name__ == "__main__":
    inFilePessoas = sys.argv[1]  # "listaIDs.txt.mini"

    prefixo = '../out/listagens/'

    Pesquisadores = list([])
    p_periodicos = dict()
    p_eventos = dict()
    p_livros = dict()
    p_cap_livros = dict()

    dicPesquisadores = dict([])

    attempts = 0
    success = 0
    no_data = 0
    not_found = 0
    bad_format = 0

    for linha in fileinput.input(inFilePessoas):
        idLattes = linha.strip()
        if idLattes == "":
            continue
        attempts = attempts + 1

        p_periodicos[idLattes] = list()
        p_eventos[idLattes] = list()
        p_livros[idLattes] = list()
        p_cap_livros[idLattes] = list()

        lastIdLattesDigit = idLattes[-1]
        xml = xmlDir + lastIdLattesDigit + "/" + idLattes + ".zip"
        if not os.path.isfile(xml):
            not_found = not_found + 1
            continue
        try:
            with zipfile.ZipFile(xml) as myzip:
                cv = myzip.open("curriculo.xml").read()
                root = ET.fromstring(cv)
        except:
            bad_format = bad_format + 1
            continue

        if root.get('DATA-ATUALIZACAO') == None:
            no_data = no_data + 1
        else:
            success = success + 1

            scrapResearcher(
                root,
                idLattes,
                dicPesquisadores
            )

            scrapPublications(
                root,
                p_periodicos,
                p_eventos,
                p_livros,
                p_cap_livros
            )

    outputResearchers(
        prefixo + "Info-pesquisadores.tsv",
        "id_lattes\tnome\tnome_citacoes\tprimeira_ga\tprimeira_a",
        dicPesquisadores
    )
    outputPublications(
        prefixo + "Publicacoes-periodicos.tsv",
        "id_lattes\ttitulo\tautores",
        p_periodicos
    )
    outputPublications(
        prefixo + "Publicacoes-eventos.tsv",
        "id_lattes\ttitulo\tautores",
        p_eventos
    )
    outputPublications(
        prefixo + "Publicacoes-livros.tsv",
        "id_lattes\ttitulo\tautores",
        p_livros
    )
    outputPublications(
        prefixo + "Publicacoes-cap_livros.tsv",
        "id_lattes\ttitulo\ttitulo_livro\tautores",
        p_cap_livros
    )

    # printStatistics(
    #     attempts,
    #     success,
    #     not_found,
    #     bad_format,
    #     no_data,
    #     lastIdLattesDigit
    # )

    print("\ndone!")
