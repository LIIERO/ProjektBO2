import numpy as np
import math
import random
from typing import Union
from copy import deepcopy

PLANTS = ['potato', 'wheat', 'rye', 'triticale', 'EMPTY']
MQ = 100  # Maksymalna jakość gleby

class FarmSimulation:
    """
    fieldNumber, N - Liczba dostępnych pól uprawnych.
    yearsNumber, Y - Liczba lat planowania upraw.
    transportCost, T - Stały koszt dojazdu na kilometr
    fieldsSurfacesList, P - Lista powierzchnii poszczególnych pól uprawnych w hektarach
    distanceMatrix, D - Lista odległości poszczególnych pól od gospodarstwa
    productionCostDict - Słownik kosztów produkcji danej rosliny na jeden hektar (koszt materiału siewnego,
        koszt pracy ludzkiej, itp.)
    plantInfluenceDict, W - Słownik wpływów poszczególnych upraw na glebe
    earningsMatrix, G - Macierz zysków z danej uprawy.
    Q - Macierz jakości gleby na danym polu w danym roku
    decisionMatrix, X - Macierz decyzyjna zawieracjąca informacje o wybranych roślinach do uprawy na dany polu w danym
        roku
    S - Słownik zamieniający nazwę roślny na przydzielony jej indeks
    """

    def __init__(self, N: int, Y: int, T: float, P: list[float], D: list[float], C: dict[str], W: dict[str],
                 G: dict[str], start_quality: list[int]):
        # Inicjalizacja stałych modelu, mogą być różne dla różnych modeli ale nie zmieniają się w trakcie symulacji
        self.fieldNumber = N
        self.yearsNumber = Y
        self.transportCost = T
        self.fieldsSurfacesList = P
        self.distanceMatrix = D
        self.productionCostDict = C
        self.plantInfluenceDict = W
        self.earningsMatrix = G
        self.b = start_quality

        self.curr_year: int = 0  # Aktualny rok
        self.earnings: float = 0  # Ilość naszych pieniędzy w PLN

        # Zerowy rząd pełen początkowych jakości, reszta to zera
        self.Q: list[list[Union[int, None]]] = [self.b] + [[None] * N for _ in range(Y - 1)]
        self.decisionMatrix: list[list[str]] = []

    def __reset_variables(self):  # Funkcja resetująca model do stanu początkowego
        self.curr_year = 0
        self.earnings = 0
        self.Q = [self.b] + [[None] * self.fieldNumber for _ in range(self.yearsNumber - 1)]
        self.decisionMatrix = []

    def display_solution(self):
        print('\nRozwiązanie dające dochód {:.2f} zł'.format(self.earnings))
        for row in self.decisionMatrix: print(row)
        print('\nMacierz jakości gleb pól na przestrzeni lat')
        for row in self.Q: print(row)
        print()

    def __simulate_year_pass(self, yearly_decision: list[str]):
        if len(self.decisionMatrix) > 0:
            for prev, cur in zip(self.decisionMatrix[-1], yearly_decision):
                if cur != 'EMPTY':
                    if prev == cur:
                        raise ValueError

        self.decisionMatrix.append(yearly_decision)

        for i in range(self.fieldNumber):
            plant = self.decisionMatrix[self.curr_year][i]

            if self.curr_year != 0:
                self.Q[self.curr_year][i] = self.Q[self.curr_year - 1][i] - self.plantInfluenceDict[
                    self.decisionMatrix[self.curr_year - 1][i]]
                if self.Q[self.curr_year][i] < 0:
                    raise IndexError
                income = 0 if self.decisionMatrix[self.curr_year - 1][i] == plant == 'EMPTY' else (
                        self.fieldsSurfacesList[i] * self.earningsMatrix[plant][math.ceil(self.Q[self.curr_year][i])])
            else:
                income = self.fieldsSurfacesList[i] * self.earningsMatrix[plant][math.ceil(self.Q[self.curr_year][i])]

            expense = 0 if plant == 'EMPTY' else (
                        self.productionCostDict[plant] * self.fieldsSurfacesList[i] + self.distanceMatrix[
                    i] * self.transportCost)  # Jeśli nic nie siejemy to nie ponosimy kosztów

            self.earnings += income - expense
            # print(self.Q[self.curr_year][i], plant, income, expense)
        self.curr_year += 1

    def simulate_farm(self, decision_matrix_X: list[list]):  # Funkcja celu
        self.__reset_variables()

        for y_dec in decision_matrix_X:
            self.__simulate_year_pass(y_dec)

        return self.earnings # Ma zwracać rozwiązanie

    def solve_greedy(self):  # Algorytm zachłanny - w każdym roku bierze to co da w nim największy zarobek
        self.__reset_variables()
        for y_dec in range(self.yearsNumber):

            dec = []
            for no_field in range(self.fieldNumber):
                pred_qual = self.Q[0][no_field] if y_dec == 0 else self.Q[self.curr_year - 1][no_field] - \
                                                                   self.plantInfluenceDict[
                                                                       self.decisionMatrix[self.curr_year - 1][
                                                                           no_field]]
                best_plant, best_income = 'NONE', -math.inf

                for plant in PLANTS:
                    if 0 <= (pred_qual - self.plantInfluenceDict[plant]) <= MQ:
                        if plant == 'EMPTY':
                            plant_inc = (self.fieldsSurfacesList[no_field] * self.earningsMatrix[plant][
                                math.ceil(pred_qual)])

                            if y_dec > 0 and plant == self.decisionMatrix[y_dec - 1][no_field]:
                                plant_inc = 0

                        elif y_dec == 0 or (y_dec > 0 and plant != self.decisionMatrix[y_dec - 1][no_field]):
                            plant_inc = (self.fieldsSurfacesList[no_field] * self.earningsMatrix[plant][
                                math.ceil(pred_qual)]) - (
                                                    self.productionCostDict[plant] * self.fieldsSurfacesList[no_field] +
                                                    self.distanceMatrix[no_field] * self.transportCost)

                        else:
                            plant_inc = -math.inf

                        if plant_inc > best_income:
                            best_plant, best_income = plant, plant_inc

                dec.append(best_plant)

            self.__simulate_year_pass(dec)
        return self.decisionMatrix

    def simulated_annealing(self, s0: list[list], k_max, stages): # Symulowane wyżarzanie
        self.__reset_variables()
        beast_s = deepcopy(s0) # Rozwiązanie najlepsze (rozwiązanie bestialskie)
        s = deepcopy(s0) # Rozwiązanie początkowe

        for k in range(k_max):
            if k_max >= 0.99**k:
                year = random.randrange(self.yearsNumber)
                field = random.randrange(self.fieldNumber)
                T = self.__annealing_temp(k, k_max)
                for _ in range(stages):
                    s_new = self.__annealing_neig(s, k_max, T, year, field)
                    if self.simulate_farm(s_new[0]) > self.simulate_farm(beast_s):
                        beast_s = s_new[0]
                    if self.__annealing_P(self.simulate_farm(s), self.simulate_farm(s_new[0]), T) >= random.uniform(0, 1):
                        s = deepcopy(s_new[0])
                        year = s_new[1]
                        field = s_new[2]
            else:
                break

        return beast_s

    @staticmethod
    def __annealing_temp(inp, k_m): # Funkcja obliczająca temperaturę
        return k_m * 0.99**inp # Najprostszy sposób

    def __annealing_neig(self, s_inp, k_m, T, last_year, last_field): # Funkcja wyznaczająca sąsiednie rozwiązanie
        range_year = self.__range_builder(last_year-T*self.yearsNumber/(2*k_m), last_year+T*self.yearsNumber/(2*k_m), self.yearsNumber)
        range_field = self.__range_builder(last_field-T*self.fieldNumber/(2*k_m), last_field+T*self.fieldNumber/(2*k_m), self.fieldNumber)
        year = random.randrange(range_year[0], range_year[1])
        field = random.randrange(range_field[0], range_field[1])
        curr_plant = s_inp[year][field]
        self.simulate_farm(s_inp)

        rand_plant = random.choice([plant for plant in PLANTS if plant != curr_plant or plant == "EMPTY"])
        if year > 0:
            while (self.Q[year - 1][field] - self.plantInfluenceDict[rand_plant]) < 0:
                rand_plant = random.choice([plant for plant in PLANTS if plant != curr_plant or plant == "EMPTY"])

        s_out = deepcopy(s_inp)
        s_out[year][field] = rand_plant

        # Zabezpieczenie przed wybraniem niedozwolonego rozwiązania
        # if rand_plant != 'EMPTY':
            # if (year > 0 and s_inp[year - 1][field] == rand_plant) or (year < self.yearsNumber-1 and s_inp[year + 1][field] == rand_plant):
        try:
            self.simulate_farm(s_out)
        except IndexError:
            # print('Nie spełnia ograniczenia jakości')
            return self.__annealing_neig(s_inp, k_m, T, last_year, last_field) # Ponowna próba
        except ValueError:
            # print('Nie spełnia ograniczenia innej rośliny w każdym roku')
            return self.__annealing_neig(s_inp, k_m, T, last_year, last_field) # Ponowna próba

        return s_out, year, field

    @staticmethod
    def __range_builder(lower, higher, max_number):
        lower = int(lower)
        higher = int(higher)
        if lower == higher:
            lower -= 1
            higher += 1
        if lower < 0:
            lower = 0
        if higher > max_number:
            higher = max_number

        return [lower, higher]

    @staticmethod
    def __annealing_P(e, e_dash, temp): # Funkcja akceptująca rozwiązanie, zmodyfikowana bo maksymalizujemy
        if e_dash > e:
            return 1
        else:
            return np.exp(((-1)*(e - e_dash))/temp)