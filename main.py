import pygame
import os
import sys

FPS = 30


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
        super().__init__(load_image('robot_steps.png'), 3, 1, x, y)
        self.walk = False  # идёт ли персонаж (для анимации)
        self.fall = False  # падает ли персонаж


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
    size = width, height = 750, 500
    screen = pygame.display.set_mode(size)
    clock = pygame.time.Clock()
    all_sprites = pygame.sprite.Group()

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                terminate()
        all_sprites.update()
        all_sprites.draw(screen)
        pygame.display.flip()
        clock.tick(FPS)


if __name__ == '__main__':
    main()
