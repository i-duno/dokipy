import pygame
import sys
import json
import time

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

VERSION = 'v1.1'

# HAHAAHA BUANG

TIMER: pygame.time.Clock = None #type: ignore
WINDOW: pygame.surface.Surface = None #type: ignore
FPS = 120

SCRIPT = sys.argv[1]
_running = True

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

AUDIO_ENG = SoundEng.AudioSystem()
DialogueHandler.initialize((RES_WIDTH, RES_HEIGHT), RENDER, AUDIO_ENG)

with open(f'./scripts/{SCRIPT}.json', 'r') as f:
    SCRIPT_CONTENT = json.load(f)

# Here we go bois bish bash bosh

# --- MAIN LOGIC
DialogueHandler.define_dialogue_box('assets/ui/textbox.png', '_intro', (0.8, 1))
DialogueHandler.switch_dialogue_box('_intro')
DialogueHandler.get_dialogue_box('_intro')[1].set_text(f'DokiPy {VERSION} loaded {SCRIPT} Press dialogue box to start. DEMO')

def move_script():
    if len(SCRIPT_CONTENT['Story']) == 0:
        global _running
        _running = False
        return
    script: dict = SCRIPT_CONTENT['Story'][0]
    SCRIPT_CONTENT['Story'].pop(0)
    
    bg_change = script.get('background_change')
    char_add = script.get('char_add')
    char_remove = script.get('char_remove')
    char_talk = script.get('char_talk')
    char_personality = script.get('char_personality')
    talk_content = script.get('talk_content')
    bgaudio_change = script.get('bgaudio_change')

    if bg_change and bg_change != "":
        DialogueHandler.switch_background(bg_change)

    if char_add:
        for char in char_add:
            CHAR_ONSTAGE[char.get('name')] = DialogueHandler.add_actor_to_scene(char.get('name'), char.get('dialoguebox'), char.get('direction'))

    if char_remove:
        for char in char_remove:
            CHAR_ONSTAGE[char].remove()

    if char_talk:
        # looking back loading the personality shouldnt be in the actor controller. oh well..
        CHAR_ONSTAGE[char_talk].assign_personality(char_personality, PERSONALITIES[char_personality]) #type: ignore
        CHAR_ONSTAGE[char_talk].say_line(talk_content, char_personality) #type: ignore

    if bgaudio_change and bgaudio_change != "":
        SoundEng.MAIN_MIX.load(bgaudio_change)
        SoundEng.MAIN_MIX.play()

DialogueHandler.get_dialogue_box('_intro')[0]._onclick(UIEng.UI_Event(move_script))

# --- LOAD SCENES
for scene in SCRIPT_CONTENT['Scenes']:
    DialogueHandler.define_background(scene.get('src'), scene.get('name'))

# --- LOAD DIALOGUE BOXES
for box in SCRIPT_CONTENT['DialogueBoxes']:
    DialogueHandler.define_dialogue_box(box.get('src'), box.get('name'), tuple(box.get('scale')))
    DialogueHandler.get_dialogue_box(box.get('name'))[0]._onclick(UIEng.UI_Event(move_script))

# --- LOAD PERSONALITIES
PERSONALITIES: dict[str, DialogueHandler.Personality] = {}
for psn in SCRIPT_CONTENT['Personalities']:
    PERSONALITIES[psn.get('name')] = DialogueHandler.Personality(
        ease_func=psn.get('diag_easing'),
        ease_length=float(psn.get('diag_easelen')),
        pos_offset=tuple(psn.get('diag_offset')),
        c_ease_func=psn.get('char_easing'),
        c_ease_length=float(psn.get('char_easelen')),
        c_pos_offset=tuple(psn.get('char_offset')),
        text_delay=None if psn.get('text_delay') < 0 else float(psn.get('text_delay')),
        font=pygame.font.SysFont(psn.get('font'), int(psn.get('font_size'))),
        talk_sound=psn.get('talk_sound'))
    
# --- LOAD CHARACTERS
CHAR_ONSTAGE: dict[str, DialogueHandler.ActorController] = {}
for char in SCRIPT_CONTENT['Characters']:
    DialogueHandler.define_actors(char.get('src'), char.get('name'))
    DialogueHandler.get_actor(char.get('name')).image_fit((int(RES_WIDTH), int(RES_HEIGHT)), 'y')
    #CHAR_ONSTAGE[char.get('name')] = DialogueHandler.add_actor_to_scene(char.get('name'), 'basic', 'left', False) no.

# --- FIRST SETUP
first_setup = SCRIPT_CONTENT['Setup']
DialogueHandler.switch_background(first_setup.get('background'))
for char in first_setup.get('characters'):
    controller = DialogueHandler.add_actor_to_scene(char.get('name'), char.get('dialoguebox'), 'left', False)
    CHAR_ONSTAGE[char.get('name')] = controller

SoundEng.MAIN_MIX.load(first_setup.get('bgaudio'))
SoundEng.MAIN_MIX.play(loops=-1)

pygame.event.set_allowed(pygame.QUIT)
while _running:
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
    pygame.display.set_caption(f"DokiPy {VERSION} [{SCRIPT}] FPS {TIMER.get_fps():.0f}")