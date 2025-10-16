import pygame
import sys
import uuid
import time

import utils.color_scheme as COLORS
import utils.sound_handler as SoundEng
import utils.ui_handler as UIEng
import utils.sprite_handler as SpriteEng
import utils.tween_handler as Tween

import src.dialogue as DialogueHandler

pygame.init()

# global variables
SCR_HEIGHT = 400
SCR_WIDTH = 800
RES_HEIGHT = 0
RES_WIDTH = 0

# workaround to run faster while not moving to opengl
# HOW DO PEOPLE GET 90 FPS ON THIS?????
RES_SCALE = 1
SCR_SCALE = 0.4

TIMER: pygame.time.Clock = None #type: ignore
WINDOW: pygame.surface.Surface = None #type: ignore
FPS = 60

# initial setup
DisplayInfo = pygame.display.Info()
print(DisplayInfo)

SCR_HEIGHT = int(DisplayInfo.current_h*SCR_SCALE)
SCR_WIDTH = int(DisplayInfo.current_w*SCR_SCALE)
RES_HEIGHT = int(SCR_HEIGHT*RES_SCALE)
RES_WIDTH = int(SCR_WIDTH*RES_SCALE)
#windowed fullscreen looks best
#extremely laggy! lol uh idk just half the resolution

WINDOW = pygame.display.set_mode((SCR_WIDTH, SCR_HEIGHT), vsync=1)
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

DialogueHandler.initialize((RES_WIDTH, RES_HEIGHT), RENDER, AUDIO_ENG)
DialogueHandler.define_background('assets/bg/club-skill.png', 'classroom')
DialogueHandler.switch_background('classroom')

DialogueHandler.define_actors('assets/sprite/3a.png', 'monika1')
DialogueHandler.add_actor_to_scene('monika1', 'left')

textbox = UIEng.ImageUI(RENDER.get_rect(), RENDER, 'assets/ui/textbox.png')

textbox.image_fit((int(RES_WIDTH*0.8), int(RES_HEIGHT*0.8)), 'x')
textbox.set_anchor((0.5, 1.1))    
textbox.position((0.5, 1))

DEFAULT_FONT = "aller" if "aller" in pygame.font.get_fonts() else None

dialogue = UIEng.TextUI(textbox.Bounds, RENDER, pygame.font.SysFont(DEFAULT_FONT, 22))
dialogue.Alignment = 'center'
dialogue.WrapWidth -= 20
dialogue.set_text("Testing testing 123, awesome sause eyahehhaehheh OVERFLOW TEST OVERFLOW TEST OVERFLOW TEST OVERFLOW TEAST")
dialogue.position((0, 0), (10, 10))
dialogue.ZIndex = 5

# just put dialogue here as py list
all_dialogue = [
    "K",
    "hyea",
    "Testing testing 123, awesome sause eyahehhaehheh"
]

def dialogueSkip():
    actorName = str(uuid.uuid4())
    DialogueHandler.define_actors('assets/sprite/3a.png', actorName)
    DialogueHandler.add_actor_to_scene(actorName, 'left')
    AUDIO_ENG.Load('assets/audio/button_press.mp3').Play()
    def upd_position(value: float):
        DialogueHandler.get_actor('monika1').PxPos = (0, value)
    Tween.Tween(0.7, 20, -40, 'bounce', upd_position)
    dialogue.set_text(all_dialogue[0])
    all_dialogue.pop(0)

textbox._onclick(UIEng.UI_Event(lambda: dialogueSkip()))
SpriteEng.update_all(0)

dt = 0
while True:
    events = pygame.event.get()
    for event in events:
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

    Tween.update_all(dt)
    mouse_pos = pygame.mouse.get_pos()
    UIEng.update_all(events, (int(mouse_pos[0]*RES_SCALE), int(mouse_pos[1]*RES_SCALE)))
  
    pygame.display.flip()
    pygame.display.set_caption(f"dokipy {TIMER.get_fps():.1f}")

    render_scaled = pygame.transform.scale(RENDER, (SCR_WIDTH, SCR_HEIGHT))
    render_scaled.convert()
    WINDOW.blit(render_scaled, (0, 0))

    dt = TIMER.tick(FPS)/1000