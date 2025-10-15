import pygame
import sys
import uuid
import time

import utils.color_scheme as COLORS
import utils.sound_handler as SoundEng
import utils.ui_handler as UIEng
import utils.sprite_handler as SpriteEng
import utils.tween_handler as Tween

# global variables
SCR_HEIGHT = 400
SCR_WIDTH = 800
TIMER: pygame.time.Clock = None #type: ignore
WINDOW: pygame.surface.Surface = None #type: ignore
FPS = 75

# todo to make this game good:
# audio framework [X]
# sprite framework !needs work
# ui framework [X] !needs work (wont follow the parent)

pygame.init()
scr_info = pygame.display.Info()
#SCR_HEIGHT = int(scr_info.current_h)
#SCR_WIDTH = int(scr_info.current_w)
WINDOW = pygame.display.set_mode((SCR_WIDTH, SCR_HEIGHT))

TIMER = pygame.time.Clock()

pygame.display.set_caption("im so sad")
WINDOW.fill(COLORS.BGCOLOR)

# load main theme music
pygame.mixer.music.load('assets/audio/main_theme.mp3')
pygame.mixer.music.play()

AUDIO_ENG = SoundEng.AudioSystem()
bg = UIEng.ImageUI(WINDOW.get_rect(), WINDOW, 'assets/bg/club-skill.png')
sprite = UIEng.ImageUI(WINDOW.get_rect(), WINDOW, 'assets/sprite/3a.png')
textbox = UIEng.ImageUI(WINDOW.get_rect(), WINDOW, 'assets/ui/textbox.png')

bg.image_fit((SCR_WIDTH, SCR_HEIGHT))
sprite.image_fit((SCR_WIDTH, SCR_HEIGHT), 'y')
sprite.set_anchor((0.5, 1))
sprite.position((0.5, 1), (0, 20))
textbox.image_fit((int(SCR_WIDTH*0.8), int(SCR_HEIGHT*0.8)), 'x')
textbox.set_anchor((0.5, 1.1))
textbox.position((0.5, 1))

dialogue = UIEng.TextUI(textbox.Bounds, WINDOW, pygame.font.Font(None, 32))
dialogue.set_text('hi')
dialogue.position((0, 0), (10, 10))

# just put dialogue here as py list

all_dialogue = [
    "uwu",
    "nigga"
]

def dialogueSkip():
    AUDIO_ENG.Load('assets/audio/button_press.mp3').Play()
    dialogue.set_text(all_dialogue[0])
    all_dialogue.pop(0)
    def upd_position(value: float):
        sprite.position((0.5, 1), (0, value))
    Tween.Tween(0.7, 20, -40, 'bounce', upd_position)

textbox._onclick(UIEng.UI_Event(lambda: dialogueSkip()))

running = True
while running:
    dt = TIMER.tick(FPS)/1000

    events = pygame.event.get()
    textbox._update_states(events, pygame.mouse.get_pos())
    for event in events:
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
    
    WINDOW.blit(*bg.get_blit())
    WINDOW.blit(*sprite.get_blit())
    WINDOW.blit(*textbox.get_blit())
    WINDOW.blit(*dialogue.get_blit())

    Tween.update_all(dt)

    # Update screen
    pygame.display.flip()
