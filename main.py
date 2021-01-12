import pygame
import os
import sys

FPS = 30
SIZE = (750, 500)
HERO_KEYS = [pygame.K_w, pygame.K_a, pygame.K_d,
             pygame.K_UP, pygame.K_LEFT, pygame.K_RIGHT]
HERO_FALL_SPEED = 100


class AnimatedSprite(pygame.sprite.Sprite):
    def __init__(self, sheet, columns, rows, x, y):
        super().__init__()
        self.frames = []
        self.cut_sheet(sheet, columns, rows)
        self.cur_frame = 0
        self.image = self.frames[self.cur_frame]
        self.rect = self.rect.move(x, y)

    def cut_sheet(self, sheet, columns, rows):
        self.rect = pygame.Rect(0, 0, sheet.get_width() // columns,
                                sheet.get_height() // rows)
        for j in range(rows):
            for i in range(columns):
                frame_location = (self.rect.w * i, self.rect.h * j)
                self.frames.append(sheet.subsurface(pygame.Rect(
                    frame_location, self.rect.size)))

    def update(self):
        self.cur_frame = (self.cur_frame + 1) % len(self.frames)
        self.image = self.frames[self.cur_frame]


class RoboticHero(AnimatedSprite):
    """
    Класс для игрока
    х и у - координаты места первого появления персонажа
    """

    def __init__(self, x=0, y=0):
        img = load_image('robot_steps.png')
        super().__init__(pygame.transform.scale(
            img, (img.get_width() // 3, img.get_height() // 3)),
            3, 1, x, y)
        self.walk = False  # идёт ли персонаж (для анимации)
        self.horizontal_speed = 0  # если > 0 - идёт вправо, < 0 - влево
        self.vertical_speed = 0  # если < 0 - вверх, > 0 - вниз
        self.x, self.y = self.rect.x, self.rect.y

    def motion(self, key):
        """
        Функция для управления персонажем.
        Принимает нажатую клавишу.
        """
        if self.vertical_speed != 0:
            return
        if key in (pygame.K_w, pygame.K_UP):  # прыжок
            self.y -= 50
            self.vertical_speed = HERO_FALL_SPEED
        elif key in (pygame.K_a, pygame.K_LEFT):
            self.horizontal_speed = -50
            self.walk = True
        elif key in (pygame.K_d, pygame.K_RIGHT):
            self.horizontal_speed = 50
            self.walk = True
        self.fix_collides()

    def stop_motion(self, key):
        """Функция для остановки персонажа (при отжатии клавиши)"""
        if key in (pygame.K_a, pygame.K_LEFT,
                   pygame.K_d, pygame.K_RIGHT) \
                and self.vertical_speed == 0:
            self.horizontal_speed = 0
            self.walk = False

    def fix_collides(self):
        """Защита от наскоков (в дальнейшем будет дополняться)"""
        pass

    def update(self):
        # print(self.horizontal_speed, self.vertical_speed)
        self.x += self.horizontal_speed / FPS
        self.y += self.vertical_speed / FPS
        self.rect.x, self.rect.y = int(self.x), int(self.y)
        if self.walk:
            self.cur_frame = (self.cur_frame + 1) % 3
            self.image = self.frames[self.cur_frame]
        self.fix_collides()


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
        if x in range(self.rect.x, self.rect.x + self.rect.w):
            if y in range(self.rect.y, self.rect.y + self.rect.h):
                return True
        return False

    def click(self, returnable=False):
        """Симуляция нажатия кнопки"""
        if returnable:
            return self.func
        else:
            self.func()


class Menu(AnimatedSprite):
    time = 0  # для контроля анимации
    buttons = [Button(),  # Старт
               Button(),  # Об игре
               Button()]  # Выход

    def __init__(self):
        # загружаем изображение
        super().__init__(pygame.transform.scale(  # сжимаем изображение
            load_image('menu_sheet.png'), (750 * 3, 500 * 3)),  # до размеров экрана
                         3, 3, 0, 0)

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
        return None

    def get_func(self, btn):
        """По экземпляру кнопки запускает её функцию"""
        return None

    def clicked(self, pos):
        btn = self.get_button(pos)
        self.get_func(btn)


class Platform(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        image = pygame.image.load('data/black_block.jpg')
        self.image = pygame.transform.scale(image, (50, 50))
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y


def load_level(filename):
    filename = "data/" + filename
    with open(filename, 'r') as mapFile:
        level_map = [line.strip() for line in mapFile]
    max_width = max(map(len, level_map))
    return list(map(lambda x: list(x.ljust(max_width, '.')), level_map))


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


def camera_func(camera, target_rect):
    l = -target_rect.x + SIZE[0] / 2.24
    t = -target_rect.y + SIZE[1] / 2.24
    w, h = camera.width, camera.height

    l = min(0, l)
    l = max(-(camera.width - SIZE[0]), l)
    t = max(-(camera.height - SIZE[1]), t)
    t = min(0, t)

    return pygame.Rect(l, t, w, h)


def terminate():
    pygame.quit()
    sys.exit()


def menu(screen):
    menu_sprite = Menu()
    menu_group = pygame.sprite.Group()
    menu_sprite.add(menu_group)

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                terminate()
            if event.type == pygame.MOUSEBUTTONDOWN:
                menu_sprite.clicked(event.pos)
        menu_group.update()
        menu_group.draw(screen)


def main():
    pygame.init()
    size = 750, 500
    screen = pygame.display.set_mode(size)
    clock = pygame.time.Clock()

    # загрузка уровня
    level_map = load_level("map.map")

    # группа спрайтов
    all_sprites = pygame.sprite.Group()
    hero = RoboticHero(50, 612)
    hero.add(all_sprites)

    # создание уровня
    background = pygame.Surface((750, 500))
    background.fill((75, 155, 200))
    blocks = []
    x = 0
    y = 0
    for row in level_map:
        for col in row:
            if col == '-':
                pl = Platform(x, y)
                all_sprites.add(pl)
                blocks.append(pl)
            x += 50
        y += 50
        x = 0

    # Камера
    total_level_width = len(level_map[0]) * 50
    total_level_height = len(level_map) * 50
    camera = Camera(camera_func, total_level_width, total_level_height)

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
        screen.blit(background, (0, 0))
        all_sprites.update()
        camera.update(hero)
        for e in all_sprites:
            screen.blit(e.image, camera.apply(e))
        pygame.display.flip()
        clock.tick(FPS)


if __name__ == '__main__':
    main()
