import pygame
import os
import sys

FPS = 30
HERO_KEYS = [pygame.K_w, pygame.K_a, pygame.K_d,
             pygame.K_UP, pygame.K_LEFT, pygame.K_RIGHT]

pygame.init()
size = 750, 500
screen = pygame.display.set_mode(size)
clock = pygame.time.Clock()


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
        self.fall = False  # падает ли персонаж
        self.time = 0

    def motion(self, key):
        """
        Функция для управления персонажем.
        Принимает нажатую клавишу.
        """
        if self.fall:
            return
        if key in (pygame.K_w, pygame.K_UP):
            self.rect.y -= 52
        elif key in (pygame.K_a, pygame.K_LEFT):
            self.rect.x -= 10
        elif key in (pygame.K_d, pygame.K_RIGHT):
            self.rect.x += 10
        self.fix_collides()

    def fix_collides(self):
        """Защита от наскоков (в дальнейшем будет дополняться)"""
        if self.rect.x < 0:
            self.rect.x = 0
        if self.rect.x + self.rect.w > 750:
            self.rect.x = 750 - self.rect.w
        if self.rect.y < 0:
            self.rect.y = 0
        if self.rect.y + self.rect.h > 450:
            self.rect.y = 500 - self.rect.h

        self.fall = self.rect.y + self.rect.h != 450

    def update(self):
        if self.walk:
            self.cur_frame = (self.cur_frame + 1) % 3
            self.image = self.frames[self.cur_frame]


class Platform:
    def __init__(self):
        image = pygame.image.load('data/black_block.jpg')
        self.image = pygame.transform.scale(image, (50, 50))


def load_level(filename):
    filename = "data/" + filename
    with open(filename, 'r') as mapFile:
        level_map = [line.strip() for line in mapFile]
    max_width = max(map(len, level_map))
    return list(map(lambda x: list(x.ljust(max_width, '.')), level_map))


def make_level(level):
    x = 0
    y = 0
    screen.fill((75, 155, 200))
    for row in level:
        for col in row:
            if col == '-':
                pl = Platform()
                screen.blit(pl.image, (x, y))
            x += 50
        y += 50
        x = 0


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


def terminate():
    pygame.quit()
    sys.exit()


def main():
    # загрузка уровня
    level_map = load_level("map.map")
    make_level(level_map)

    all_sprites = pygame.sprite.Group()
    hero = RoboticHero(y=362)
    hero.fix_collides()
    hero.add(all_sprites)

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                terminate()
            if event.type == pygame.KEYDOWN:
                if event.key in HERO_KEYS:
                    hero.motion(event.key)
        level_map = load_level("map.map")
        make_level(level_map)
        all_sprites.update()
        all_sprites.draw(screen)
        pygame.display.flip()
        clock.tick(FPS)


if __name__ == '__main__':
    main()
