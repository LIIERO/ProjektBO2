import math

# Dane pozyskane z internetu:
T = 6 / 15 * 8 * 2 * 7.546  # spalanie na godzine/predkośc*ile razy trzeba pojechać * 2 * cena paliwa

Cwheat = (87.43 + 19.76) * 2.5 + (87.43 + 27.56) * 2 + (87.43 + 18.80) * 2 + (
            87.43 + 31.9) * 2.5 + 850 * 1.22 + 366 * 1.22 + 540 + 1458 + 1699 + 148 + 34
Crye = (87.43 + 19.76) * 2 + (87.43 + 27.56) * 1.5 + (87.43 + 18.80) * 2 + (87.43 + 31.9) * 2.5 + 3000
Cpotato = 2 * ((87.43 + 19.76) * 2.5 + (87.43 + 27.56) * 2 + (87.43 + 18.80) * 2 + (
            87.43 + 31.9) * 2.5) + 17519.3412754
Ctriticale = (87.43 + 19.76) * 2.5 + (87.43 + 27.56) * 2 + (87.43 + 18.80) * 2 + (87.43 + 31.9) * 2.5 + 3573
Cpickled_corn = 8361.06
Ccorn = 6589.15
Crape = 6311.11
C = {'potato': Cpotato, 'wheat': Cwheat, 'rye': Crye, 'triticale': Ctriticale, 'pickled_corn': Cpickled_corn, 'corn': Ccorn, 'rape': Crape, 'EMPTY': 0}

W = {'potato': 4, 'wheat': 9, 'rye': 2, 'triticale': 5, 'pickled_corn': 3, 'corn': 4, 'rape': 3, 'EMPTY': (lambda x: int(-4 + 4 * (x**2 / (100**2))))}

G = {'potato': [], 'wheat': [], 'rye': [], 'triticale': [], 'pickled_corn': [], 'corn': [], 'rape': [], 'EMPTY': []}
MQ = 100  # Maksymalna jakość gleby
for i in range(MQ):
        G['potato'].append(0 if i < 10 else (math.e ** ((i - 10) / 10) / 8103.08 * 13 + 28) * 650 + 1259.42)
        G['wheat'].append(0 if i < 38 else (math.e ** ((i - 38) / 10) / 492.75 * 10 + 3.9) * 1509.5 + 1259.42)
        G['rye'].append((math.e ** (i / 10) / 22026.47 * 5.5 + 2.1) * 1199.4 + 1259.42)
        G['triticale'].append(0 if i < 20 else (math.e ** ((i - 20) / 10) / 2980.96 * 9 + 3) * 1412.2 + 1259.42)
        G['pickled_corn'].append(0 if i < 20 else (math.e**((i-20) / 10)/2980.96 * 50 + 30)*200+1609.42)
        G['corn'].append(0 if i < 25 else (math.e**((i-25)/10)/1808.04*8.5 + 3.2)*1800 + 1109.42)
        G['rape'].append(0 if i < 10 else (math.e**((i-10)/10)/8103.08*4.5 + 1.7)*2650 + 1609.42)
        G['EMPTY'].append(40)

# Dane dowolne:
default_N = 5
default_Y = 5

default_P = [1.05, 4.14, 1.69, 1.81, 3.66] # Powierzchnie pól
default_D = [2.08, 7.07, 8.42, 1.37, 6.60] # Odległości od pól
default_b = [90, 34, 54, 5, 16]  # Początkowe jakości gleb na każdym polu

MAXN = 10 # Maksymalna dopuszczalna liczba pól (uwaga ze zmianą tej wartości)
MAXY = 10 # Maksymalna dopuszczalna liczba lat (można zmieniać)

MAX_AN_ITER = 10000 # Maksymalna liczba iteracji w symulowanym wyżarzaniu
