import os
import pygame
from pygame.locals import *

UNIT_SCALE = 9
SCREENSIZE = Rect(0, 0, 90*UNIT_SCALE, 90*UNIT_SCALE)

DEFAULT_ANIMATION_STATE = 0
MISS_ANIMIATION_STATE = 1
GOOD_ANIMATION_STATE = 2
GREAT_ANIMATION_STATE = 3
PERFECT_ANIMATION_STATE = 4

def get_spacing(x):
    """Calculates the position that a button should be rendered"""
    return (3 + x * 21) * UNIT_SCALE

class Button:
    def __init__(self, row, col):
        self.loc_x = get_spacing(row)
        self.loc_y = get_spacing(col)
        self.animation_frame = 0
        self.is_animating = False

    def update(self, frame_advance, done):
        if done:
            self.animation_frame = 0
            self.is_animating = False
        else:
            self.animation_frame += frame_advance
            self.is_animating = True

    def render(self, surface, BUTTON_TEXTURES):
        if self.animation_frame == len(BUTTON_TEXTURES) -1:
            self.is_animating = False
        
        if self.is_animating:
            surface.blit(BUTTON_TEXTURES[self.animation_frame % len(BUTTON_TEXTURES)], (self.loc_x, self.loc_y) )
            self.animation_frame += 1
        else:
            surface.blit(BUTTON_TEXTURES[0], (self.loc_x, self.loc_y) )

def load_asset(file):
    """Loads and converts an image"""
    file = os.path.join("./assets", file)
    try:
        surface = pygame.image.load(file)
    except pygame.error:
        raise SystemExit('Could not load image "%s" %s'%(file, pygame.get_error()))
    return surface.convert()

def main():
    pygame.init()

    bestdepth = pygame.display.mode_ok(SCREENSIZE.size, 0, 32)
    screen = pygame.display.set_mode(SCREENSIZE.size, 0, bestdepth)

    texture_names = [
        'empty.png',
        '1.png',
        '2.png',
        '3.png',
        '4.png',
        '5.png',
        '6.png',
        '7.png',
        '8.png',
        'perfect_1.png',
        'perfect_2.png',
        'perfect_3.png',
        'perfect_4.png',
        'perfect_5.png',
        'perfect_6.png',
        'perfect_7.png',
        'perfect_8.png',
    ]

    raw_textures = [load_asset(name) for name in texture_names]
    scaled_textures = [
        pygame.transform.scale(texture, (20 * UNIT_SCALE, 20 * UNIT_SCALE))
        for texture in raw_textures
    ]

    BUTTON_TEXTURES = scaled_textures

    button_container = []
    for row in range(0,4):
        for col in range(0,4):
            button_container.append(Button(row,col))

    lets_quit = False

    count = 0

    def render_buttons():
        for button in button_container:
            button.render(screen, BUTTON_TEXTURES)
        pygame.display.flip()
        pygame.time.delay(50)

    render_buttons()
    pygame.time.delay(1000)
    button_container[0].update(1,False)
    render_buttons()
    button_container[5].update(1,False)
    render_buttons()
    button_container[10].update(1,False)
    render_buttons()
    button_container[15].update(1,False)
    render_buttons()
    button_container[12].update(1,False)
    render_buttons()
    button_container[9].update(1,False)
    render_buttons()
    button_container[6].update(1,False)
    render_buttons()
    button_container[3].update(1,False)
    render_buttons()
    while not lets_quit:
        render_buttons()
        count = count + 1
        if count == 500:
            lets_quit = True

    pygame.quit()

if __name__ == '__main__': main()
