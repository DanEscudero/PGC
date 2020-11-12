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


def getKey(pub, key, finder='DADOS-BASICOS-DO-ARTIGO'):
    return strValidar(
        pub.find(finder), key
    ).replace("\n", " ").replace("\t", " ").strip()


def isEventComplete(evento):
    return evento.find('DADOS-BASICOS-DO-TRABALHO').get('NATUREZA') == 'COMPLETO'


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


def scrapPublications(root, P_periodicos, P_eventos, P_livros, P_cap_livros):
    for jornal in root.iter('ARTIGO-PUBLICADO'):
        P_periodicos[idLattes].append(scrapJournal(jornal))

    for evento in root.iter('TRABALHO-EM-EVENTOS'):
        if isEventComplete(evento):
            P_eventos[idLattes].append(scrapEvent(evento))

    for livro in root.iter('LIVRO-PUBLICADO-OU-ORGANIZADO'):
        P_livros[idLattes].append(scrapBook(livro))

    for capitulo in root.iter('CAPITULO-DE-LIVRO-PUBLICADO'):
        P_cap_livros[idLattes].append(scrapChapter(capitulo))


def scrapResearcher(root, idLattes, dicPesquisadores):
    nome = getName(root)
    nomeEmCitacoes = getCitationNames(root)
    (primeiraGA, primeiraA) = getAreas()

    dicPesquisadores[idLattes] = f'\t{nome}\t{nomeEmCitacoes}\t{primeiraGA}\t{primeiraA}'


def outputResearchers(path, header, dic):
    def getter(idLattes, record):
        return f"{idLattes}\t{record}\n"
    outputToFile(path, header, dic, getter)


def outputPublications(path, header, dic):
    def getter(idLattes, record):
        return f"{idLattes}\t" + "\t".join(record) + "\n"
    outputToFile(path, header, dic, getter)


def outputToFile(path, header, dic, getter):
    f = open(path, 'w')
    f.write(f"{header}\n")
    for (idLattes, record) in dic.items():
        line = getter(idLattes, record)
        f.write(line)
    f.close()


def printStatistics(attempt, success, not_found, bad_format, no_data):
    counts = "attempt > " + str(attempt) + "\n"
    counts = counts + 'success > ' + str(success) + '\n'
    counts = counts + 'not_found > ' + str(not_found) + '\n'
    counts = counts + 'bad_format > ' + str(bad_format) + '\n'
    counts = counts + 'no_data > ' + str(no_data) + '\n'

    f = open('../out/statisticts.txt', 'a')
    f.write(counts)
    f.close()


if __name__ == "__main__":
    inFilePessoas = sys.argv[1]  # "listaIDs.txt.mini"

    prefixo = '../out/listagens/'

    Pesquisadores = list([])
    P_periodicos = dict()
    P_eventos = dict()
    P_livros = dict()
    P_cap_livros = dict()

    dicPesquisadores = dict([])

    attempt = 0
    success = 0
    no_data = 0
    not_found = 0
    bad_format = 0

    for linha in fileinput.input(inFilePessoas):
        idLattes = linha.strip()
        if idLattes == "":
            continue
        print("PROCESSANDO >>->>", idLattes)
        attempt = attempt + 1

        P_periodicos[idLattes] = list()
        P_eventos[idLattes] = list()
        P_livros[idLattes] = list()
        P_cap_livros[idLattes] = list()

        xml = xmlDir + idLattes[-1] + "/" + idLattes + ".zip"
        if not os.path.isfile(xml):
            not_found = not_found + 1
            # dicPesquisadores[idLattes] = f"CV-COM-PROBLEMA-NO-SEU-FORMATO/CONTEÚDO"
            print("[ERRO] CV nao existe no diretorio base:", idLattes)
            continue
        try:
            with zipfile.ZipFile(xml) as myzip:
                cv = myzip.open("curriculo.xml").read()
                root = ET.fromstring(cv)
        except:
            bad_format = bad_format + 1
            # dicPesquisadores[idLattes] = f"CV-COM-PROBLEMA-NO-SEU-FORMATO/CONTEÚDO"
            print("[ERRO] CV com problema com no seu formato/conteúdo:", idLattes)
            continue

        if root.get('DATA-ATUALIZACAO') == None:
            no_data = no_data + 1
            # dicPesquisadores[idLattes] = f"CV-COM-PROBLEMA-NO-SEU-FORMATO/CONTEÚDO"
            print("[ERRO] CV desconsiderado por nao ter dados:", idLattes)
        else:
            success = success + 1

            scrapResearcher(
                root,
                idLattes,
                dicPesquisadores
            )

            scrapPublications(
                root,
                P_periodicos,
                P_eventos,
                P_livros,
                P_cap_livros
            )

    outputResearchers(
        prefixo + "Info-pesquisadores.csv",
        "id_lattes\tnome\tnome_citacoes\tprimeira_ga\tprimeira_a",
        dicPesquisadores
    )

    # outputPublications(
    #     prefixo + "Publicacoes-periodicos.csv",
    #     "id_lattes\ttitulo\tautores",
    #     P_periodicos
    # )
    # outputPublications(
    #     prefixo + "Publicacoes-eventos.csv",
    #     "id_lattes\ttitulo\tautores",
    #     P_eventos
    # )
    # outputPublications(
    #     prefixo + "Publicacoes-livros.csv",
    #     "id_lattes\ttitulo\tautores",
    #     P_livros
    # )
    # outputPublications(
    #     prefixo + "Publicacoes-cap_livros.csv",
    #     "id_lattes\ttitulo\ttitulo_livro\tautores",
    #     P_cap_livros
    # )

    printStatistics(attempt, success, not_found, bad_format, no_data)

    print("\ndone!")
