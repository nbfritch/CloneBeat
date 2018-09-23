"""Clonebeat"""
import os
import json
import pygame
from pygame.locals import Rect

UNIT_SCALE: int = 9
SCREENSIZE = Rect(0, 0, 90*UNIT_SCALE, 90*UNIT_SCALE)

NOT_ANIMATING_STATE: int = 0
NOT_HIT_ANIMATION_STATE: int = 1
MISS_ANIMIATION_STATE: int = 2
GOOD_ANIMATION_STATE: int = 3
GREAT_ANIMATION_STATE: int = 4
PERFECT_ANIMATION_STATE: int = 5

ANIMATION_PRE_OFFSET: int = 28 / 60 * 1000
ANIMATION_POST_OFFSET: int = 8 / 60 * 1000

KEY_MAPPING = {
    pygame.K_1: 0,
    pygame.K_q: 1,
    pygame.K_a: 2,
    pygame.K_z: 3,
    pygame.K_2: 4,
    pygame.K_w: 5,
    pygame.K_s: 6,
    pygame.K_x: 7,
    pygame.K_3: 8,
    pygame.K_e: 9,
    pygame.K_d: 10,
    pygame.K_c: 11,
    pygame.K_4: 12,
    pygame.K_r: 13,
    pygame.K_f: 14,
    pygame.K_v: 15
}

def load_asset(file):
    """Loads and converts an image"""
    file = os.path.join("./assets", file)
    try:
        surface = pygame.image.load(file)
    except pygame.error:
        raise SystemExit('Could not load image "%s" %s'%(file, pygame.get_error()))
    return surface.convert()

def get_spacing(number: int) -> int:
    """Calculates the position that a button should be rendered"""
    return (3 + number * 21) * UNIT_SCALE

def validate_song(song_array) -> bool:
    """Function to ensure that a song does not define button presses
        that are faster than the game can display"""
    ids = set(x['id'] for x in song_array)
    if max(ids) > 15:
        return False

    for i in ids:
        button_instructions = [s['offset'] for s in song_array if s['id'] == i]
        button_instructions.sort()
        if button_instructions:
            previous = button_instructions[0]
            for index in range(1, len(button_instructions)):
                if button_instructions[index] - previous < 190:
                    return False
                button_instructions[index] = previous

    return True

class Game:
    """Class that represents the game"""
    def __init__(self, screen):
        self.screen = screen
        self.buttons = []
        self.instructions = []
        self.textures = []

    def init(self) -> None:
        """Loads textures and creates buttons"""
        self._load_textures()
        self._create_buttons()

    def _create_buttons(self) -> None:
        """Build us some buttons"""
        id_count = 0
        for row in range(0, 4):
            for col in range(0, 4):
                self.buttons.append(Button(id_count, row, col, self.screen, self.textures))
                id_count += 1

    def _load_textures(self) -> None:
        """Load and scale the textures from file"""
        texture_names = [f"{x}.png" for x in range(0, 28)]

        raw_textures = [load_asset(name) for name in texture_names]
        scaled_textures = [
            pygame.transform.scale(texture, (20 * UNIT_SCALE, 20 * UNIT_SCALE))
            for texture in raw_textures
        ]

        self.textures = scaled_textures

    def load_song(self, song_instructions) -> None:
        """Load a song array to be played"""
        self.instructions = song_instructions


    def run(self) -> None:
        """Main game loop"""
        song_duration = max(set(i['offset'] for i in self.instructions))

        for button in self.buttons:
            button.blank()
            button.instructions = [x['offset'] for x in self.instructions if x['id'] == button.button_id]
            button.instructions.sort()
        pygame.display.flip()

        game_start_time = pygame.time.get_ticks()
        game_end_time = game_start_time + song_duration + 5000
        frame_start_time = game_start_time

        while frame_start_time < game_end_time:
            frame_start_time = pygame.time.get_ticks()
            events = pygame.event.get()
            for event in events:
                if event.type == pygame.KEYDOWN:
                    if event.key in list(KEY_MAPPING.keys()):
                        self.buttons[KEY_MAPPING[event.key]].hit(frame_start_time)
                        print(f"Key {KEY_MAPPING[event.key]}")

            for butt in self.buttons:
                butt.render(frame_start_time)
            pygame.display.flip()

class Button:
    """Touch the button"""
    def __init__(self, button_id, row, col, screen, textures):
        self.button_id = button_id
        self.loc_x = get_spacing(row)
        self.loc_y = get_spacing(col)
        self.animation_state = NOT_ANIMATING_STATE
        self.screen = screen
        self.instructions = []
        self.textures = textures

    def _draw(self, frame):
        """Meta method to render the square"""
        self.screen.blit(self.textures[frame % len(self.textures)], (self.loc_x, self.loc_y))

    def blank(self):
        """Shortcut to show a blank square"""
        self._draw(0)

    def hit(self, time):
        """Represents a hit on the button"""
        for i in self.instructions:
            if time >= i - ANIMATION_PRE_OFFSET and time <= i + ANIMATION_POST_OFFSET:
                frame = (time - i) / 16
                if frame in range(0, 12):
                    self.animation_state = GOOD_ANIMATION_STATE
                elif frame in range(12, 18):
                    self.animation_state = GREAT_ANIMATION_STATE
                elif frame in range(18, 32):
                    self.animation_state = PERFECT_ANIMATION_STATE
                elif frame in range(32, 40):
                    self.animation_state = GREAT_ANIMATION_STATE
                return

    def render(self, time):
        """Draw the button onto the surface"""
        for i in self.instructions:
            if time >= i - ANIMATION_PRE_OFFSET and time <= i + ANIMATION_POST_OFFSET:
                frame = int((time - (i - ANIMATION_PRE_OFFSET)) / 16)
                self._draw(frame)
                return
        self._draw(0)

def main():
    """Entry point of game"""
    pygame.init()

    start_time = pygame.time.get_ticks()
    bestdepth = pygame.display.mode_ok(SCREENSIZE.size, 0, 32)
    screen = pygame.display.set_mode(SCREENSIZE.size, 0, bestdepth)

    gaimu = Game(screen)
    gaimu.init()

    song_file = open('./song.jsonc', 'r')
    song = json.loads(song_file.read())
    song_file.close()
    if not validate_song(song):
        print("ERR, could not validate song")
        exit(1)

    gaimu.load_song(song)

    end_time = pygame.time.get_ticks()
    print(f"Finished initialization in {end_time - start_time} ms")

    gaimu.run()

    pygame.quit()

if __name__ == '__main__':
    main()
