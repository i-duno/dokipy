from __future__ import annotations
import pygame
import typing
import uuid

UIOBJ: dict[str, UI] = {}

def update_all(Event: list[pygame.event.Event], MousePos: tuple[int, int]):
    # iterate through UI object first 
    sort_stack = list(UIOBJ.values())
    sort_stack.sort(key=lambda ui: ui.ZIndex)

    for v in sort_stack:
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
        self.Surface = pygame.Surface((bounds.width, bounds.height))
        self.ParentSurface = parent_surf
        self.ParentRect = parent_rect
        self.Anchor = (0.0, 0.0)
        self.ScaledPos = (0.0, 0.0)
        self.PxPos = (0.0, 0.0)
        self.ID = str(uuid.uuid4())
        self.DrawArea = pygame.Rect(0, 0, self.Bounds.width, self.Bounds.height)
        self.ImageFitTuple = (bounds.width, bounds.height, 'x')
        self.OnStack = True
        self.ZIndex = 0
        
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
    
    def set_visible(self, state: bool):
        """
        Toggles ui element from render stack
        """
        if state:
            if not self.OnStack:
                UIOBJ[self.ID] = self
                self.OnStack = True
        else:
            if self.ID in UIOBJ:
                self.OnStack = False
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
        self.Surface = pygame.transform.smoothscale(self.Surface, size)
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
        self.Surface = pygame.transform.smoothscale(self.Surface, (newX, newY))
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
        
        if not pygame.font.match_font("Aller"):
            print("The Aller_RG font is not installed on your computer, download it online PLEASEEEEE, using given")

        self.Font = font
        self.FG = (255, 255, 255, 255)
        self.BG = None
        self.Text = ""
        self.Lines = []
        self.BorderColor = (0, 0, 0)
        self.BorderThick = 1
        self.WrapWidth = parent_rect.width
        self.Alignment: typing.Literal['left', 'right', 'center'] = 'left'
    
    def set_border(self, thickness: int = 1, color: tuple[int, int, int] = (0, 0, 0)):
        """
        Changes border config and draws again
        """

        self.BorderColor = color
        self.BorderThick = thickness
        self.set_text(self.Text)

    def draw_border(self, tosurface: pygame.Surface):
        """
        Already being called within set_text
        """
        #Improve this, border will be slower on higher numbers
        for i in range(-self.BorderThick, self.BorderThick+1):
            for j in range(-self.BorderThick, self.BorderThick+1):
                if i == j == 0:
                    continue
                for li, line in enumerate(self.Lines):
                    txt_surf = self.Font.render(line, True, self.BorderColor)

                    x_offset = self.BorderThick
                    line_size = self.Font.size(line)
                    if self.Alignment == 'center':
                        x_offset += (self.WrapWidth-line_size[0])//2
                    elif self.Alignment == 'right':
                        x_offset += self.WrapWidth-line_size[0]
                    else: # do nothing on left
                        pass

                    offset_pos = (i*self.BorderThick + x_offset, j*self.BorderThick + self.BorderThick + li*self.Font.get_linesize())
                    tosurface.blit(txt_surf, offset_pos)

    def flip_image(self, x: bool, y: bool):
        """
        Flips the image.
        """
        self.Surface = pygame.transform.flip(self.Surface, x, y)
    
    def set_text(self, text: str, wrap: typing.Union[int, None] = None):
        """
        Sets the text to str
        """
        words = text.split(' ')
        self.Lines = []
        currentline = ''

        if wrap is None:
            self.WrapWidth: int = self.WrapWidth
        else:
            self.WrapWidth = wrap

        for word in words:
            cacheline = currentline + f"{word} "
            size_x, _ = self.Font.size(cacheline)
            if size_x >= self.WrapWidth:
                self.Lines.append(currentline)
                currentline = f"{word} "
            else:
                currentline = cacheline
        self.Lines.append(currentline)
 
        boundHeight = self.Font.get_linesize() * len(self.Lines)
        self.Text = "\n".join(self.Lines)

        text_surf = pygame.Surface((self.WrapWidth + self.BorderThick*2, boundHeight + self.BorderThick*2), pygame.SRCALPHA)
        self.draw_border(text_surf)
        
        for i, line in enumerate(self.Lines):
            txt_surf = self.Font.render(line, True, self.FG, self.BG)

            x_offset = self.BorderThick
            line_size = self.Font.size(line)
            if self.Alignment == 'center':
                x_offset += (self.WrapWidth-line_size[0])//2
            elif self.Alignment == 'right':
                x_offset += self.WrapWidth-line_size[0]
            else: # do nothing on left
                pass

            text_surf.blit(txt_surf, (x_offset, self.BorderThick + (i*self.Font.get_linesize())))

        self.Surface = text_surf
        self.Bounds = self.Surface.get_rect()
        self.Bounds.width += self.BorderThick*2
        self.Bounds.height += self.BorderThick*2

        # immediately call position
        self.update_rect_size()
        self.position()

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
        self.Surface = self.Surface.convert_alpha()
        self.Bounds = self.Surface.get_rect()

    def replace_image(self, source: str):
        """
        Replaces image and resizes it to match original image
        """
        self.Surface = pygame.image.load(source)
        self.Surface = self.Surface.convert_alpha()
        self.resize((self.Bounds.width, self.Bounds.height))