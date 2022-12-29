import math

# Dane pozyskane z internetu:
T = 6 / 15 * 8 * 2 * 7.546  # spalanie na godzine/predkośc*ile razy trzeba pojechać * 2 * cena paliwa

Cwheat = (87.43 + 19.76) * 2.5 + (87.43 + 27.56) * 2 + (87.43 + 18.80) * 2 + (
            87.43 + 31.9) * 2.5 + 850 * 1.22 + 366 * 1.22 + 540 + 1458 + 1699 + 148 + 34
Crye = (87.43 + 19.76) * 2 + (87.43 + 27.56) * 1.5 + (87.43 + 18.80) * 2 + (87.43 + 31.9) * 2.5 + 3000
Cpotato = 2 * ((87.43 + 19.76) * 2.5 + (87.43 + 27.56) * 2 + (87.43 + 18.80) * 2 + (
            87.43 + 31.9) * 2.5) + 17519.3412754
Ctriticale = (87.43 + 19.76) * 2.5 + (87.43 + 27.56) * 2 + (87.43 + 18.80) * 2 + (87.43 + 31.9) * 2.5 + 3573
C = {'potato': Cpotato, 'wheat': Cwheat, 'rye': Crye, 'triticale': Ctriticale, 'EMPTY': 0}

W = {'potato': 5, 'wheat': 8, 'rye': 3, 'triticale': 5, 'EMPTY': -5}

G = {'potato': [], 'wheat': [], 'rye': [], 'triticale': [], 'EMPTY': []}

MQ = 100  # Maksymalna jakość gleby
for i in range(MQ):
    G['potato'].append(0 if i < 12 else (math.e ** ((i - 12) / 10) / 6002.91 * 17 + 24) * 710 + 558 + 1761.46)
    G['wheat'].append(0 if i < 35 else (math.e ** ((i - 35) / 10) / 601.845 * 10 + 3.9) * 1490 + 558)
    G['rye'].append((math.e ** (i / 10) / 19930.4 * 6 + 3) * 1150 + 558)
    G['triticale'].append(0 if i < 17 else (math.e ** ((i - 17) / 10) / 3640.95 * 9 + 3) * 1339 + 558)
    G['EMPTY'].append(40)

# Dane dowolne:
default_N = 5
default_Y = 5

default_P = [1.05, 4.14, 1.69, 1.81, 3.66] # Powierzchnie pól
default_D = [2.08, 7.07, 8.42, 1.37, 6.60] # Odległości od pól
default_b = [90, 34, 54, 5, 16]  # Początkowe jakości gleb na każdym polu

MAXN = 6 # Maksymalna dopuszczalna liczba pól (uwaga ze zmianą tej wartości)
MAXY = 6 # Maksymalna dopuszczalna liczba lat (można zmieniać)
