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
    def initial_result(self): #inicjalizacja generacji 0

        chromosome = deepcopy(self.chromosome)
        chrom = deepcopy(chromosome[0])
        chrom.append(self.__simulate_one_field(chromosome[0]))
        chromosome[0] = chrom
        j = 1
        for i in deepcopy(chromosome[1:]):
            flag = False
            i_inp = deepcopy(i)
            while not flag:
                i = deepcopy(i_inp)
                flag = True
                year = random.randrange(len(i))
                curr_plant = i[year]
                rand_plant = random.choice([plant for plant in self.plants if plant != curr_plant])
                i[year] = rand_plant
                for l in chromosome: #sprawdzenie czy dany chromosom nie jest już w generacji
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
                    chrom.append(self.__simulate_one_field(i))
                    chromosome[j] = chrom
                    j += 1
        self.chromosome = chromosome

    def selection(self): #selekcja metodą ruletki
        sum_earnings = sum([i[-1] for i in self.chromosome]) #suma ocen wszystkich chromosonów w generacji
        chromosome_probab = [i[-1]/sum_earnings for i in self.chromosome] # szansa na wylosowanie danego chromosomu w ruletce
        chromosomes = deepcopy([i[:-1] for i in self.chromosome])
        parent_index = np.random.choice(len(chromosomes), 2, p=chromosome_probab) #wyselekcjowanie dwóch rodziców za pomocą ruletki
        return chromosomes[parent_index[0]], chromosomes[parent_index[1]]

    def crossover(self, selection): #procedura krzyżowania
        first, second = deepcopy(selection)
        k = np.random.randint(0, len(first), 2)
        k = sorted(k)
        for i in range(k[0], k[1]):
            first[i], second[i] = second[i], first[i]
        return first, second


    def __simulate_one_field(self, decisons: list[str]):
        for i in range(self.farm.yearsNumber-1):
            if decisons[i+1] != 'EMPTY':
                if decisons[i] == decisons[i+1]:
                    raise ValueError
        earnings = 0
        for i in range(self.farm.yearsNumber):
            plant = decisons[i]
            if i != 0:
                self.farm.Q[i][self.field_number] = self.farm.Q[i-1][self.field_number] - self.farm.plantInfluenceDict[decisons[i-1]]

                if self.farm.Q[i][self.field_number] < 0:
                    raise IndexError
                income = 0 if decisons[i - 1][self.field_number] == plant == 'EMPTY' else (
                        self.farm.fieldsSurfacesList[self.field_number] * self.farm.earningsMatrix[plant][math.ceil(self.farm.Q[i][self.field_number])])
            else:
                income = self.farm.fieldsSurfacesList[self.field_number]*self.farm.earningsMatrix[plant][math.ceil(self.farm.Q[i][self.field_number])]

            expense = 0 if plant == 'EMPTY' else (self.farm.productionCostDict[plant] * self.farm.fieldsSurfacesList[self.field_number] +
                                                  self.farm.distanceMatrix[
                                                      self.field_number] * self.farm.transportCost)  # Jeśli nic nie siejemy to nie ponosimy kosztów
            earnings += income - expense
        return earnings


def genetic_algorithm(farm: main.FarmSimulation, plants):
    greedy_result = farm.solve_greedy()
    j = 0
    farm.earnings = 0
    for i in list(zip(*greedy_result[::-1])):
        i = deepcopy(list(i))
        chromosomes = [i for _ in range(5)]
        genetic = Genetic(chromosomes, plants, j, farm)
        genetic.initial_result()
        selection = genetic.selection()
        childs = genetic.crossover(selection)
        print(43)
        j += 1


