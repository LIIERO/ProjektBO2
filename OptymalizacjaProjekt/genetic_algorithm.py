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
        self.beast_chromosome = list([0])
        self.best_generation_number = 0

    def initial_result(self):  # inicjalizacja generacji 0

        chromosome = deepcopy(self.chromosome)
        chrom = deepcopy(chromosome[0])
        chrom.append(self.__simulate_one_field(chromosome[0]))
        chromosome[0] = chrom
        j = 1
        for i in deepcopy(chromosome[1:]):
            flag = False
            i_inp = deepcopy(i)
            attempts = 0
            while not flag:
                i = deepcopy(i_inp)
                flag = True
                year = random.randrange(len(i))
                curr_plant = i[year]
                rand_plant = random.choice([plant for plant in self.plants if plant != curr_plant])
                i[year] = rand_plant
                for l in chromosome:  # sprawdzenie czy dany chromosom nie jest już w generacji
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
                    chrom = deepcopy(i)
                    income = self.__simulate_one_field(i)
                    if income > 0 or attempts > 10:
                        chrom.append(income)
                        chromosome[j] = chrom
                        j += 1
                    else:
                        attempts += 1
                        flag = False
        self.chromosome = chromosome

    def selection_rank(self, generation_number):  # selekcja metodą rankingową
        self.chromosome.sort(key=lambda x: x[-1]) #sortowanie chromosomów w danej generacji
        if self.beast_chromosome[-1] < self.chromosome[-1][-1]:
            self.beast_chromosome = deepcopy(self.chromosome[-1])
            self.best_generation_number = generation_number
        chromosomes = deepcopy([i[:-1] for i in self.chromosome])
        return chromosomes[-1], chromosomes[-2] #wybór dwóch najlepszych wyników

    def selection_roulette(self, generation_number):  # selekcja metodą ruletki
        list_value_chromosome = [i[-1] for i in self.chromosome]
        max_val = max(list_value_chromosome)
        max_index = list_value_chromosome.index(max_val)
        if self.beast_chromosome[-1] < max_val:
            self.beast_chromosome = deepcopy(self.chromosome[max_index])
            self.best_generation_number = generation_number
        min_earnings = min(list_value_chromosome)
        if min_earnings < 0:  # jeśli mamy rozwiązanie o ujemnych dochodach
            sum_earnings = sum([i[-1] - min_earnings for i in self.chromosome])
            chromosome_probab = [(i[-1] - min_earnings) / sum_earnings for i in
                                 self.chromosome]  # szansa na wylosowanie danego chromosomu w ruletce
        else:
            sum_earnings = sum(list_value_chromosome)  # suma ocen wszystkich chromosonów w generacji
            chromosome_probab = [i[-1] / sum_earnings for i in
                                 self.chromosome]  # szansa na wylosowanie danego chromosomu w ruletce
        chromosomes = deepcopy([i[:-1] for i in self.chromosome])
        parent_index = np.random.choice(len(chromosomes), 2,
                                        p=chromosome_probab)  # wyselekcjowanie dwóch rodziców za pomocą ruletki
        return chromosomes[parent_index[0]], chromosomes[parent_index[1]]

    def crossover(self, selection):  # procedura krzyżowania
        sel = deepcopy(selection)
        flag = False
        while not flag:
            sel_out = deepcopy(sel)
            flag = True
            k = np.random.randint(0, len(sel_out[0]), 2)
            k = sorted(k)
            for i in range(k[0], k[1]):
                sel_out[0][i], sel_out[1][i] = sel_out[0][i], sel_out[1][i]
            try:
                self.__simulate_one_field(sel_out[0])
                self.__simulate_one_field(sel_out[1])
            except IndexError:
                # print('Nie spełnia ograniczenia jakości')
                flag = False  # Ponowna próba

            except ValueError:
                # print('Nie spełnia ograniczenia innej rośliny w każdym roku')
                flag = False  # Ponowna próba

            if flag:
                sel = deepcopy(sel_out)

        return sel

    def mutation(self, crossover):
        mutation = deepcopy(crossover)
        mutation = list(mutation)
        mutation_out = [mutation[0] if i < 3 else mutation[1] for i in range(6)]
        j = 0
        for i in deepcopy(mutation_out):
            flag = False
            i_inp = deepcopy(i)
            attempts = 0
            while not flag:
                i = deepcopy(i_inp)
                flag = True
                year = random.randrange(len(i))
                curr_plant = i[year]
                rand_plant = random.choice([plant for plant in self.plants if plant != curr_plant])
                i[year] = rand_plant
                if j >= 3:
                    for l in mutation_out[3:]:  # sprawdzenie czy dany chromosom nie jest już w generacji
                        if l[year] == i[year]:
                            flag = False
                else:
                    for l in mutation_out[:3]:  # sprawdzenie czy dany chromosom nie jest już w generacji
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
                        mutation_out[j] = mut
                        j += 1
                    else:
                        attempts += 1
                        flag = False

        return mutation_out

    def __simulate_one_field(self, decisons: list[str]):
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


def genetic_algorithm(farm: main.FarmSimulation, plants, selection_type="roulette"):
    greedy_result = farm.solve_greedy()
    j = 0
    farm.earnings = 0
    genetic_result = []
    beast_genetic_result = []
    beast_generation_number = []
    for i in list(zip(*greedy_result[::-1])):
        i = deepcopy(list(i))
        chromosomes = [i for _ in range(6)]
        genetic = Genetic(chromosomes, plants, j, farm)
        genetic.initial_result()
        for generation_number in range(100):
            if selection_type == "roulette":
                selection = genetic.selection_roulette(generation_number)
            elif selection_type == "rank":
                selection = genetic.selection_rank(generation_number)
            children = genetic.crossover(selection)
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
    print(f"Wynik z algorytmu genetycznego dla 100 pełnych pokoleń (z metodą selekcji: {selection_type}):")
    farm.simulate_farm(genetic_result)
    farm.display_solution()

    beast_genetic_result = [i[:-1] for i in beast_genetic_result]
    beast_genetic_result = zip(*beast_genetic_result[::])
    beast_genetic_result = list(beast_genetic_result)
    print(f"Najlepszy rozwiązanie który pojawiło się w trakcie trwania algorytmu genetycznego z metodą selekcji: {selection_type} (w {beast_generation_number} generacjach ) :")
    farm.simulate_farm(beast_genetic_result)
    farm.display_solution()
