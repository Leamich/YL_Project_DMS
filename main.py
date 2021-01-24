import pygame
import os
import sys

# Константы
FPS = 30
SIZE = (750, 500)
HERO_FALL_SPEED = 100
HERO_JUMP_SPEED = -800
HERO_RUN_SPEED = 180
HERO_KEYS = [pygame.K_w, pygame.K_a, pygame.K_d,
             pygame.K_UP, pygame.K_LEFT, pygame.K_RIGHT]

# Переменные
level_number = 0  # номер текущего уровня


class AnimatedSprite(pygame.sprite.Sprite):
    """Класс анимированного спрайта"""

    def __init__(self, sheet, columns, rows, x, y):
        super().__init__()
        self.frames = []
        self.frames_2 = []
        self.cut_sheet(sheet, columns, rows)
        self.cut_sheet_2(sheet, columns, rows)
        self.cur_frame = 0
        self.image = self.frames_2[self.cur_frame]
        self.rect = self.rect.move(x, y)

    def cut_sheet(self, sheet, columns, rows):
        columns = columns // 2
        self.rect = pygame.Rect(0, 0, sheet.get_width() // 6,
                                sheet.get_height() // rows)
        for j in range(rows):
            for i in range(columns):
                frame_location = (self.rect.w * (i + 3), self.rect.h * j)
                self.frames.append(sheet.subsurface(pygame.Rect(
                    frame_location, self.rect.size)))

    # Обрезка картинки для анимации движения вправо
    def cut_sheet_2(self, sheet, columns, rows):
        columns_full = columns
        columns = columns // 2
        self.rect = pygame.Rect(0, 0, sheet.get_width() // columns_full,
                                sheet.get_height() // rows)
        for j in range(rows):
            for i in range(columns):
                frame_location = (self.rect.w * i, self.rect.h * j)
                self.frames_2.append(sheet.subsurface(pygame.Rect(
                    frame_location, self.rect.size)))

    # Обновление анимации
    def update(self):
        self.cur_frame = (self.cur_frame + 1) % 9  # len(self.frames)
        self.image = self.frames_2[self.cur_frame]


# Основной класс персонажа
class RoboticHero(AnimatedSprite):
    """
    Класс для игрока
    х и у - координаты места первого появления персонажа
    """

    def __init__(self, x=0, y=0):
        img = load_image('robot_steps.png')
        super().__init__(pygame.transform.scale(
            img, (img.get_width() // 3, img.get_height() // 3)),
            6, 1, x, y)
        self.tp_coords = [(350, 864), (970, 64), (1870, 864)]
        self.direction = True
        self.on_ground = True
        self.bool = True
        self.walk = False  # идёт ли персонаж (для анимации)
        self.horizontal_speed = 0  # если > 0 - идёт вправо, < 0 - влево
        self.vertical_speed = 0  # если < 0 - вверх, > 0 - вниз
        self.x, self.y = self.rect.x, self.rect.y

    def motion(self, key):
        """
        Функция для управления персонажем.
        Принимает нажатую клавишу.
        """
        if key in (pygame.K_w, pygame.K_UP):  # прыжок
            if self.bool:
                self.vertical_speed = HERO_JUMP_SPEED
                self.bool = False
        if key in (pygame.K_a, pygame.K_LEFT):
            self.horizontal_speed = -HERO_RUN_SPEED
            self.walk = True
        if key in (pygame.K_d, pygame.K_RIGHT):
            self.horizontal_speed = HERO_RUN_SPEED
            self.walk = True

    def stop_motion(self, key):
        """Функция для остановки персонажа (при отжатии клавиши)"""
        if key in (pygame.K_a, pygame.K_LEFT,
                   pygame.K_d, pygame.K_RIGHT):
            self.horizontal_speed = 0
            self.walk = False
            if self.direction:
                self.image = self.frames_2[0]
            else:
                self.image = self.frames[2]
            keys = pygame.key.get_pressed()  # нажатые клавиши
            if keys[pygame.K_a] or keys[pygame.K_LEFT]:
                self.motion(pygame.K_LEFT)  # если зажата левая кнопка
            elif keys[pygame.K_d] or keys[pygame.K_RIGHT]:
                self.motion(pygame.K_RIGHT)  # если зажата правая кнопка

    # Функция обновления координат персонажа
    def update(self):
        self.count_money()

        if self.walk:
            if self.horizontal_speed > 0:
                self.direction = True
                self.cur_frame = (self.cur_frame + 1) % 3
                self.image = self.frames_2[self.cur_frame]
            elif self.horizontal_speed < 0:
                self.direction = False
                self.cur_frame = (self.cur_frame + 1) % 3
                self.image = self.frames[self.cur_frame]
        self.on_ground = False
        self.y += self.vertical_speed / FPS
        self.rect.y = int(self.y)
        self.fix_collides(0, self.vertical_speed)
        self.x += self.horizontal_speed / FPS
        self.rect.x = int(self.x)
        self.fix_collides(self.horizontal_speed, 0)
        self.x = self.rect.x
        self.y = self.rect.y
        if not self.on_ground:
            self.vertical_speed += HERO_FALL_SPEED
        if self.x == self.tp_coords[level_number - 1][0] and self.y == self.tp_coords[level_number - 1][1]:
            next_level()

    def fix_collides(self, xvel, yvel):
        """Защита от наскоков (в дальнейшем будет дополняться)"""
        for pl in platforms:
            if pygame.sprite.collide_rect(self, pl):
                if xvel > 0:
                    self.rect.right = pl.rect.left
                if xvel < 0:
                    self.rect.left = pl.rect.right
                if yvel > 0:
                    self.rect.bottom = (pl.rect.top - 1)
                    self.on_ground = True
                    self.vertical_speed = 0
                    self.bool = True
                if yvel < 0:
                    self.rect.top = pl.rect.bottom
                    self.vertical_speed = 0

    def count_money(self):
        c = len(pygame.sprite.spritecollide(self, moneys, dokill=True))
        count_money.apply(c)


class Button:
    """Класс, симулирующий кнопку"""

    def __init__(self, rect=None, func=None):
        self.rect = rect  # прямоугольник, где находится кнопка
        self.func = func  # функция при нажатии

    def click_in_pos(self, pos):
        """
        Метод возвращает Boolean в зависимости от того,
        была ли нажата кнопка
        """
        if self.rect is None:
            return False

        x, y = pos
        if self.rect.x <= x <= self.rect.x + self.rect.w:
            if self.rect.y <= y <= self.rect.y + self.rect.h:
                return True
        return False

    def click(self, returnable=False):
        """Симуляция нажатия кнопки"""
        if returnable:
            return self.func()
        else:
            self.func()


class Menu(AnimatedSprite):
    """Реализация главного меню"""
    time = 0  # для контроля анимации
    buttons = [Button(pygame.Rect(72, 97, 203, 61)),  # Старт
               Button(pygame.Rect(74, 195, 193, 60)),  # Об игре
               Button(pygame.Rect(70, 285, 201, 61))]  # Выход

    def __init__(self):
        # загружаем изображение
        super().__init__(pygame.transform.scale(  # сжимаем изображение
            load_image('menu_sheet.png'), (SIZE[0] * 3, SIZE[1] * 3)),  # до размеров экрана
            3, 3, 0, 0)

        # Функции для кнопок
        self.buttons[0].func = lambda: False  # выход из функции меню
        self.buttons[1].func = about_game  # вывод информации об авторах
        self.buttons[2].func = terminate  # выход из игры

    def update(self):
        self.time += 1  # счётчик для уменьшения скорости анимации
        # смена кадра 10 раз в секунду (примерно)
        if self.time % 3 == 0 \
                and self.cur_frame < len(self.frames) - 1:  # анимация проходит только один раз
            super().update()

    def get_button(self, pos):
        """
        По позиции клика определяет какая была нажата кнопка
        Если кнопка не была нажата возвращает None
        """
        for btn in self.buttons:  # пробегаем по кнопкам
            if btn.click_in_pos(pos):  # если клик попал на кнопку
                return btn  # возращаем её

        # иначе возвращаем муляж кнопки,
        # с значением True для цикла меню
        return Button(func=lambda: True)

    def get_func(self, btn):
        """По экземпляру кнопки запускает её функцию"""
        # вызываем функцию кнопки и говорим,
        # что намереваемся получить значение
        return btn.click(returnable=True)

    def clicked(self, pos):
        """Обработка нажатия кнопки"""
        btn = self.get_button(pos)
        return self.get_func(btn)


class PauseMenu(Menu):
    """
    Класс для паузы и меню конца игры.
    Принимает аргумент bool для определения типа меню
    True - меню паузы, False - конца игры
    """

    def __init__(self, game_over_menu=False):
        pygame.sprite.Sprite.__init__(self)

        def start_menu():  # запуск меню для кнопки
            global level_number
            level_number = 0
            main()
            return False

        if game_over_menu:
            im = load_image('game_over.png')

            # подравниваем изображение
            # под рамки меню паузы
            im = pygame.transform.scale(im, (376, 219))

            # вывод счёта
            font = pygame.font.Font(None, 50)
            im.blit(font.render(
                str(count_money.count), True, (0, 0, 0)
            ), (200, 67))

        else:
            im = load_image('menu_pause.png')
            im = pygame.transform.scale(im,
                                        (im.get_width() // 8,
                                         im.get_height() // 8))
        self.image = im
        self.rect = self.image.get_rect()
        self.rect.x, self.rect.y = 200, 150
        if game_over_menu:
            self.buttons = [Button(pygame.Rect(253, 269, 271, 55), start_menu)]  # В меню
        else:
            self.buttons = [Button(pygame.Rect(246, 174, 276, 51), lambda: False),  # Продолжить
                            Button(pygame.Rect(253, 269, 271, 55), start_menu)]  # В меню

    def update(self):
        # update нужен исключительно оригинальный
        pygame.sprite.Sprite.update(self)


class Platform(pygame.sprite.Sprite):
    """
    Класс для платформ
    x и y - координаты появления блока,
    block - тип блока (от 1 до 3)
    """

    def __init__(self, x, y, block):
        super().__init__()
        if block == 1:  # чёрный блок
            image = pygame.image.load('data/black_block.jpg')
        elif block == 2:  # белый
            image = pygame.image.load('data/white_block.jpg')
        elif block == 3:  # финиш
            image = pygame.image.load('data/trans_level_block.jpg')
        self.image = pygame.transform.scale(image, (50, 50))
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y


class Camera:
    """Класс камеры для отрисовки уровня на экране"""

    def __init__(self, camera_func, width, height):
        self.camera_func = camera_func  # функция обработки
        self.state = pygame.Rect(0, 0, width, height)

    def apply(self, target):
        """
        Переносит target (спрайт)
        в соответствии с положением камеры
        """
        return target.rect.move(self.state.topleft)

    def update(self, target):
        """Нацеливает камеру на target (спрайт)"""
        self.state = self.camera_func(self.state, target.rect)


class MoneyBlock(pygame.sprite.Sprite):
    """
    Класс для монеток (квадратиков).
    Принимает позицию появления
    """

    def __init__(self, x, y):
        im = load_image('money_block.png')
        im = pygame.transform.scale(im, (40,
                                         190))
        super().__init__(moneys)

        # обрезаем спрайт-лист
        self.frames = list()
        self.cut_sheet(im, 1, 4)

        self.image = self.frames[0]
        self.rect = self.image.get_rect()
        self.rect.x, self.rect.y = x, y

        # переменные для контроля анимации
        self.cur_frame = 0
        self.time = 0

        # загрузка картинки для счётчика очков
        if count_money.image_cube is None:
            count_money.image_cube = self.frames[0]

    def cut_sheet(self, sheet, columns, rows):
        """Обрезка спрайт-листа на кадры"""
        self.rect = pygame.Rect(0, 0, sheet.get_width() // columns,
                                sheet.get_height() // rows)
        for j in range(rows):
            for i in range(columns):
                frame_location = (self.rect.w * i, self.rect.h * j)
                self.frames.append(sheet.subsurface(pygame.Rect(
                    frame_location, self.rect.size)))

    def update(self):
        self.time += 1
        # задержка анимации до 6 кадров в секунду
        if self.time == 5:
            self.time = 0
            self.cur_frame = (self.cur_frame + 1) % len(self.frames)
            self.image = self.frames[self.cur_frame]


class MoneyCount(pygame.sprite.Sprite):
    """Класс для счётчика монет"""

    def __init__(self):
        super().__init__()
        self.count = 0  # количество монеток
        self.image_cube = None  # картинка куба

    def apply(self, count):
        """
        Изменяет значение счётчика на
        заданное count
        """
        self.count += count  # изменяем счётчик

        # отрисовка счётчика
        im = pygame.Surface((120, 50))
        font = pygame.font.Font(None, 30)
        im.blit(
            font.render(f'x {self.count}', True, (255, 255, 255)),
            pygame.Rect(50, 20, 25, 50)
        )
        im.blit(self.image_cube, pygame.Rect(0, 0, 50, 50))

        self.image = im
        self.rect = self.image.get_rect()
        self.rect.x, self.rect.y = 640, 0


def load_level(filename):
    """
    Функция для загрузки уровня.
    filename - название файла карты
    """
    filename = "data/" + filename
    with open(filename, 'r') as mapFile:
        level_map = [line.strip() for line in mapFile]
    max_width = max(map(len, level_map))
    return list(map(lambda x: list(x.ljust(max_width, '.')), level_map))


def load_image(name, colorkey=None):
    """Функция для загрузки изображения"""
    fullname = os.path.join('data', name)
    if not os.path.isfile(fullname):
        print(f"Файл с изображением '{fullname}' не найден")
        sys.exit()
    image = pygame.image.load(fullname)
    if colorkey is not None:
        image = image.convert()
        if colorkey == -1:
            colorkey = image.get_at((0, 0))
        image.set_colorkey(colorkey)
    else:
        image = image.convert_alpha()
    return image


def camera_func(camera, target_rect):
    """Функция для сдвига уровня (нацеливание камеры)"""
    left = -target_rect.x + SIZE[0] / 2.24
    top = -target_rect.y + SIZE[1] / 2.24
    w, h = camera.width, camera.height

    left = min(0, left)
    left = max(-(camera.width - SIZE[0]), left)
    top = max(-(camera.height - SIZE[1]), top)
    top = min(0, top)

    return pygame.Rect(left, top, w, h)


def next_level():
    """Переход на следующий уровень"""
    if level_number != 3:  # если уровни остались
        main()  # перезапускаем игру и переходим на следующий уровень
    else:
        pause(game_over_menu=True)  # запуск конечного меню


def terminate():
    """Функция для обработки выхода из игры"""
    pygame.quit()
    sys.exit()


def about_game():
    """
    Функция для главного меню
    Выводит авторов игры (они там, внизу, да)
    """
    font = pygame.font.Font(None, 30)
    texts = list()

    # проходим по строчкам
    # и рэндерим каждую по отдельности
    for line in ('Portal 2D',
                 'Авторы:',
                 'Дамир Сагитов',
                 'Михаил Леонтьев',
                 'Сергей Голышев'):
        texts.append(font.render(line, True, (0, 0, 0)))

    # помещаем их на изображение меню
    for i, render_line in enumerate(texts):
        menu_sprite.image.blit(render_line, (400, 200 + i * 20))
    return True


def menu():
    """Функция для запуска главного меню"""
    global menu_sprite  # для функции about_game

    # технические мелочи
    menu_sprite = Menu()
    menu_group = pygame.sprite.Group()
    menu_sprite.add(menu_group)
    clock = pygame.time.Clock()

    running = True
    while running:
        for event in pygame.event.get():
            # нельзя недооценивать сумасбродство игрока
            if event.type == pygame.QUIT:
                terminate()

            # обработка нажатия мыши
            if event.type == pygame.MOUSEBUTTONDOWN:
                running = menu_sprite.clicked(event.pos)

        menu_group.update()
        menu_group.draw(screen)
        pygame.display.flip()
        clock.tick(FPS)


def pause(game_over_menu=False):
    """
    Функция для открытия меню паузы и конца игры.

    restart_menu определяет, будет ли запущено меню паузы
    или меню конца игры.
    """
    clock = pygame.time.Clock()

    # инициализация меню
    menu_group = pygame.sprite.Group()
    menu_sprite = PauseMenu(game_over_menu=game_over_menu)
    menu_group.add(menu_sprite)

    # цикл работает абсолютно также,
    # как и в menu()
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                terminate()
            if event.type == pygame.MOUSEBUTTONDOWN:
                running = menu_sprite.clicked(event.pos)
        menu_group.update()
        menu_group.draw(screen)
        pygame.display.flip()
        clock.tick(FPS)


def setup_level(map_file, hero_pos):
    """
    Функция для установки уровня
    (например, установка начальной позиции и тому подобное)
    """
    # перемещаем персонажа на старт
    global hero

    # 'убиваем' героя и создаём нового
    hero.kill()
    hero = RoboticHero(*hero_pos)
    all_sprites.add(hero)

    # загрузка уровня
    level_map = load_level(map_file)

    # создание уровня
    background = pygame.Surface((750, 500))
    background.fill((0, 0, 0))
    platforms = []
    x = 0
    y = 0
    for row in level_map:
        for col in row:
            if col == '-':
                block = 1
                pl = Platform(x, y, block)
                all_sprites.add(pl)
                platforms.append(pl)
            elif col == '=':
                block = 2
                pl = Platform(x, y, block)
                all_sprites.add(pl)
                platforms.append(pl)
            elif col == '+':
                block = 3
                pl = Platform(x, y, block)
                all_sprites.add(pl)
                platforms.append(pl)
            elif col == '0':
                pl = MoneyBlock(x, y)
                all_sprites.add(pl)
            x += 50
        y += 50
        x = 0

    return platforms, level_map


def main():
    global screen, all_sprites,\
        hero, platforms,\
        level_number, moneys,\
        count_money

    # конфигурация уровней
    fon = ["Portal_fon.jpg", "Portal_fon_2.jpg", "Portal_fon_3.jpg"]  # фоны уровней
    level = ['map.map', 'map_2.map', 'map_3.map']  # карты уровней
    hero_coords = [(50, 864), (1700, 64), (1000, 864)]  # начальные позиции

    clock = pygame.time.Clock()

    # если это начало игры или конец
    if level_number == 0 or level_number == 3:
        level_number = 0  # обнуляем уровни
        count_money = MoneyCount() # обнуляем монетки
        menu()  # запуск меню

    # группы спрайтов
    all_sprites = pygame.sprite.Group()
    moneys = pygame.sprite.Group()
    stay_sprites = pygame.sprite.Group()

    hero = RoboticHero()  # появление hero будет задано в setup_level

    # установка уровня
    platforms, level_map = setup_level(level[level_number], hero_coords[level_number])

    # Фон
    bg = load_image(fon[level_number])
    bg = pygame.transform.scale(bg, (850, 500))
    bd_rect = bg.get_rect()

    # Камера
    total_level_width = len(level_map[0]) * 50
    total_level_height = len(level_map) * 50
    camera = Camera(camera_func, total_level_width, total_level_height)

    # Кнопка паузы
    # за основу мы берём класс Button и добавляем к нему спрайт
    pause_btn = Button(func=pause)
    pause_btn.sprite = pygame.sprite.Sprite(stay_sprites)
    pause_btn.sprite.image = pygame.transform.scale(load_image('pause.png'),
                                                    (50, 50))
    pause_btn.sprite.rect = pause_btn.sprite.image.get_rect()
    pause_btn.sprite.rect.x, pause_btn.sprite.rect.y = 20, 20
    pause_btn.rect = pause_btn.sprite.rect

    # добавляем count_money в группу и отрисовываем
    # отрисовываем с помощью apply, не изменяя значение count
    # (передавая ему 0)
    count_money.add(stay_sprites)
    count_money.apply(0)

    # анимация для кнопки и счётчика не поддерживается,
    # поэтому обновить можно только один раз
    stay_sprites.update()

    level_number += 1

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                terminate()

            if event.type == pygame.KEYDOWN:
                if event.key in HERO_KEYS:  # если клавиша входит в СКД (Союз Клавиш Движения)
                    hero.motion(event.key)  # отправляем её роботу на обработку

            if event.type == pygame.KEYUP:
                if event.key in HERO_KEYS:  # если клавиша входит в СКД (Союз Клавиш Движения)
                    hero.stop_motion(event.key)  # отправляем роботу сигнал об отжатии клавиши
                if event.key == pygame.K_INSERT:
                    next_level()  # (для разработчиков) досрочный конец уровня

            if event.type == pygame.MOUSEBUTTONDOWN:
                if pause_btn.click_in_pos(event.pos):  # если пользователь нажал на кнопку
                    hero.stop_motion(pygame.K_RIGHT)  # останавливаем робота
                    pause_btn.click()  # нажимаем её

        # рисуем фон
        screen.blit(bg, bd_rect)

        # обновляем спрайты
        all_sprites.update()

        # центрируем камеру и обновляем блоки (и монетки)
        camera.update(hero)
        for e in all_sprites:
            screen.blit(e.image, camera.apply(e))

        # рисуем недвижимые элементы
        stay_sprites.draw(screen)

        pygame.display.flip()
        clock.tick(FPS)


if __name__ == '__main__':
    pygame.init()
    pygame.display.set_caption("Portal 2D")
    screen = pygame.display.set_mode(SIZE)

    count_money = MoneyCount()

    main()
