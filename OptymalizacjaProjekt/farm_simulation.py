import numpy as np
import math
import random
from typing import NewType, Union
from copy import deepcopy

"""Plant = NewType('Plant', str)
Earnings = NewType('Earnings', dict)
Degradation = NewType('Degradation', dict)"""

PLANTS = ['potato', 'wheat', 'rye', 'triticale', 'pickled_corn', 'corn', 'rape', 'EMPTY']
MQ = 100  # Maksymalna jakość gleby

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


class FarmSimulation(object):
    """ Klasa symulująca gospodarstwo w problemie

    """
    def __init__(self, N: int, Y: int, T: float, P: list[float], D: list[float], C: dict[str], W: dict[str],
                 G: dict[str], start_quality: list[int]):
        """Inicjalizacja stałych modelu, mogą być różne dla różnych modeli ale nie zmieniają się w trakcie symulacji

        zmienna Q - macierz jakości gleby w danym roku na danym polu

        zmienna decisionMatrix - macierz zmiennych decyzyjnych

        :param N: fieldNumber - Liczba dostępnych pól uprawnych.
        :param Y: yearsNumber - Liczba lat planowania upraw
        :param T: transportCost - Stały koszt dojazdu na kilometr
        :param P: fieldsSurfacesList - Lista powierzchnii poszczególnych pól uprawnych w hektarach
        :param D: distanceMatrix - Lista odległości poszczególnych pól od gospodarstwa
        :param C: productionCostDict - Słownik kosztów produkcji danej rosliny na jeden hektar (koszt materiału
            siewnego, koszt pracy ludzkiej, itp.)
        :param W: plantInfluenceDict - Słownik wpływów poszczególnych upraw na glebe
        :param G: earningsMatrix - Macierz zysków z danej uprawy.
        :param start_quality: b - macierz początkowych jakości gleb
        :returns: None
        """
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

        # zmiewnna Q - macierz jakości gleby w danym roku na danym polu
        # Zerowy rząd pełen początkowych jakości, reszta to zera
        self.Q: list[list[Union[int, None]]] = [self.b] + [[None] * N for _ in range(Y - 1)]

        # macierz zmiennych decyzyjnych
        self.decisionMatrix: list[list[str]] = []

    def __reset_variables(self) -> None:
        """Funkcja resetująca model do stanu początkowego, bez inicjowania nowego obiektu

        :arg: None
        :returns: None
        """
        self.curr_year = 0
        self.earnings = 0
        self.Q = [self.b] + [[None] * self.fieldNumber for _ in range(self.yearsNumber - 1)]
        self.decisionMatrix = []

    def display_solution(self) -> None:
        """ Funkcja do wyświetlania rozwiązań

        :return: None
        """
        print('\nRozwiązanie dające dochód {:.2f} zł'.format(self.earnings))
        for row in self.decisionMatrix:
            print(row)
        print('\nMacierz jakości gleb pól na przestrzeni lat')
        for row in self.Q:
            print(row)
        print()

    def __simulate_year_pass(self, yearly_decision: list[str]) -> None:
        """ Metoda symulująca przejście roku na farmie na podstawie decyzji w roku,

        aktualizacja macierzy jakości gleb Q

        aktualizacja

        :param yearly_decision: lista (wiersz) roślin jakie tego roku zasadziliśmy na poszczególnych polach
        :return: None
        """

        # dodatkowy warunek logiczny zapewniający że puste pole nie powtatrza się dwa razy pod rząd
        if len(self.decisionMatrix) > 0:
            for prev, cur in zip(self.decisionMatrix[-1], yearly_decision):
                if cur != 'EMPTY':
                    if prev == cur:
                        raise ValueError

        # po zapewnieniu zgodności dodajemy nasze rozwiązanie do macierzy decyzyjnej
        self.decisionMatrix.append(yearly_decision)

        # przejście po wszystkich polach w roku
        for i in range(self.fieldNumber):
            plant = self.decisionMatrix[self.curr_year][i]

            # aktualizacja jakości gleby na danym polu po uprawie rośliny (nie zerowy rok)
            if self.curr_year != 0:
                # odjęcie jakości po uprawie rośliny w tym roku od jakości z poprzedniego roku
                self.Q[self.curr_year][i] = self.Q[self.curr_year - 1][i] - self.plantInfluenceDict[
                    self.decisionMatrix[self.curr_year - 1][i]] if self.decisionMatrix[self.curr_year - 1][i] != 'EMPTY' \
                    else self.Q[self.curr_year - 1][i] - self.plantInfluenceDict[
                    self.decisionMatrix[self.curr_year - 1][i]](self.Q[self.curr_year - 1][i])

                # zabezpieczenie przed spadkiem jakości poniżej dolnej granicy (<0)
                if self.Q[self.curr_year][i] < 0:
                    raise IndexError

                # obliczanie przychodu, jeśli dwa razy nie uprawiamy to zerowy przychód
                income = 0 if self.decisionMatrix[self.curr_year - 1][i] == plant == 'EMPTY' else (
                        self.fieldsSurfacesList[i] * self.earningsMatrix[plant][math.ceil(self.Q[self.curr_year][i])])

            else:
                # obliczanie przychodu jeśli rok zerowy, nie trzeba sprawdzać poprzedniego roku
                income = self.fieldsSurfacesList[i] * self.earningsMatrix[plant][math.ceil(self.Q[self.curr_year][i])]

            # obliczanie kosztów uprawy w obecnym roku
            expense = 0 if plant == 'EMPTY' else (self.productionCostDict[plant] * self.fieldsSurfacesList[i] +
                                                  self.distanceMatrix[
                                                      i] * self.transportCost)  # Jeśli nic nie siejemy to nie ponosimy kosztów

            # od łącznego przychodu trzeba odjąć wydatki
            self.earnings += income - expense

        # następny rok, aktualizacja countera
        self.curr_year += 1

    def simulate_farm(self, decision_matrix_X: list[list]):
        """ Funkcja symulująca zyski z hodowli przez kilka lat (z określonej liczby pól), tożsama z funkcją celu w
        modelu matematycznym

        :param decision_matrix_X:
        :return:
        """
        self.__reset_variables()

        # przejście przez wszystkie wiersze (lata)
        for y_dec in decision_matrix_X:
            #
            self.__simulate_year_pass(y_dec)

        return self.earnings  # Ma zwracać rozwiązanie

    def solve_greedy(self) -> list[list[str]]:
        """Algorytm zachłanny - w każdym roku bierze to co da w nim największy zarobek

        :return self.decisionMatrix:
        """
        self.__reset_variables()
        for y_dec in range(self.yearsNumber):

            dec = []
            for no_field in range(self.fieldNumber):
                pred_qual = self.Q[0][no_field] if y_dec == 0 else self.Q[self.curr_year - 1][no_field] - \
                                                                   self.plantInfluenceDict[
                                                                       self.decisionMatrix[self.curr_year - 1][
                                                                           no_field]] if \
                self.decisionMatrix[self.curr_year - 1][
                    no_field] != 'EMPTY' else self.Q[self.curr_year - 1][no_field] - \
                                              self.plantInfluenceDict[
                                                  self.decisionMatrix[self.curr_year - 1][
                                                      no_field]](self.Q[self.curr_year - 1][no_field])
                best_plant, best_income = 'NONE', -math.inf

                for plant in PLANTS:

                    if plant == 'EMPTY':
                        if y_dec != 0:
                            if not 0 <= (pred_qual - self.plantInfluenceDict[plant](self.Q[y_dec - 1][no_field])) <= MQ:
                                break
                        plant_inc = (self.fieldsSurfacesList[no_field] * self.earningsMatrix[plant][
                            math.ceil(pred_qual)])

                        if y_dec > 0 and plant == self.decisionMatrix[y_dec - 1][no_field]:
                            plant_inc = 0
                        if plant_inc > best_income:
                            best_plant, best_income = plant, plant_inc
                    elif 0 <= (pred_qual - self.plantInfluenceDict[plant]) <= MQ and plant != "EMPTY":

                        if y_dec == 0 or (y_dec > 0 and plant != self.decisionMatrix[y_dec - 1][no_field]):
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

    def simulated_annealing(self, s0: list[list], k_max):  # Symulowane wyżarzanie
        """Nasza implementaacja algorytmu symulowanego wyżarzania

        :param s0:
        :param k_max:
        :return: best_s:
        """
        # upewniamy się że zmienne są początkowe
        self.__reset_variables()

        best_s = deepcopy(s0)  # Rozwiązanie najlepsze
        s = deepcopy(s0)  # Rozwiązanie początkowe
        solutions = [self.simulate_farm(s0)] + [-1]*(k_max - 1) # Lista będąca zapisem przebiegu wartości rozwiązań do wyświetlenia na wykresie
        i = 1
        for k in range(k_max-1, 0, -1):

            # przypisywanie nowej temperatury co iteracje
            T = self.__annealing_temp(k, k_max)
            s_new = self.__annealing_neig(s)

            solutions[i] = self.simulate_farm(s)  # Zapis rozwiązania w każdej iteracji

            if self.simulate_farm(s_new) > self.simulate_farm(best_s):
                best_s = deepcopy(s_new)

            if self.__annealing_P(self.simulate_farm(s), self.simulate_farm(s_new), T) >= random.uniform(0, 1):
                s = deepcopy(s_new)

            i += 1
        return best_s, solutions

    @staticmethod
    def __annealing_temp(inp, k_max):
        """Funkcja obliczająca temperaturę w algorytmie symulowanego wyżarzania

        :param inp: wyrażenie (1 - (k + 1)/k_max)
        :param k_max: maxymalna liczba iteracji pętli for w głównej metodzie algorytmu SA
        :return: temperatura
        """
        if inp >= 0:
            return inp  # Najprostszy sposób

        else:
            return 1 / k_max

    def __annealing_neig(self, s_inp):
        """Funkcja wyznaczająca sąsiednie/nowe rozwiązanie

        :param s_inp: macierz decyzji/obecne rozwiązanie
        :return s_out: Kandydat na nowe rozwiązanie
        """
        # w sposób pseudo losowy dobieramy rok i pole
        year = random.randrange(self.yearsNumber)
        field = random.randrange(self.fieldNumber)
        curr_plant = s_inp[year][field]

        # losowe przyjęcie rośliny pod warunkiem że jest różna od obecnej
        # z listy stworzonej przez list compehension pod warunkiem ze różni się
        rand_plant = random.choice([plant for plant in PLANTS if plant != curr_plant])

        s_out = deepcopy(s_inp)
        s_out[year][field] = rand_plant

        # próbujemy symulacji, jeżeli wyrzuci błąd rekurencyjnie próbujemy ponowie
        try:
            self.simulate_farm(s_out)

        except IndexError:
            # print('Nie spełnia ograniczenia jakości')
            return self.__annealing_neig(s_inp)  # Ponowna próba

        except ValueError:
            # print('Nie spełnia ograniczenia innej rośliny w każdym roku')
            return self.__annealing_neig(s_inp)  # Ponowna próba

        return s_out

    @staticmethod
    def __annealing_P(e, e_new, temp):
        """ Funkcja akceptująca rozwiązanie, zmodyfikowana bo maksymalizujemy

        :param e: wartość funkcji celu dla obecnego rozwiązania
        :param e_new: wartość funkcji celu dla nowego rozwiązania
        :param temp: obecna temperatura
        :return: prawdopodobieństwo wyboru nowego rozwiązania
        """
        if e_new > e:
            return 1
        else:
            return np.exp((e_new - e) / temp)
