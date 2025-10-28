from pico2d import load_image, get_time
from sdl2 import SDL_KEYDOWN, SDLK_RIGHT, SDL_KEYUP, SDLK_LEFT

from state_machine import StateMachine


def right_down(e):
    return e[0] == 'INPUT' and e[1].type == SDL_KEYDOWN and e[1].key == SDLK_RIGHT
def right_up(e):
    return e[0] == 'INPUT' and e[1].type == SDL_KEYUP and e[1].key == SDLK_RIGHT
def left_down(e):
    return e[0] == 'INPUT' and e[1].type == SDL_KEYDOWN and e[1].key == SDLK_LEFT
def left_up(e):
    return e[0] == 'INPUT' and e[1].type == SDL_KEYUP and e[1].key == SDLK_LEFT


class Run:
    def __init__(self, boy):
        self.boy = boy

    def enter(self, e):
        if right_down(e) or left_up(e):
            self.boy.dir = self.boy.face_dir = 1
        elif left_down(e) or right_up(e):
            self.boy.dir = self.boy.face_dir = -1

    def exit(self, e):
        pass

    def do(self):
        self.boy.frame = (self.boy.frame + 1) % 3
        self.boy.x += self.boy.dir * 5

    def draw(self):
        if self.boy.face_dir == 1: # right
            self.boy.image.clip_draw(self.boy.frame * 100, 100, 100, 100, self.boy.x, self.boy.y)
        else: # face_dir == -1: # left
            self.boy.image.clip_draw(self.boy.frame * 100, 0, 100, 100, self.boy.x, self.boy.y)


class Idle:

    def __init__(self, boy):
        self.boy = boy

    def enter(self, e):
        self.boy.dir = 0
        self.boy.wait_start_time = get_time()

    def exit(self, e):
        pass

    def do(self):
        self.boy.frame = (self.boy.frame + 1) %1

    def draw(self):
        if self.boy.face_dir == 1:  # right
            self.boy.image.clip_draw(self.boy.frame * 180, 920, 180, 230, self.boy.x, self.boy.y)
        else:  # face_dir == -1: # left
            self.boy.image.clip_composite_draw(self.boy.frame * 180, 920, 180, 230, 0, 'h', self.boy.x, self.boy.y, 180, 230)


class Boy:
    def __init__(self):
        self.x, self.y = 500, 100
        self.frame = 0
        self.face_dir = 1
        self.dir = 0
        self.velocity = 0
        self.size = 1.0
        self.image = load_image('사진수집/character/캐릭터1.png')

        self.IDLE = Idle(self)
        self.Run = Run(self)
        self.state_machine = StateMachine(
            self.IDLE,
            {
                self.IDLE : {right_up : self.Run, left_up : self.Run, left_down : self.Run, right_down : self.Run},
                self.Run : {left_down : self.IDLE, right_down : self.IDLE, left_up : self.IDLE, right_up : self.IDLE},
            }
        )


    def update(self):
        self.state_machine.update()

    def draw(self):
        self.state_machine.draw()

    def handle_event(self, event):
        self.state_machine.handle_state_event(('INPUT', event))
        pass