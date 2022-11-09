
# import numpy as np
import math
import random
from typing import NewType, Union

"""Plant = NewType('Plant', str)
Earnings = NewType('Earnings', dict)
Degradation = NewType('Degradation', dict)"""

PLANTS = ('potato', 'wheat', 'rye', 'triticale', 'EMPTY')
MQ = 100 # Maksymalna jakość gleby

class FarmSimulation:
    """
    N - Liczba dostępnych pól uprawnych.
    Y - Liczba lat planowania upraw.
    T - Stały koszt dojazdu na kilometr
    P - Lista powierzchnii poszczególnych pól uprawnyvh w hektarach
    D - Lista odległości poszczególnych pól od gospodarstwa
    C - Słownik kosztów produkcji danej rosliny na jeden hektar (koszt materiału siewnego,
    koszt pracy ludzkiej, itp.)
    W- Słownik wpływów poszczególnych upraw na glebe
    G - Macierz zysków z danej uprawy.
    Q - Macierz jakości gleby na danym polu w danym roku
    X - Macierz decyzyjna zawieracjąca informacje o wybranych roślinach do uprawy na dany polu w danym roku
    S - Słownik zamieniający nazwę roślny na przydzielony jej indeks
    """
    def __init__(self, N: int, Y: int, T: float, P: list[float], D: list[float], C: dict[str], W: dict[str], G: dict[str], start_quality: list[int]):
        # Inicjalizacja stałych modelu, mogą być różne dla różnych modeli ale nie zmieniają się w trakcie symulacji
        self.N, self.Y, self.T, self.P, self.D, self.C, self.W, self.G, self.b  = N, Y, T, P, D, C, W, G, start_quality

        self.curr_year: int = 0 # Aktualny rok
        self.earnings: float = 0 # Ilość naszych pieniędzy w PLN

        # Zerowy rząd pełen początkowych jakości, reszta to zera
        self.Q: list[list[Union[int, None]]] = [self.b] + [[None]*N for _ in range(Y-1)]
        self.X: list[list[str]] = []

    def __reset_variables(self): # Funkcja resetująca model do stanu początkowego
        self.curr_year = 0
        self.earnings = 0
        self.Q = [self.b] + [[None]*self.N for _ in range(self.Y-1)]
        self.X = []

    def __display_solution(self):
        print('\nRozwiązanie dające dochód {:.2f} zł'.format(self.earnings))
        for row in self.X: print(row)
        print('\nMacierz jakości gleb pól na przestrzeni lat')
        for row in self.Q: print(row)
        print()

    def __simulate_year_pass(self, yearly_decision: list[str]):
        inc_from_empty = True
        if len(self.X) > 0:
            for prev, cur in zip(self.X[-1], yearly_decision):
                if cur != 'EMPTY':
                    if prev == cur: raise ValueError
                elif prev == 'EMPTY':
                    inc_from_empty = False

        self.X.append(yearly_decision)
        for i in range(self.N):
            if self.curr_year != 0: self.Q[self.curr_year][i] = self.Q[self.curr_year - 1][i] - self.W[self.X[self.curr_year - 1][i]]
            plant = self.X[self.curr_year][i]

            income = (self.P[i] * self.G[plant][math.ceil(self.Q[self.curr_year][i])]) if inc_from_empty else 0
            expense = 0 if plant == 'EMPTY' else (self.C[plant] * self.P[i] + self.D[i] * self.T) # Jeśli nic nie siejemy to nie ponosimy kosztów

            self.earnings += income - expense
            # print(self.Q[self.curr_year][i], plant, income, expense)
        self.curr_year += 1

    def simulate_farm(self, decision_matrix_X: list[list]): # Funkcja celu
        self.__reset_variables()
        for y_dec in decision_matrix_X:
            self.__simulate_year_pass(y_dec)
        self.__display_solution()

    def solve_greedy(self): # Algorytm zachłanny - w każdym roku bierze to co da w nim największy zarobek
        self.__reset_variables()
        for y_dec in range(self.Y):
            dec = []
            for no_field in range(self.N):
                pred_qual = self.Q[0][no_field] if y_dec == 0 else self.Q[self.curr_year - 1][no_field] - self.W[self.X[self.curr_year - 1][no_field]]
                best_plant, best_income = 'NONE', -math.inf
                for plant in PLANTS:
                    if 0 <= (pred_qual - self.W[plant]) <= MQ:
                        if plant == 'EMPTY':
                            plant_inc = (self.P[no_field] * self.G[plant][math.ceil(pred_qual)])
                            if y_dec > 0 and plant == self.X[y_dec - 1][no_field]: plant_inc = 0
                        elif y_dec == 0 or (y_dec > 0 and plant != self.X[y_dec - 1][no_field]):
                            plant_inc = (self.P[no_field] * self.G[plant][math.ceil(pred_qual)]) - (self.C[plant] * self.P[no_field] + self.D[no_field] * self.T)
                        else: plant_inc = -math.inf
                        if plant_inc > best_income:
                            best_plant, best_income = plant, plant_inc

                dec.append(best_plant)

            self.__simulate_year_pass(dec)
        self.__display_solution()


