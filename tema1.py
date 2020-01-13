import psutil
import os
import time
import sys
import stopit

# input_date3 si 5 merg bine pe toate
# input_date6 nu are solutie
# input_date7 blocheaza df ul din cauza stack ului de recursivitate
# input_date9 blocheaza bf ul din cauza memoriei

timeout = float(sys.argv[1])
nrSolutiiCautateBF = nrSolutiiCautateDF = nrSolutiiCautateDFI = int(sys.argv[2])
directorInput = sys.argv[3]
continuaDF = continuaDFI = True
fisier_curent = ""


def files_in_folder(folder_path):
    files = []
    for f in os.listdir(folder_path):
        if os.path.isfile(os.path.join(folder_path, f)):
            files.append(os.path.join(folder_path, f))
    return files


def citire_din_fisier(path):
    words = []
    with open(path, 'r') as fin:
        start = fin.readline().split("cuvant start: ")[1].strip('\n')
        for line in fin:
            words.append(line.strip('\n'))
    words.append(start)
    return start, words


def scrie_in_fisier(content):
    fisier_iesire = fisier_curent.split('\\')[-1].replace("input", "output")
    with open(fisier_iesire, 'a') as fout:
        fout.write(content)


def calcMaxMem():
    global maxMem
    process = psutil.Process(os.getpid())
    memCurenta = process.memory_info()[0]
    if maxMem < memCurenta:
        maxMem = memCurenta


class NodParcurgere:
    def __init__(self, info, parinte):
        self.info = info
        self.parinte = parinte

    def obtineDrum(self):
        listaDrum = [self.info]
        nod = self
        while nod.parinte is not None:
            listaDrum.insert(0, nod.parinte.info)
            nod = nod.parinte
        return listaDrum

    def afisDrum(self):
        print(self.sirAfisare())

    def sirAfisare(self):
        listaDrum = self.obtineDrum()
        sir = "Pentru cuvantul de start \"" + listaDrum[0] + "\": " + ", ".join(listaDrum) + '\n\n\n'
        sir += '#' * 10 + '\n\n\n'
        return sir

    def contineInDrum(self, infoNodNou):
        nodDrum = self
        while nodDrum is not None:
            if infoNodNou == nodDrum.info:
                return True
            nodDrum = nodDrum.parinte
        return False

    def __repr__(self):
        sir = self.info + "(drum = "
        drum = self.obtineDrum()
        sir += ", ".join(drum)
        sir += ")"
        return sir


class Graph:
    def __init__(self, words, start):
        self.words = words
        self.start = start

    def genereazaSuccesori(self, nodCurent):
        listaSuccesori = []
        for k in range(len(nodCurent.info), 1, -1):  # k merge de la lungimea cuvantului pana la 2
            for i in range(len(self.words)):  # parcurgem toate cuvintele
                # verific ca ultimele k litere din primul cuvant sa fie egale cu primele k din al doilea
                if nodCurent.info[-k:].lower() == self.words[i][0:k].lower():
                    # verific sa nu adaug acelasi cuvant
                    # ex: ultimele 6 litere din 'asasin' sunt egale cu primele 6 din 'asasin' pt ca e acelasi cuvant
                    if k != len(nodCurent.info) and k != len(self.words[i]):
                        nodNou = NodParcurgere(self.words[i], nodCurent)
                        listaSuccesori.append(nodNou)
        return listaSuccesori

    def __repr__(self):
        sir = ""
        for (k,
             v) in self.__dict__.items():
            sir += "{} = {}\n".format(k, v)
        return sir


# ############################## BREADTH FIRST ############################
@stopit.threading_timeoutable(default="Algoritmul de breadth first a intrat in timeout")
def breadth_first(graph, start):
    global nrSolutiiCautateBF
    c = [NodParcurgere(start, None)]
    continua = True
    while len(c) > 0 and continua:
        nodCurent = c.pop(0)
        lSuccesori = graph.genereazaSuccesori(nodCurent)

        if len(lSuccesori) == 0:  # daca un cuvant nu are succesori, inseamna ca am gasit solutie
            afisare_solutie(nodCurent)
            nrSolutiiCautateBF -= 1
            if nrSolutiiCautateBF == 0:
                continua = False
        else:  # daca are succesori, verific ca acestia sa nu fie din cei care exista deja in drum
            elimina_succesorii_existenti_in_drum(lSuccesori, nodCurent)
            if len(lSuccesori) != 0:
                c.extend(lSuccesori)  # daca dupa eliminare au mai ramas succesori, ii adaug in coada
        calcMaxMem()
    return "Breadth first s-a finalizat cu succes"


def afisare_solutie(nodCurent):
    # nodCurent.afisDrum()
    output = nodCurent.sirAfisare()
    scrie_in_fisier(output)


def elimina_succesorii_existenti_in_drum(lSuccesori, nodCurent):
    for succesor in lSuccesori:
        if succesor.info in nodCurent.obtineDrum():  # daca exista, ii sterg
            lSuccesori.remove(succesor)


# ##################################### DEPTH FIRST ################################


@stopit.threading_timeoutable(default="Algoritmul de depth first a intrat in timeout")
def depth_first(gr, start):
    df(gr, NodParcurgere(start, None))
    return "Depth first s-a finalizat cu succes"


