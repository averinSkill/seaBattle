import random

class BoardException(Exception):
    pass
class MyCantPlaceException(BoardException):
    def __str__(self):
        return "Не могу поставить!!!"
class MyRepShot(BoardException):
    def __str__(self):
        return "Сюда уже стрелял!!!"
class MyOutRange(BoardException):
    def __str__(self):
        return "Выстрел за пределы доски!"


class Dot():
    def __init__(self, row, col):
        self.row = row
        self.col = col
    def __eq__(self, other):
        return self.row == other.row and self.col == other.col
    def __str__(self):
        return f"Dot({self.row}, {self.col})"
    def __add__(self, other):
        # return self.row + other.row and self.col + other.col
        return f"Dot({self.row + other.row}, {self.col + other.col})"
    def __repr__(self):
        return f"Dot({self.row}, {self.col})"

# print(Dot(1,2) == Dot(1,3))

class Ship():
    def __init__(self, n_deck, pnt, hv):
        self.n_deck = n_deck
        self.pnt = pnt
        self.hv = hv
        self.ship_dots = []
    @property
    def dots(self):
        for i in range(self.n_deck):
            if self.hv == 0:
                self.ship_dots.append(Dot(self.pnt.row, self.pnt.col + i))
            else:
                self.ship_dots.append(Dot(self.pnt.row + i, self.pnt.col))
        return self.ship_dots


class Board():
    def __init__(self, size, hid=True):
        self.size = size
        self.hid = hid
        self.ships_list = []
        self.ships_count = 0
        self.busy_list = []
        self.near = [Dot(i, j) for i in range(-1, 2) for j in range(-1, 2)]
        self.board = [['o'] * self.size for _ in range(self.size)]
        self.shot_list = []
    def __str__(self):
        num = '1  2  3  4  5  6'
        res = ' ' * 4 + '   '.join(num.split('  '))
        for row, i in zip(self.board, num.split('  ')):
            res += f"\n{i} | {' | '.join(str(j) for j in row)} |"
        if not self.hid:
            res = res.replace('■', 'o')
            res = res.replace('.', 'o')
        return res
    def add_ship(self, ship_dots):
        if all([self.not_out(dot) for dot in ship_dots]):
            if all(i not in self.busy_list for i in ship_dots):
                for i in ship_dots:
                    self.board[i.row][i.col] = '■'
                    self.busy_list.append(Dot(i.row, i.col))
                self.ships_list.append(ship_dots)
                self.ships_count += 1
                self.contour(ship_dots)
                return True
            
    def contour(self, ship_dots):
        for i in ship_dots:
            for j in self.near:
                dot = Dot(i.row+j.row, i.col+j.col)
                if self.not_out(dot):
                    if dot not in self.busy_list:
                        self.busy_list.append(dot)
                        self.board[dot.row][dot.col] = '.'

    def not_out(self, dot):
        if -1 < dot.row < self.size and -1 < dot.col < self.size:
            return True
    def shot(self, dot):
        if self.not_out(dot):
            if dot not in self.shot_list:
                for i in enumerate(self.ships_list):
                    if dot in i[1]:
                        self.board[dot.row][dot.col] = 'X'
                        if len(i[1]) > 1:
                            print("Ранил!")
                        else:
                            print("Убил!")
                            self.contour(i[1])
                        return True
                    else:
                        print("Мимо!")
                        self.board[dot.row][dot.col] = 'T'
                        return False
                self.shot_list.append(dot)
            else:
                print("Сюда уже стрелял!")
                return False
        else:
            print("Выстрел за пределы доски!")
            return False

# s = Ship(3, Dot(1,1), 0)
# s2 = Ship(2, Dot(4,4), 1)
# b = Board()
# b.add_ship(s.dots)
# b.add_ship(s2.dots)
# print(b.shot(Dot(-1,1)))
# print(b)
# print(b.out(Dot(1,1)))



def user_input(label="", n=1, type_n=""):
    place = input(f"\n {label}:  ")
    if n == 1 and isinstance(type_n, str):
        return place
    if isinstance(type_n, int):
        try:
            if n == 2 and len(place) == 2:
                place = [place[0], place[1]]
            elif n == 2 and len(place) == 3:
                place = place.split(place[1])
            x, y = map(int, place)
            return x-1, y-1
        except BoardException:
            print('Введите числа от 1 до 6')


