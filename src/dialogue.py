from __future__ import annotations
import typing
import pygame

import utils.tween_handler as Tween
import utils.sound_handler as SoundEng
import utils.ui_handler as UIEng
import utils.sprite_handler as SpriteEng

RES_SIZE = (0, 0)
SURFACE: pygame.Surface = None #type: ignore
SOUND_ENG: SoundEng.AudioSystem = None #type: ignore

def initialize(res_size: tuple[int, int], surface: pygame.Surface, soundeng: SoundEng.AudioSystem):
    '''
    Initializes module
    '''
    global RES_SIZE, SURFACE, SOUND_ENG
    RES_SIZE = res_size
    SURFACE = surface
    SOUND_ENG = soundeng

STORED_DIALOGUE: dict[str, tuple[UIEng.ImageUI, UIEng.TextUI]] = {}
ACTIVE_DIALOGUE: typing.Union[tuple[UIEng.ImageUI, UIEng.TextUI], None] = None

ACTIVE_TEXT_TWEEN: typing.Union[Tween.Loop, None] = None

def define_dialogue_box(src: str, alias: str, scale_size: tuple[float, float]):
    '''
    Define the background of the dialogue scene
    '''
    bg = UIEng.ImageUI(SURFACE.get_rect(), SURFACE, src)
    bg.image_fit((int(RES_SIZE[0]*scale_size[0]), int(RES_SIZE[1]*scale_size[1])), 'x')
    bg.set_anchor((0.5, 1.2))
    bg.position((0.5, 1))
    bg.set_visible(False)
    bg.ZIndex = 1

    text = UIEng.TextUI(bg.Bounds, SURFACE, pygame.font.SysFont(None, 24)) #overwritten anyways
    text.set_visible(False)
    text.ZIndex = 2
    text.PxPos = (20, 15)
    text.WrapWidth -= 20*2

    text.set_text('')

    global STORED_DIALOGUE
    STORED_DIALOGUE[alias] = (bg, text)

def get_dialogue_box(alias: str) -> tuple[UIEng.ImageUI, UIEng.TextUI]:
    
    global STORED_DIALOGUE
    if alias in STORED_DIALOGUE:
        return STORED_DIALOGUE[alias]
    return None #type: ignore

def switch_dialogue_box(alias: str):

    global STORED_DIALOGUE, ACTIVE_DIALOGUE
    if alias in STORED_DIALOGUE:
        if ACTIVE_DIALOGUE == STORED_DIALOGUE[alias]:
            return True #dont do anything stupid
        if ACTIVE_DIALOGUE is not None:
            ui, text = ACTIVE_DIALOGUE
            ui.set_visible(False)
            text.set_visible(False)
            ACTIVE_DIALOGUE = None
        ACTIVE_DIALOGUE = STORED_DIALOGUE[alias]
        ui, text = ACTIVE_DIALOGUE
        ui.set_visible(True)
        text.set_visible(True)
    else:
        return None

STORED_BACKGROUNDS: dict[str, UIEng.ImageUI] = {}
ACTIVE_BACKGROUND: typing.Union[UIEng.ImageUI, None] = None 

def define_background(src: str, alias: str):
    '''
    Define the background of the dialogue scene
    '''
    bg = UIEng.ImageUI(SURFACE.get_rect(), SURFACE, src)
    bg.image_fit(RES_SIZE)
    bg.set_anchor((0.5, 1))
    bg.position((0.5, 1))
    bg.set_visible(False)
    bg.ZIndex = -10

    global STORED_BACKGROUNDS
    STORED_BACKGROUNDS[alias] = bg

def get_background(alias: str) -> typing.Union[UIEng.UI, None]:
    '''
    Returns UI object
    '''
    global ACTIVE_BACKGROUND, STORED_BACKGROUNDS

    if not alias in STORED_BACKGROUNDS:
        return None
    return STORED_BACKGROUNDS[alias]

def switch_background(alias: str):
    '''
    Switches background
    '''
    global ACTIVE_BACKGROUND, STORED_BACKGROUNDS

    if not alias in STORED_BACKGROUNDS:
        return False
    
    if ACTIVE_BACKGROUND:
        ACTIVE_BACKGROUND.set_visible(False)
        ACTIVE_BACKGROUND = None
    ACTIVE_BACKGROUND = STORED_BACKGROUNDS[alias]
    ACTIVE_BACKGROUND.set_visible(True)
    return True

STORED_ACTORS: dict[str, SpriteEng.AnimatableSprite] = {}
ACTIVE_ACTORS: list[SpriteEng.AnimatableSprite] = []
ACTIVE_CONTROLLERS: list[ActorController] = []

class Personality:
    def __init__(self, ease_func: str = 'elastic', ease_length: float=0.5, pos_offset: tuple[int, int] = (0, 0),
                 c_ease_func: str = 'bounce', c_ease_length: float=0.7, c_pos_offset: tuple[int, int] = (0, 0),
                 text_delay: typing.Union[float, None] = None, font: pygame.Font = pygame.Font(None, 20),
                 talk_sound: str = 'assets/audio/button_press.mp3') -> None:
        self.EaseFunction = ease_func
        self.EaseTime = ease_length
        self.PxOffset = pos_offset

        self.CharEaseFunction = c_ease_func
        self.CharEaseTime = c_ease_length
        self.CharPxOffset = c_pos_offset

        self.TextDelay = text_delay
        self.Font = font
        self.TalkSound = talk_sound

