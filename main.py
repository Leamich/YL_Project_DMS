import pygame
import os
import sys

# Константы
FPS = 30
SIZE = (750, 500)
HERO_FALL_SPEED = 100
HERO_JUMP_SPEED = -800
HERO_RUN_SPEED = 100
HERO_KEYS = [pygame.K_w, pygame.K_a, pygame.K_d,
             pygame.K_UP, pygame.K_LEFT, pygame.K_RIGHT]


# Класс анимации
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

    def cut_sheet(self, sheet, columns, rows):
        columns = columns // 2
        self.rect = pygame.Rect(0, 0, sheet.get_width() // 6,
                                sheet.get_height() // rows)
        for j in range(rows):
            for i in range(columns):
                frame_location = (self.rect.w * i, self.rect.h * j)
                self.frames.append(sheet.subsurface(pygame.Rect(
                    frame_location, self.rect.size)))

    def cut_sheet_2(self, sheet, columns, rows):
        columns = columns // 2
        self.rect = pygame.Rect(0, 0, sheet.get_width() // 6,
                                sheet.get_height() // rows)
        for j in range(rows):
            for i in range(columns):
                frame_location = (self.rect.w * (i + 3), self.rect.h * j)
                self.frames_2.append(sheet.subsurface(pygame.Rect(
                    frame_location, self.rect.size)))

    def update(self):
        self.cur_frame = (self.cur_frame + 1) % 6  # len(self.frames)
        self.image = self.frames[self.cur_frame]


# Основной класс персонажа
class RoboticHero(AnimatedSprite):
    """
    Класс для игрока
    х и у - координаты места первого появления персонажа
    """
    def __init__(self, x=0, y=0):
        img = load_image('robot_steps_6.png')
        super().__init__(pygame.transform.scale(
            img, (img.get_width() // 3, img.get_height() // 3)),
            6, 1, x, y)
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
                   pygame.K_d, pygame.K_RIGHT):  # and self.vertical_speed == 0:
            self.horizontal_speed = 0
            self.walk = False
            if self.direction:
                self.image = self.frames_2[0]
            else:
                self.image = self.frames[2]

    # Функция обновления координат персонажа
    def update(self, platforms):
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
        self.fix_collides(0, self.vertical_speed, platforms)
        self.x += self.horizontal_speed / FPS
        self.rect.x = int(self.x)
        self.fix_collides(self.horizontal_speed, 0, platforms)
        self.x = self.rect.x
        self.y = self.rect.y
        if not self.on_ground:
            self.vertical_speed += HERO_FALL_SPEED
     
    def fix_collides(self, xvel, yvel, platforms):
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


# Класс инициализации блоков-платформ
class Platform(pygame.sprite.Sprite):
    def __init__(self, x, y, black):
        super().__init__()
        if black:
            image = pygame.image.load('data/black_block.jpg')
        else:
            image = pygame.image.load('data/white_block.jpg')
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


# Основная функция
def main():
    pygame.init()
    screen = pygame.display.set_mode(SIZE)
    clock = pygame.time.Clock()
    pygame.display.set_caption("Portal 2D")

    # Фон
    bg = pygame.image.load('data/Portal_fon.jpg')
    bg = pygame.transform.scale(bg, (850, 500))
    bd_rect = bg.get_rect()

    # загрузка уровня
    level_map = load_level("map.map")
    screen.blit(bg, bd_rect)

    # группа спрайтов
    all_sprites = pygame.sprite.Group()
    hero = RoboticHero(50, 912)
    hero.add(all_sprites)

    # создание уровня
    background = pygame.Surface((750, 500))
    background.fill((0, 0, 0))
    platforms = []
    x = 0
    y = 0
    for row in level_map:
        for col in row:
            if col == '-':
                black = True
                pl = Platform(x, y, black)
                all_sprites.add(pl)
                platforms.append(pl)
            elif col == '=':
                black = False
                pl = Platform(x, y, black)
                all_sprites.add(pl)
                platforms.append(pl)
            x += 50
        y += 50
        x = 0

    # Камера
    total_level_width = len(level_map[0]) * 50
    total_level_height = len(level_map) * 50
    camera = Camera(camera_func, total_level_width, total_level_height)

    # Основной цикл
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
        screen.blit(bg, bd_rect)
        all_sprites.update(platforms)
        camera.update(hero)
        for e in all_sprites:
            screen.blit(e.image, camera.apply(e))
        pygame.display.flip()
        clock.tick(FPS)


if __name__ == '__main__':
    main()
