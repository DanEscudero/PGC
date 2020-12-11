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

Extrai IDs dos doutores e escreve nos arquivos `/ids-doutores/ids{N}.txt` (N entre 0 e 9). **N** se refere ao último dígito ID Lattes do pesquisador.

### Leitura de informações

    python3 xml2tables.py <listaIDS>

Lista as informações de pesquisadores e informações para ./base-cv/

As informações estatísticas sobre a base são extraídas para ./statistics.tsv

---

## Para desenvolver:

    source ENV/bin/activate

    ./helpers/install.sh

    ...

    ./helpers/freeze.sh

---
