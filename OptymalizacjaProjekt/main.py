
import sys
# from PyQt5.QtWidgets import QApplication, QStackedWidget
from PyQt5.QtGui import QIcon
from GUI import app, widget, okno_init, okno_init2, okno

def main():
    # Symulacja
    widget.addWidget(okno_init)
    widget.addWidget(okno_init2)
    widget.addWidget(okno)

    widget.setCurrentWidget(okno_init)
    widget.setWindowIcon(QIcon('field.jpg'))
    widget.setWindowTitle("Symulator gospodarstwa")
    widget.setGeometry(50, 50, 300, 100)

    widget.show()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()