def main():

    # Dane pozyskane z internetu:
    T = 6/15*8*2*7.546 #spalanie na godzine/predkośc*ile razy trzeba pojechać * 2 * cena paliwa

    Cwheat = (87.43+19.76)*2.5 + (87.43+27.56)*2 + (87.43+18.80)*2 + (87.43+31.9)*2.5 + 850 * 1.22 + 366 * 1.22 + 540 + 1458 + 1699 + 148 + 34
    Crye = (87.43+19.76)*2 + (87.43+27.56)*1.5 + (87.43+18.80)*2 + (87.43+31.9)*2.5 + 3000
    Cpotato = 2*((87.43+19.76)*2.5 + (87.43+27.56)*2 + (87.43+18.80)*2 + (87.43+31.9)*2.5) +17519.3412754
    Ctriticale = (87.43+19.76)*2.5 + (87.43+27.56)*2 + (87.43+18.80)*2 + (87.43+31.9)*2.5 + 3573
    C = {'potato': Cpotato, 'wheat': Cwheat, 'rye': Crye, 'triticale': Ctriticale, 'EMPTY': 0}

    W = {'potato': 5, 'wheat': 8, 'rye': 3, 'triticale': 5, 'EMPTY': -5}

    G = {'potato': [], 'wheat': [], 'rye': [], 'triticale': [], 'EMPTY': []}
    for i in range(MQ):
        G['potato'].append(0 if i < 12 else (math.e ** ((i - 12) / 10)/6002.91 * 17 + 24) * 710 + 558+1761.46)
        G['wheat'].append(0 if i < 35 else (math.e**((i-35)/10)/601.845*10+3.9)*1490+558)
        G['rye'].append((math.e**(i/10)/19930.4*6+3)*1150+558)
        G['triticale'].append(0 if i < 17 else (math.e**((i-17)/10)/3640.95*9+3)*1339+558)
        G['EMPTY'].append(40)

    # Dane dowolne:
    N = 5
    Y = 5

    P = [1.05, 4.14, 1.69, 1.81, 3.66]
    # P = [random.uniform(1, 6) for _ in range(N)]
    D = [2.08, 7.07, 8.42, 1.37, 6.60]
    # D = [random.uniform(0.1, 10) for _ in range(N)]
    b = [90, 34, 54, 5, 16] # Początkowe jakości gleb na każdym polu
    # b = random.sample(range(0, MQ), N)


    # Symulacja
    f_sim = FarmSimulation(N, Y, T, P, D, C, W, G, b)

    X = [['wheat', 'wheat', 'wheat', 'wheat', 'wheat'],
         ['rye', 'rye', 'rye', 'rye', 'rye'],
         ['wheat', 'wheat', 'wheat', 'wheat', 'wheat'],
         ['rye', 'rye', 'rye', 'rye', 'rye'],
         ['wheat', 'wheat', 'wheat', 'wheat', 'wheat']]
    f_sim.simulate_farm(X) # Przykład dla samej pszenicy

    # Algorytm zachłanny
    f_sim.solve_greedy()

if __name__ == '__main__':
    main()
