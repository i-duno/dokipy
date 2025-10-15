from __future__ import annotations
import pygame
import typing
import uuid

UIOBJ: dict[str, UI] = {}

def update_all(Event: list[pygame.event.Event], MousePos: tuple[int, int]):
    for v in list(UIOBJ.values()):
        # keep updating position
        v.ParentSurface.blit(*v.get_blit())
        v._update_states(Event, MousePos)
        v.position()

class UI_Event:
    """
    Wrapper for UI events _onclick, _onhover, _onleave
    """
    def __init__(self, function: typing.Callable) -> None:
        self._EVENT_ID: str = ""
        self.func = function
        self.master: typing.Union[None, dict] = None 

    def Unbind(self):
        if self.master is None:
            return
        del self.master[self._EVENT_ID]

class UI:
    """
    Base class for all UI elements
    """
    def __init__(self, parent_rect: pygame.Rect, parent_surf: pygame.Surface, bounds: typing.Union[pygame.Rect, None] = None) -> None:
        if bounds is None:
            bounds = pygame.Rect(10, 10, 100, 50)
        self.Bounds = bounds
        self.Hovering = False
        self.Active = False
        self.Surface = pygame.Surface((bounds.width, bounds.height), pygame.SRCALPHA)
        self.ParentSurface = parent_surf
        self.ParentRect = parent_rect
        self.Anchor = (0.0, 0.0)
        self.ScaledPos = (0.0, 0.0)
        self.PxPos = (0.0, 0.0)
        self.ID = str(uuid.uuid4())
        self.DrawArea = pygame.Rect(0, 0, self.Bounds.width, self.Bounds.height)
        self.ImageFitTuple = (bounds.width, bounds.height, 'x')
        
        self.Events: dict[typing.Literal['onhover', 'onleave', 'onclick'], dict[str, UI_Event]] = {
            'onhover': {},
            'onleave': {},
            'onclick': {},
        }

        self.Bounds.x, self.Bounds.y = self.ParentRect.x+self.Bounds.x, self.ParentRect.y+self.Bounds.y

        UIOBJ[self.ID] = self

    def _update_states(self, event: list[pygame.event.Event], mousepos: tuple[int, int]):
        """
        Update onhover, onleave, onclick events and trigger any events binded to them
        """
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
    
    def delete(self):
        """
        Delete ui element
        """
        if self.ID in UIOBJ:
            del UIOBJ[self.ID]

    def _onhover(self, ev: UI_Event):
        """
        Bind to mouse hover
        """
        id = str(uuid.uuid4())
        self.Events['onhover'][id] = ev
        ev.master = self.Events['onhover']
        ev._EVENT_ID = id

    def _onclick(self, ev: UI_Event):
        """
        Bind to mouse click
        """
        id = str(uuid.uuid4())
        self.Events['onclick'][id] = ev
        ev.master = self.Events['onclick']
        ev._EVENT_ID = id

    def _onleave(self, ev: UI_Event):
        """
        Bind to mouse leave
        """
        id = str(uuid.uuid4())
        self.Events['onleave'][id] = ev
        ev.master = self.Events['onleave']
        ev._EVENT_ID = id

    # rect and stuff
    def get_ratio(self) -> float:
        """
        Get current image aspect ratio
        """
        self.update_rect_size()
        return self.Bounds.width/self.Bounds.height
    
    def update_rect_size(self):
        """
        Updates the current bounds and draw area of the UI element
        """
        surfRect = self.Surface.get_rect()
        self.Bounds.width, self.Bounds.height = surfRect.width, surfRect.height
        self.DrawArea.width, self.DrawArea.height = surfRect.width, surfRect.height

    def resize(self, size: tuple[int, int]):
        """
        Resizes the surface to given coordinate without constraint
        """
        self.Surface = pygame.transform.scale(self.Surface, size)
        self.update_rect_size()

    def image_fit(self, size: tuple[int, int], keep: typing.Literal['x', 'y'] = 'x'):
        """
        Fit the image into a given axis while keeping its aspect ratio
        """
        # get ratio
        ratio = self.get_ratio()
        self.resize(size)
        self.resize_ratio(ratio, keep)
        self.ImageFitTuple = (*size, keep) #keep reference

    def resize_ratio(self, ratio: float, keep: typing.Literal['x', 'y'] = 'x'):
        """
        Resizes the image with the given ratio
        
        with 'x' being y = x/ratio
        with 'y' being x = y/ratio
        """
        newX, newY = float(self.Bounds.width), float(self.Bounds.height)
        if keep == 'x':
            # r = w/h
            # w = rh
            newY = newX/ratio
        else:
            newX = newY/ratio
        self.Surface = pygame.transform.scale(self.Surface, (newX, newY))
        self.update_rect_size()

    def set_anchor(self, coordinate: tuple[float, float]=(0, 0)):
        """
        Sets the anchor used in positioning the UI with .position
        Top left is (0, 0) bottom right is (1, 1)
        """
        cx, cy = coordinate
        cx, cy = int(cx*self.DrawArea.width), int(cy*self.DrawArea.height)
        
        self.Bounds.x -= cx
        self.Bounds.y -= cy
        self.Anchor = coordinate

    def position(self, coordinate_scale: typing.Union[tuple[float, float], None] = None, coordinate_px: typing.Union[tuple[float, float], None] = None):
        """
        Position UI element with coordinates scale and px
        Position = scale*size + px
        """
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
        #anchor (consider draw area instead)
        ax, ay = int(self.Anchor[0]*self.DrawArea.width), int(self.Anchor[1]*self.DrawArea.height)
        cx, cy = cx-ax, cy-ay
        self.Bounds.x, self.Bounds.y = int(cx), int(cy)

        self.ScaledPos = coordinate_scale
        self.PxPos = coordinate_px
    
    def get_blit(self):
        """
        Return surface, bounds, draw area to pass to .blit
        """
        return (self.Surface, self.Bounds, self.DrawArea)

class TextUI(UI):
    """
    Text UI class
    """
    def __init__(self, parent_rect: pygame.Rect, parent_surf: pygame.Surface, font: pygame.font.Font, bounds: typing.Union[pygame.Rect, None] = None) -> None:
        super().__init__(parent_rect, parent_surf, bounds)
        self.Font = font
        self.FG = (255, 255, 255, 255)
        self.BG = None
        self.Text = ""
    
    def set_text(self, text: str):
        """
        Sets the text to str
        """
        self.Text = text
        text_surf = self.Font.render(self.Text, True, self.FG, self.BG)
        self.Surface = text_surf
        self.Bounds = self.Surface.get_rect()

    def get_text(self):
        """
        Get current displayed text (if .Text is not modified)
        """
        return self.Text
    
    def change_font(self, font: pygame.font.Font):
        """
        Changes the font and redraws text
        """
        self.Font = font
        self.set_text(self.Text)

    def change_colors(self, bg, fg):
        """
        Changes the colors and redraws text
        """
        self.BG = bg
        self.FG = fg
        self.set_text(self.Text)

class ImageUI(UI):
    """
    Image UI class, similar to base UI but surface is an image.
    """
    def __init__(self, parent_rect: pygame.Rect, parent_surf: pygame.Surface, source: str, bounds: typing.Union[pygame.Rect, None] = None) -> None:
        super().__init__(parent_rect, parent_surf, bounds)
        self.Surface = pygame.image.load(source)
        self.Surface.convert_alpha()
        self.Bounds = self.Surface.get_rect()