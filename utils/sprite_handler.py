from __future__ import annotations
import pygame
import typing
import uuid

from . import ui_handler

ANIMOBJ: dict[str, Animation] = {}

def update_all(dt: float):
    for v in list(ANIMOBJ.values()):
        v.step_dt(dt)

class Animation:
    """
    Animation class
    """
    def __init__(self, sprite: AnimatableSprite, source: str, dimentions: tuple[int, int], grid: tuple[int, int], length: float):
        self.Surface = pygame.image.load(source)
        self.Surface = self.Surface.convert_alpha()
        self.Dimentions = dimentions
        self.Grid = grid
        self.ID = str(uuid.uuid4())

        self.DrawCanvas = pygame.Rect(0, 0, self.Dimentions[0], self.Dimentions[1])
        
        self.AnimSpeed = 1
        self.Playing = False
        self.Frame = 0
        self.TotalFrames = grid[0]*grid[1]
        self.InternalTime = 0
        self.TimeTilNextFrame = length/self.TotalFrames
        self.Sprite = sprite

        self.CurrentLoop = 0
        self.Loops = 0

    def step(self):
        """
        Steps the animation by 1 frame
        """
        self.Frame += 1
        if self.Frame >= self.TotalFrames:
            self.Frame = 0
            self.CurrentLoop += 1
            if self.CurrentLoop > self.Loops:
                # end animation
                self.stop_animation()
        x_pos, y_pos = self.Frame%self.Grid[0], self.Frame//self.Grid[1]
        self.DrawCanvas.x = x_pos*self.Dimentions[0]
        self.DrawCanvas.y = y_pos*self.Dimentions[1]
        self.Sprite.DrawArea = self.DrawCanvas
    
    def step_dt(self, dt: float):
        """
        Steps the animation by time, calls .step when frame should switch
        """
        self.InternalTime += (dt*self.AnimSpeed)
        if self.InternalTime >= self.TimeTilNextFrame:
            self.InternalTime = self.InternalTime%self.TimeTilNextFrame
            self.step()

    def stop_animation(self):
        """
        Stop the animation
        """
        self.Loops = 0
        self.CurrentLoop = 0
        self.InternalTime = 0
        self.Frame = 0
        self.Playing = False

        del ANIMOBJ[self.ID]

    def play_animation(self, loops: int = 0):
        """
        Play the animation, note that resizing the character during animation is not tested
        """
        # add self to update all
        if self.ID in ANIMOBJ:
            ANIMOBJ[self.ID].stop_animation()
        ANIMOBJ[self.ID] = self
        self.Playing = True
        self.Loops = loops

        # calculate resize
        # get scale factor, and apply to bounds again to offset
        aspect_ratio = self.Dimentions[1]/self.Dimentions[0] #h/w of sprite
        dims = self.Sprite.Bounds
        x_size, y_size = dims.width/self.Dimentions[0], dims.height/self.Dimentions[1]
        x_size = x_size*aspect_ratio
        self.Sprite.resize((int(x_size*dims.width), int(y_size*dims.height)))

class AnimatableSprite(ui_handler.ImageUI):
    def __init__(self, parent_rect: pygame.Rect, parent_surf: pygame.Surface, source: str, bounds: typing.Union[pygame.Rect, None] = None) -> None:
        super().__init__(parent_rect, parent_surf, source, bounds)
        self.Tracks: dict[str, Animation] = {}

    def load_track(self, source: str, track_name: str, dimentions: tuple[int, int], grid: tuple[int, int], length: float) -> Animation:
        """
        Returns an animation track from given sprite, dimention, grid, and animation length
        """
        self.Tracks[track_name] = Animation(self, source, dimentions, grid, length)
        return self.Tracks[track_name]
    
    def get_animation(self, track_name: str) -> tuple[bool, typing.Union[Animation, None]]:
        """
        Get animation track stored
        """
        if track_name in self.Tracks:
            return (True, self.Tracks[track_name])
        else:
            return (False, None)
    
    #overwrite to accomodate dimention change
    def update_rect_size(self):
        surfRect = self.Surface.get_rect()
        x_diff, y_diff = surfRect.width/self.Bounds.width, surfRect.height/self.Bounds.height
        self.Bounds.width, self.Bounds.height = surfRect.width, surfRect.height
        self.DrawArea.width, self.DrawArea.height = surfRect.width, surfRect.height
        
        for v in self.Tracks.values():
            v.Surface = pygame.transform.scale(v.Surface, (surfRect.width, surfRect.height))
            v.Dimentions = (int(v.Dimentions[0]*x_diff), int(v.Dimentions[1]*y_diff))
            v.DrawCanvas.width, v.DrawCanvas.height = v.Dimentions[0], v.Dimentions[1]