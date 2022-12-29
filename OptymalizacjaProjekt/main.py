
import sys
# from PyQt5.QtWidgets import QApplication, QStackedWidget
from GUI import app, widget, okno_init, okno_init2, okno

def main():
    # Symulacja
    widget.addWidget(okno_init)
    widget.addWidget(okno_init2)
    widget.addWidget(okno)

    widget.setCurrentWidget(okno_init)

    # if okno_init.set_default: N, Y = default_N, default_Y
    # else: N, Y = okno_init.N, okno_init.Y

    widget.show()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()
