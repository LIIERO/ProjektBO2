
# import numpy as np
from typing import NewType

Plant = NewType('Plant', str)
Earnings = NewType('Earnings', dict)
Degradation = NewType('Degradation', dict)

class FarmSimulation:
    def __init__(self, N: int, Y: int, T: float, P: float, D: list[float], C: dict[str], W: dict[str], G: dict[str]):
        # Inicjalizacja stałych modelu, mogą być różne dla różnych modeli ale nie zmieniają się w trakcie symulacji
        self.N, self.Y, self.T, self.P, self.D, self.C, self.W, self.G = N, Y, T, P, D, C, W, G

        self.curr_year: int = 0 # Aktualny rok
        self.earnings: float = 0 # Ilość naszych pieniędzy w PLN
        # self.Q = np.ndarray((Y, N)) # Macierz jakości gleby, do wypełnienia początkowymi wartościami
        # Zerowy rząd pełen początkowych jakości, reszta to zera
        MQ = 100 # Maksymalna jakość gleby
        self.Q: list[list[float]] = [[MQ]*N] + [[None]*N for _ in range(Y-1)]

        # self.X = np.ndarray((Y, N)) # Rozwiązanie
        self.X: list[list] = []



    def simulate_year_pass(self, yearly_decision: list[str]): #Prywatna metoda
        # self.X[y] = yearly_decision
        self.X.append(yearly_decision)

        for i in range(self.N): # self.Q[self.y][i] -> to musi być jako funkcja bo jakość gleby trzeba by zaokrąglić do intów
            if self.curr_year != 0: self.Q[self.curr_year][i] = self.Q[self.curr_year - 1][i] - self.W[self.X[self.curr_year - 1][i]]
            self.earnings += (self.Q[self.curr_year][i] * 0.01 * self.G[self.X[self.curr_year][i]]) - self.C[self.X[self.curr_year][i]] * self.P - self.D[i] * self.T
            self.curr_year += 1
            # print(i, self.curr_year)

    def simulate_farm(self, decision_matrix_X: list[list]): # Funkcja celu
        for y_dec in decision_matrix_X:
            self.simulate_year_pass(y_dec)
        return self.earnings


def main():
    N = 5
    Y = 5
    T = 0.5
    P = 5
    D = [1, 2, 3, 4, 5]
    C = {'potato': 200, 'wheat': 100, 'rye': 120}
    W = {'potato': 20, 'wheat': 10, 'rye': 15}
    G = {'potato': 400, 'wheat': 250, 'rye': 300}


    f_sim = FarmSimulation(N, Y, T, P, D, C, W, G)

    X = [['wheat', 'wheat', 'wheat', 'wheat', 'wheat'],
         ['wheat', 'wheat', 'wheat', 'wheat', 'wheat'],
         ['wheat', 'wheat', 'wheat', 'wheat', 'wheat'],
         ['wheat', 'wheat', 'wheat', 'wheat', 'wheat'],
         ['wheat', 'wheat', 'wheat', 'wheat', 'wheat']]

    print(f_sim.simulate_farm(X))

if __name__ == '__main__':
    main()
