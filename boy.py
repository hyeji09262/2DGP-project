from pico2d import load_image, get_time, load_font
from sdl2 import SDL_KEYDOWN, SDLK_RIGHT, SDL_KEYUP, SDLK_LEFT

import game_framework
from state_machine import StateMachine


PIXEL_PER_METER = (10.0 / 0.3) # 10 pixel 30 cm
RUN_SPEED_KMPH = 20.0 # Km / Hour
RUN_SPEED_MPM = (RUN_SPEED_KMPH * 1000.0 / 60.0)
RUN_SPEED_MPS = (RUN_SPEED_MPM / 60.0)
RUN_SPEED_PPS = (RUN_SPEED_MPS * PIXEL_PER_METER)


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
        self.boy.frame = (self.boy.frame + 1) % 4
        self.boy.x += self.boy.dir * RUN_SPEED_PPS * game_framework.frame_time

    def draw(self):
        W, H = 100, 160  # 프레임 가로/세로
        PITCH = 100  # 다음 프레임까지 이동량(여백 없으면 W와 같게)
        START_X = 230 # 첫 프레임의 left
        START_Y= 1075 # 줄의 bottom(y)

        left = START_X + (self.boy.frame % 4) * PITCH
        bottom = START_Y

        if self.boy.face_dir == -1:
            self.boy.image.clip_draw(left, bottom, W, H, self.boy.x, self.boy.y)
        else:
            self.boy.image.clip_composite_draw(
                left, bottom, W, H,
                0, 'h',  # 회전 0, flip='h'
                self.boy.x, self.boy.y,
                W, H  # 출력 크기도 W,H로 통일(깜빡임 방지)
            )

class Idle:

    def __init__(self, boy):
        self.boy = boy

    def enter(self, e):
        self.boy.dir = 0
        self.boy.wait_start_time = get_time()

    def exit(self, e):
        pass

    def do(self):
        self.boy.frame = (self.boy.frame + 1) % 2


    def draw(self):
        W, H = 100, 180
        PITCH = 100 # 프레임 간 간격 (칸폭+여백)
        START_X = 220
        START_Y = 1260  # 그 줄의 bottom

        left = START_X + (self.boy.frame % 2) * PITCH
        bottom = START_Y

        if self.boy.face_dir == -1:
            self.boy.image.clip_draw(left, bottom, W, H, self.boy.x, self.boy.y)
        else:
            self.boy.image.clip_composite_draw(
                left, bottom, W, H,
                0, 'h',  # 회전 0, 가로 반전
                self.boy.x, self.boy.y,
                W, H  # 양쪽 크기 동일 (깜빡임/튀는 느낌 방지)
            )

class Boy:
    def __init__(self):
        self.font = load_font('ENCR10B.TTF', 16)

        self.x, self.y = 500, 200
        self.frame = 0
        self.face_dir = 1
        self.dir = 0
        self.velocity = 0
        self.size = 1.0
        self.image = load_image('사진수집/character/캐릭터2.png')

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

    def handle_event(self, event):
        self.state_machine.handle_state_event(('INPUT', event))
        pass

    def draw(self):
        self.state_machine.draw()

    def handle_event(self, event):
        self.state_machine.handle_state_event(('INPUT', event))
        pass