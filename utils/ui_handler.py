from __future__ import annotations
import pygame
import typing
import uuid

class UI_Event:
    def __init__(self, function: typing.Callable) -> None:
        self._EVENT_ID: str = ""
        self.func = function
        self.master: typing.Union[None, dict] = None 

    def Unbind(self):
        if self.master is None:
            return
        del self.master[self._EVENT_ID]

class UI:
    def __init__(self, parent_rect: pygame.Rect, parent_surf: pygame.Surface, bounds: pygame.Rect = pygame.Rect(10, 10, 100, 50)) -> None:
        self.Bounds = bounds
        self.Hovering = False
        self.Active = False
        self.Surface = pygame.Surface((bounds.width, bounds.height), pygame.SRCALPHA)
        self.ParentSurface = parent_surf
        self.ParentRect = parent_rect
        self.Anchor = (0.0, 0.0)
        self.ScaledPos = (0.0, 0.0)
        self.PxPos = (0.0, 0.0)
        
        self.Events: dict[typing.Literal['onhover', 'onleave', 'onclick'], dict[str, UI_Event]] = {
            'onhover': {},
            'onleave': {},
            'onclick': {},
        }

        self.Bounds.x, self.Bounds.y = self.ParentRect.x+self.Bounds.x, self.ParentRect.y+self.Bounds.y

    def _update_states(self, event: list[pygame.event.Event], mousepos: tuple[int, int]):
        collided = self.Bounds.collidepoint(mousepos)

        def trigger_event(ev_name: typing.Literal['onhover', 'onleave', 'onclick']):
            for v in self.Events[ev_name].values():
                try:
                    v.func()
                except Exception as e:
                    print(f'exception at ui {e}')

        #update onhover
        if not self.Hovering and collided:
            self.Hovering = True
            trigger_event('onhover')
        elif not collided:
            if self.Hovering:
                trigger_event('onleave')
            self.Hovering = False

        active = False
        if collided:
            for ev in event:
                if ev.type == pygame.MOUSEBUTTONUP:
                    trigger_event('onclick')
                    active = True
        if active:
            self.Active = True
        else:
            self.Active = False

    def _onhover(self, ev: UI_Event):
        id = str(uuid.uuid4())
        self.Events['onhover'][id] = ev
        ev.master = self.Events['onhover']
        ev._EVENT_ID = id

    def _onclick(self, ev: UI_Event):
        id = str(uuid.uuid4())
        self.Events['onclick'][id] = ev
        ev.master = self.Events['onclick']
        ev._EVENT_ID = id

    def _onleave(self, ev: UI_Event):
        id = str(uuid.uuid4())
        self.Events['onleave'][id] = ev
        ev.master = self.Events['onleave']
        ev._EVENT_ID = id

    # rect and stuff
    def get_ratio(self) -> float:
        self.update_rect_size()
        return self.Bounds.width/self.Bounds.height
    
    def update_rect_size(self):
        surfRect = self.Surface.get_rect()
        self.Bounds.width, self.Bounds.height = surfRect.width, surfRect.height

    def resize(self, size: tuple[int, int]):
        self.Surface = pygame.transform.scale(self.Surface, size)
        self.update_rect_size()

    def image_fit(self, size: tuple[int, int], keep: typing.Literal['x', 'y'] = 'x'):
        # get ratio
        ratio = self.get_ratio()
        self.resize(size)
        self.resize_ratio(ratio, keep)

    def resize_ratio(self, ratio: float, keep: typing.Literal['x', 'y'] = 'x'):
        newX, newY = float(self.Bounds.width), float(self.Bounds.height)
        if keep == 'x':
            # r = w/h
            # w = rh
            newY = newX/ratio
        else:
            newX = newY*ratio
        self.Surface = pygame.transform.scale(self.Surface, (newX, newY))
        self.update_rect_size()

    def set_anchor(self, coordinate: tuple[float, float]=(0, 0)):
        cx, cy = coordinate
        cx, cy = int(cx*self.Bounds.width), int(cy*self.Bounds.height)
        
        self.Bounds.x -= cx
        self.Bounds.y -= cy
        self.Anchor = coordinate

    def position(self, coordinate_scale: typing.Union[tuple[float, float], None] = None, coordinate_px: typing.Union[tuple[float, float], None] = None):
        if coordinate_scale is None:
            coordinate_scale = self.ScaledPos
        if coordinate_px is None:
            coordinate_px = self.PxPos
        #scaling
        cx, cy = coordinate_scale
        cx, cy = int(cx*self.ParentRect.width), int(cy*self.ParentRect.height)
        #pixel
        px, py = coordinate_px
        cx, cy = px+cx, py+cy
        #relative
        cx, cy = self.ParentRect.x+cx, self.ParentRect.y+cy
        #anchor
        ax, ay = int(self.Anchor[0]*self.Bounds.width), int(self.Anchor[1]*self.Bounds.height)
        cx, cy = cx-ax, cy-ay
        self.Bounds.x, self.Bounds.y = int(cx), int(cy)

        self.ScaledPos = coordinate_scale
        self.PxPos = coordinate_px
    
    def get_blit(self):
        return (self.Surface, self.Bounds)

class TextUI(UI):
    def __init__(self, parent_rect: pygame.Rect, parent_surf: pygame.Surface, font: pygame.font.Font, bounds: pygame.Rect = pygame.Rect(10, 10, 100, 50)) -> None:
        super().__init__(parent_rect, parent_surf, bounds)
        self.Font = font
        self.FG = (255, 255, 255, 255)
        self.BG = None
        self.Text = ""
    
    def set_text(self, text: str):
        self.Text = text
        text_surf = self.Font.render(self.Text, True, self.FG, self.BG)
        self.Surface = text_surf
        self.Bounds = self.Surface.get_rect()
        self.position()

    def get_text(self):
        return self.Text
    
    def change_font(self, font: pygame.font.Font):
        self.Font = font
        self.set_text(self.Text)

    def change_colors(self, bg, fg):
        self.BG = bg
        self.FG = fg
        self.set_text(self.Text)

class ImageUI(UI):
    def __init__(self, parent_rect: pygame.Rect, parent_surf: pygame.Surface, source: str, bounds: pygame.Rect = pygame.Rect(10, 10, 100, 50)) -> None:
        super().__init__(parent_rect, parent_surf, bounds)
        self.Surface = pygame.image.load(source)
        self.Surface.convert_alpha()
        self.Bounds = self.Surface.get_rect()
       