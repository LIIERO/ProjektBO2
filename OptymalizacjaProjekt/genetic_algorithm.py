import math
import random
import numpy as np
from copy import deepcopy

import farm_simulation


class Genetic(object):
    def __init__(self, chromosome, plants, field_number, farm: farm_simulation.FarmSimulation):
        """

        :param chromosome:
        :param plants:
        :param field_number:
        :param farm:
        """
        self.chromosome = chromosome
        self.farm = farm
        self.plants: list[str] = plants
        self.field_number: int = field_number
        self.best_chromosome = list([-np.inf])
        self.best_generation_number = 0

    def initial_result(self):  #
        """inicjalizacja generacji 0

        :return: None
        """

        chromosome = deepcopy(self.chromosome)
        # kopia pierrwszego chromosomu do którego będziemy dodawać zysk tego chromosomu
        chrom = deepcopy(chromosome[0])
        # dodanie zysku z danego chromosomu
        chrom.append(self.__simulate_one_field(chromosome[0]))
        chromosome[0] = chrom
        nr_chromosom = 1  # zmienna określająca numer w tym momencie obsługiwanego chromosomu

        for i in deepcopy(chromosome[nr_chromosom:]):
            flag = False  # flaga informująca nas o powodzeniu mutacji chromosomu
            i_inp = deepcopy(i)  # zapisanie początkowych wartości danego chromosomu
            attempts = 0  # zmienna określająca ilość podejść do wygenererowania danego chromosomu

            while not flag:
                # zresetowanie ewentualnych zmian w chromosomie
                i = deepcopy(i_inp)
                flag = True
                year = random.randrange(len(i))  # generacja losowego roku z zakresu
                curr_plant = i[year]  # sprawdzenie jaka roślina jest przewidziana na dany rok
                rand_plant = random.choice(
                    [plant for plant in self.plants if plant != curr_plant])  # wylosowanie rośliny z zakresu możliwych
                i[year] = rand_plant  # zmiana rośliny w danym roku na wcześniej wylosowaną

                for l in chromosome:  # sprawdzenie czy dany chromosom nie jest już w generacji
                    if l[year] == i[year]:
                        flag = False

                try:  # sprawdzenie czy taki chromosom spełnia wszystkie ogranczenia problemu
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

                    if income > 0 or attempts > 10:  # jeśli istnieje taka możliwość wygenerowanie chromosomu od dodatnim zysku
                        chrom.append(income)
                        chromosome[nr_chromosom] = chrom
                        nr_chromosom += 1

                    else:
                        attempts += 1
                        flag = False

        self.chromosome = chromosome  # zapisanie wygenerowanych chromosomó do modelu

    def selection_rank(self, generation_number):  #
        """selekcja metodą rankingową

        :param generation_number:
        :return:
        """
        self.chromosome.sort(key=lambda x: x[-1])  # sortowanie chromosomów w danej generacji

        # sprawdzenie czy najlepszy z chromosomów w danej generacji jest najlepszy w całej populacji
        if self.best_chromosome[-1] < self.chromosome[-1][-1]:
            self.best_chromosome = deepcopy(self.chromosome[-1])
            self.best_generation_number = generation_number

        chromosomes = deepcopy([i[:-1] for i in self.chromosome])  # wycięcie zysków dla danego chromosomu

        return chromosomes[-1], chromosomes[-2]  # wybór dwóch najlepszych wyników

    def selection_roulette(self, generation_number):
        """selekcja metodą ruletki

        :param generation_number:
        :return:
        """
        list_value_chromosome = [i[-1] for i in self.chromosome]  # wykonanie listy z zysków kolejnych chromosomów
        max_val = max(list_value_chromosome)  # poszukiwania najwiękzej wielkości w liście
        max_index = list_value_chromosome.index(max_val)  # poszukiwanie indeksu największej wartości

        if self.best_chromosome[
            -1] < max_val:  # sprawdzenie czy wartość najlepszego chromosomu w generacji jest najlepsza w całej populacji
            self.best_chromosome = deepcopy(self.chromosome[max_index])
            self.best_generation_number = generation_number

        min_earnings = min(list_value_chromosome)  # znalezienie najmniejszej wartości w liście zysków

        # jeśli mamy rozwiązanie o ujemnych dochodach to dodajemy do pozostałych rozwiązań tą wartość, aby pozwolić
        # sobie na poprawne losowanie
        if min_earnings < 0:
            # suma ocen wszystkich chromosomów dla przypadku z ujemnymi zyskami
            sum_earnings = sum([i[-1] - min_earnings for i in self.chromosome])

            # szansa na wylosowanie danego chromosomu w ruletce
            chromosome_probab = [(i[-1] - min_earnings) / sum_earnings for i in self.chromosome]

        else:
            # suma ocen wszystkich chromosonów w generacji dla braku ujemnej wartości zysku
            sum_earnings = sum(list_value_chromosome)

            # szansa na wylosowanie danego chromosomu w ruletce
            chromosome_probab = [i[-1] / sum_earnings for i in self.chromosome]

        chromosomes = deepcopy([i[:-1] for i in self.chromosome])
        parent_index = []

        # wylosowanie takiej ilośći rodziców aby ich sumaryczna ilośći była równa ilości chromosomów w dotychczasowej
        # generacji
        for m in range(len(self.chromosome) // 2):
            # wyselekcjowanie rodziców za pomocą ruletki
            parent_index.append(list(np.random.choice(len(chromosomes), 2,p=chromosome_probab)))

        parent_index = [item for k in parent_index for item in k]
        parent = [chromosomes[k] for k in
                  parent_index]  # zapisanie otrzymancyh rosziców w  postaci listy wartości indeksó

        return parent

    def crossover(self, selection, selection_type, number_chromosome):
        """procedura krzyżowania
        sama funkcja jest podzielona dla crossovera ruletkowego i rankingowego

        :param selection:
        :param selection_type:
        :return:
        """
        sel = deepcopy(selection)

        children = []

        if selection_type == "rank":  # krzyżowanie dla przypadku selekcji rankingowej
            sel_out = deepcopy(sel)

            for _ in range(
                    int(number_chromosome/2)):  # wygenerowanie tylu potomków iel liczyła dotychczasowan ilość chromosomów w generacji
                flag = False
                while not flag:
                    flag = True
                    k = np.random.randint(0, len(sel_out[0]), 2)  # losowanie przedziału krzyżowania
                    k = sorted(k)  # posortowane otrzymanych indeksów

                    for i in range(k[0], k[1]):
                        sel_out[0][i], sel_out[1][i] = sel_out[0][i], sel_out[1][
                            i]  # krzyżownanie obu rodziców w danym przedziale

                    try:  # srawdzenie czy obydwaj potomkowie spełniają założenia problemu
                        self.__simulate_one_field(sel_out[0])
                        self.__simulate_one_field(sel_out[1])

                    except IndexError:
                        # print('Nie spełnia ograniczenia jakości')
                        flag = False  # Ponowna próba

                    except ValueError:
                        # print('Nie spełnia ograniczenia innej rośliny w każdym roku')
                        flag = False  # Ponowna próba
                    # for k in children:
                    #     if k == sel_out:
                    #         flag = False

                    if flag:
                        children.append(deepcopy(sel_out[0]))
                        children.append(deepcopy(sel_out[1]))

        elif selection_type == "roulette":  # krzyżowane dla selekcji z metodą ruletki
            sel_out = deepcopy(sel)
            for m in range(int(number_chromosome/2)):  # krzyżowanie kolejnych rodziców, tak by ich liczba była identyczna do istniejących już chromosomó
                flag = False
                while not flag:  # reszta kometarzy identyczna jak dla metody rankingowej
                    flag = True

                    k = np.random.randint(0, len(sel_out[0][:-1]), 2)
                    k = sorted(k)

                    for i in range(k[0], k[1]):
                        sel_out[2 * m][i], sel_out[2 * m + 1][i] = sel_out[2 * m][i], sel_out[2 * m + 1][i]

                    try:
                        self.__simulate_one_field(sel_out[2 * m])
                        self.__simulate_one_field(sel_out[2 * m + 1])

                    except IndexError:
                        # print('Nie spełnia ograniczenia jakości')
                        flag = False  # Ponowna próba

                    except ValueError:
                        # print('Nie spełnia ograniczenia innej rośliny w każdym roku')
                        flag = False  # Ponowna próba

                    if flag:
                        children.append(deepcopy(sel_out[2 * m]))
                        children.append(deepcopy(sel_out[2 * m+1]))
        return children

    def mutation(self, crossover):  #
        """procedura mutacji

        :param crossover:
        :return:
        """
        mutation = deepcopy(crossover)
        mutation_out = [i + [random.random()] for i in mutation] #prawdopodobieństwo mutacji
        j = 0
        for i in deepcopy(mutation_out):
            i_inp = deepcopy(i[:-1])
            income = self.__simulate_one_field(i_inp)
            if i[-1] >= 0.6:

                changes = math.ceil((i[-1] - 0.6)*len(i_inp)) #wyliczenie liczby zmian w mutacji
                best_mutations_for_one_chromosome = [] # lista w której będziemy dokonać zmiany
                max_income = -math.inf
                for _ in range(4): # podjęcie kilku prób mutacji
                    attempts = 0 #liczba prób uzyskania dodatniego zysku

                    mutations_for_one_chromosome = deepcopy(i_inp)  #lista w której będziemy dokonać zmiany
                    years = [] #lista zawierająca już podmienione lata
                    attempts_error = 0 #licznik powstrzymujący przed wejście w nieskończoną pętle

                    for _ in range(changes):
                        flag = False

                        while not flag:

                            flag = True
                            year = random.randrange(len(mutations_for_one_chromosome)) #dobieramy rok zmiany
                            for l in years:
                                if l == year:
                                    flag = False

                            curr_plant = mutations_for_one_chromosome[year]
                            rand_plant = random.choice([plant for plant in self.plants if plant != curr_plant])
                            mutations_for_one_chromosome[year] = rand_plant #podmieniamy dotychczasowy gen na wylosowany

                            try:
                                self.__simulate_one_field(mutations_for_one_chromosome)

                            except IndexError:
                                # print('Nie spełnia ograniczenia jakości')
                                attempts_error += 1
                                if attempts_error <= 1000:
                                    flag = False  # Ponowna próba
                                else:
                                    mutations_for_one_chromosome[year] = curr_plant  # przywracamy starą wartość
                                    flag = True

                            except ValueError:
                                # print('Nie spełnia ograniczenia innej rośliny w każdym roku')

                                attempts_error += 1
                                if attempts_error <= 1000:
                                    flag = False  # Ponowna próba
                                else:
                                    mutations_for_one_chromosome[year] = curr_plant  # przywracamy starą wartość
                                    flag = True

                            if flag:
                                income = self.__simulate_one_field(mutations_for_one_chromosome)

                                if income < 0 and attempts < 10: #sprawdzamy czy zysk nie jest ujemny i czy nie próbujemy już zbyt długo uzyskać dodatniego zysku
                                    mutations_for_one_chromosome[year] = curr_plant # przywracamy starą wartość
                                    attempts += 1 #zwiększamy licznik podejść
                                    flag = False
                                else:
                                    years.append(year) #dodajemy rok do już podmienionych
                            else:
                                mutations_for_one_chromosome[year] = curr_plant #jeśli flaga jest negatywna przywracamy dotychczasową wartość


                    income = self.__simulate_one_field(mutations_for_one_chromosome)
                    if income > max_income:
                        max_income = income
                        best_mutations_for_one_chromosome = deepcopy(mutations_for_one_chromosome)
                i_inp = deepcopy(best_mutations_for_one_chromosome)

                income = self.__simulate_one_field(best_mutations_for_one_chromosome)

            i_inp.append(income)
            mutation[j] = deepcopy(i_inp)
            j += 1

        return mutation

    def __simulate_one_field(self, decisons: list[str]):  # symulacja wartości zysków dla jednego pola
        for i in range(self.farm.yearsNumber - 1):
            if decisons[i + 1] != 'EMPTY':
                if decisons[i] == decisons[i + 1]:
                    raise ValueError

        earnings = 0

        for i in range(self.farm.yearsNumber):
            plant = decisons[i]

            if i != 0:
                self.farm.Q[i][self.field_number] = self.farm.Q[i - 1][self.field_number] - \
                                                    self.farm.plantInfluenceDict[decisons[i - 1]] \
                                                    if decisons[i - 1] != "EMPTY" else self.farm.Q[i - 1][self.field_number] - \
                                                    self.farm.plantInfluenceDict[decisons[i - 1]](self.farm.Q[i - 1][self.field_number])

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


def genetic_algorithm(farm: farm_simulation.FarmSimulation,
                      plants,
                      number_chromosome,
                      selection_type="roulette",
                      generation_quantity: int = 50):
    """

    :param farm:
    :param plants:
    :param number_chromosome:
    :param selection_type:
    :param generation_quantity:
    :return:
    """
    greedy_result = farm.solve_greedy()  # rozwiązanie konstrukcyjne

    farm.earnings = 0
    genetic_result = []
    beast_genetic_result = []
    beast_generation_number = []
    income_in_each_generation = [[None for _ in range(len(list(zip(*greedy_result[::-1]))))] for _ in range(generation_quantity)]
    field_number = 0

    for i in list(zip(*greedy_result[::-1])):  # transpozycja macierzy wyników greddy
        i = deepcopy(list(i))
        chromosomes = [i for _ in range(number_chromosome)]
        genetic = Genetic(chromosomes, plants, field_number, farm)
        genetic.initial_result()

        for generation_number in range(generation_quantity):

            if selection_type == "roulette":
                selection = genetic.selection_roulette(generation_number)
                children = genetic.crossover(selection, selection_type, number_chromosome)

            elif selection_type == "rank":
                selection = genetic.selection_rank(generation_number)
                children = genetic.crossover(selection, selection_type, number_chromosome)



            mutation = genetic.mutation(children)
            genetic.chromosome = deepcopy(mutation)


            income_in_each_generation[generation_number][field_number] = max([io[-1] for io in genetic.chromosome])

        max_earnings = max([io[-1] for io in genetic.chromosome])  # maksymalna ocena chromosomu dla ostatniej generacji
        for m in genetic.chromosome:
            if m[-1] == max_earnings:
                genetic_result.append(m)
                break


        beast_generation_number.append(genetic.best_generation_number)
        beast_genetic_result.append(genetic.best_chromosome)
        field_number += 1

    genetic_result = [i[:-1] for i in genetic_result]
    genetic_result = zip(*genetic_result[::])
    genetic_result = list(genetic_result)



    beast_genetic_result = [i[:-1] for i in beast_genetic_result]
    beast_genetic_result = zip(*beast_genetic_result[::])
    beast_genetic_result = list(beast_genetic_result)
    # print(


    farm.simulate_farm(genetic_result)

    farm.simulate_farm(beast_genetic_result)
    print("Numery poszczególnych generacji dla kolejnych pól dla których otrzymaliśmy najlepsze wyniki:")
    print(beast_generation_number)
    return farm.earnings, [sum(income_in_each_generation[t][:]) for t in range(generation_quantity)]
