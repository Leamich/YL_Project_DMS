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
numb = 0


# Класс анимации персонажа и меню
class AnimatedSprite(pygame.sprite.Sprite):
    def __init__(self, sheet, columns, rows, x, y):
        super().__init__()
        self.frames = []
        self.frames_2 = []
        self.cut_sheet(sheet, columns, rows)
        self.cut_sheet_2(sheet, columns, rows)
        self.cur_frame = 0
        self.image = self.frames_2[self.cur_frame]
        self.rect = self.rect.move(x, y)

    # Обрезка картинки для анимации движения влево
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
        self.tp_coords = [(350, 864), (970, 64), (1900, 864)]
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
        if self.x == self.tp_coords[numb - 1][0] and self.y == self.tp_coords[numb - 1][1]:
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


def next_level():
    if numb != 2:
        main()
    else:



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
        self.buttons[0].func = lambda: False
        self.buttons[1].func = about_game
        self.buttons[2].func = terminate

    def update(self):
        self.time += 1  # счётчик для уменьшения скорости анимации
        # смена кадра 10 раз в секунду (примерно)
        if self.time % 3 == 0 \
                and self.cur_frame < len(self.frames) - 1:
            super().update()

    def get_button(self, pos):
        """
        По позиции клика определяет какая была нажата кнопка
        Если кнопка не была нажата возвращает None
        """
        for btn in self.buttons:
            if btn.click_in_pos(pos):
                return btn
        return Button(func=lambda: True)

    def get_func(self, btn):
        """По экземпляру кнопки запускает её функцию"""
        return btn.click(returnable=True)

    def clicked(self, pos):
        """Обработка нажатия кнопки"""
        btn = self.get_button(pos)
        return self.get_func(btn)


class PauseMenu(Menu):
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)

        def start_menu():  # запуск меню для кнопки
            menu()
            return False

        im = load_image('menu_pause.png')
        self.image =\
            pygame.transform.scale(im,
                                   (im.get_width() // 8,
                                    im.get_height() // 8))
        self.rect = self.image.get_rect()
        self.rect.x, self.rect.y = 200, 150
        self.buttons = [Button(pygame.Rect(246, 174, 276, 51), lambda: False),  # Продолжить
                        Button(pygame.Rect(253, 269, 271, 55), start_menu)]  # В меню

    def update(self):
        pygame.sprite.Sprite.update(self)


class Platform(pygame.sprite.Sprite):
    def __init__(self, x, y, block):
        super().__init__()
        if block == 1:
            image = pygame.image.load('data/black_block.jpg')
        elif block == 2:
            image = pygame.image.load('data/white_block.jpg')
        elif block == 3:
            image = pygame.image.load('data/translevelblock.jpg')
        self.image = pygame.transform.scale(image, (50, 50))
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y


# Функция загрузки уровня
def load_level(filename):
    filename = "data/" + filename
    with open(filename, 'r') as mapFile:
        level_map = [line.strip() for line in mapFile]
    max_width = max(map(len, level_map))
    return list(map(lambda x: list(x.ljust(max_width, '.')), level_map))


# Я не понял зачем эта функция
def load_image(name, colorkey=None):
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


# Камера
class Camera:
    def __init__(self, camera_func, width, height):
        self.camera_func = camera_func
        self.state = pygame.Rect(0, 0, width, height)

    def apply(self, target):
        return target.rect.move(self.state.topleft)

    def update(self, target):
        self.state = self.camera_func(self.state, target.rect)


# Функция для координат камеры
def camera_func(camera, target_rect):
    l = -target_rect.x + SIZE[0] / 2.24
    t = -target_rect.y + SIZE[1] / 2.24
    w, h = camera.width, camera.height

    l = min(0, l)
    l = max(-(camera.width - SIZE[0]), l)
    t = max(-(camera.height - SIZE[1]), t)
    t = min(0, t)

    return pygame.Rect(l, t, w, h)


# Функция закрытия приложения
def terminate():
    pygame.quit()
    sys.exit()


def about_game():
    font = pygame.font.Font(None, 30)
    texts = list()
    for i in ('Portal 2D',
              'Авторы:',
              'Дамир Сагитов',
              'Михаил Леонтьев',
              'Сергей Голышев'):
        texts.append(font.render(i, True, (0, 0, 0)))
    for i, j in enumerate(texts):
        menu_sprite.image.blit(j, (400, 200 + i * 20))
    return True


def menu():
    global menu_sprite

    menu_sprite = Menu()
    menu_group = pygame.sprite.Group()
    menu_sprite.add(menu_group)
    clock = pygame.time.Clock()

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


def pause():
    clock = pygame.time.Clock()

    # инициализация меню
    menu_group = pygame.sprite.Group()
    menu_sprite = PauseMenu()
    menu_group.add(menu_sprite)

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
    # перемещаем персонажа на старт
    global hero

    hero.kill()
    hero = RoboticHero(*hero_pos)
    all_sprites.add(hero)

    # загрузка уровня
    level_map = load_level(map_file)

    # создание уровня
    background = pygame.Surface((750, 500))
    background.fill((75, 155, 200))
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
            x += 50
        y += 50
        x = 0

    return background, platforms, level_map


def main():
    global screen
    global all_sprites
    global hero
    global platforms
    global numb

    level = ['map.map', 'map2.map', 'map3.map']
    hero_coords = [(50, 864), (1700, 64), (1000, 864)]

    pygame.init()
    screen = pygame.display.set_mode(SIZE)
    clock = pygame.time.Clock()
    pygame.display.set_caption("Portal 2D")
    if numb == 0:
        menu()  # запуск меню

    # группа спрайтов
    all_sprites = pygame.sprite.Group()
    hero = RoboticHero()

    # установка уровня
    background, platforms, level_map = setup_level(level[numb], hero_coords[numb])
    numb += 1

    # Фон
    bg = pygame.image.load('data/Portal_fon.jpg')
    bg = pygame.transform.scale(bg, (850, 500))
    bd_rect = bg.get_rect()

    # Камера
    total_level_width = len(level_map[0]) * 50
    total_level_height = len(level_map) * 50
    camera = Camera(camera_func, total_level_width, total_level_height)

    # Кнопка паузы
    pause_group = pygame.sprite.Group()

    pause_btn = Button(func=pause)
    pause_btn.sprite = pygame.sprite.Sprite(pause_group)
    pause_btn.sprite.image = pygame.transform.scale(load_image('pause.png'),
                                                    (50, 50))
    pause_btn.sprite.rect = pause_btn.sprite.image.get_rect()
    pause_btn.sprite.rect.x, pause_btn.sprite.rect.y = 20, 20
    pause_btn.rect = pause_btn.sprite.rect
    pause_group.update()

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                terminate()
            if event.type == pygame.KEYDOWN:
                if event.key in HERO_KEYS:
                    hero.motion(event.key)
            if event.type == pygame.KEYUP:
                if event.key in HERO_KEYS:
                    hero.stop_motion(event.key)
            if event.type == pygame.MOUSEBUTTONDOWN:
                if pause_btn.click_in_pos(event.pos):
                    pause_btn.click()
                    hero.stop_motion(pygame.K_RIGHT)
        screen.blit(background, (0, 0))

        screen.blit(bg, bd_rect)
        all_sprites.update()
        camera.update(hero)
        for e in all_sprites:
            screen.blit(e.image, camera.apply(e))
        pause_group.draw(screen)
        pygame.display.flip()
        clock.tick(FPS)


if __name__ == '__main__':
    main()
