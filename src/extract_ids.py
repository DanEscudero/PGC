import csv

if __name__ == '__main__':
    path = '../tar/BD-Lattes---nomes-e-caracteristicas---doutores.csv'

    fps = []
    for i in range(0, 10):
        fps.append(open('../xml2tables/ids-doutores/ids' + str(i) + '.txt', 'w'))

    with open(path) as tsvfile:
        tsvreader = csv.reader(tsvfile, delimiter="\t")
        for line in tsvreader:
            id = line[0]
            lastDigit = id[-1]

            if (lastDigit == 's'):
                continue

            fp = fps[int(lastDigit)]
            fp.write(str(id) + "\n")

    for fp in fps:
        fp.close()
