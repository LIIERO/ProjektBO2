import math
import random
import numpy as np
from copy import deepcopy

import main


class Genetic(object):
    def __init__(self, chromosome, plants, field_number, farm: main.FarmSimulation):
        self.chromosome = chromosome
        self.farm = farm
        self.plants = plants
        self.field_number = field_number
        self.beast_chromosome = list([-np.inf])
        self.best_generation_number = 0

    def initial_result(self):  # inicjalizacja generacji 0

        chromosome = deepcopy(self.chromosome)
        chrom = deepcopy(chromosome[0])  #kopia pierrwszego chromosomu do którego będziemy dodawać zysk tego chromosomu
        chrom.append(self.__simulate_one_field(chromosome[0]))#dodanie zysku z danego chromosomu
        chromosome[0] = chrom
        nr_chromosom = 1 #zmienna określająca numer w tym momencie obsługiwanego chromosomu
        for i in deepcopy(chromosome[nr_chromosom:]):
            flag = False #flaga informująca nas o powodzeniu mutacji chromosomu
            i_inp = deepcopy(i) #zapisanie początkowych wartości danego chromosomu
            attempts = 0 #zmienna określająca ilość podejść do wygenererowania danego chromosomu
            while not flag:
                i = deepcopy(i_inp) #zresetowanie ewentualnych zmian w chromosomie
                flag = True
                year = random.randrange(len(i)) #generacja losowego roku z zakresu
                curr_plant = i[year] #sprawdzenie jaka roślina jest przewidziana na dany rok
                rand_plant = random.choice([plant for plant in self.plants if plant != curr_plant]) #wylosowanie rośliny z zakresu możliwych
                i[year] = rand_plant #zmiana rośliny w danym roku na wcześniej wylosowaną
                for l in chromosome:  # sprawdzenie czy dany chromosom nie jest już w generacji
                    if l[year] == i[year]:
                        flag = False

                try: #sprawdzenie czy taki chromosom spełnia wszystkie ogranczenia problemu
                    self.__simulate_one_field(i)
                except IndexError:
                    # print('Nie spełnia ograniczenia jakości')
                    flag = False  # Ponowna próba

                except ValueError:
                    # print('Nie spełnia ograniczenia innej rośliny w każdym roku')
                    flag = False  # Ponowna próba
                if flag:
                    chrom = deepcopy(i)
                    income = self.__simulate_one_field(i)
                    if income > 0 or attempts > 10: #jeśli istnieje taka możliwość wygenerowanie chromosomu od dodatnim zysku
                        chrom.append(income)
                        chromosome[nr_chromosom] = chrom
                        nr_chromosom += 1
                    else:
                        attempts += 1
                        flag = False
        self.chromosome = chromosome # zapisanie wygenerowanych chromosomó do modelu

    def selection_rank(self, generation_number):  # selekcja metodą rankingową
        self.chromosome.sort(key=lambda x: x[-1]) #sortowanie chromosomów w danej generacji
        if self.beast_chromosome[-1] < self.chromosome[-1][-1]: #sprawdzenie czy najlepszy z chromosomów w danej generacji jest najlepszy w całej populacji
            self.beast_chromosome = deepcopy(self.chromosome[-1])
            self.best_generation_number = generation_number
        chromosomes = deepcopy([i[:-1] for i in self.chromosome]) #wycięcie zysków dla danego chromosomu
        return chromosomes[-1], chromosomes[-2] #wybór dwóch najlepszych wyników

    def selection_roulette(self, generation_number):  # selekcja metodą ruletki
        list_value_chromosome = [i[-1] for i in self.chromosome] #wykonanie listy z zysków kolejnych chromosomów
        max_val = max(list_value_chromosome) #poszukiwania najwiękzej wielkości w liście
        max_index = list_value_chromosome.index(max_val) # poszukiwanie indeksu największej wartości
        if self.beast_chromosome[-1] < max_val: #sprawdzenie czy wartość najlepszego chromosomu w generacji jest najlepsza w całej populacji
            self.beast_chromosome = deepcopy(self.chromosome[max_index])
            self.best_generation_number = generation_number
        min_earnings = min(list_value_chromosome) #znalezienie najmniejszej wartości w liście zysków
        if min_earnings < 0:  # jeśli mamy rozwiązanie o ujemnych dochodach to dodajemy do pozostałych rozwiązań tą wartość, aby pozwolić sobie na poprawne losowanie
            sum_earnings = sum([i[-1] - min_earnings for i in self.chromosome]) #suma ocen wszystkich chromosomów dla przypadku z ujemnymi zyskami
            chromosome_probab = [(i[-1] - min_earnings) / sum_earnings for i in
                                 self.chromosome]  # szansa na wylosowanie danego chromosomu w ruletce
        else:
            sum_earnings = sum(list_value_chromosome)  # suma ocen wszystkich chromosonów w generacji dla braku ujemnej wartości zysku
            chromosome_probab = [i[-1] / sum_earnings for i in
                                 self.chromosome]  # szansa na wylosowanie danego chromosomu w ruletce
        chromosomes = deepcopy([i[:-1] for i in self.chromosome])
        parent_index = []
        for m in range(len(self.chromosome)//2): #wylosowanie takiej ilośći rodziców aby ich sumaryczna ilośći była równa ilości chromosomów w dotychczasowej generacji
            parent_index.append(list(np.random.choice(len(chromosomes), 2,
                                            p=chromosome_probab))) # wyselekcjowanie rodziców za pomocą ruletki
        parent_index = [item for k in parent_index for item in k]
        parent = [chromosomes[k] for k in parent_index]#zapisanie otrzymancyh rosziców w  postaci listy wartości indeksó
        return parent

    def crossover(self, selection, selection_type):  # procedura krzyżowania
        sel = deepcopy(selection)
        flag = False
        children = []
        if selection_type == "rank":#krzyżowanie dla przypadku selekcji rankingowej
            sel_out = deepcopy(sel)
            for _ in range(len(self.chromosome)//2): #wygenerowanie tylu potomków iel liczyła dotychczasowan ilość chromosomów w generacji
                while not flag:
                        flag = True
                        k = np.random.randint(0, len(sel_out[0]), 2) #losowanie przdziału krzyżowania
                        k = sorted(k) #posortowane otrzymanych indeksów
                        for i in range(k[0], k[1]):
                            sel_out[0][i], sel_out[1][i] = sel_out[0][i], sel_out[1][i] #krzyżownanie obu rodziców w danym przedziale
                        try:#srawdzenie czy obydwaj potomkowie spełniają założenia problemu
                            self.__simulate_one_field(sel_out[0])
                            self.__simulate_one_field(sel_out[1])
                        except IndexError:
                            # print('Nie spełnia ograniczenia jakości')
                            flag = False  # Ponowna próba

                        except ValueError:
                            # print('Nie spełnia ograniczenia innej rośliny w każdym roku')
                            flag = False  # Ponowna próba

                        if flag:
                            children.append(deepcopy(sel_out))
        elif selection_type == "roulette": #krzyżowane dla selekcji z metodą ruletki
            sel_out = deepcopy(sel)
            for m in range(len(sel_out) // 2): #krzyżowanie kolejnych rodziców, tak by ich liczba była identyczna do istniejących już chromosomó
                while not flag: #reszta kometarzy identyczna jak dla metody rankingowej
                    flag = True
                    children = []
                    k = np.random.randint(0, len(sel_out[0][:-1]), 2)
                    k = sorted(k)
                    for i in range(k[0], k[1]):
                        sel_out[2*m][i], sel_out[2*m+1][i] = sel_out[2*m][i], sel_out[2*m+1][i]
                    try:
                        self.__simulate_one_field(sel_out[2*m])
                        self.__simulate_one_field(sel_out[2*m+1])
                    except IndexError:
                        # print('Nie spełnia ograniczenia jakości')
                        flag = False  # Ponowna próba
                    except ValueError:
                        # print('Nie spełnia ograniczenia innej rośliny w każdym roku')
                        flag = False  # Ponowna próba
                    if flag:
                        children.append(deepcopy(sel_out))

        return children

    def mutation(self, crossover): #procedura mutacji
        mutation = deepcopy(crossover)
        mutation_out = list(mutation[0])
        j = 0
        for i in deepcopy(mutation_out): #komentarze identyczne jak dla metody inicjallizującej

            flag = False
            i_inp = deepcopy(i)
            attempts = 0
            mutations_for_one_parents = []
            for m in range(10):

                while not flag:
                    i = deepcopy(i_inp)
                    flag = True
                    year = random.randrange(len(i))
                    curr_plant = i[year]
                    rand_plant = random.choice([plant for plant in self.plants if plant != curr_plant])
                    i[year] = rand_plant

                    for l in mutations_for_one_parents:  # sprawdzenie czy dany chromosom nie jest już w generacji
                        if l[year] == i[year]:
                            flag = False
                    try:
                        self.__simulate_one_field(i)
                    except IndexError:
                        # print('Nie spełnia ograniczenia jakości')
                        flag = False  # Ponowna próba

                    except ValueError:
                        # print('Nie spełnia ograniczenia innej rośliny w każdym roku')
                        flag = False  # Ponowna próba
                    if flag:
                        mut = deepcopy(i)
                        income = self.__simulate_one_field(i)
                        if income > 0 or attempts > 10:
                            mut.append(income)
                            mutations_for_one_parents.append(mut)
                        else:
                            attempts += 1
                            flag = False
            mutations_for_one_parents.sort(key=lambda x: x[-1])  # sortowanie mutacji
            mutation_out[j] = deepcopy(mutations_for_one_parents[-1]) #wybranie najlepszej mutacji
            j += 1


        return mutation_out

    def __simulate_one_field(self, decisons: list[str]): #symulacja wartości zysków dla jednego pola
        for i in range(self.farm.yearsNumber - 1):
            if decisons[i + 1] != 'EMPTY':
                if decisons[i] == decisons[i + 1]:
                    raise ValueError
        earnings = 0
        for i in range(self.farm.yearsNumber):
            plant = decisons[i]
            if i != 0:
                self.farm.Q[i][self.field_number] = self.farm.Q[i - 1][self.field_number] - \
                                                    self.farm.plantInfluenceDict[decisons[i - 1]]

                if self.farm.Q[i][self.field_number] < 0:
                    raise IndexError
                income = 0 if decisons[i - 1] == plant == 'EMPTY' else (
                        self.farm.fieldsSurfacesList[self.field_number] * self.farm.earningsMatrix[plant][
                    math.ceil(self.farm.Q[i][self.field_number])])
            else:
                income = self.farm.fieldsSurfacesList[self.field_number] * self.farm.earningsMatrix[plant][
                    math.ceil(self.farm.Q[i][self.field_number])]

            expense = 0 if plant == 'EMPTY' else (
                        self.farm.productionCostDict[plant] * self.farm.fieldsSurfacesList[self.field_number] +
                        self.farm.distanceMatrix[
                            self.field_number] * self.farm.transportCost)  # Jeśli nic nie siejemy to nie ponosimy kosztów
            earnings += income - expense
        return earnings


def genetic_algorithm(farm: main.FarmSimulation, plants, number_chromosome, selection_type="roulette"):
    greedy_result = farm.solve_greedy() #rozwiązanie konstrukcyjne
    j = 0
    farm.earnings = 0
    genetic_result = []
    beast_genetic_result = []
    beast_generation_number = []
    for i in list(zip(*greedy_result[::-1])): #transpozycja macierzy wyników greddy
        i = deepcopy(list(i))
        chromosomes = [i for _ in range(number_chromosome)]
        genetic = Genetic(chromosomes, plants, j, farm)
        genetic.initial_result()
        for generation_number in range(50):
            if selection_type == "roulette":
                selection = genetic.selection_roulette(generation_number)
                children = genetic.crossover(selection, selection_type)
            elif selection_type == "rank":
                selection = genetic.selection_rank(generation_number)
                children = genetic.crossover(selection, selection_type)
            mutation = genetic.mutation(children)
            genetic.chromosome = deepcopy(mutation)


        max_earnings = max([io[-1] for io in genetic.chromosome])  # maksymalna ocena chromosomu dla ostatniej generacji
        for m in genetic.chromosome:
            if m[-1] == max_earnings:
                genetic_result.append(m)
                break
        beast_generation_number.append(genetic.best_generation_number)
        beast_genetic_result.append(genetic.beast_chromosome)
        j += 1

    genetic_result = [i[:-1] for i in genetic_result]
    genetic_result = zip(*genetic_result[::])
    genetic_result = list(genetic_result)
    print(f"Wynik z algorytmu genetycznego dla 50 pełnych pokoleń (z metodą selekcji: {selection_type}):")
    farm.simulate_farm(genetic_result)
    farm.display_solution()

    beast_genetic_result = [i[:-1] for i in beast_genetic_result]
    beast_genetic_result = zip(*beast_genetic_result[::])
    beast_genetic_result = list(beast_genetic_result)
    print(f"Najlepszy rozwiązanie który pojawiło się w trakcie trwania algorytmu genetycznego z metodą selekcji: {selection_type} (w {beast_generation_number} generacjach ) :")
    farm.simulate_farm(beast_genetic_result)
    farm.display_solution()

    farm.simulate_farm(genetic_result)
    return farm.earnings
