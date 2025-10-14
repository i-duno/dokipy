import pygame
import sys

import utils.color_scheme as COLORS

# global variables
SCR_HEIGHT = 400
SCR_WIDTH = 800
TIMER: pygame.time.Clock = None #type: ignore
WINDOW: pygame.surface.Surface = None #type: ignore
FPS = 30

pygame.init()
scr_info = pygame.display.Info()
SCR_HEIGHT = int(scr_info.current_h)
SCR_WIDTH = int(scr_info.current_w)
WINDOW = pygame.display.set_mode((SCR_WIDTH, SCR_HEIGHT))

TIMER = pygame.time.Clock()

pygame.display.set_caption("im so sad")
WINDOW.fill(COLORS.BGCOLOR)

# load main theme music
pygame.mixer.music.load('assets/audio/main_theme.mp3')
pygame.mixer.music.play()

# for now, just draw the background
def bg_load(source: str):
    resX, _ = WINDOW.get_size()
    bmap = pygame.image.load(source)
    bmap.convert_alpha()
    imgX, _ = bmap.get_size()
    ratioX = resX/imgX
    bmap = pygame.transform.scale(bmap, (imgX*ratioX, SCR_HEIGHT))
    rect = bmap.get_rect()
    rect.center = (SCR_WIDTH//2, SCR_HEIGHT//2)
    WINDOW.blit(bmap, (0, 0))

def sprite_load(source: str):
    _, resY = WINDOW.get_size()
    bmap = pygame.image.load(source)
    bmap.convert_alpha()
    imgX, imgY = bmap.get_size()
    ratioY = resY/imgY
    bmap = pygame.transform.scale(bmap, (imgX*ratioY, SCR_HEIGHT))
    rect = bmap.get_rect()
    rect.center = (SCR_WIDTH//2, SCR_HEIGHT//2)
    WINDOW.blit(bmap, rect)

bg_load('assets/bg/club-skill.png')
sprite_load('assets/sprite/3a.png')

running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
            break

    # Update screen
    pygame.display.update()
    TIMER.tick(60)