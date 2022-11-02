
# import numpy as np

class FarmSimulation:
    def __init__(self, N: int, Y: int, T: float, P: float, D: list[float], C: dict[str], W: dict[str], G: list[dict[str]]):
        # Inicjalizacja stałych modelu, mogą być różne dla różnych modeli ale nie zmieniają się w trakcie symulacji
        self.N, self.Y, self.T, self.P, self.D, self.C, self.W, self.G = N, Y, T, P, D, C, W, G

        self.y: int = 0 # Aktualny rok
        self.earnings: float = 0 # Ilość naszych pieniędzy w PLN
        # self.Q = np.ndarray((Y, N)) # Macierz jakości gleby, do wypełnienia początkowymi wartościami
        # Zerowy rząd pełen początkowych jakości, reszta to zera
        self.Q: list[list]

        # self.X = np.ndarray((Y, N)) # Rozwiązanie
        self.X: list[list] = []

    def simulate_year_pass(self, yearly_decision: list[str]): #Prywatna metoda
        # self.X[y] = yearly_decision
        self.X.append(yearly_decision)

        for i in range(self.N): # self.Q[self.y][i] -> to musi być jako funkcja bo jakość gleby trzeba by zaokrąglić do intów
            self.earnings += self.G[self.Q[self.y][i]][self.X[self.y][i]] - self.C[self.X[self.y][i]] * self.P - self.D[i] * self.T
            if self.y != 0: self.Q[self.y][i] = self.Q[self.y - 1][i] + self.W[self.X[self.y - 1][i]]

            self.y += 1

    def simulate_farm(self, decision_matrix_X: list[list]): # Funkcja celu
        for y_dec in decision_matrix_X:
            self.simulate_year_pass(y_dec)
        return self.earnings


def main():
    pass

if __name__ == '__main__':
    main()
