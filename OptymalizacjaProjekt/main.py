
# import numpy as np
from typing import NewType

Plant = NewType('Plant', str)
Earnings = NewType('Earnings', dict)
Degradation = NewType('Degradation', dict)

plant_list = ['potato', 'wheat', 'rye', 'EMPTY'] # Empty - zostaw pole puste
MQ = 100 # Maksymalna jakość gleby

class FarmSimulation:
    def __init__(self, N: int, Y: int, T: float, P: float, D: list[float], C: dict[str], W: dict[str], G: dict[str]):
        # Inicjalizacja stałych modelu, mogą być różne dla różnych modeli ale nie zmieniają się w trakcie symulacji
        self.N, self.Y, self.T, self.P, self.D, self.C, self.W, self.G = N, Y, T, P, D, C, W, G

        self.curr_year: int = 0 # Aktualny rok
        self.earnings: float = 0 # Ilość naszych pieniędzy w PLN

        # TODO: Zmienne koszty transportu dla różnych roślin

        # self.Q = np.ndarray((Y, N)) # Macierz jakości gleby, do wypełnienia początkowymi wartościami
        # Zerowy rząd pełen początkowych jakości, reszta to zera
        # TODO: Ogarnąć degradację żeby miała sens i dodać ograniczenia
        self.Q: list[list[float]] = [[MQ]*N] + [[None]*N for _ in range(Y-1)]
        self.X: list[list] = []

    def __reset_variables(self):
        self.curr_year = 0
        self.earnings = 0
        self.Q = [[MQ] * self.N] + [[None] * self.N for _ in range(self.Y - 1)]
        self.X = []

    def __display_solution(self):
        print(f'Rozwiązanie dające dochód {self.earnings} zł')
        for row in self.X: print(row)
        print()

    def __simulate_year_pass(self, yearly_decision: list[str]):
        # self.X[y] = yearly_decision
        self.X.append(yearly_decision)
        for i in range(self.N): # self.Q[self.y][i] -> to musi być jako funkcja bo jakość gleby trzeba by zaokrąglić do intów
            if self.curr_year != 0: self.Q[self.curr_year][i] = self.Q[self.curr_year - 1][i] - self.W[self.X[self.curr_year - 1][i]]
            income = (self.Q[self.curr_year][i] * 0.01 * self.P * self.G[self.X[self.curr_year][i]])
            expense = (self.C[self.X[self.curr_year][i]] * self.P + self.D[i] * self.T)
            self.earnings += income - expense
        self.curr_year += 1

    def simulate_farm(self, decision_matrix_X: list[list]): # Funkcja celu
        self.__reset_variables()
        for y_dec in decision_matrix_X:
            self.__simulate_year_pass(y_dec)
        self.__display_solution()


    def solve_naive(self): # Znajduje najlepsze
        self.__reset_variables()
        for y_dec in range(self.Y):
            dec = []
            for no_field in range(self.N):
                pred_qual = MQ if y_dec == 0 else self.Q[self.curr_year - 1][no_field] - self.W[self.X[self.curr_year - 1][no_field]]
                best_plant, best_income = 'EMPTY', 0
                for plant in plant_list:
                    plant_inc = (pred_qual * 0.01 * self.P * self.G[plant]) - (self.C[plant] * self.P + self.D[no_field] * self.T)
                    if plant_inc > best_income:
                        best_plant, best_income = plant, plant_inc
                dec.append(best_plant)

            self.__simulate_year_pass(dec)
        self.__display_solution()


def main():
    # TODO: Ogarnąć rzeczywiste dane
    N = 5
    Y = 5
    T = 0.5
    P = 5
    D = [1, 2, 3, 4, 5]
    C = {'potato': 200, 'wheat': 100, 'rye': 120, 'EMPTY': 0}
    W = {'potato': 20, 'wheat': 10, 'rye': 15, 'EMPTY': -10}
    G = {'potato': 400, 'wheat': 250, 'rye': 300, 'EMPTY': 0}

    f_sim = FarmSimulation(N, Y, T, P, D, C, W, G)

    X = [['wheat', 'wheat', 'wheat', 'wheat', 'wheat'],
         ['wheat', 'wheat', 'wheat', 'wheat', 'wheat'],
         ['wheat', 'wheat', 'wheat', 'wheat', 'wheat'],
         ['wheat', 'wheat', 'wheat', 'wheat', 'wheat'],
         ['wheat', 'wheat', 'wheat', 'wheat', 'wheat']]

    f_sim.simulate_farm(X)
    f_sim.solve_naive()
if __name__ == '__main__':
    main()
