# PGC

## Construção da árvore

    python3 treeBuilder.py <Grande Área> <Termo de Busca> <Nível> <Limite>

Uma árvore é definida com o conjunto de 3 parâmetros: Grande Área (raíz da árvore), Nível (Altura máxima da árvore) e Limite (Número máximo de filhos por nó, limitado a 500).

A árvore é construída e codificada de forma textual em `/out/GrandeÁrea_Nível_Limite`

## Extração de métricas

    python3 treeMetrics.py <Grande Área> <Termo de Busca> <Nível> <Limite=max>

Imprime métricas relacionadas à arvore. A definição da árvore é a mesma que se dá na seção **Construção da árvore**

## Extração de termos da árvore

    python3 termsExtractor.py <Grande Área> <Termo de Busca> <Nível> <Limite=max>

Busca pelo `Termo de Busca` dentro da árvore.

## Extração de informações do Lattes

### Extração de IDs

    python3 extract_ids.py

Extrai IDs dos doutores e escreve nos arquivos `/ids-doutores/idsN.txt` (N entre 0 e 9). **N** se refere ao último dígito ID Lattes do pesquisador.

### Leitura de informações

    python3 xml2tables.py <listaIDS>

A partir das informações contidas em `BD-Lattes---nomes-e-caracteristicas---doutores.csv`, lista informações dos pesquisadores contidos em `listaIDS`. Escreve diversos arquivos de output.

### Extração de informações gerais sobre doutores

    python3 lattes_scrap.py

Gera informações quantitativas a partir do arquivo `BD-Lattes---nomes-e-caracteristicas---doutores.csv`

---

## Para desenvolver:

    source ENV/bin/activate

    ./helpers/install.sh

    ...

    ./helpers/freeze.sh

---