def df(gr, nodCurent):
    global nrSolutiiCautateDF, continuaDF
    if not continuaDF:
        return

    lSuccesori = gr.genereazaSuccesori(nodCurent)
    if len(lSuccesori) == 0:  # daca un cuvant nu are succesori, inseamna ca am gasit solutie
        afisare_solutie(nodCurent)
        nrSolutiiCautateDF -= 1
        if nrSolutiiCautateDF == 0:
            continuaDF = False
    else:  # daca are succesori, verific ca acestia sa nu fie din cei care exista deja in drum
        elimina_succesorii_existenti_in_drum(lSuccesori, nodCurent)
        if len(lSuccesori) != 0:
            for sc in lSuccesori:
                df(gr, sc)
    calcMaxMem()


# ################################# iterative deepening depth first search #######################
@stopit.threading_timeoutable(default="Algoritmul de iterative deepening depth first search a intrat in timeout")
def depth_first_iterative_deepening(gr, start, adancimeMax):
    for i in range(1, adancimeMax):
        dfi(gr, i, NodParcurgere(start, None))
    return "Iterative deepening depth first search s-a realizat cu succes"


def dfi(gr, adMaxCurenta, nodCurent):
    global nrSolutiiCautateDFI, continuaDFI
    if adMaxCurenta <= 0 or not continuaDFI:
        return
    adMaxCurenta -= 1

    lSuccesori = gr.genereazaSuccesori(nodCurent)
    if len(lSuccesori) == 0:  # daca un cuvant nu are succesori, inseamna ca am gasit solutie
        afisare_solutie(nodCurent)
        nrSolutiiCautateDFI -= 1
        if nrSolutiiCautateDFI == 0:
            continuaDFI = False
    else:  # daca are succesori, verific ca acestia sa nu fie din cei care exista deja in drum
        elimina_succesorii_existenti_in_drum(lSuccesori, nodCurent)
        if len(lSuccesori) != 0:
            for sc in lSuccesori:
                dfi(gr, adMaxCurenta, sc)
    calcMaxMem()


algorithms = [breadth_first, depth_first, depth_first_iterative_deepening]
maxMem = 0
adancimeMaxima = 12
fisiere = files_in_folder(directorInput)


def call_algorithms():
    global maxMem
    global fisier_curent
    for algorithm in algorithms:
        for i in range(0, len(fisiere)):
            fisier_curent = fisiere[i]
            scrie_in_fisier("Solutii " + str(algorithm).split()[1].upper() + ':\n')
            maxMem = 0
            start, words = citire_din_fisier(fisiere[i])
            gr = Graph(words, start)
            try:
                if algorithm != depth_first_iterative_deepening:
                    t1 = time.time()
                    print(algorithm(gr, start, timeout=timeout))
                else:
                    t1 = time.time()
                    print(algorithm(gr, start, adancimeMaxima, timeout=timeout))
                t2 = time.time()
                milis = round(1000 * (t2 - t1))
                print(
                    "Memorie maxim folosita la {}: {}. Timp: {}\n\n\n".format(str(algorithm).split()[1], maxMem, milis))
            except Exception as e:
                print(e)


call_algorithms()

#
# # APELARE BREADTH FIRST
# for i in range(0, len(fisiere)):
#     fisier_curent = fisiere[i]
#     scrie_in_fisier("Solutii BREADTH FIRST:\n")
#     maxMem = 0
#     start, words = citire_din_fisier(fisiere[i])
#     gr = Graph(words, start)
#     t1 = time.time()
#     print(breadth_first(gr, start, timeout=timeout))
#     t2 = time.time()
#     milis = round(1000 * (t2 - t1))
#     print("Memorie maxim folosita la breadth first: {}. Timp: {}\n\n\n".format(maxMem, milis))
#
# # APELARE DEPTH FIRST
# for i in range(0, len(fisiere)):
#     fisier_curent = fisiere[i]
#     scrie_in_fisier("Solutii DEPTH FIRST:\n")
#     maxMem = 0
#     start, words = citire_din_fisier(fisiere[i])
#     gr = Graph(words, start)
#     t1 = time.time()
#     print(depth_first(gr, start, timeout=timeout))
#     t2 = time.time()
#     milis = round(1000 * (t2 - t1))
#     print("Memorie maxim folosita la depth first: {}. Timp: {}\n\n\n".format(maxMem, milis))
#
# # APELARE DEPTH FIRST ITERATIVE DEEPENING
# for i in range(0, len(fisiere)):
#     fisier_curent = fisiere[i]
#     scrie_in_fisier("Solutii DEPTH FIRST ITERATIVE DEEPENING:\n")
#     maxMem = 0
#     start, words = citire_din_fisier(fisiere[i])
#     gr = Graph(words, start)
#     t1 = time.time()
#     print(depth_first_iterative_deepening(gr, start, adancimeMaxima, timeout=timeout))
#     t2 = time.time()
#     milis = round(1000 * (t2 - t1))
#     print("Memorie maxim folosita la depth first iterative deepening: {}. Timp: {}\n\n\n".format(maxMem, milis))
#
