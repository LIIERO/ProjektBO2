from data import *
import sys
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QWidget, QLabel, QGridLayout, QLineEdit, QPushButton, QHBoxLayout, QMessageBox, QApplication, QStackedWidget

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
        skipBtn = QPushButton("&Ustaw domyślne parametry", self)
        LayoutT.addWidget(continueBtn, 2, 0, 1, 3)
        LayoutT.addWidget(skipBtn, 3, 0, 1, 3)

        self.setLayout(LayoutT)

        continueBtn.clicked.connect(self.cont)
        skipBtn.clicked.connect(self.skip)

        self.setGeometry(50, 50, 300, 100)
        self.setWindowIcon(QIcon('field.jpg'))
        self.setWindowTitle("Symulator gospodarstwa")
        # self.show()

    @staticmethod
    def skip():
        global N, Y
        N, Y = default_N, default_Y
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
        LayoutT.addWidget(continueBtn, 3, 0)

        self.setLayout(LayoutT)

        continueBtn.clicked.connect(self.cont)

        # continueBtn.clicked.connect(self.cont)

        self.setGeometry(50, 50, 300, 100)
        self.setWindowIcon(QIcon('field.jpg'))
        self.setWindowTitle("Symulator gospodarstwa")
        # self.show()

    def cont(self):
        widget.setCurrentWidget(okno)


class FarmGUI(Window):
    def __init__(self, def_N, def_Y, def_P, def_D, def_b, parent=None):
        self.N, self.Y, self.P, self.D, self.b = def_N, def_Y, def_P, def_D, def_b

        self.resultEdt = QLineEdit()
        self.sim = FarmSimulation(self.N, self.Y, T, self.P, self.D, C, W, G, self.b)

        super().__init__(parent)
        self.interface()

    def interface(self):

        # etykiety
        label1 = QLabel("Liczba pól:", self)
        label2 = QLabel("Liczba symulowanych lat:", self)
        label3 = QLabel("Zysk:", self)

        # przypisanie widgetów do układu tabelarycznego
        LayoutT = QGridLayout()
        LayoutT.addWidget(label1, 0, 0)
        LayoutT.addWidget(label2, 0, 1)
        LayoutT.addWidget(label3, 0, 2)

        # 1-liniowe pola edycyjne
        fieldEdt = QLineEdit()
        yearEdt = QLineEdit()

        self.resultEdt.readonly = True
        self.resultEdt.setToolTip('Wpisz wszystkie parametry i wybierz interesujący algorytm...')
        self.resultEdt.resize(self.resultEdt.sizeHint())

        LayoutT.addWidget(fieldEdt, 1, 0)
        LayoutT.addWidget(yearEdt, 1, 1)
        LayoutT.addWidget(self.resultEdt, 1, 2)

        # przyciski
        greedyBtn = QPushButton("&greedy", self)
        annealingBtn = QPushButton("&annealing", self)
        genetic_rouleBtn = QPushButton("&genetic_roule", self)
        genetic_rankBtn = QPushButton("&genetic_rank", self)
        endBtn = QPushButton("&end", self)
        endBtn.resize(endBtn.sizeHint())

        LayoutH = QHBoxLayout()
        LayoutH.addWidget(greedyBtn)
        LayoutH.addWidget(annealingBtn)
        LayoutH.addWidget(genetic_rouleBtn)
        LayoutH.addWidget(genetic_rankBtn)

        LayoutT.addLayout(LayoutH, 2, 0, 1, 3)
        LayoutT.addWidget(endBtn, 3, 0, 1, 3)

        # przypisanie utworzonego układu do okna
        self.setLayout(LayoutT)

        endBtn.clicked.connect(self.end)
        greedyBtn.clicked.connect(self.greedy)
        annealingBtn.clicked.connect(self.annealing)
        genetic_rouleBtn.clicked.connect(self.genetic)
        genetic_rankBtn.clicked.connect(self.genetic)

        self.setGeometry(50, 50, 300, 100)
        self.setWindowIcon(QIcon('field.jpg'))
        self.setWindowTitle("Symulator gospodarstwa")
        # self.show()

    def annealing(self):
        greedy_s = self.sim.solve_greedy()
        iterations = 1000 #zmiennić żeby dało się ustawić
        sol = self.sim.simulated_annealing(greedy_s, iterations, 3)
        self.sim.simulate_farm(sol)

        self.resultEdt.setText(str(round(self.sim.earnings, 3)))

    def genetic(self):

        sender = self.sender()
        wynik = ""

        try:
            if sender.text() == "&genetic_roule":
                wynik = genetic_algorithm.genetic_algorithm(self.sim, PLANTS, 11, "roulette")
            elif sender.text() == "&genetic_rank":
                wynik = genetic_algorithm.genetic_algorithm(self.sim, PLANTS, 11, "rank")
            self.resultEdt.setText(str(round(wynik, 3)))
        except ValueError:
            QMessageBox.warning(self, "Błąd", "Błędne dane", QMessageBox.Ok)

    def greedy(self):
        self.sim.solve_greedy()
        self.resultEdt.setText(str(round(self.sim.earnings, 3)))

N, Y = None, None

app = QApplication(sys.argv)
widget = QStackedWidget()

okno_init = InitWindow()
okno_init2 = Init2Window()
okno = FarmGUI(default_N, default_Y, default_P, default_D, default_b)
