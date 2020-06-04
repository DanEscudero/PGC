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

##############################################################################################
xmlDir = "../tar/"

##############################################################################################
Termos    = list()
dicTermos = dict()

#########################################################################################
def remove_accents(input_str):
    nkfd_form = unicodedata.normalize('NFKD', input_str)
    return u"".join([c for c in nkfd_form if not unicodedata.combining(c)])

#########################################################################################
def filtrarPublicacao(titulo, pChave=[]):
    if len(Termos)==0:
        return (True, "")

    freq = [0]*len(Termos)

    texto = titulo
    for ppp in pChave:
        texto = texto + " " + ppp
    texto = remove_accents(texto)

    for (iTermo, Termo) in enumerate(Termos):
        numeroDePartesAchadas = 0 

        for parteT in dicTermos[Termo]:
            if "*" in parteT:
                parteT = parteT.strip("*")
                if re.search(r"\b" + parteT, texto, re.IGNORECASE):
                    numeroDePartesAchadas += 1 
            else:
                if re.search(r"\b" + parteT + r"\b", texto, re.IGNORECASE):
                    numeroDePartesAchadas += 1 

        if numeroDePartesAchadas == len(dicTermos[Termo]): # se todas as partes termos achado
            freq[iTermo] += 1
            
    if sum(freq)>=1:
        freq = "\t".join(str(i) for i in freq)
        return (True, freq)    # freq = "1 2 0 0 0 0 1" # do tamanho da lista de termos
    else:
        return (False, "")


##############################################################################################
def agrupaCoautores(lista):
    autores = list()
    for aut in lista:
        aut_nome  = aut.get('NOME-PARA-CITACAO').split(";")[0].strip()
        aut_ordem = int(aut.get('ORDEM-DE-AUTORIA'))
        autores.append( (aut_nome, aut_ordem) )
    autores.sort(key=operator.itemgetter(1))
    nomes = ""
    for (a,b) in autores:
        nomes += a + "; "
    nomes = nomes.rstrip("; ")

    return nomes

#########################################################################################
def intValidar(ano):
    if ano==None:
        return 0
    else:
        try:
            return int(ano)
        except:
            return 0

#########################################################################################
def strValidar(objeto, atributo):
    if objeto==None:
        return ""
    else:
        try:
            x = objeto.get(atributo)
            if x==None:
                return ""
            else:
                return x
        except:
            return ""

#########################################################################################
def procurarPrimeiro(vetor):
    for v in vetor:
        if v!='':
            return v
    return ""

