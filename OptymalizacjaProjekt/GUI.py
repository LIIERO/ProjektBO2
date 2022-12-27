from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QWidget, QLabel, QGridLayout, QLineEdit, QPushButton, QHBoxLayout, QMessageBox

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
    def __init__(self, default_N, default_Y, parent=None):
        super().__init__(parent)
        self.start_interface_size()

        self.N, self.Y = default_N, default_Y
        self.set_default = True

    def start_interface_size(self):
        LayoutT = QGridLayout()

        label1 = QLabel("Podaj liczbę pól:", self)
        label2 = QLabel("Podaj liczbę symulowanych lat:", self)
        LayoutT.addWidget(label1, 0, 0)
        LayoutT.addWidget(label2, 0, 1)

        fieldEdt = QLineEdit()
        yearEdt = QLineEdit()
        LayoutT.addWidget(fieldEdt, 1, 0)
        LayoutT.addWidget(yearEdt, 1, 1)

        continueBtn = QPushButton("&Kontynuuj", self)
        skipBtn = QPushButton("&Ustaw domyślne parametry", self)
        LayoutT.addWidget(continueBtn, 2, 0, 1, 3)
        LayoutT.addWidget(skipBtn, 3, 0, 1, 3)

        self.setLayout(LayoutT)

        skipBtn.clicked.connect(self.end)
        self.N = fieldEdt.text()
        self.Y = yearEdt.text()

        self.setGeometry(50, 50, 300, 100)
        self.setWindowIcon(QIcon('field.jpg'))
        self.setWindowTitle("Symulator gospodarstwa")
        self.show()


class FarmGUI(Window):
    def __init__(self, default_N, default_Y, T, default_P, default_D, C, W, G, default_b, parent=None):
        self.N, self.Y, self.P, self.D, self.b = default_N, default_Y, default_P, default_D, default_b
        self.resultEdt = None # Tylko deklaracja

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
        self.resultEdt = QLineEdit()

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
        self.show()

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