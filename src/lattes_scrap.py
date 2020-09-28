import csv

if __name__ == '__main__':
    path = '../../tar/BD-Lattes---nomes-e-caracteristicas---doutores.csv'
    watching_areas = ['neuro-ciência']

    with open(path) as tsvfile:
        tsvreader = csv.reader(tsvfile, delimiter="\t")
        info = []
        keys = []
        all_areas = set()

        totals = dict()
        num_required_keys = ['Periódicos', 'Eventos', 'Livros', 'Cap-Livros']
        required_keys = ['Nome']
        required_keys += num_required_keys

        for k in num_required_keys:
            totals[k] = 0

        # metricas observadas
        max_nome = ''
        max_publicacoes = 0
        total_publicacoes = 0
        total_pesquisadores = 0

        i = -1
        for line in tsvreader:
            i = i + 1

            if (i == 0):
                keys = line
                continue

            d = dict()
            full_d = dict()

            # build full_d
            j = 0
            for item in line:
                full_d[keys[j]] = item
                j = j + 1

            all_areas.add(full_d['Primeira-Área'])

            if (full_d['Primeira-Área'].lower() in watching_areas):
                # add required keys
                for required_key in required_keys:
                    d[required_key] = full_d[required_key]

                info.append(d)

        tsvfile.close()

    for p in info:
        p_publicacoes = 0
        for k in num_required_keys:
            totals[k] = totals[k] + int(p[k])
            p_publicacoes = p_publicacoes + int(p[k])

        total_publicacoes = total_publicacoes + p_publicacoes
        if (p_publicacoes > max_publicacoes):
            max_publicacoes = p_publicacoes
            max_nome = p['Nome']

    total_pesquisadores = len(info)

    print(all_areas)
    exit()

    print('total_pesquisadores', total_pesquisadores)
    print('total_publicacoes  ', total_publicacoes)

    print('max_nome           ', max_nome)
    print('max_publicacoes    ', max_publicacoes)

    print('totais             ', totals)
