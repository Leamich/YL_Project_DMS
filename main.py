import pygame
import os
import sys

FPS = 30
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
            self.y -= 20
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
                   pygame.K_d, pygame.K_RIGHT)\
                and self.vertical_speed == 0:
            self.horizontal_speed = 0
            self.walk = False

    def fix_collides(self):
        """Защита от наскоков (в дальнейшем будет дополняться)"""
        if self.rect.x < 0:
            self.rect.x = 0
        if self.rect.x + self.rect.w > 750:
            self.rect.x = 750 - self.rect.w
        if self.rect.y < 0:
            self.rect.y = 0
        if self.rect.y + self.rect.h > 500:
            self.rect.y = 500 - self.rect.h

    def update(self):
        self.x += self.horizontal_speed / FPS
        self.y += self.vertical_speed / FPS
        self.rect.x, self.rect.y = int(self.x), int(self.y)
        if self.walk:
            self.cur_frame = (self.cur_frame + 1) % 3
            self.image = self.frames[self.cur_frame]


def load_image(name, colorkey=None):
    fullname = os.path.join('data', name)
    # если файл не существует, то выходим
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
    pygame.init()
    size = 750, 500
    screen = pygame.display.set_mode(size)
    clock = pygame.time.Clock()

    all_sprites = pygame.sprite.Group()
    hero = RoboticHero(0, 0)
    hero.fix_collides()
    hero.add(all_sprites)

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
        screen.fill((255, 255, 255))
        all_sprites.update()
        all_sprites.draw(screen)
        pygame.display.flip()
        clock.tick(FPS)


if __name__ == '__main__':
    main()
