from data import *
import sys, os
import random
import matplotlib.pyplot as plt
import numpy as np
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QWidget, QLabel, QGridLayout, QLineEdit, QPushButton, QMessageBox, QApplication, QStackedWidget

import genetic_algorithm
from farm_simulation import PLANTS, FarmSimulation

class Window(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

    def end(self):
        self.close()

    def closeEvent(self, event):
        odp = QMessageBox.question(
            self, 'Komunikat',
            "Czy na pewno chcesz wyjść?",
            QMessageBox.Yes | QMessageBox.No, QMessageBox.No)

        if odp == QMessageBox.Yes:
            event.accept()
        else:
            event.ignore()

    def keyPressEvent(self, e):
        if e.key() == Qt.Key_Escape:
            self.close()


class InitWindow(Window): # Nie dokończone
    def __init__(self, parent=None):
        super().__init__(parent)
        self.fieldEdt = QLineEdit()
        self.yearEdt = QLineEdit()

        self.N, self.Y = None, None
        self.set_default = True

        self.interface()

    def interface(self):
        LayoutT = QGridLayout()

        label1 = QLabel("Podaj liczbę pól:", self)
        label2 = QLabel("Podaj liczbę symulowanych lat:", self)
        LayoutT.addWidget(label1, 0, 0)
        LayoutT.addWidget(label2, 0, 1)

        self.fieldEdt.setText(str(default_N))
        self.yearEdt.setText(str(default_Y))
        LayoutT.addWidget(self.fieldEdt, 1, 0)
        LayoutT.addWidget(self.yearEdt, 1, 1)

        continueBtn = QPushButton("&Kontynuuj", self)
        skipBtn = QPushButton("&Użyj parametrów domyślnych (N = 5, Y = 5)", self)
        LayoutT.addWidget(continueBtn, 2, 0, 1, 3)
        LayoutT.addWidget(skipBtn, 3, 0, 1, 3)

        self.setLayout(LayoutT)

        continueBtn.clicked.connect(self.cont)
        skipBtn.clicked.connect(self.skip)

        # self.setGeometry(50, 50, 300, 100)

    @staticmethod
    def skip():
        global N, Y, P, D, b
        N, Y, P, D, b = default_N, default_Y, default_P, default_D, default_b
        okno.interface()
        widget.setCurrentWidget(okno)

    def cont(self):
        global N, Y
        self.set_default = False
        self.N = self.fieldEdt.text()
        self.Y = self.yearEdt.text()

        try:
            N = int(self.N)
            Y = int(self.Y)
            if N < 1 or N > MAXN or Y < 1 or Y > MAXY: raise ValueError
            okno_init2.interface() # Interfejs następnego okna wywołany dopiero jak ustalone N
            widget.setCurrentWidget(okno_init2)
        except ValueError:
            QMessageBox.warning(self, "Błąd", "Błędne dane", QMessageBox.Ok)


class Init2Window(Window):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.surfaceEdt, self.distanceEdt, self.qualityEdt = None, None, None

    def interface(self):
        self.surfaceEdt = [QLineEdit() for _ in range(N)]
        self.distanceEdt = [QLineEdit() for _ in range(N)]
        self.qualityEdt = [QLineEdit() for _ in range(N)]

        LayoutT = QGridLayout()

        label1 = QLabel("Podaj powierzchnie każdego pola [ha]:", self)
        label2 = QLabel("Podaj dystanse do każdego pola [km]:", self)
        label3 = QLabel("Podaj początkowe jakości gleby [int 1 -> 99]:", self)
        LayoutT.addWidget(label1, 0, 0)
        LayoutT.addWidget(label2, 1, 0)
        LayoutT.addWidget(label3, 2, 0)

        for n, _ in enumerate(self.surfaceEdt): LayoutT.addWidget(self.surfaceEdt[n], 0, n+1)
        for n, _ in enumerate(self.distanceEdt): LayoutT.addWidget(self.distanceEdt[n], 1, n+1)
        for n, _ in enumerate(self.qualityEdt): LayoutT.addWidget(self.qualityEdt[n], 2, n+1)

        continueBtn = QPushButton("&Kontynuuj", self)
        randBtn = QPushButton("&Losuj dane", self)
        LayoutT.addWidget(continueBtn, 3, 0)
        LayoutT.addWidget(randBtn, 3, 1, 1, 3)

        self.setLayout(LayoutT)

        continueBtn.clicked.connect(self.cont)
        randBtn.clicked.connect(self.random_data)
        # self.setGeometry(50, 50, 300, 100)

    def random_data(self):
        Pr = [round(random.uniform(0.1, 5), 3) for _ in range(N)]
        Dr = [round(random.uniform(0.1, 10), 3) for _ in range(N)]
        br = random.sample(range(1, MQ-1), N)
        for n in range(N):
            self.surfaceEdt[n].setText(str(Pr[n]))
            self.distanceEdt[n].setText(str(Dr[n]))
            self.qualityEdt[n].setText(str(br[n]))

    def cont(self):
        global P, D, b
        try:
            P = [float(f.text()) for f in self.surfaceEdt]
            D = [float(f.text()) for f in self.distanceEdt]
            b = [int(f.text()) for f in self.qualityEdt]
            if min(P) <= 0 or min(D) <= 0 or min(b) <= 0 or max(b) >= 100:
                raise ValueError

            okno.interface()
            widget.setCurrentWidget(okno)
        except ValueError:
            QMessageBox.warning(self, "Błąd", "Błędne dane", QMessageBox.Ok)



class FarmGUI(Window):
    def __init__(self, parent=None):
        # self.N, self.Y, self.P, self.D, self.b = def_N, def_Y, def_P, def_D, def_b
        self.current_algorithm = None # Jakim algorytmem zostało wyznaczone aktualne rozwiązanie
        self.solutions = []
        self.best_solutions = []

        self.resultEdt = QLineEdit()
        self.anIterEdt = QLineEdit()
        self.sim = None

        super().__init__(parent)
        # self.interface()

    def interface(self):
        self.sim = FarmSimulation(N, Y, T, P, D, C, W, G, b)

        # etykiety
        label1 = QLabel(f"Liczba pól = {N}", self)
        label2 = QLabel(f"Liczba lat = {Y}", self)
        label3 = QLabel("Zysk:", self)

        # przypisanie widgetów do układu tabelarycznego
        LayoutT = QGridLayout()

        LayoutL = QGridLayout()
        LayoutL.addWidget(label1, 0, 0)
        LayoutL.addWidget(label2, 0, 1)
        LayoutL.addWidget(label3, 0, 2)

        self.resultEdt.readonly = True
        self.resultEdt.setToolTip('Wpisz wszystkie parametry i wybierz interesujący algorytm...')
        # self.resultEdt.resize(self.resultEdt.sizeHint())

        # przyciski
        greedyBtn = QPushButton("&greedy", self)
        annealingBtn = QPushButton("&annealing v1", self)
        annealingv2Btn = QPushButton("&annealing v2", self)
        genetic_rouleBtn = QPushButton("&genetic roule", self)
        genetic_rankBtn = QPushButton("&genetic rank", self)

        LayoutL.addWidget(annealingBtn, 1, 0)
        LayoutL.addWidget(genetic_rouleBtn, 1, 1)
        LayoutL.addWidget(self.resultEdt, 1, 2)

        LayoutL.addWidget(annealingv2Btn, 2, 0)
        LayoutL.addWidget(genetic_rankBtn, 2, 1)
        LayoutL.addWidget(greedyBtn, 2, 2)

        LayoutT.addLayout(LayoutL, 0, 0, 1, 3)

        LayoutT.addWidget(QLabel("Temperatura maksymalna: ", self), 3, 0)
        LayoutT.addWidget(self.anIterEdt, 3, 1)
        self.anIterEdt.setText(str(1000))

        showgraphBtn = QPushButton("&wyświetl przebieg rozwiązań", self)
        LayoutT.addWidget(showgraphBtn, 4, 0, 1, 3)
        showgraphBtn.clicked.connect(self.display_solution_graph)

        # przypisanie utworzonego układu do okna
        self.setLayout(LayoutT)

        greedyBtn.clicked.connect(self.greedy)
        annealingBtn.clicked.connect(self.annealingv1)
        annealingv2Btn.clicked.connect(self.annealingv2)
        genetic_rouleBtn.clicked.connect(self.genetic)
        genetic_rankBtn.clicked.connect(self.genetic)

        # self.setGeometry(50, 50, 300, 100)

    def show_best_solution(self):
        if self.current_algorithm:
            os.system('cls')
            print(f"Rozwiązanie wyznaczone algorytmem {self.current_algorithm}.\n")
            self.sim.display_solution()

    def display_solution_graph(self):
        if self.current_algorithm in ['annealing', 'genetic']:
            plt.figure(figsize=(10, 8), dpi=80)
            plt.plot(self.solutions)
            plt.plot(self.best_solutions)
            plt.legend(['kolejne rozwiązania', 'najlepsze rozwiązania'])
            w = 'Iteracje' if self.current_algorithm == 'annealing' else 'Generacje'
            plt.xlabel(w)
            plt.ylabel('Wartość funkcji celu')
            plt.title('Przebieg rozwiązań')
            plt.show()
        elif self.current_algorithm == 'greedy':
            QMessageBox.warning(self, "Błąd", "Algorytm zachłanny nie ma przebiegu", QMessageBox.Ok)
        else:
            QMessageBox.warning(self, "Błąd", "Najpierw użyj wybranego algorytmu", QMessageBox.Ok)

    def annealing(self, stages=None):
        try:
            it = int(self.anIterEdt.text())
            if it < 1 or it > MAX_AN_ITER: raise ValueError

            greedy_s = self.sim.solve_greedy()

            if stages is None:
                wynik, solutions = self.sim.simulated_annealing(greedy_s, it)
            else:
                wynik, solutions = self.sim.simulated_annealing_v2(greedy_s, it, stages)
            self.solutions = solutions

            cur_best = solutions[0]
            best_solutions = [cur_best]
            for n, sol in enumerate(solutions):
                if n != 0:
                    if sol > cur_best: cur_best = sol
                    best_solutions.append(cur_best)
            self.best_solutions = best_solutions
            self.sim.simulate_farm(wynik)

            self.resultEdt.setText(str(round(self.sim.earnings, 3)))
            self.current_algorithm = 'annealing'
            self.show_best_solution()
        except ValueError:
            QMessageBox.warning(self, "Błąd", "Błędne dane", QMessageBox.Ok)

    def annealingv1(self):
        self.annealing()

    def annealingv2(self):
        stages = 4 # ustalone 4 etapy
        self.annealing(stages)

    def genetic(self):

        sender = self.sender()
        wynik = ""

        try:
            generation_quantities = int(Y*25)
            # print(generation_quantities) # TODO: Zrób coś z tym
            if sender.text() == "&genetic roule":
                if Y + N < 3:
                    amount_chromoses = 8
                elif abs(Y-N) < 4:
                    amount_chromoses = Y+N+4
                elif min([Y, N]) > 4:
                    amount_chromoses = min([Y, N])*2+4
                else:
                    amount_chromoses = 8
                wynik, solutions = genetic_algorithm.genetic_algorithm(self.sim, PLANTS, amount_chromoses, "roulette", generation_quantities)
            elif sender.text() == "&genetic rank":
                if Y + N < 3:
                    amount_chromoses = 8
                elif abs(Y - N) < 4:
                    amount_chromoses = Y + N + 4
                else:
                    amount_chromoses = 8
                wynik, solutions = genetic_algorithm.genetic_algorithm(self.sim, PLANTS, amount_chromoses, "rank", generation_quantities)
            self.resultEdt.setText(str(round(wynik, 3)))
            solutions = [el for el in solutions if el is not None]
            self.solutions = solutions
            cur_best = solutions[0]
            best_solutions = [cur_best]
            for n, sol in enumerate(solutions):
                if n != 0:
                    if sol > cur_best: cur_best = sol
                    best_solutions.append(cur_best)
            self.best_solutions = best_solutions
            self.current_algorithm = 'genetic'
            self.show_best_solution()
        except ValueError:
            QMessageBox.warning(self, "Błąd", "Błędne dane", QMessageBox.Ok)

    def greedy(self):
        self.current_algorithm = 'greedy'
        self.sim.solve_greedy()
        self.resultEdt.setText(str(round(self.sim.earnings, 3)))
        self.show_best_solution()

N, Y = 0, 0
P, D, b = [], [], []

app = QApplication(sys.argv)
widget = QStackedWidget()

okno_init = InitWindow()
okno_init2 = Init2Window()
okno = FarmGUI()
