import pygame
import sys

FPS = 30


def terminate():
    pygame.quit()
    sys.exit()


def main():
    pygame.init()
    size = width, height = 750, 500
    screen = pygame.display.set_mode(size)
    clock = pygame.time.Clock()

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                terminate()
        pygame.display.flip()
        clock.tick(FPS)


if __name__ == '__main__':
    main()
