import pygame
import sys
import json

pygame.init()

import utils.sound_handler as SoundEng
import utils.ui_handler as UIEng
import utils.tween_handler as Tween

import src.dialogue as DialogueHandler
import cProfile
import pstats

profiler = cProfile.Profile()
profiler.enable()

# global variables
SCR_HEIGHT = 400
SCR_WIDTH = 800
RES_HEIGHT = 0
RES_WIDTH = 0

RES_SCALE = 1
SCR_SCALE = 0.5

TIMER: pygame.time.Clock = None #type: ignore
WINDOW: pygame.surface.Surface = None #type: ignore
FPS = 120

SCRIPT = sys.argv[1]

# initial setup
DisplayInfo = pygame.display.Info()
print(DisplayInfo)

SCR_HEIGHT = int(DisplayInfo.current_h*SCR_SCALE)
SCR_WIDTH = int(DisplayInfo.current_w*SCR_SCALE)
RES_HEIGHT = int(SCR_HEIGHT*RES_SCALE)
RES_WIDTH = int(SCR_WIDTH*RES_SCALE)

WINDOW = pygame.display.set_mode((SCR_WIDTH, SCR_HEIGHT))
TIMER = pygame.time.Clock()

RENDER = pygame.Surface((RES_WIDTH, RES_HEIGHT))

pygame.display.set_icon(pygame.image.load('assets/sprite/3a.png'))

# todo to make this game good:
# nothing yet, maybe character movement?

# load main theme music
SoundEng.MAIN_MIX.load('assets/audio/main_theme.mp3')
SoundEng.MAIN_MIX.play()

AUDIO_ENG = SoundEng.AudioSystem()

DialogueHandler.initialize((RES_WIDTH, RES_HEIGHT), RENDER, AUDIO_ENG)
DialogueHandler.define_background('assets/bg/club-skill.png', 'classroom')
DialogueHandler.switch_background('classroom')

DEFAULT_FONT = "aller" if "aller" in pygame.font.get_fonts() else None

DialogueHandler.define_dialogue_box('assets/ui/textbox.png', 'Basic', (0.8, 1))
DialogueHandler.switch_dialogue_box('Basic')

DialogueHandler.define_actors('assets/sprite/3a.png', 'monika1')
actor_monika = DialogueHandler.add_actor_to_scene('monika1', 'Basic', 'left')

Regular_Personality = DialogueHandler.Personality(pos_offset=(30, 0), font=pygame.font.SysFont(DEFAULT_FONT, 24), c_pos_offset=(0, -40))
actor_monika.assign_personality('default', Regular_Personality)

# just put dialogue here as py list
all_dialogue = [
    "KHello, testing 123",
    "hyea",
    "Testing testing 123, awesome sause eyahehhaehheh"
]

def dialogueSkip():
    AUDIO_ENG.Load('assets/audio/button_press.mp3').Play()
    actor_monika.say_line('Hello there! i will eat your liver')
DialogueHandler.get_dialogue_box('Basic')[0]._onclick(UIEng.UI_Event(dialogueSkip))

pygame.event.set_allowed(pygame.QUIT)
while True:
    dt = TIMER.tick(FPS)/1000
    events = pygame.event.get()
    for event in events:
        if event.type == pygame.QUIT:
            pygame.quit()
            profiler.disable()
            stats = pstats.Stats(profiler).sort_stats('tottime')
            stats.print_stats(25)
            sys.exit()

    Tween.update_all(dt)
    mouse_pos = pygame.mouse.get_pos()
    UIEng.update_all(events, (int(mouse_pos[0]*RES_SCALE), int(mouse_pos[1]*RES_SCALE)))

    render_scaled = pygame.transform.scale(RENDER, (SCR_WIDTH, SCR_HEIGHT))
    WINDOW.blit(render_scaled, (0, 0))

    pygame.display.flip()
    pygame.display.set_caption(f"DokiPy v1.1 [{SCRIPT}] FPS {TIMER.get_fps():.0f}")