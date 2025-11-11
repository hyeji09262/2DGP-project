from pico2d import load_image, get_time, load_font, SDL_KEYDOWN, SDLK_RIGHT, SDL_KEYUP, SDLK_LEFT

import game_framework
from state_machine import StateMachine


PIXEL_PER_METER = (10.0 / 0.3) # 10 pixel 30 cm
RUN_SPEED_KMPH = 25.0 # Km / Hour
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
        PITCH = 105  # 다음 프레임까지 이동량(여백 없으면 W와 같게)
        START_X = 225 # 첫 프레임의 left
        START_Y= 1075 # 줄의 bottom(y)

        left = START_X + (self.boy.frame % 4) * PITCH
        bottom = START_Y

        sx, sy = self.boy.screen_xy()

        if self.boy.face_dir == -1:  # 왼쪽 바라봄(반전 없음)
            self.boy.image.clip_draw(left, bottom, W, H, sx, sy)
        else:  # 오른쪽(수평 반전)
            self.boy.image.clip_composite_draw(left, bottom, W, H,
                                               0, 'h', sx, sy, W, H)


class Idle:

    def __init__(self, boy):
        self.boy = boy
        self.seq = [0, 0, 0, 0, 1]
        self.fps = 8.0
        self.acc = 0.0

    def enter(self, e):
        self.boy.dir = 0
        self.idx = 0
        self.acc = 0.0
        self.boy.frame = self.seq[self.idx]


    def exit(self, e):
        pass

    def do(self):
        self.acc += game_framework.frame_time
        step = 1.0 / self.fps
        while self.acc >= step:
            self.acc -= step
            # 다음 프레임으로
            self.seq = self.seq[1:] + self.seq[:1]
            self.boy.frame = self.seq[0]



    def draw(self):
        W, H = 100, 180
        PITCH = 105# 프레임 간 간격 (칸폭+여백)
        START_X = 220
        START_Y = 1260  # 그 줄의 bottom

        left = START_X + (self.boy.frame % 2) * PITCH
        bottom = START_Y

        sx, sy = self.boy.screen_xy()

        if self.boy.face_dir == -1:  # 왼쪽
            self.boy.image.clip_draw(left, bottom, W, H, sx, sy)
        else:  # 오른쪽(수평 반전)
            self.boy.image.clip_composite_draw(left, bottom, W, H,
                                               0, 'h', sx, sy, W, H)


class Boy:
    def __init__(self):
        self.font = load_font('ENCR10B.TTF', 16)

        self.x, self.y = 2500, 340
        self.frame = 0
        self.face_dir = 1
        self.dir = 0
        self.velocity = 0
        self.size = 1.0
        self.image = load_image('사진수집/character/캐릭터2.png')
        self.camera = None

        self.IDLE = Idle(self)
        self.Run = Run(self)
        self.state_machine = StateMachine(
            self.IDLE,
            {
                self.IDLE : {right_up : self.Run, left_up : self.Run, left_down : self.Run, right_down : self.Run},
                self.Run : {left_down : self.IDLE, right_down : self.IDLE, left_up : self.IDLE, right_up : self.IDLE},
            }
        )

    def screen_xy(self):
        if self.camera:
            return self.camera.world_to_screen(self.x, self.y)
        return self.x, self.y


    def update(self):
        self.state_machine.update()

    def handle_event(self, event):
        self.state_machine.handle_state_event(('INPUT', event))


    def draw(self):
        self.state_machine.draw()
        if self.camera:
            sx, sy = self.camera.world_to_screen(self.x, self.y)
        else:
             sx, sy = self.x, self.y

    def handle_event(self, event):
        self.state_machine.handle_state_event(('INPUT', event))
        pass

    def set_camera(self, cam):
        self.camera = cam

    def screen_xy(self):
        if self.camera:
            return self.camera.world_to_screen(self.x, self.y)
        return self.x, self.y