class ActorController:
    def __init__(self, actor: SpriteEng.AnimatableSprite, alias: str, dialogue_alias: str) -> None:
        self.Actor = actor
        self.Alias = alias
        dialogueBox = get_dialogue_box(dialogue_alias)
        if dialogueBox is None:
            print("Error: dialogue box does not exist!")
            return
        self.UIBG = dialogueBox[0]
        self.UIText = dialogueBox[1]
        self.DialogueAlias = dialogue_alias

        self.Personalities: dict[str, Personality] = {}

        # construct default personality
        self.Personalities['_default'] = Personality()

    def update_actor_position(self, delay: float = 1):
        '''
        Update actor position depending on stored actors
        '''
        actors = len(ACTIVE_ACTORS)
        index = ACTIVE_ACTORS.index(self.Actor)
        # reposition as grid-like spacing in center
        # note: we ignore the actor's width
        allocated_size = 0.5 # try to focus on center
        base_x_offset = 0.25
        allocated_center = base_x_offset+(allocated_size/2)

        x_offset = allocated_center
        if actors == 1:
            pass
        else:
            step = allocated_size / (actors-1)
            x_offset = base_x_offset + (step*index)

        def updt(f: float):
            self.Actor.ScaledPos = (f, self.Actor.ScaledPos[1])

        Tween.Tween(delay, x_offset, self.Actor.ScaledPos[0], 'ease_out_quad', updt)
        return x_offset

    def assign_personality(self, alias: str, personality: Personality):
        self.Personalities[alias] = personality

    def say_line(self, text: str, personality: str = '_default'):
        use_personality = self.Personalities[personality]
        SOUND_ENG.Load(use_personality.TalkSound).Play()
        switch_dialogue_box(self.DialogueAlias)

        if self.UIText.Font != use_personality.Font:
            self.UIText.change_font(use_personality.Font)

        global ACTIVE_TEXT_TWEEN
        if ACTIVE_TEXT_TWEEN:
            ACTIVE_TEXT_TWEEN.kill()

        def update_position(t: tuple[float, float]):
            self.UIBG.PxPos = t
        Tween.TweenTuple(use_personality.EaseTime, list(self.UIBG.PxPos), list(use_personality.PxOffset), use_personality.EaseFunction, update_position) #type: ignore

        def update_char_position(t: tuple[float, float]):
            self.Actor.PxPos = t
        Tween.TweenTuple(use_personality.CharEaseTime, list(self.Actor.PxPos), list(use_personality.CharPxOffset), use_personality.CharEaseFunction, update_char_position) #type: ignore

        delay = use_personality.TextDelay if use_personality.TextDelay is not None else len(text)*0.02
        
        if delay > 0:
            text_list = list(text)
            all_text = ""

            def update_text(lp_c: int):
                nonlocal all_text

                if len(text_list) <= 0:
                    if ACTIVE_TEXT_TWEEN:
                        ACTIVE_TEXT_TWEEN.kill()
                    return

                char = text_list[0]
                text_list.pop(0)
                all_text += char
                self.UIText.set_text(all_text)
            ACTIVE_TEXT_TWEEN = Tween.Loop(delay/len(text), update_text)

    def remove(self):
        copy = self.Actor.ScaledPos[0]
        def updt(f: float):
            self.Actor.ScaledPos = (copy, f)
        Tween.Tween(1, 2, 1, 'ease_out_quad', updt)
        index = ACTIVE_ACTORS.index(self.Actor)
        del ACTIVE_ACTORS[index]

        index = ACTIVE_CONTROLLERS.index(self)
        del ACTIVE_CONTROLLERS[index]

        #Update actors again
        for v in ACTIVE_CONTROLLERS:
            v.update_actor_position(1)

def define_actors(src: str, alias: str, size_scale: int = 1):
    '''
    Define actors
    '''
    bg = SpriteEng.AnimatableSprite(SURFACE.get_rect(), SURFACE, src)
    bg.image_fit((RES_SIZE[0]*size_scale, RES_SIZE[1]*size_scale), 'y')
    bg.set_anchor((0.5, 1))
    bg.position((0.5, 1))
    bg.set_visible(False)
    bg.ZIndex = 0

    global STORED_ACTORS
    STORED_ACTORS[alias] = bg

def get_actor(alias: str) -> SpriteEng.AnimatableSprite:
    '''
    Returns animatable sprite object
    '''
    global STORED_ACTORS

    if not alias in STORED_ACTORS:
        return None #type: ignore
    return STORED_ACTORS[alias]

def add_actor_to_scene(alias: str, dialogue_alias: str, direction: typing.Union[typing.Literal['left', 'right'], int] = 'right', tween: bool = True) -> ActorController:
    '''
    Adds actor to the scene
    Can add from left, right or insert to index
    Returns actor index.
    '''
    global ACTIVE_ACTORS, STORED_ACTORS

    if not alias in STORED_ACTORS:
        return None #type: ignore (i know)
    actor = STORED_ACTORS[alias]
    actor.PxPos = (0, 20)
    
    INDEX = 0
    controller = ActorController(actor, alias, dialogue_alias)
    
    if type(direction) == int:
        INDEX = direction
        ACTIVE_ACTORS.insert(INDEX, actor)
    elif direction == 'left':
        INDEX = 0
        ACTIVE_ACTORS.insert(INDEX, actor)
    else:
        INDEX = len(ACTIVE_ACTORS)
        ACTIVE_ACTORS.append(actor)

    ACTIVE_CONTROLLERS.append(controller)
    x_pos = controller.update_actor_position(0)

    actor.position((x_pos, 2))
    if tween:
        def updt(f: float):
            actor.ScaledPos = (actor.ScaledPos[0], f)
        Tween.Tween(1, 1, 2, 'ease_out_quad', updt)
    actor.set_visible(True)

    if not tween:
        controller.Actor.ScaledPos = (x_pos, 1)

    for v in ACTIVE_CONTROLLERS:
        x_pos = v.update_actor_position(1 if tween else 0)
        if not tween:
            v.Actor.ScaledPos = (x_pos, 1)

    return controller