class Player():
    def __init__(self, board, enemy):
        self.board = board
        self.enemy = enemy
    def ask(self):
        pass
    def move(self):
        while True:
            try:
                target = self.ask()
                repeat = self.board.shot(target)
                return repeat
            except BoardException:
                pass


class User(Player):
    def ask(self):
        while True:
            x,y = user_input("Ваш ход. Введите координаты", n=2, type_n=1)
            return Dot(x, y)


class AI(Player):
    def ask(self):
        x, y = [random.randint(0, 5), random.randint(0, 5)]
        print(f"Ход компа: {x+1}, {y+1}")
        return Dot(x, y)


class Game:
    def __init__(self, size=6):
        self.size = size
        # my_brd = self.user_make_board()
        my_brd = self.rand_make_board()
        ai_brd = self.rand_make_board()
        ai_brd.hid = False

        self.ai = AI(ai_brd, my_brd)
        self.us = User(my_brd, ai_brd)

    def random_board2(self):
        lens = [3, 2, 2, 1, 1, 1, 1]
        board = Board(size=self.size)
        attempts = 0
        for deck in lens:
            while True:
                attempts += 1
                if attempts > 2000:
                    return None
                s = Ship(deck, Dot(random.randint(0, self.size), random.randint(0, self.size)), random.randint(0, 1))
                try:
                    board.add_ship(s.dots)
                    break
                except MyCantPlaceException:
                    pass
        board.busy_list = []
        return board

    def random_board(self):
        s_n = [3, 2, 2, 1, 1, 1, 1]
        board = Board()
        k = 0
        for deck in s_n:
            while True:
                k += 1
                if k > 2000:
                    return None
                s = Ship(deck, Dot(random.randint(0, self.size), random.randint(0, self.size)), random.randint(0, 1))
                try:
                    board.add_ship(s.dots)
                    print(board.ships_list)
                    break
                except BoardException:
                    pass
        board.busy_list = []
        print(f"Расставил {board.ships_count} кораблей", board.ships_list)
        return board


    def rand_make_board(self):
        board = None
        while board is None:
            board = self.random_board2()
            return board


    def user_make_board(self):
        s_n = [3, 2, 2, 1, 1, 1, 1]
        s_n_str = ["трех", "двух", "двух", "одно", "одно", "одно", "одно"]
        board = Board()
        print("Расстановка кораблей:")

        while len(s_n):
            board.show_board()
            place = input(f"\n Введите координаты носа {s_n_str[0]}палубного корабля:  ")
            if len(place) > 3 or not (place[0].isdigit() and place[1].isdigit()):
                print('Введите числа от 0 до 2')
                continue
            if len(place) == 2:
                place = [place[0], place[1]]
            elif len(place) == 3:
                place = place.split(place[1])
            x, y = map(int, place)
            hor_vert = input(f"\n {s_n_str[0]}палубный {x},{y}. Ориентация: hor / vert  ")
            s = Ship(s_n[0], [x - 1, y - 1], hor_vert)
            if board.add_ship(s.dots):
                s_n.pop(0)
                s_n_str.pop(0)
        board.contour_list = []
        return board

    def greet(self):
        print("-------------------")
        print("  Приветсвуем вас  ")
        print("      в игре       ")
        print("    морской бой    ")
        print("-------------------")
        print(" формат ввода: x y ")
        print(" x - номер строки  ")
        print(" y - номер столбца ")

    def loop(self):
        num = 0
        while True:
            print("-" * 20)
            print("Доска пользователя:")
            print(self.us.board)
            print("-" * 20)
            print("Доска компьютера:")
            print(self.ai.board.ships_list)
            print(self.ai.board)
            if num % 2 == 0:
                print("-" * 20)
                print("Ходит пользователь!")
                repeat = self.us.move()
            else:
                print("-" * 20)
                print("Ходит компьютер!")
                repeat = self.ai.move()
            if repeat:
                num -= 1

            if self.ai.board.ships_count == 0:
                print("-" * 20)
                print("Пользователь выиграл!")
                break

            if self.us.board.ships_count == 0:
                print("-" * 20)
                print("Компьютер выиграл!")
                break
            num += 1

    def start(self):
        self.greet()
        self.loop()


g = Game()
g.start()