# ---------------------------------------------------------
if __name__ == "__main__":
    inFilePessoas   = sys.argv[1]  # "listaIDs.txt.mini"

    if len(sys.argv)>2: # Leitura de termos (um por linha, veja exemplo)
        inFileTermos    = sys.argv[2]  

        for linha in fileinput.input(inFileTermos):
            t = linha.strip()
            if len(t)>0:
                Termos.append( t )
 
                nt = remove_accents(t) #unicodedata.normalize('NFKD', t)
                partes = nt.split(" AND ")
                partes = [x.strip(' ').lower() for x in partes]  # tiramos os esp
                dicTermos[t] = partes
        
        print ("TERMOS CONSIDERADOS PELA BUSCA:")
        for (i,_t) in enumerate(Termos):
            print(f"{i}\t{_t:40s}\t{dicTermos[_t]}")

    prefixo = inFilePessoas[:-4]
    prefixo = '../out/listagens/'

    ou_caracteristicas= prefixo + "Tabela-consolidada.csv"

    ou_periodico      = prefixo + "Publicacoes-periodicos.csv"
    ou_eventos        = prefixo + "Publicacoes-eventos.csv"
    ou_livros         = prefixo + "Publicacoes-livros.csv"
    ou_cap_livros     = prefixo + "Publicacoes-cap_livros.csv"
    
    ##########################################################################################
    # Leitura das pessoas
    ##########################################################################################
    Pesquisadores = list([])
    P_periodicos = dict()
    P_eventos    = dict()
    P_livros     = dict()
    P_cap_livros = dict()

    dicPesquisadores = dict([])
    dicFormacoes     = dict([])
    dicAtuacoes      = dict([])

    O_posdoutorado   = dict()
    O_doutorado      = dict()
    O_mestrado       = dict()
    O_tcc            = dict()
    O_ic             = dict()
    O_outra          = dict()  ## nao tem especializacao nos CVs Lattes para orientados?

    attempt         = 0
    success         = 0
    not_found       = 0
    bad_format      = 0
    disconsiderated = 0

    for linha in fileinput.input(inFilePessoas):
        idLattes = linha.strip()
        if idLattes=="":
            continue
        print ("PROCESSANDO >>->>", idLattes)
        attempt = attempt + 1

        #####################################################################################
        # Variáveis importantes
        #####################################################################################
        Pesquisadores.append(idLattes)
        P_periodicos[idLattes]      = list()
        P_eventos[idLattes]         = list()
        P_livros[idLattes]          = list()
        P_cap_livros[idLattes]      = list()

        O_posdoutorado[idLattes]    = list()
        O_doutorado[idLattes]       = list()
        O_mestrado[idLattes]        = list()
        O_tcc[idLattes]             = list()
        O_ic[idLattes]              = list()
        O_outra[idLattes]           = list()

        dicFormacoes[idLattes]      = dict()
        dicFormacoes[idLattes]["E"] = list()
        dicFormacoes[idLattes]["G"] = list()
        dicFormacoes[idLattes]["M"] = list()
        dicFormacoes[idLattes]["D"] = list()
        dicFormacoes[idLattes]["P"] = list()

        dicAtuacoes[idLattes]       = list()

        #####################################################################################
        xml = xmlDir + idLattes[-1] +"/"+ idLattes + ".zip" 
        if not os.path.isfile(xml):
            not_found = not_found + 1
            print ("[ERRO] CV nao existe no diretorio base:", idLattes)
            dicPesquisadores[idLattes] = f"'{idLattes}\tCV-NAO-FOI-COLETADO-DA-PLATAFORMA-LATTES"
            continue
        try:
            with zipfile.ZipFile(xml) as myzip:
                cv   = myzip.open("curriculo.xml").read()
                root = ET.fromstring(cv)
        except:
            bad_format = bad_format + 1
            print ("[ERRO] CV com problema com no seu formato/conteúdo:", idLattes)
            dicPesquisadores[idLattes] = f"'{idLattes}\tCV-COM-PROBLEMA-NO-SEU-FORMATO/CONTEÚDO"
            continue
            
        dataCV   = root.get('DATA-ATUALIZACAO')

        if dataCV==None:
            disconsiderated = disconsiderated + 1
            print ("[ERRO] CV desconsiderado por nao ter dados:", idLattes)
            dicPesquisadores[idLattes] = f"'{idLattes}\tCV-COM-PROBLEMA-NO-SEU-FORMATO/CONTEÚDO"
        else:
            success = success + 1
            nome              = root.find('DADOS-GERAIS').get('NOME-COMPLETO').replace("\n"," ").replace("\t"," ").strip()
            nomeEmCitacoes    = root.find('DADOS-GERAIS').get('NOME-EM-CITACOES-BIBLIOGRAFICAS').replace("\n"," ").replace("\t"," ").strip()
            paisNacimento     = root.find('DADOS-GERAIS').get('PAIS-DE-NASCIMENTO')
            paisNacionalidade = root.find('DADOS-GERAIS').get('PAIS-DE-NACIONALIDADE')

            #####################################################################################
            # ENDEREÇO PROFISSIONAL
            #####################################################################################
            ep_Instituicao = ""
            ep_Orgao = ""
            ep_Unidade = ""
            ep_Pais = ""
            ep_UF = ""
            ep_Cidade = ""

            #####################################################################################
            # PRIMEIRA GRANDE ÁREA  && PRIMEIRA ÁREA
            #####################################################################################
            vetorDeGA = 10*[""]
            vetorDeA  = 10*[""]

            for areas in root.iter('AREAS-DE-ATUACAO'):
                for area in areas.iter('AREA-DE-ATUACAO'):
                    ga  = strValidar(area, 'NOME-GRANDE-AREA-DO-CONHECIMENTO')
                    a   = strValidar(area, 'NOME-DA-AREA-DO-CONHECIMENTO')
                    seq = intValidar(strValidar(area, 'SEQUENCIA-AREA-DE-ATUACAO'))-1

                    #print (ga, a, seq)
                    if seq<10:
                        vetorDeGA[seq] = ga
                        vetorDeA[seq]  = a

            primeiraGA = procurarPrimeiro(vetorDeGA)
            primeiraA  = procurarPrimeiro(vetorDeA)

            #####################################################################################
            # COLETANDO AS INFORMACOES DE PUBLICACOES
            #####################################################################################
            f0 = f'\'{idLattes}\t{nome}\t\'{dataCV}\t{paisNacimento}\t{paisNacionalidade}\t{nomeEmCitacoes}\t{len(dicFormacoes[idLattes]["E"])}\t{len(dicFormacoes[idLattes]["G"])}\t{len(dicFormacoes[idLattes]["M"])}\t{len(dicFormacoes[idLattes]["D"])}\t{len(dicFormacoes[idLattes]["P"])}\t{ep_Instituicao}\t{ep_Orgao}\t{ep_Unidade}\t{ep_Pais}\t{ep_UF}\t{ep_Cidade}\t{primeiraGA}\t{primeiraA}'
            dicPesquisadores[idLattes] = f0

            #####################################################################################
            # PUBLICACÕES EM PERIÓDICOS
            #####################################################################################

            for jornal in root.iter('ARTIGO-PUBLICADO'):
                titulo    = strValidar(jornal.find('DADOS-BASICOS-DO-ARTIGO'), 'TITULO-DO-ARTIGO').replace("\n"," ").replace("\t"," ").strip()
                ano       = intValidar(jornal.find('DADOS-BASICOS-DO-ARTIGO').get('ANO-DO-ARTIGO'))
                doi       = strValidar(jornal.find('DADOS-BASICOS-DO-ARTIGO'), 'DOI')
                veiculo   = strValidar(jornal.find('DETALHAMENTO-DO-ARTIGO'), 'TITULO-DO-PERIODICO-OU-REVISTA').replace("\n"," ").replace("\t"," ").strip()
                issn      = strValidar(jornal.find('DETALHAMENTO-DO-ARTIGO'), 'ISSN').strip()
                volume    = strValidar(jornal.find('DETALHAMENTO-DO-ARTIGO'), 'VOLUME').strip()
                fasciculo = strValidar(jornal.find('DETALHAMENTO-DO-ARTIGO'), 'FASCICULO').strip()
                serie     = strValidar(jornal.find('DETALHAMENTO-DO-ARTIGO'), 'SERIE').strip()
                pinicial  = strValidar(jornal.find('DETALHAMENTO-DO-ARTIGO'), 'PAGINA-INICIAL').strip()
                pfinal    = strValidar(jornal.find('DETALHAMENTO-DO-ARTIGO'), 'PAGINA-FINAL').strip()
                autores  = agrupaCoautores(jornal.findall('AUTORES'))

                pChave = []
                if jornal.find('PALAVRAS-CHAVE') != None:
                    for numPalavraChave in ["1", "2", "3", "4", "5", "6"]:
                        ppp = strValidar(jornal.find('PALAVRAS-CHAVE'),"PALAVRA-CHAVE-" + numPalavraChave).strip()
                        if ppp!="":
                            pChave.append(ppp)

                (inserir, frequencias) = filtrarPublicacao(titulo, pChave)

                if inserir:
                    pChave = str(pChave)
                    P_periodicos[idLattes].append( (titulo, str(ano), doi, veiculo, issn, volume, fasciculo, serie, pinicial, pfinal, pChave, autores, str(len(autores.split(";"))), frequencias ) )

            #####################################################################################
            # PUBLICACÕES EM EVENTOS - COMPLETO
            #####################################################################################
            for evento in root.iter('TRABALHO-EM-EVENTOS'):
                if evento.find('DADOS-BASICOS-DO-TRABALHO').get('NATUREZA') == 'COMPLETO':
                    titulo    = strValidar(evento.find('DADOS-BASICOS-DO-TRABALHO'), 'TITULO-DO-TRABALHO').replace("\n"," ").replace("\t"," ").strip()
                    ano       = intValidar(evento.find('DADOS-BASICOS-DO-TRABALHO').get('ANO-DO-TRABALHO'))
                    doi       = strValidar(evento.find('DADOS-BASICOS-DO-TRABALHO'), 'DOI')
                    veiculo   = strValidar(evento.find('DETALHAMENTO-DO-TRABALHO'), 'NOME-DO-EVENTO').replace("\n"," ").replace("\t"," ").strip()
                    isbn      = strValidar(evento.find('DETALHAMENTO-DO-TRABALHO'), 'ISBN').strip()
                    volume    = strValidar(evento.find('DETALHAMENTO-DO-TRABALHO'), 'VOLUME').strip()
                    fasciculo = strValidar(evento.find('DETALHAMENTO-DO-TRABALHO'), 'FASCICULO').strip()
                    serie     = strValidar(evento.find('DETALHAMENTO-DO-TRABALHO'), 'SERIE').strip()
                    pinicial  = strValidar(evento.find('DETALHAMENTO-DO-TRABALHO'), 'PAGINA-INICIAL').strip()
                    pfinal    = strValidar(evento.find('DETALHAMENTO-DO-TRABALHO'), 'PAGINA-FINAL').strip()
                    autores   = agrupaCoautores(evento.findall('AUTORES'))

                    pChave = []
                    if evento.find('PALAVRAS-CHAVE') != None:
                        for numPalavraChave in ["1", "2", "3", "4", "5", "6"]:
                            ppp = strValidar(evento.find('PALAVRAS-CHAVE'), "PALAVRA-CHAVE-" + numPalavraChave).strip()
                            if ppp!="":
                                pChave.append(ppp)
                 
                    (inserir, frequencias) = filtrarPublicacao(titulo, pChave)

                    if inserir:
                        pChave = str(pChave)
                        P_eventos[idLattes].append( (titulo, str(ano), doi, veiculo, isbn, volume, fasciculo, serie, pinicial, pfinal, pChave, autores, str(len(autores.split(";"))), frequencias ) )
                     
        
            #####################################################################################
            # PUBLICACÕES EM LIVROS
            #####################################################################################
            for livro in root.iter('LIVRO-PUBLICADO-OU-ORGANIZADO'):
                titulo    = strValidar(livro.find('DADOS-BASICOS-DO-LIVRO'), 'TITULO-DO-LIVRO').replace("\n"," ").replace("\t"," ").strip()
                ano       = intValidar(livro.find('DADOS-BASICOS-DO-LIVRO').get('ANO'))
                tipo      = strValidar(livro.find('DADOS-BASICOS-DO-LIVRO'), 'TIPO').strip()
                natureza  = strValidar(livro.find('DADOS-BASICOS-DO-LIVRO'), 'NATUREZA').strip()
                volumes   = strValidar(livro.find('DETALHAMENTO-DO-LIVRO'), 'NUMERO-DE-VOLUMES').strip()
                paginas   = strValidar(livro.find('DETALHAMENTO-DO-LIVRO'), 'NUMERO-DE-PAGINAS').strip()
                isbn      = strValidar(livro.find('DETALHAMENTO-DO-LIVRO'), 'ISBN').strip()
                edicao    = strValidar(livro.find('DETALHAMENTO-DO-LIVRO'), 'NUMERO-DA-EDICAO-REVISAO').strip()
                serie     = strValidar(livro.find('DETALHAMENTO-DO-LIVRO'), 'NUMERO-DA-SERIE').strip()
                editora   = strValidar(livro.find('DETALHAMENTO-DO-LIVRO'), 'NOME-DA-EDITORA').replace("\n"," ").replace("\t"," ").strip()
                autores   = agrupaCoautores(livro.findall('AUTORES'))

                pChave = []
                if livro.find('PALAVRAS-CHAVE') != None:
                    for numPalavraChave in ["1", "2", "3", "4", "5", "6"]:
                        ppp = strValidar(livro.find('PALAVRAS-CHAVE'), "PALAVRA-CHAVE-" + numPalavraChave).strip()
                        if ppp!="":
                            pChave.append(ppp)
                
                (inserir, frequencias) = filtrarPublicacao(titulo, pChave)

                if inserir:
                    pChave = str(pChave)
                    P_livros[idLattes].append( (titulo, str(ano), tipo, natureza, volumes, paginas, isbn, edicao, serie, editora, pChave, autores, str(len(autores.split(";"))), frequencias ) )


            #####################################################################################
            # PUBLICACÕES EM CAPÍTULOS DE LIVRO
            #####################################################################################
            for capitulo in root.iter('CAPITULO-DE-LIVRO-PUBLICADO'):
                titulo      = strValidar(capitulo.find('DADOS-BASICOS-DO-CAPITULO'), 'TITULO-DO-CAPITULO-DO-LIVRO').replace("\n"," ").replace("\t"," ").strip()
                ano         = intValidar(capitulo.find('DADOS-BASICOS-DO-CAPITULO').get('ANO'))
                tipo        = strValidar(capitulo.find('DADOS-BASICOS-DO-CAPITULO'), 'TIPO').strip()
                tituloLivro = strValidar(capitulo.find('DETALHAMENTO-DO-CAPITULO'), 'TITULO-DO-LIVRO').replace("\n"," ").replace("\t"," ").strip()
                pagina1     = strValidar(capitulo.find('DETALHAMENTO-DO-CAPITULO'), 'PAGINA-INICIAL').strip()
                pagina2     = strValidar(capitulo.find('DETALHAMENTO-DO-CAPITULO'), 'PAGINA-FINAL').strip()
                isbn        = strValidar(capitulo.find('DETALHAMENTO-DO-CAPITULO'), 'ISBN').strip()
                editora     = strValidar(capitulo.find('DETALHAMENTO-DO-CAPITULO'), 'NOME-DA-EDITORA').replace("\n"," ").replace("\t"," ").strip()
                autores     = agrupaCoautores(capitulo.findall('AUTORES'))

                pChave = []
                if capitulo.find('PALAVRAS-CHAVE') != None:
                    for numPalavraChave in ["1", "2", "3", "4", "5", "6"]:
                        ppp = strValidar(capitulo.find('PALAVRAS-CHAVE'), "PALAVRA-CHAVE-" + numPalavraChave).strip()
                        if ppp!="":
                            pChave.append(ppp)

                (inserir, frequencias) = filtrarPublicacao(titulo, pChave)

                if inserir:
                    pChave = str(pChave)
                    P_cap_livros[idLattes].append( (titulo, str(ano), tipo, tituloLivro, pagina1, pagina2, isbn, editora, pChave, autores, str(len(autores.split(";"))), frequencias ) )

    #######################################################################3
    # Nota: Estará na base se PELO MENOS uma publicação (dos 4 tipos) tenha sido identificada
    #######################################################################3
    Pesquisadores_na_base = list()
    if len(Termos)==0:
        for idLattes in Pesquisadores:
            Pesquisadores_na_base.append(idLattes)
    else:
        for idLattes in Pesquisadores:
            if len(P_periodicos[idLattes]) + len(P_eventos[idLattes]) + len(P_livros[idLattes]) + len(P_cap_livros[idLattes]):
                Pesquisadores_na_base.append(idLattes)

    #######################################################################3
    # SALVANDO AS PUBLICAÇÕES
    #######################################################################3
    cabecalho_termos = "\t".join(Termos)

    f = open(ou_periodico, 'a')
    f.write( f"ID-Lattes\tTítulo\tAno\tDOI\tVeículo\tISSN\tVolume\tFascículo\tSerie\tP-inicial\tP-final\tPalavras-chave\tAutores\tQuantidade-autores\t{cabecalho_termos}" )
    for idLattes in Pesquisadores:
        if idLattes in Pesquisadores_na_base and len(P_periodicos[idLattes])>0:
            for pub in P_periodicos[idLattes]:
                f.write( f"\n{idLattes}\t" + "\t".join( pub ) )
    f.write("\n")
    f.close()


    f = open(ou_eventos, 'a')
    f.write( f"ID-Lattes\tTítulo\tAno\tDOI\tVeículo\tISBN\tVolume\tFascículo\tSerie\tP-inicial\tP-final\tPalavras-chave\tAutores\tQuantidade-autores\t{cabecalho_termos}" )
    for idLattes in Pesquisadores:
        if idLattes in Pesquisadores_na_base and len(P_eventos[idLattes])>0:
            for pub in P_eventos[idLattes]:
                f.write( f"\n{idLattes}\t" + "\t".join( pub ) )
    f.write("\n")
    f.close()


    f = open(ou_livros, 'a')
    f.write( f"ID-Lattes\tTítulo\tAno\tTipo\tNatureza\tVolumes\tPáginas\tISBN\tEdição\tSérie\tEditora\tPalavras-chave\tAutores\tQuantidade-autores\t{cabecalho_termos}" )
    for idLattes in Pesquisadores:
        if idLattes in Pesquisadores_na_base and len(P_livros[idLattes])>0:
            for pub in P_livros[idLattes]:
                f.write( f"\n{idLattes}\t" + "\t".join( pub ) )
    f.write("\n")
    f.close()


    f = open(ou_cap_livros, 'a')
    f.write( f"ID-Lattes\tTítulo\tAno\tTipo\tTítulo-do-livro\tP-inicial\tP-final\tISBN\tEditora\tPalavras-chave\tAutores\tQuantidade-autores\t{cabecalho_termos}" )
    for idLattes in Pesquisadores:
        if idLattes in Pesquisadores_na_base and len(P_cap_livros[idLattes])>0:
            for pub in P_cap_livros[idLattes]:
                f.write( f"\n{idLattes}\t" + "\t".join( pub ) )
    f.write("\n")
    f.close()

    counts = "attempt > " + str(attempt) + "\n"
    counts = counts + 'success > ' + str(success) + '\n'
    counts = counts + 'not_found > ' + str(not_found) + '\n'
    counts = counts + 'bad_format > ' + str(bad_format) + '\n'
    counts = counts + 'disconsiderated > ' + str(disconsiderated) + '\n'
    
    f = open('../out/statisticts.txt', 'a')
    f.write(counts)

    #######################################################################3
    print("\ndone!")
    #######################################################################3
