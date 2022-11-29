import numpy as np
import math
import random
from typing import NewType, Union
from copy import deepcopy

"""Plant = NewType('Plant', str)
Earnings = NewType('Earnings', dict)
Degradation = NewType('Degradation', dict)"""

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
            if y_dec > 2:
                a = 4

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

    def simulated_annealing(self, s0: list[list], k_max):
        self.__reset_variables()

        s = deepcopy(s0) # Rozwiązanie początkowe
        for k in range(k_max):
            T = self.__annealing_temp(1 - ((k + 1) / k_max))
            s_new = self.__annealing_neig(s)

            '''print()
            for row in s_new:
                print(row)'''

            if self.__annealing_P(self.simulate_farm(s), self.simulate_farm(s_new), T) >= random.uniform(0, 1):
                s = deepcopy(s_new)

        return s

    @staticmethod
    def __annealing_temp(inp): # Funkcja obliczająca temperaturę
        if inp > 0:
            return inp # Najprostszy sposób
        else:
            return 0.01

    def __annealing_neig(self, s_inp): # Funkcja wyznaczająca sąsiednie rozwiązanie

        year = random.randrange(self.yearsNumber)
        field = random.randrange(self.fieldNumber)
        curr_plant = s_inp[year][field]
        rand_plant = random.choice([plant for plant in PLANTS if plant != curr_plant])

        s_out = deepcopy(s_inp)
        s_out[year][field] = rand_plant

        # Zabezpieczenie przed wybraniem niedozwolonego rozwiązania
        # if rand_plant != 'EMPTY':
            # if (year > 0 and s_inp[year - 1][field] == rand_plant) or (year < self.yearsNumber-1 and s_inp[year + 1][field] == rand_plant):

        try:
            self.simulate_farm(s_out)
        except IndexError:
            # print('Nie spełnia ograniczenia jakości')
            return self.__annealing_neig(s_inp) # Ponowna próba
        except ValueError:
            # print('Nie spełnia ograniczenia innej rośliny w każdym roku')
            return self.__annealing_neig(s_inp) # Ponowna próba

        return s_out

    @staticmethod
    def __annealing_P(e, e_dash, temp): # Funkcja akceptująca rozwiązanie, zmodyfikowana bo maksymalizujemy
        if e_dash > e: return 1
        else: return np.exp(((-1)*(e - e_dash))/temp)



def main():
    # Dane pozyskane z internetu:
    T = 6 / 15 * 8 * 2 * 7.546  # spalanie na godzine/predkośc*ile razy trzeba pojechać * 2 * cena paliwa

    Cwheat = (87.43 + 19.76) * 2.5 + (87.43 + 27.56) * 2 + (87.43 + 18.80) * 2 + (
                87.43 + 31.9) * 2.5 + 850 * 1.22 + 366 * 1.22 + 540 + 1458 + 1699 + 148 + 34
    Crye = (87.43 + 19.76) * 2 + (87.43 + 27.56) * 1.5 + (87.43 + 18.80) * 2 + (87.43 + 31.9) * 2.5 + 3000
    Cpotato = 2 * ((87.43 + 19.76) * 2.5 + (87.43 + 27.56) * 2 + (87.43 + 18.80) * 2 + (
                87.43 + 31.9) * 2.5) + 17519.3412754
    Ctriticale = (87.43 + 19.76) * 2.5 + (87.43 + 27.56) * 2 + (87.43 + 18.80) * 2 + (87.43 + 31.9) * 2.5 + 3573
    C = {'potato': Cpotato, 'wheat': Cwheat, 'rye': Crye, 'triticale': Ctriticale, 'EMPTY': 0}

    W = {'potato': 5, 'wheat': 8, 'rye': 3, 'triticale': 5, 'EMPTY': -5}

    G = {'potato': [], 'wheat': [], 'rye': [], 'triticale': [], 'EMPTY': []}
    for i in range(MQ):
        G['potato'].append(0 if i < 12 else (math.e ** ((i - 12) / 10) / 6002.91 * 17 + 24) * 710 + 558 + 1761.46)
        G['wheat'].append(0 if i < 35 else (math.e ** ((i - 35) / 10) / 601.845 * 10 + 3.9) * 1490 + 558)
        G['rye'].append((math.e ** (i / 10) / 19930.4 * 6 + 3) * 1150 + 558)
        G['triticale'].append(0 if i < 17 else (math.e ** ((i - 17) / 10) / 3640.95 * 9 + 3) * 1339 + 558)
        G['EMPTY'].append(40)

    # Dane dowolne:
    N = 5
    Y = 5

    P = [1.05, 4.14, 1.69, 1.81, 3.66]
    # P = [random.uniform(1, 6) for _ in range(N)]
    D = [2.08, 7.07, 8.42, 1.37, 6.60]
    # D = [random.uniform(0.1, 10) for _ in range(N)]
    b = [90, 34, 54, 5, 16]  # Początkowe jakości gleb na każdym polu
    # b = random.sample(range(0, MQ), N)

    # Symulacja
    f_sim = FarmSimulation(N, Y, T, P, D, C, W, G, b)

    X = [['wheat', 'wheat', 'wheat', 'wheat', 'wheat'],
         ['rye', 'rye', 'rye', 'rye', 'rye'],
         ['wheat', 'wheat', 'wheat', 'wheat', 'wheat'],
         ['rye', 'rye', 'rye', 'rye', 'rye'],
         ['wheat', 'wheat', 'wheat', 'wheat', 'wheat']]
    print('Przykład')
    f_sim.simulate_farm(X)  # Przykład dla samej pszenicy
    f_sim.display_solution()

    # Algorytm zachłanny
    print('Rozwiązanie algorytmu zachłannego')
    greedy_s = f_sim.solve_greedy()
    f_sim.display_solution()

    # Wyżarzanie
    iterations = 1000  # Maksymalna liczba iteracji

    print('Wyżarzanie dla rozwiązania począkowego zachłannego')
    sol = f_sim.simulated_annealing(greedy_s, iterations)
    f_sim.simulate_farm(sol)
    f_sim.display_solution()

    print('Wyżarzanie dla rozwiązania począkowego przykładowego')
    sol = f_sim.simulated_annealing(X, iterations)
    f_sim.simulate_farm(sol)
    f_sim.display_solution()


if __name__ == '__main__':
    main()
