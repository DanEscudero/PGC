#!/usr/bin/python3
import xml.etree.ElementTree as ET
import re 
import sys
import fileinput
import operator
import locale
import os
#import unicodedata
locale.setlocale(locale.LC_ALL, "pt_BR.utf8")

regex = r"[-'a-zA-ZÀ-ÖØ-öø-ÿ0-9][-'a-zA-ZÀ-ÖØ-öø-ÿ0-9]+"   # raw string

##############################################################################################
xmlDir = "./XMLs/"
##############################################################################################

##############################################################################################

## Os nomes dos coautores nao sao considerados
##############################################
def agrupaCoautores(lista):
    autores = list()
    for aut in lista: #jornal.findall('AUTORES'): 
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
def salvarArquivo(ouFile, s):
    arquivo = open(ouFile, 'w')
    arquivo.write(s)  # .encode('utf8'))
    arquivo.close()

#########################################################################################
def remove_accents(input_str):
    nkfd_form = unicodedata.normalize('NFKD', input_str)
    return u"".join([c for c in nkfd_form if not unicodedata.combining(c)])

#########################################################################################
def filtrarPublicacao(titulo, pChave):
    freq = [0]*len(Termos)
    resp = False

    texto = titulo
    for ppp in pChave:
        texto = texto + " " + ppp
    texto = remove_accents(texto)

    #print ("*******************************")
    #print (titulo)
    #print (texto)
    for (iTermo, Termo) in enumerate(Termos):
        numeroDePartesAchadas =0 

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
            #print (">>>>>>>::::::", Termo)
            
    if sum(freq)>=1:
        freq = "\t".join(str(i) for i in freq)
        resp = True

    ## resp = True / False
    ## freq = "1 2 0 0 0 0 1" # do tamanho da lista de termos
    return (resp, freq)

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

    prefixo = inFilePessoas[:-4]
    ou_caracteristicas= prefixo + "---Tabela-consolidada.csv"

    ou_atuacoes       = prefixo + "---Atuacoes-profissionais.csv"
    ou_formacoes      = prefixo + "---Formacoes-academicas.csv"

    ou_periodico      = prefixo + "---Publicacoes-periodicos.csv"
    ou_eventos        = prefixo + "---Publicacoes-eventos.csv"
    ou_livros         = prefixo + "---Publicacoes-livros.csv"
    ou_cap_livros     = prefixo + "---Publicacoes-cap_livros.csv"

    ou_posdoutorado   = prefixo + "---Orientacoes-posdoutorado.csv"
    ou_doutorado      = prefixo + "---Orientacoes-doutorado.csv"
    ou_mestrado       = prefixo + "---Orientacoes-mestrado.csv"
    ou_tcc            = prefixo + "---Orientacoes-tcc.csv"
    ou_ic             = prefixo + "---Orientacoes-ic.csv"
    ou_outra          = prefixo + "---Orientacoes-outranatureza.csv"

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


    for linha in fileinput.input(inFilePessoas):
        idLattes = linha.strip()
        if idLattes=="":
            continue
        print ("\n\n>>->>", idLattes)

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
        xml      = xmlDir +"/"+ idLattes + ".xml"      
        if not os.path.isfile(xml):
            print ("[ERRO] CV nao existe no diretorio base:", idLattes)
            dicPesquisadores[idLattes] = f"{idLattes}\tCV-NAO-FOI-COLETADO-DA-PLATAFORMA-LATTES"
            continue
        try:
            root     = ET.parse(xml).getroot()
        except:
            print ("[ERRO] CV com problema com no seu formato/conteúdo:", idLattes)
            dicPesquisadores[idLattes] = f"{idLattes}\tCV-COM-PROBLEMA-NO-SEU-FORMATO/CONTEÚDO"
            continue
            
        dataCV   = root.get('DATA-ATUALIZACAO')

        if dataCV==None:
            print ("[ERRO] CV desconsiderado por nao ter dados:", idLattes)
            dicPesquisadores[idLattes] = f"{idLattes}\tCV-COM-PROBLEMA-NO-SEU-FORMATO/CONTEÚDO"
        else:
            nome              = root.find('DADOS-GERAIS').get('NOME-COMPLETO').replace("\n"," ").replace("\t"," ").strip()
            nomeEmCitacoes    = root.find('DADOS-GERAIS').get('NOME-EM-CITACOES-BIBLIOGRAFICAS').replace("\n"," ").replace("\t"," ").strip()
            paisNacimento     = root.find('DADOS-GERAIS').get('PAIS-DE-NASCIMENTO')
            paisNacionalidade = root.find('DADOS-GERAIS').get('PAIS-DE-NACIONALIDADE')

            #####################################################################################
            # FORMACOES
            #####################################################################################

            for formacoes in root.iter('FORMACAO-ACADEMICA-TITULACAO'):
                for xx in formacoes.iter('ESPECIALIZACAO'):
                    if strValidar(xx,'STATUS-DO-CURSO')=="CONCLUIDO":
                        f_ano1            = strValidar(xx, 'ANO-DE-INICIO')
                        f_ano2            = strValidar(xx, 'ANO-DE-CONCLUSAO')
                        f_nomeInstituicao = strValidar(xx, 'NOME-INSTITUICAO')
                        f_nomeCurso       = strValidar(xx, 'NOME-CURSO')
                        f_bolsa           = strValidar(xx, 'FLAG-BOLSA')
                        f_nomeAgencia     = strValidar(xx, 'NOME-AGENCIA')
                        f_idOrientador    = strValidar(xx, 'NUMERO-ID-ORIENTADOR')
                        dicFormacoes[idLattes]["E"].append ( (f_ano1, f_ano2, f_nomeInstituicao, f_nomeCurso, f_bolsa, f_nomeAgencia, f_idOrientador)  )

                for xx in formacoes.iter('GRADUACAO'):
                    if strValidar(xx,'STATUS-DO-CURSO')=="CONCLUIDO":
                        f_ano1            = strValidar(xx, 'ANO-DE-INICIO')
                        f_ano2            = strValidar(xx, 'ANO-DE-CONCLUSAO')
                        f_nomeInstituicao = strValidar(xx, 'NOME-INSTITUICAO')
                        f_nomeCurso       = strValidar(xx, 'NOME-CURSO')
                        f_bolsa           = strValidar(xx, 'FLAG-BOLSA')
                        f_nomeAgencia     = strValidar(xx, 'NOME-AGENCIA')
                        f_idOrientador    = strValidar(xx, 'NUMERO-ID-ORIENTADOR')
                        dicFormacoes[idLattes]["G"].append ( (f_ano1, f_ano2, f_nomeInstituicao, f_nomeCurso, f_bolsa, f_nomeAgencia, f_idOrientador)  )

                for xx in formacoes.iter('MESTRADO'):
                    if strValidar(xx,'STATUS-DO-CURSO')=="CONCLUIDO":
                        f_ano1            = strValidar(xx, 'ANO-DE-INICIO')
                        f_ano2            = strValidar(xx, 'ANO-DE-CONCLUSAO')
                        f_nomeInstituicao = strValidar(xx, 'NOME-INSTITUICAO')
                        f_nomeCurso       = strValidar(xx, 'NOME-CURSO')
                        f_bolsa           = strValidar(xx, 'FLAG-BOLSA')
                        f_nomeAgencia     = strValidar(xx, 'NOME-AGENCIA')
                        f_idOrientador    = strValidar(xx, 'NUMERO-ID-ORIENTADOR')
                        dicFormacoes[idLattes]["M"].append ( (f_ano1, f_ano2, f_nomeInstituicao, f_nomeCurso, f_bolsa, f_nomeAgencia, f_idOrientador)  )

                for xx in formacoes.iter('DOUTORADO'):
                    if strValidar(xx,'STATUS-DO-CURSO')=="CONCLUIDO":
                        f_ano1            = strValidar(xx, 'ANO-DE-INICIO')
                        f_ano2            = strValidar(xx, 'ANO-DE-CONCLUSAO')
                        f_nomeInstituicao = strValidar(xx, 'NOME-INSTITUICAO')
                        f_nomeCurso       = strValidar(xx, 'NOME-CURSO')
                        f_bolsa           = strValidar(xx, 'FLAG-BOLSA')
                        f_nomeAgencia     = strValidar(xx, 'NOME-AGENCIA')
                        f_idOrientador    = strValidar(xx, 'NUMERO-ID-ORIENTADOR')
                        dicFormacoes[idLattes]["D"].append ( (f_ano1, f_ano2, f_nomeInstituicao, f_nomeCurso, f_bolsa, f_nomeAgencia, f_idOrientador)  )

                for xx in formacoes.iter('POS-DOUTORADO'):
                    if strValidar(xx,'STATUS-DO-CURSO')=="CONCLUIDO":
                        f_ano1            = strValidar(xx, 'ANO-DE-INICIO')
                        f_ano2            = strValidar(xx, 'ANO-DE-CONCLUSAO')
                        f_nomeInstituicao = strValidar(xx, 'NOME-INSTITUICAO')
                        f_nomeCurso       = strValidar(xx, 'NOME-CURSO')
                        f_bolsa           = strValidar(xx, 'FLAG-BOLSA')
                        f_nomeAgencia     = strValidar(xx, 'NOME-AGENCIA')
                        f_idOrientador    = strValidar(xx, 'NUMERO-ID-ORIENTADOR')
                        dicFormacoes[idLattes]["P"].append ( (f_ano1, f_ano2, f_nomeInstituicao, f_nomeCurso, f_bolsa, f_nomeAgencia, f_idOrientador)  )

            #####################################################################################
            # ATUAÇÕES PROFISSIONAIS (COM DEDICAÇÃO EXCLUSIVA)
            #####################################################################################

            for aa in root.iter('ATUACAO-PROFISSIONAL'):
                ap_nomeInstituicao = strValidar(aa,'NOME-INSTITUICAO')
                for vv in aa.iter('VINCULOS'):
                    ap_tipo          = strValidar(vv, 'TIPO-DE-VINCULO').replace("\n"," ").replace("\t"," ").strip()
                    ap_enquadramento = strValidar(vv, 'ENQUADRAMENTO-FUNCIONAL').replace("\n"," ").replace("\t"," ").strip()

                    ap_deExclusiva = strValidar(vv, 'FLAG-DEDICACAO-EXCLUSIVA')
                    ap_mesInicio   = strValidar(vv, 'MES-INICIO')
                    ap_anoInicio   = strValidar(vv, 'ANO-INICIO')
                    ap_mesFim      = strValidar(vv, 'MES-FIM')
                    ap_anoFim      = strValidar(vv, 'ANO-FIM')

                    ap_outrasInfos = strValidar(vv, 'OUTRAS-INFORMACOES').replace("\n"," ").replace("\t"," ").strip()
                    ap_outroVinc   = strValidar(vv, 'OUTRO-VINCULO-INFORMADO').replace("\n"," ").replace("\t"," ").strip()
                    ap_outroEnq    = strValidar(vv, 'OUTRO-ENQUADRAMENTO-FUNCIONAL-INFORMADO').replace("\n"," ").replace("\t"," ").strip()

                    if ap_deExclusiva=="SIM":
                        dicAtuacoes[idLattes].append( (ap_nomeInstituicao, ap_tipo, ap_enquadramento, ap_mesInicio, ap_anoInicio, ap_mesFim, ap_anoFim, ap_outrasInfos, ap_outroVinc, ap_outroEnq ) )

            #####################################################################################
            # ENDEREÇO PROFISSIONAL
            #####################################################################################
            for profissional in root.iter('ENDERECO-PROFISSIONAL'):
                ep_Instituicao  = strValidar(profissional, 'NOME-INSTITUICAO-EMPRESA').replace("\n"," ").replace("\t"," ").strip()
                ep_Orgao        = strValidar(profissional, 'NOME-ORGAO').replace("\n"," ").replace("\t"," ").strip()
                ep_Unidade      = strValidar(profissional, 'NOME-UNIDADE').replace("\n"," ").replace("\t"," ").strip()
                ep_Pais         = strValidar(profissional, 'PAIS').replace("\n"," ").replace("\t"," ").strip()
                ep_UF           = strValidar(profissional, 'UF').replace("\n"," ").replace("\t"," ").strip()
                ep_Cidade       = strValidar(profissional, 'CIDADE').replace("\n"," ").replace("\t"," ").strip()

            #print ("\t\t", ep_Instituicao)
            #print ("\t\t", ep_Orgao)
            #print ("\t\t", ep_Unidade)
            #print ("\t\t", ep_Pais)
            #print ("\t\t", ep_UF)
            #print ("\t\t", ep_Cidade)

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
            f0 = f'{idLattes}\t{nome}\t{dataCV}\t{paisNacimento}\t{paisNacionalidade}\t{nomeEmCitacoes}\t{len(dicFormacoes[idLattes]["E"])}\t{len(dicFormacoes[idLattes]["G"])}\t{len(dicFormacoes[idLattes]["M"])}\t{len(dicFormacoes[idLattes]["D"])}\t{len(dicFormacoes[idLattes]["P"])}\t{ep_Instituicao}\t{ep_Orgao}\t{ep_Unidade}\t{ep_Pais}\t{ep_UF}\t{ep_Cidade}\t{primeiraGA}\t{primeiraA}'
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

                pChave = str(pChave)
                P_periodicos[idLattes].append( (titulo, str(ano), doi, veiculo, issn, volume, fasciculo, serie, pinicial, pfinal, pChave, autores, str(len(autores.split(";"))) ) )

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
                    #autores   = agrupaCoautores(evento.findall('AUTORES'))

                    pChave = []
                    if evento.find('PALAVRAS-CHAVE') != None:
                        for numPalavraChave in ["1", "2", "3", "4", "5", "6"]:
                            ppp = strValidar(evento.find('PALAVRAS-CHAVE'), "PALAVRA-CHAVE-" + numPalavraChave).strip()
                            if ppp!="":
                                pChave.append(ppp)
                 
                    pChave = str(pChave)
                    P_eventos[idLattes].append( (titulo, str(ano), doi, veiculo, isbn, volume, fasciculo, serie, pinicial, pfinal, pChave) )
                     
        
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
                #autores   = agrupaCoautores(livro.findall('AUTORES'))

                pChave = []
                if livro.find('PALAVRAS-CHAVE') != None:
                    for numPalavraChave in ["1", "2", "3", "4", "5", "6"]:
                        ppp = strValidar(livro.find('PALAVRAS-CHAVE'), "PALAVRA-CHAVE-" + numPalavraChave).strip()
                        if ppp!="":
                            pChave.append(ppp)

                pChave = str(pChave)
                P_livros[idLattes].append( (titulo, str(ano), tipo, natureza, volumes, paginas, isbn, edicao, serie, editora, pChave) )


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
                #autores     = agrupaCoautores(capitulo.findall('AUTORES'))

                pChave = []
                if capitulo.find('PALAVRAS-CHAVE') != None:
                    for numPalavraChave in ["1", "2", "3", "4", "5", "6"]:
                        ppp = strValidar(capitulo.find('PALAVRAS-CHAVE'), "PALAVRA-CHAVE-" + numPalavraChave).strip()
                        if ppp!="":
                            pChave.append(ppp)

                pChave = str(pChave)
                P_cap_livros[idLattes].append( (titulo, str(ano), tipo, tituloLivro, pagina1, pagina2, isbn, editora, pChave) )


            #####################################################################################
            # COLETANDO AS INFORMACOES DE ORIENTACOES CONCLUÍDAS
            #####################################################################################


            #####################################################################################
            # Orientações de Mestrado
            #####################################################################################

            for orientacao in root.iter('ORIENTACOES-CONCLUIDAS-PARA-MESTRADO'):
                natureza   = strValidar(orientacao.find('DADOS-BASICOS-DE-ORIENTACOES-CONCLUIDAS-PARA-MESTRADO'), 'NATUREZA').strip()
                tipo       = strValidar(orientacao.find('DADOS-BASICOS-DE-ORIENTACOES-CONCLUIDAS-PARA-MESTRADO'), 'TIPO').strip()
                titulo     = strValidar(orientacao.find('DADOS-BASICOS-DE-ORIENTACOES-CONCLUIDAS-PARA-MESTRADO'), 'TITULO').replace("\n"," ").replace("\t"," ").strip()
                ano        = intValidar(orientacao.find('DADOS-BASICOS-DE-ORIENTACOES-CONCLUIDAS-PARA-MESTRADO').get('ANO'))
                pais       = strValidar(orientacao.find('DADOS-BASICOS-DE-ORIENTACOES-CONCLUIDAS-PARA-MESTRADO'), 'PAIS').strip()
                idioma     = strValidar(orientacao.find('DADOS-BASICOS-DE-ORIENTACOES-CONCLUIDAS-PARA-MESTRADO'), 'IDIOMA').strip()

                tipoOrientacao  = strValidar(orientacao.find('DETALHAMENTO-DE-ORIENTACOES-CONCLUIDAS-PARA-MESTRADO'), 'TIPO-DE-ORIENTACAO').strip()
                nomeOrientado   = strValidar(orientacao.find('DETALHAMENTO-DE-ORIENTACOES-CONCLUIDAS-PARA-MESTRADO'), 'NOME-DO-ORIENTADO').strip()
                nomeInstituicao = strValidar(orientacao.find('DETALHAMENTO-DE-ORIENTACOES-CONCLUIDAS-PARA-MESTRADO'), 'NOME-DA-INSTITUICAO').strip()
                nomeOrgao       = strValidar(orientacao.find('DETALHAMENTO-DE-ORIENTACOES-CONCLUIDAS-PARA-MESTRADO'), 'NOME-ORGAO').strip()
                nomeCurso       = strValidar(orientacao.find('DETALHAMENTO-DE-ORIENTACOES-CONCLUIDAS-PARA-MESTRADO'), 'NOME-DO-CURSO').strip()
                flagBolsa       = strValidar(orientacao.find('DETALHAMENTO-DE-ORIENTACOES-CONCLUIDAS-PARA-MESTRADO'), 'FLAG-BOLSA').strip()
                nomeAgencia     = strValidar(orientacao.find('DETALHAMENTO-DE-ORIENTACOES-CONCLUIDAS-PARA-MESTRADO'), 'NOME-DA-AGENCIA').strip()

                O_mestrado[idLattes].append( (natureza, tipo, titulo, str(ano), pais, idioma, tipoOrientacao, nomeOrientado, nomeInstituicao, nomeOrgao, nomeCurso, flagBolsa, nomeAgencia)  )

            #####################################################################################
            # Orientações de Doutorado
            #####################################################################################

            for orientacao in root.iter('ORIENTACOES-CONCLUIDAS-PARA-DOUTORADO'):
                natureza   = strValidar(orientacao.find('DADOS-BASICOS-DE-ORIENTACOES-CONCLUIDAS-PARA-DOUTORADO'), 'NATUREZA').strip()
                tipo       = strValidar(orientacao.find('DADOS-BASICOS-DE-ORIENTACOES-CONCLUIDAS-PARA-DOUTORADO'), 'TIPO').strip()
                titulo     = strValidar(orientacao.find('DADOS-BASICOS-DE-ORIENTACOES-CONCLUIDAS-PARA-DOUTORADO'), 'TITULO').replace("\n"," ").replace("\t"," ").strip()
                ano        = intValidar(orientacao.find('DADOS-BASICOS-DE-ORIENTACOES-CONCLUIDAS-PARA-DOUTORADO').get('ANO'))
                pais       = strValidar(orientacao.find('DADOS-BASICOS-DE-ORIENTACOES-CONCLUIDAS-PARA-DOUTORADO'), 'PAIS').strip()
                idioma     = strValidar(orientacao.find('DADOS-BASICOS-DE-ORIENTACOES-CONCLUIDAS-PARA-DOUTORADO'), 'IDIOMA').strip()

                tipoOrientacao  = strValidar(orientacao.find('DETALHAMENTO-DE-ORIENTACOES-CONCLUIDAS-PARA-DOUTORADO'), 'TIPO-DE-ORIENTACAO').strip()
                nomeOrientado   = strValidar(orientacao.find('DETALHAMENTO-DE-ORIENTACOES-CONCLUIDAS-PARA-DOUTORADO'), 'NOME-DO-ORIENTADO').strip()
                nomeInstituicao = strValidar(orientacao.find('DETALHAMENTO-DE-ORIENTACOES-CONCLUIDAS-PARA-DOUTORADO'), 'NOME-DA-INSTITUICAO').strip()
                nomeOrgao       = strValidar(orientacao.find('DETALHAMENTO-DE-ORIENTACOES-CONCLUIDAS-PARA-DOUTORADO'), 'NOME-ORGAO').strip()
                nomeCurso       = strValidar(orientacao.find('DETALHAMENTO-DE-ORIENTACOES-CONCLUIDAS-PARA-DOUTORADO'), 'NOME-DO-CURSO').strip()
                flagBolsa       = strValidar(orientacao.find('DETALHAMENTO-DE-ORIENTACOES-CONCLUIDAS-PARA-DOUTORADO'), 'FLAG-BOLSA').strip()
                nomeAgencia     = strValidar(orientacao.find('DETALHAMENTO-DE-ORIENTACOES-CONCLUIDAS-PARA-DOUTORADO'), 'NOME-DA-AGENCIA').strip()

                O_doutorado[idLattes].append( (natureza, tipo, titulo, str(ano), pais, idioma, tipoOrientacao, nomeOrientado, nomeInstituicao, nomeOrgao, nomeCurso, flagBolsa, nomeAgencia)  )

            #####################################################################################
            # Orientações de Pós-Doutorado
            #####################################################################################

            for orientacao in root.iter('ORIENTACOES-CONCLUIDAS-PARA-POS-DOUTORADO'):
                natureza   = strValidar(orientacao.find('DADOS-BASICOS-DE-ORIENTACOES-CONCLUIDAS-PARA-POS-DOUTORADO'), 'NATUREZA').strip()
                tipo       = strValidar(orientacao.find('DADOS-BASICOS-DE-ORIENTACOES-CONCLUIDAS-PARA-POS-DOUTORADO'), 'TIPO').strip()
                titulo     = strValidar(orientacao.find('DADOS-BASICOS-DE-ORIENTACOES-CONCLUIDAS-PARA-POS-DOUTORADO'), 'TITULO').replace("\n"," ").replace("\t"," ").strip()
                ano        = intValidar(orientacao.find('DADOS-BASICOS-DE-ORIENTACOES-CONCLUIDAS-PARA-POS-DOUTORADO').get('ANO'))
                pais       = strValidar(orientacao.find('DADOS-BASICOS-DE-ORIENTACOES-CONCLUIDAS-PARA-POS-DOUTORADO'), 'PAIS').strip()
                idioma     = strValidar(orientacao.find('DADOS-BASICOS-DE-ORIENTACOES-CONCLUIDAS-PARA-POS-DOUTORADO'), 'IDIOMA').strip()

                tipoOrientacao  = strValidar(orientacao.find('DETALHAMENTO-DE-ORIENTACOES-CONCLUIDAS-PARA-POS-DOUTORADO'), 'TIPO-DE-ORIENTACAO').strip()
                nomeOrientado   = strValidar(orientacao.find('DETALHAMENTO-DE-ORIENTACOES-CONCLUIDAS-PARA-POS-DOUTORADO'), 'NOME-DO-ORIENTADO').strip()
                nomeInstituicao = strValidar(orientacao.find('DETALHAMENTO-DE-ORIENTACOES-CONCLUIDAS-PARA-POS-DOUTORADO'), 'NOME-DA-INSTITUICAO').strip()
                nomeOrgao       = strValidar(orientacao.find('DETALHAMENTO-DE-ORIENTACOES-CONCLUIDAS-PARA-POS-DOUTORADO'), 'NOME-ORGAO').strip()
                nomeCurso       = strValidar(orientacao.find('DETALHAMENTO-DE-ORIENTACOES-CONCLUIDAS-PARA-POS-DOUTORADO'), 'NOME-DO-CURSO').strip()
                flagBolsa       = strValidar(orientacao.find('DETALHAMENTO-DE-ORIENTACOES-CONCLUIDAS-PARA-POS-DOUTORADO'), 'FLAG-BOLSA').strip()
                nomeAgencia     = strValidar(orientacao.find('DETALHAMENTO-DE-ORIENTACOES-CONCLUIDAS-PARA-POS-DOUTORADO'), 'NOME-DA-AGENCIA').strip()

                O_posdoutorado[idLattes].append( (natureza, tipo, titulo, str(ano), pais, idioma, tipoOrientacao, nomeOrientado, nomeInstituicao, nomeOrgao, nomeCurso, flagBolsa, nomeAgencia)  )
    
            #####################################################################################
            # Orientações de TCC
            #####################################################################################

            for orientacao in root.iter('OUTRAS-ORIENTACOES-CONCLUIDAS'):
                natureza   = strValidar(orientacao.find('DADOS-BASICOS-DE-OUTRAS-ORIENTACOES-CONCLUIDAS'), 'NATUREZA').strip()
                tipo       = strValidar(orientacao.find('DADOS-BASICOS-DE-OUTRAS-ORIENTACOES-CONCLUIDAS'), 'TIPO').strip()
                titulo     = strValidar(orientacao.find('DADOS-BASICOS-DE-OUTRAS-ORIENTACOES-CONCLUIDAS'), 'TITULO').replace("\n"," ").replace("\t"," ").strip()
                ano        = intValidar(orientacao.find('DADOS-BASICOS-DE-OUTRAS-ORIENTACOES-CONCLUIDAS').get('ANO'))
                pais       = strValidar(orientacao.find('DADOS-BASICOS-DE-OUTRAS-ORIENTACOES-CONCLUIDAS'), 'PAIS').strip()
                idioma     = strValidar(orientacao.find('DADOS-BASICOS-DE-OUTRAS-ORIENTACOES-CONCLUIDAS'), 'IDIOMA').strip()

                tipoOrientacao  = strValidar(orientacao.find('DETALHAMENTO-DE-OUTRAS-ORIENTACOES-CONCLUIDAS'), 'TIPO-DE-ORIENTACAO').strip()
                nomeOrientado   = strValidar(orientacao.find('DETALHAMENTO-DE-OUTRAS-ORIENTACOES-CONCLUIDAS'), 'NOME-DO-ORIENTADO').strip()
                nomeInstituicao = strValidar(orientacao.find('DETALHAMENTO-DE-OUTRAS-ORIENTACOES-CONCLUIDAS'), 'NOME-DA-INSTITUICAO').strip()
                nomeOrgao       = strValidar(orientacao.find('DETALHAMENTO-DE-OUTRAS-ORIENTACOES-CONCLUIDAS'), 'NOME-ORGAO').strip()
                nomeCurso       = strValidar(orientacao.find('DETALHAMENTO-DE-OUTRAS-ORIENTACOES-CONCLUIDAS'), 'NOME-DO-CURSO').strip()
                flagBolsa       = strValidar(orientacao.find('DETALHAMENTO-DE-OUTRAS-ORIENTACOES-CONCLUIDAS'), 'FLAG-BOLSA').strip()
                nomeAgencia     = strValidar(orientacao.find('DETALHAMENTO-DE-OUTRAS-ORIENTACOES-CONCLUIDAS'), 'NOME-DA-AGENCIA').strip()

                if natureza=='TRABALHO_DE_CONCLUSAO_DE_CURSO_GRADUACAO':
                    O_tcc[idLattes].append( (natureza, tipo, titulo, str(ano), pais, idioma, tipoOrientacao, nomeOrientado, nomeInstituicao, nomeOrgao, nomeCurso, flagBolsa, nomeAgencia)  )
                if natureza=='INICIACAO_CIENTIFICA':
                    O_ic[idLattes].append( (natureza, tipo, titulo, str(ano), pais, idioma, tipoOrientacao, nomeOrientado, nomeInstituicao, nomeOrgao, nomeCurso, flagBolsa, nomeAgencia)  )
                if natureza=='ORIENTACAO-DE-OUTRA-NATUREZA':
                    O_outra[idLattes].append( (natureza, tipo, titulo, str(ano), pais, idioma, tipoOrientacao, nomeOrientado, nomeInstituicao, nomeOrgao, nomeCurso, flagBolsa, nomeAgencia)  )


            #####################################################################################
            #####################################################################################


    #######################################################################3
    # SALVANDO AS CARACTERÍSTICAS DO PESQUISADOR (CONSOLIDADO)
    #######################################################################3
    f = open(ou_caracteristicas, 'w')
    f.write( "ID-Lattes\tNome\tAtualizacao-CV\tNascimento\tNacionalidade\tNome-em-Citações\tEspecialização\tGraduação\tMestrado\tDoutorado\tPosdoc\tEnd.Prof.Instituição\tEnd.Prof.Órgão\tEnd.Prof.Unidade\tEnd.Prof.Pais\tEnd.Prof.UF\tEnd.Prof.Cidade\tPrimeira-Grande-Área\tPrimeira-Área\tPeriódicos\tEventos\tLivros\tCap-Livros\tSupervisões-Pós-Doutorado\tOrientações-Doutorado\tOrientações-Mestrado\tOrientações-TCC\tOrientações-IC\tOrientações-Outra-Natureza" )
    for idLattes in Pesquisadores:
        f.write( "\n" + f"{dicPesquisadores[idLattes]}\t{len(P_periodicos[idLattes])}\t{len(P_eventos[idLattes])}\t{len(P_livros[idLattes])}\t{len(P_cap_livros[idLattes])}\t{len(O_posdoutorado[idLattes])}\t{len(O_doutorado[idLattes])}\t{len(O_mestrado[idLattes])}\t{len(O_tcc[idLattes])}\t{len(O_ic[idLattes])}\t{len(O_outra[idLattes])}" )
    f.close()

    #######################################################################3
    # SALVANDO AS FORMAÇÕES
    #######################################################################3
    f = open(ou_formacoes, 'w')
    f.write( "ID-Lattes\tTipo-Formação\tAno-Inicio\tAno-Conclusão\tInstituição\tCurso\tBolsa\tAgência-da-bolsa\tID-Orientador" )
    for idLattes in Pesquisadores:
        for tipo in ["E","G","M","D","P"]:
            for ff in dicFormacoes[idLattes][tipo]:
                f.write( f"\n{idLattes}\t{tipo}\t" + "\t".join(ff) )
    f.close()

    #######################################################################3
    # SALVANDO AS ATUAÇÕES
    #######################################################################3
    f = open(ou_atuacoes, 'w')
    f.write( "ID-Lattes\tInstituição\tTipo-Vínculo\tEnquadramento\tMês-Inicio\tAno-Inicio\tMês-Fim\tAno-Fim\tOutras-Informações\tOutro-Vínculo\tOutro-Enquadramento-Funcional" )
    for idLattes in Pesquisadores:
        for aa in dicAtuacoes[idLattes]:
            f.write( f"\n{idLattes}\t" + "\t".join(aa) )
    f.close()


    #######################################################################3
    # SALVANDO AS PUBLICAÇÕES
    #######################################################################3
    f = open(ou_periodico, 'w')
    f.write( "ID-Lattes\tTítulo\tAno\tDOI\tVeículo\tISSN\tVolume\tFascículo\tSerie\tP-inicial\tP-final\tPalavras-chave\tAutores\tQuantidade-autores" )
    for idLattes in Pesquisadores:
        if  len(P_periodicos[idLattes]) >0:
            for pub in P_periodicos[idLattes]:
                f.write( f"\n{idLattes}\t" + "\t".join( pub ) )
    f.close()


    f = open(ou_eventos, 'w')
    f.write( "ID-Lattes\tTítulo\tAno\tDOI\tVeículo\tISBN\tVolume\tFascículo\tSerie\tP-inicial\tP-final\tPalavras-chave\t" )
    for idLattes in Pesquisadores:
        if  len(P_eventos[idLattes]) >0:
            for pub in P_eventos[idLattes]:
                f.write( f"\n{idLattes}\t" + "\t".join( pub ) )
    f.close()


    f = open(ou_livros, 'w')
    f.write( "ID-Lattes\tTítulo\tAno\tTipo\tNatureza\tVolumes\tPáginas\tISBN\tEdição\tSérie\tEditora\tPalavras-chave\t" )
    for idLattes in Pesquisadores:
        if  len(P_livros[idLattes]) >0:
            for pub in P_livros[idLattes]:
                f.write( f"\n{idLattes}\t" + "\t".join( pub ) )
    f.close()


    f = open(ou_cap_livros, 'w')
    f.write( "ID-Lattes\tTítulo\tAno\tTipo\tTítulo-do-livro\tP-inicial\tP-final\tISBN\tEditora\tPalavras-chave\t" )
    for idLattes in Pesquisadores:
        if  len(P_cap_livros[idLattes]) >0:
            for pub in P_cap_livros[idLattes]:
                f.write( f"\n{idLattes}\t" + "\t".join( pub ) )
    f.close()

    #######################################################################3
    # SALVANDO AS ORIENTAÇÕES
    #######################################################################3
    f = open(ou_posdoutorado, 'w')
    f.write( "ID-Lattes\tNatureza\tTipo\tTítulo\tAno\tPais\tIdioma\tTipo-orientação\tNome-orientado\tNome-instituição\tNome-orgao\tNome-curso\tFlag-bolsa\tNome-Agência\t" )
    for idLattes in Pesquisadores:
        if  len(O_posdoutorado[idLattes]) >0:
            for ori in O_posdoutorado[idLattes]:
                f.write( f"\n{idLattes}\t" + "\t".join( ori ) )
    f.close()

    f = open(ou_doutorado, 'w')
    f.write( "ID-Lattes\tNatureza\tTipo\tTítulo\tAno\tPais\tIdioma\tTipo-orientação\tNome-orientado\tNome-instituição\tNome-orgao\tNome-curso\tFlag-bolsa\tNome-Agência\t" )
    for idLattes in Pesquisadores:
        if  len(O_doutorado[idLattes]) >0:
            for ori in O_doutorado[idLattes]:
                f.write( f"\n{idLattes}\t" + "\t".join( ori ) )
    f.close()

    f = open(ou_mestrado, 'w')
    f.write( "ID-Lattes\tNatureza\tTipo\tTítulo\tAno\tPais\tIdioma\tTipo-orientação\tNome-orientado\tNome-instituição\tNome-orgao\tNome-curso\tFlag-bolsa\tNome-Agência\t" )
    for idLattes in Pesquisadores:
        if  len(O_mestrado[idLattes]) >0:
            for ori in O_mestrado[idLattes]:
                f.write( f"\n{idLattes}\t" + "\t".join( ori ) )
    f.close()

    f = open(ou_tcc, 'w')
    f.write( "ID-Lattes\tNatureza\tTipo\tTítulo\tAno\tPais\tIdioma\tTipo-orientação\tNome-orientado\tNome-instituição\tNome-orgao\tNome-curso\tFlag-bolsa\tNome-Agência\t" )
    for idLattes in Pesquisadores:
        if  len(O_tcc[idLattes]) >0:
            for ori in O_tcc[idLattes]:
                f.write( f"\n{idLattes}\t" + "\t".join( ori ) )
    f.close()

    f = open(ou_ic, 'w')
    f.write( "ID-Lattes\tNatureza\tTipo\tTítulo\tAno\tPais\tIdioma\tTipo-orientação\tNome-orientado\tNome-instituição\tNome-orgao\tNome-curso\tFlag-bolsa\tNome-Agência\t" )
    for idLattes in Pesquisadores:
        if  len(O_ic[idLattes]) >0:
            for ori in O_ic[idLattes]:
                f.write( f"\n{idLattes}\t" + "\t".join( ori ) )
    f.close()

    f = open(ou_outra, 'w')
    f.write( "ID-Lattes\tNatureza\tTipo\tTítulo\tAno\tPais\tIdioma\tTipo-orientação\tNome-orientado\tNome-instituição\tNome-orgao\tNome-curso\tFlag-bolsa\tNome-Agência\t" )
    for idLattes in Pesquisadores:
        if  len(O_outra[idLattes]) >0:
            for ori in O_outra[idLattes]:
                f.write( f"\n{idLattes}\t" + "\t".join( ori ) )
    f.close()



    #######################################################################3
    print("\ndone!")
    #######################################################################3

####
'''
with zipfile.ZipFile(cvPath) as myzip:
                    obj = myzip.open("curriculo.xml")
                    cvLattesHTML = obj.read()
                    obj.close()
'''
