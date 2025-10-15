import pygame
import typing

class Image:
    def __init__(self, source: str, parent: pygame.Surface) -> None:
        self.surface = pygame.image.load(source)
        self.surface.convert_alpha()
        self.rect = self.surface.get_rect()
        self.parent = parent
        self.anchor = (0.0, 0.0)
        pass

    def get_ratio(self) -> float:
        self.update_rect_size()
        return self.rect.width/self.rect.height
    
    def update_rect_size(self):
        surfRect = self.surface.get_rect()
        self.rect.width, self.rect.height = surfRect.width, surfRect.height

    def resize(self, size: tuple[int, int]):
        self.surface = pygame.transform.scale(self.surface, size)
        self.update_rect_size()

    def image_fit(self, size: tuple[int, int], keep: typing.Literal['x', 'y'] = 'x'):
        # get ratio
        ratio = self.get_ratio()
        self.resize(size)
        self.resize_ratio(ratio, keep)

    def resize_ratio(self, ratio: float, keep: typing.Literal['x', 'y'] = 'x'):
        newX, newY = float(self.rect.width), float(self.rect.height)
        if keep == 'x':
            # r = w/h
            # w = rh
            newY = newX/ratio
        else:
            newX = newY*ratio
        self.surface = pygame.transform.scale(self.surface, (newX, newY))
        self.update_rect_size()

    def set_anchor(self, coordinate: tuple[float, float]=(0, 0)):
        cx, cy = coordinate
        cx, cy = int(cx*self.rect.width), int(cy*self.rect.height)
        
        self.rect.x -= cx
        self.rect.y -= cy
        self.anchor = coordinate

    def position(self, coordinate_scale: tuple[float, float] = (0, 0), coordinate_px: tuple[int, int] = (0, 0)):
        parent_rect = self.parent.get_rect()
        #scaling
        cx, cy = coordinate_scale
        cx, cy = int(cx*parent_rect.width), int(cy*parent_rect.height)
        #pixel
        px, py = coordinate_px
        cx, cy = px+cx, py+cy
        #relative
        cx, cy = parent_rect.x+cx, parent_rect.y+cy
        #anchor
        ax, ay = int(self.anchor[0]*self.rect.width), int(self.anchor[1]*self.rect.height)
        cx, cy = cx-ax, cy-ay
        self.rect.x, self.rect.y = cx, cy
    
    def get_blit(self):
        return (self.surface, self.rect)