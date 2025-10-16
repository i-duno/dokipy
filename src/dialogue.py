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

STORED_BACKGROUNDS: dict[str, UIEng.UI] = {}
ACTIVE_BACKGROUND: typing.Union[UIEng.UI, None] = None 

def initialize(res_size: tuple[int, int], surface: pygame.Surface, soundeng: SoundEng.AudioSystem):
    '''
    Initializes module
    '''
    global RES_SIZE, SURFACE, SOUND_ENG
    RES_SIZE = res_size
    SURFACE = surface
    SOUND_ENG = soundeng

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

class ActorController:
    def __init__(self, actor: SpriteEng.AnimatableSprite, alias: str) -> None:
        self.Actor = actor
        self.Alias = alias

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

def define_actors(src: str, alias: str, size_scale: int = 1):
    '''
    Define actors
    '''
    bg = SpriteEng.AnimatableSprite(SURFACE.get_rect(), SURFACE, src)
    bg.image_fit((RES_SIZE[0]*size_scale, RES_SIZE[1]*size_scale), 'y')
    bg.set_anchor((0.5, 1))
    bg.position((0.5, 1))
    bg.set_visible(False)
    bg.ZIndex = -10

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

def add_actor_to_scene(alias: str, direction: typing.Union[typing.Literal['left', 'right'], int] = 'right') -> typing.Union[ActorController, None]:
    '''
    Adds actor to the scene
    Can add from left, right or insert to index
    Returns actor index.
    '''
    global ACTIVE_ACTORS, STORED_ACTORS

    if not alias in STORED_ACTORS:
        return None
    actor = STORED_ACTORS[alias]
    actor.PxPos = (0, 20)
    actor.position((0.5, 2))
    def updt(f: float):
        actor.ScaledPos = (actor.ScaledPos[0], f)
    Tween.Tween(1, 1, 2, 'ease_out_quad', updt)
    actor.set_visible(True)
    
    INDEX = 0
    controller = ActorController(actor, alias)
    
    if type(direction) == int:
        INDEX = direction
        ACTIVE_ACTORS.insert(INDEX, actor)
    elif direction == 'left':
        INDEX = 0
        ACTIVE_ACTORS.insert(INDEX, actor)
    else:
        INDEX = len(ACTIVE_ACTORS)
        ACTIVE_ACTORS.append(actor)

    controller.update_actor_position(0)

    for v in ACTIVE_CONTROLLERS:
        v.update_actor_position()

    ACTIVE_CONTROLLERS.append(controller)
    
    return controller