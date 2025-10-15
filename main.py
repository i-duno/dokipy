import pygame
import sys
import uuid
import time

import utils.color_scheme as COLORS
import utils.sound_handler as SoundEng
import utils.ui_handler as UIEng
import utils.sprite_handler as SpriteEng
import utils.tween_handler as Tween

pygame.init()

# global variables
SCR_HEIGHT = 400
SCR_WIDTH = 800
RES_HEIGHT = 0
RES_WIDTH = 0

RES_SCALE = 1
SCR_SCALE = 0.5

#PLEASE RUN FASTER
#omg im actually gonna freak out bro i need to learn open gl????
#please dont do this to me

TIMER: pygame.time.Clock = None #type: ignore
WINDOW: pygame.surface.Surface = None #type: ignore
FPS = 180

# initial setup
DisplayInfo = pygame.display.Info()
print(DisplayInfo)

SCR_HEIGHT = int(DisplayInfo.current_h*SCR_SCALE)
SCR_WIDTH = int(DisplayInfo.current_w*SCR_SCALE)
RES_HEIGHT = int(SCR_HEIGHT*RES_SCALE)
RES_WIDTH = int(SCR_WIDTH*RES_SCALE)
#windowed fullscreen looks best
#extremely laggy! lol uh idk just half the resolution

WINDOW = pygame.display.set_mode((SCR_WIDTH, SCR_HEIGHT), pygame.DOUBLEBUF)
TIMER = pygame.time.Clock()
WINDOW.fill(COLORS.BGCOLOR)

RENDER = pygame.Surface((RES_WIDTH, RES_HEIGHT))

pygame.display.set_caption(f"dokipy dt: {0}")
pygame.display.set_icon(pygame.image.load('assets/sprite/3a.png'))

# todo to make this game good:
# nothing yet, maybe character movement?

# load main theme music
SoundEng.MAIN_MIX.load('assets/audio/main_theme.mp3')
SoundEng.MAIN_MIX.play()

AUDIO_ENG = SoundEng.AudioSystem()

bg = UIEng.ImageUI(RENDER.get_rect(), RENDER, 'assets/bg/club-skill.png')
sprite = UIEng.ImageUI(RENDER.get_rect(), RENDER, 'assets/sprite/3a.png')
textbox = UIEng.ImageUI(RENDER.get_rect(), RENDER, 'assets/ui/textbox.png')

bg.image_fit((RES_WIDTH, RES_HEIGHT))
sprite.set_anchor((0.5, 1))
sprite.position((0.5, 1), (0, 20))
sprite.image_fit((int(RES_WIDTH), int(RES_HEIGHT)), 'y')

textbox.image_fit((int(RES_WIDTH*0.8), int(RES_HEIGHT*0.8)), 'x')
textbox.set_anchor((0.5, 1.1))    
textbox.position((0.5, 1))

DEFAULT_FONT = "aller" if "aller" in pygame.font.get_fonts() else None

dialogue = UIEng.TextUI(textbox.Bounds, RENDER, pygame.font.SysFont(DEFAULT_FONT, 18))
dialogue.set_text("Testing testing 123, awesome sause eyahehhaehheh OVERFLOW TEST OVERFLOW TEST OVERFLOW TEST OVERFLOW TEAST")
dialogue.position((0, 0), (10, 10))

# just put dialogue here as py list
all_dialogue = [
    "K",
    "hyea",
    "Testing testing 123, awesome sause eyahehhaehheh"
]

def dialogueSkip():
    AUDIO_ENG.Load('assets/audio/button_press.mp3').Play()
    dialogue.set_text(all_dialogue[0])
    if all_dialogue[0] == 'ea':
        sprite.replace_image('assets/ui/textbox.png')
    all_dialogue.pop(0)
    def upd_position(value: float):
        sprite.PxPos = (0, value)
        # Update screen
        pygame.display.flip()
    Tween.Tween(0.7, 20, -40, 'bounce', upd_position)

textbox._onclick(UIEng.UI_Event(lambda: dialogueSkip()))

while True:
    dt = TIMER.tick(FPS)/1000

    events = pygame.event.get()
    for event in events:
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

    Tween.update_all(dt)
    mouse_pos = pygame.mouse.get_pos()
    UIEng.update_all(events, (int(mouse_pos[0]*RES_SCALE), int(mouse_pos[1]*RES_SCALE)))
    SpriteEng.update_all(dt)
    pygame.display.flip()
    pygame.display.set_caption(f"dokipy dt: {dt}")

    render_scaled = pygame.transform.scale(RENDER, (SCR_WIDTH, SCR_HEIGHT))
    render_scaled.convert()
    WINDOW.blit(render_scaled, (0, 0))