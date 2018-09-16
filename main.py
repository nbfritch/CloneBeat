"""Clonebeat"""
import os
import json
import pygame
from pygame.locals import Rect

UNIT_SCALE = 9
SCREENSIZE = Rect(0, 0, 90*UNIT_SCALE, 90*UNIT_SCALE)

NOT_ANIMATING_STATE = 0
NOT_HIT_ANIMATION_STATE = 1
MISS_ANIMIATION_STATE = 2
GOOD_ANIMATION_STATE = 3
GREAT_ANIMATION_STATE = 4
PERFECT_ANIMATION_STATE = 5

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

def get_spacing(number):
    """Calculates the position that a button should be rendered"""
    return (3 + number * 21) * UNIT_SCALE

def validate_song(song_array):
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

    def create_buttons(self):
        """Build us some buttons"""
        id_count = 0
        for row in range(0, 4):
            for col in range(0, 4):
                self.buttons.append(Button(row, col, id_count))
                id_count += 1

    def load_textures(self):
        """Load and scale the textures from file"""
        texture_names = [f"{x}.png" for x in range(0, 28)]

        raw_textures = [load_asset(name) for name in texture_names]
        scaled_textures = [
            pygame.transform.scale(texture, (20 * UNIT_SCALE, 20 * UNIT_SCALE))
            for texture in raw_textures
        ]

        self.textures = scaled_textures

    def load_song(self, song_instructions):
        """Load a song array to be played"""
        self.instructions = song_instructions

    def next_instruction(self):
        """Returns array of the next instructions to be executed"""
        current_instructions = []
        first_instruction = self.instructions.pop()
        current_instructions.append(first_instruction)
        while self.instructions[0]['offset'] == first_instruction['offset']:
            current_instructions.append(self.instructions.pop())
        return current_instructions

    def run(self):
        """Main game loop"""
        song_duration = max(set(i['offset'] for i in self.instructions))

        print(song_duration)

        for button in self.buttons:
            button.blank(self.screen, self.textures)
            button.instructions = [x['offset'] for x in self.instructions if x['id'] == button.id]
            button.instructions.sort()
        pygame.display.flip()

        game_start_time = pygame.time.get_ticks()
        last_render = game_start_time
        game_end_time = game_start_time + song_duration + 5000
        frame_start_time = game_start_time

        self.instructions.reverse()

        while frame_start_time < game_end_time:
            frame_start_time = pygame.time.get_ticks()
            events = pygame.event.get()
            for event in events:
                if event.type == pygame.KEYDOWN:
                    if event.key in list(KEY_MAPPING.keys()):
                        self.buttons[KEY_MAPPING[event.key]].hit()
                        print(f"Key {KEY_MAPPING[event.key]}")

            if frame_start_time > last_render + 15:
                frame_advance = (last_render - frame_start_time) / 16
                for button in self.buttons:
                    button.render(self.screen, self.textures, frame_advance)

                last_render = pygame.time.get_ticks()

class Button:
    """Touch the button"""
    def __init__(self, row, col, button_id):
        self.button_id = button_id
        self.loc_x = get_spacing(row)
        self.loc_y = get_spacing(col)
        self.animation_state = NOT_ANIMATING_STATE
        self.frame = 0

    def blank(self, surface, textures):
        """Shortcut to show a blank square"""
        surface.blit(textures[0], (self.loc_x, self.loc_y))
        self.frame = 1

    def hit(self):
        """Represents a hit on the button"""
        if self.animation_state == NOT_HIT_ANIMATION_STATE:
            if self.frame in range(23, 27):
                self.animation_state = PERFECT_ANIMATION_STATE
            elif self.frame in range(15, 23):
                self.animation_state = GREAT_ANIMATION_STATE
            elif self.frame in range(1, 15):
                self.animation_state = GOOD_ANIMATION_STATE

    def render(self, surface, textures, frame_advance=1):
        """Draw the button onto the surface"""
        if self.animation_state == NOT_ANIMATING_STATE:
            return

        if self.animation_state == NOT_HIT_ANIMATION_STATE:
            self.frame = self.frame + frame_advance
            if self.frame >= 27:
                self.animation_state = MISS_ANIMIATION_STATE
            surface.blit(textures[self.frame], (self.loc_x, self.loc_y))
            return

        if self.animation_state == GOOD_ANIMATION_STATE:
            return

        if self.animation_state == GREAT_ANIMATION_STATE:
            return

        if self.animation_state == PERFECT_ANIMATION_STATE:
            return

        if self.animation_state == MISS_ANIMIATION_STATE:
            return

def load_asset(file):
    """Loads and converts an image"""
    file = os.path.join("./assets", file)
    try:
        surface = pygame.image.load(file)
    except pygame.error:
        raise SystemExit('Could not load image "%s" %s'%(file, pygame.get_error()))
    return surface.convert()

def main():
    """Entry point of game"""
    pygame.init()

    start_time = pygame.time.get_ticks()
    bestdepth = pygame.display.mode_ok(SCREENSIZE.size, 0, 32)
    screen = pygame.display.set_mode(SCREENSIZE.size, 0, bestdepth)

    gaimu = Game(screen)
    gaimu.create_buttons()
    gaimu.load_textures()
    song_file = open('./song.jsonc', 'r')
    song = json.loads(song_file.read())
    song_file.close()
    if not validate_song(song):
        print("ERR, could not validate song")
        exit(1)

    gaimu.load_song(song)

    for _ in range(0, 500):
        gaimu.run()
        pygame.time.delay(16)

    end_time = pygame.time.get_ticks()
    print(f"Finished initialization in {end_time - start_time} ms")
    del start_time
    del end_time

    pygame.quit()

if __name__ == '__main__':
    main()
