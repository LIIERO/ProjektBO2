
# import numpy as np
import math
import random
from copy import deepcopy
from typing import NewType

Plant = NewType('Plant', str)
Earnings = NewType('Earnings', dict)
Degradation = NewType('Degradation', dict)

plant_list = ['potato', 'wheat', 'rye', 'triticale', 'EMPTY'] # Empty - zostaw pole puste
MQ = 100 # Maksymalna jakość gleby




class FarmSimulation:
    '''
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
    '''
    def __init__(self, N: int, Y: int, T: float, P: list[float], D: list[float], C: dict[str], W: dict[str], G: list[list[float]], S:dict[str]):
        # Inicjalizacja stałych modelu, mogą być różne dla różnych modeli ale nie zmieniają się w trakcie symulacji
        self.N, self.Y, self.T, self.P, self.D, self.C, self.W, self.G, self.S = N, Y, T, P, D, C, W, G, S

        self.curr_year: int = 0 # Aktualny rok
        self.earnings: float = 0 # Ilość naszych pieniędzy w PLN

        # TODO: Zmienne koszty transportu dla różnych roślin

        # self.Q = np.ndarray((Y, N)) # Macierz jakości gleby, do wypełnienia początkowymi wartościami
        # Zerowy rząd pełen początkowych jakości, reszta to zera
        # TODO: Ogarnąć degradację żeby miała sens i dodać ograniczenia
        b = random.sample(range(0, MQ), N)

        self.Q: list[list[int]] = [b] + [[None]*N for _ in range(Y-1)]
        global RQ
        RQ = deepcopy(self.Q)
        self.X: list[list] = []

    def __reset_variables(self):
        #funkcja resetująca układ do stanu początkowego
        self.curr_year = 0
        self.earnings = 0

        self.Q = deepcopy(RQ)
        self.X = []

    def __display_solution(self):
        print(f'Rozwiązanie dające dochód {self.earnings} zł')
        for row in self.X: print(row)
        print()
        for row in self.Q: print(row)

    def __simulate_year_pass(self, yearly_decision: list[str]):
        #funkcja realizujące funkcje celu
        # self.X[y] = yearly_decision
        self.X.append(yearly_decision)
        for i in range(self.N): # self.Q[self.y][i] -> to musi być jako funkcja bo jakość gleby trzeba by zaokrąglić do intów
            if self.curr_year != 0: self.Q[self.curr_year][i] = self.Q[self.curr_year - 1][i] - self.W[self.X[self.curr_year - 1][i]]

            income = (self.P[i] * self.G[self.S[self.X[self.curr_year][i]]][math.ceil(self.Q[self.curr_year][i])])

            expense = (self.C[self.X[self.curr_year][i]] * self.P[i] + self.D[i] * self.T)

            self.earnings += income - expense
        self.curr_year += 1

    def simulate_farm(self, decision_matrix_X: list[list]): # Funkcja celu
        self.__reset_variables()
        for y_dec in decision_matrix_X:
            a = RQ
            self.__simulate_year_pass(y_dec)
        self.__display_solution()


    def solve_naive(self): # Znajduje najlepsze
        self.__reset_variables()
        for y_dec in range(self.Y):
            dec = []
            for no_field in range(self.N):
                pred_qual = self.Q[0][no_field] if y_dec == 0 else self.Q[self.curr_year - 1][no_field] - self.W[self.X[self.curr_year - 1][no_field]]
                best_plant, best_income = 'EMPTY', 0
                for plant in plant_list:
                    if 0 <= (pred_qual - self.W[plant]) <= 100:
                        plant_inc = (self.P[no_field] * self.G[self.S[plant]][math.ceil(pred_qual)]) - (self.C[plant] * self.P[no_field] + self.D[no_field] * self.T)
                        if plant_inc > best_income:
                            best_plant, best_income = plant, plant_inc
                dec.append(best_plant)

            self.__simulate_year_pass(dec)
        self.__display_solution()


def main():
    # TODO: Ogarnąć rzeczywiste dane
    N = 5
    Y = 5
    T = 6/15*8*2*7.546 #spalanie na godzine/predkośc*ile razy trzeba pojechać * 2 * cena paliwa
    P = [random.uniform(1, 6) for _ in range(N)]
    D = [random.uniform(0.1, 10) for _ in range(N)]
    Cwheat = (87.43+19.76)*2.5 + (87.43+27.56)*2 + (87.43+18.80)*2 + (87.43+31.9)*2.5 + 850 * 1.22 + 366 * 1.22 + 540 + 1458 + 1699 + 148 + 34
    Crye = (87.43+19.76)*2 + (87.43+27.56)*1.5 + (87.43+18.80)*2 + (87.43+31.9)*2.5 + 3000
    Cpotato = 2*((87.43+19.76)*2.5 + (87.43+27.56)*2 + (87.43+18.80)*2 + (87.43+31.9)*2.5) +17519.3412754
    Ctriticale = (87.43+19.76)*2.5 + (87.43+27.56)*2 + (87.43+18.80)*2 + (87.43+31.9)*2.5 + 3573
    C = {'potato': Cpotato, 'wheat': Cwheat, 'rye': Crye, 'triticale': Ctriticale, 'EMPTY': 0}
    W = {'potato': 5, 'wheat': 8, 'rye': 3, 'triticale': 5, 'EMPTY': -5}
    G = []
    row_wheat = []
    row_rye = []
    row_triticale = []
    row_potato = []
    row_empty = []

    for i in range(100):
        if i < 12:
            row_potato.append(0)
        else:
            row_potato.append((math.e ** ((i - 12) / 10)/6002.91 * 16 + 24) * 700 + 558+1761.46)
    G.append(row_potato)

    for i in range(100):
        if i < 35:
                row_wheat.append(0)
        else:
            row_wheat.append((math.e**((i-35)/10)/601.845*8+3.84)*1450+558)
    G.append(row_wheat)
    for i in range(100):
            row_rye.append((math.e**(i/10)/19930.4*6+3)*1120+558)
    G.append(row_rye)
    for i in range(100):
        if i < 17:
                row_triticale.append(0)
        else:
            row_triticale.append((math.e**((i-17)/10)/3640.95*9+3)*1339+558)
    G.append(row_triticale)
    for i in range(100):
        row_empty.append(40)
    G.append(row_empty)
    S = {'potato': 0, 'wheat': 1, 'rye': 2, 'triticale': 3, 'EMPTY': 4}

    f_sim = FarmSimulation(N, Y, T, P, D, C, W, G, S)


    X = [['wheat', 'wheat', 'wheat', 'wheat', 'wheat'],
         ['wheat', 'wheat', 'wheat', 'wheat', 'wheat'],
         ['wheat', 'wheat', 'wheat', 'wheat', 'wheat'],
         ['wheat', 'wheat', 'wheat', 'wheat', 'wheat'],
         ['wheat', 'wheat', 'wheat', 'wheat', 'wheat']]

    f_sim.simulate_farm(X)
    # TODO Sprawdzić czemu nie bierze ziemniaków i pszenżyta
    f_sim.solve_naive()
if __name__ == '__main__':
    main()
