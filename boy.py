from pico2d import (load_image, get_time, load_font, SDL_KEYDOWN, SDLK_RIGHT, SDL_KEYUP,
                    SDLK_LEFT , SDLK_LCTRL, SDLK_UP)

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
def jump_key(e):
    return e[0] == 'INPUT' and e[1].type == SDL_KEYDOWN and e[1].key == SDLK_LCTRL

class Run:
    def __init__(self, boy):
        self.boy = boy

    def enter(self, e):
        if right_down(e):
            self.boy.dir = self.boy.face_dir = 1
        elif left_down(e):
            self.boy.dir = self.boy.face_dir = -1

    def exit(self, e):
        pass

    def do(self):
        self.boy.frame = (self.boy.frame + 1) % 4
        self.boy.x += self.boy.dir * RUN_SPEED_PPS * game_framework.frame_time

    def draw(self):
        W, H = 55, 80
        PITCH = 65  # 프레임 간 간격 (칸폭+여백)
        START_X = 0
        START_Y = 615  # 그 줄의 bottom

        left = START_X + (self.boy.frame % 4) * PITCH
        bottom = START_Y

        sx, sy = self.boy.screen_xy()

        S = self.boy.scale
        DW, DH = int(W * S), int(H * S)

        foot_fix = (DH - H) // 2
        y = sy - foot_fix  - self.boy.foot_run_adj

        if self.boy.face_dir == -1:  # 왼쪽 바라봄(반전 없음)
            self.boy.image.clip_composite_draw(left, bottom, W, H,0,'', sx, y, DW,DH)
        else:  # 오른쪽(수평 반전)
            self.boy.image.clip_composite_draw(left, bottom, W, H,
                                               0, 'h', sx, y, DW,DH)


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
        W, H = 55, 80
        PITCH = 58 # 프레임 간 간격 (칸폭+여백)
        START_X = 0
        START_Y = 720  # 그 줄의 bottom

        left = START_X + (self.boy.frame % 2) * PITCH
        bottom = START_Y

        sx, sy = self.boy.screen_xy()

        S = self.boy.scale
        DW, DH = int(W * S), int(H * S)

        foot_fix = (DH - H) // 2
        y = sy - foot_fix  - self.boy.foot_idle_adj

        if self.boy.face_dir == -1:  # 왼쪽
            self.boy.image.clip_composite_draw(left, bottom, W, H,0,'', sx, y,DW,DH)
        else:  # 오른쪽(수평 반전)
            self.boy.image.clip_composite_draw(left, bottom, W, H,
                                               0, 'h', sx, y,DW,DH)

class Hit:
    HIT_TIME = 0.2
    IF_TIME = 0.5
    KNOCK_PPS = 250

    W, H = 55, 80
    PITCH = 60  # 프레임 간 간격 (칸폭+여백)
    START_X = 0
    START_Y = 100  # 그 줄의 bottom

    FRAMES = 1
    FPS = 2

    def __init__(self, boy):
        self.boy = boy
        self.t = 0.0
        self.acc = 0.0
        self.f = 0
        self.knock_dir = -1
        self.if_timer = 0.0

    def enter(self, e):
        # e == ('TAKE_HIT', from_dir)  → from_dir: 공격자가 바라보는 방향(+1/-1)
        _, from_dir = e
        self.t = self.HIT_TIME
        self.acc = 0.0
        self.f = 0
        # 공격 반대방향으로 밀림
        self.knock_dir = -1 if from_dir > 0 else 1
        self.boy.if_timer = self.IF_TIME  # i-frame 시작

    def exit(self, e):
            pass

    def do(self):
            dt = game_framework.frame_time
            # 경직 시간 카운트
            self.t -= dt
            if self.t <= 0:
                self.boy.state_machine.handle_state_event(('END_HIT', 0))
                return

            # 넉백
            self.boy.x += self.knock_dir * self.KNOCK_PPS * dt
            self.boy.x += self.boy.dir * RUN_SPEED_PPS * dt

            # 피격 프레임 애니
            self.acc += dt
            step = 1.0 / self.FPS
            while self.acc >= step:
                self.acc -= step
                self.f = (self.f + 1) % self.FRAMES

    def draw(self):
            W, H = self.W, self.H
            left = self.START_X + (self.f % self.FRAMES) * self.PITCH
            bottom = self.START_Y

            sx, sy = self.boy.screen_xy()
            S = self.boy.scale
            DW, DH = int(W * S), int(H * S)

            foot_fix = (DH - H) // 2
            y = sy - foot_fix - getattr(self.boy, 'foot_idle_adj', 0)

            flip = '' if self.boy.face_dir == -1 else 'h'
            self.boy.image.clip_composite_draw(left, bottom, W, H, 0, flip, sx,y, DW, DH)

class Jump:
    GRAVITY_PPS = 1500.0
    JUMP_SPEED_PPS = 600.0
    MOVE_RATIO = 0.6

    def __init__(self, boy):
        self.boy = boy
        self.vy = 0.0
        self.acc = 0.0
        self.fps = 8.0
        self.hdir = 0

    def enter(self, e):
        self.vy = self.JUMP_SPEED_PPS
        self.acc = 0.0
        self.boy.in_air = True

        if self.boy.dir != 0:
            self.hdir = self.boy.dir
        else:
            self.hdir = 0

    def exit(self, e):
        self.boy.in_air = False
        self.vy = 0.0

    def do(self):
        dt = game_framework.frame_time
        self.vy -= self.GRAVITY_PPS * dt
        self.boy.y += self.vy * dt
        self.boy.x += self.hdir * RUN_SPEED_PPS * self.MOVE_RATIO * dt
        self.boy.frame = (self.boy.frame + 1) % 1

        if self.boy.camera and hasattr(self.boy.camera, 'ground_y'):
            ground_y = self.boy.camera.ground_y(self.boy.x)
        else:
            ground_y = self.boy.base_ground_y

        if self.boy.y <= ground_y:
            self.boy.y = ground_y
            self.boy.state_machine.handle_state_event(('LAND', 0))
            return

    def draw(self):
        W, H = 55, 80
        PITCH = 65
        START_X = 0
        START_Y = 615

        left = START_X + (self.boy.frame % 4) * PITCH
        bottom = START_Y

        sx, sy = self.boy.screen_xy()

        S = self.boy.scale
        DW, DH = int(W * S), int(H * S)

        foot_fix = (DH - H) // 2
        y = sy - foot_fix - self.boy.foot_run_adj

        flip = '' if self.boy.face_dir == -1 else 'h'
        self.boy.image.clip_composite_draw(left, bottom, W, H, 0, flip, sx, y, DW, DH)


class Boy:
    def __init__(self):
        self.font = load_font('ENCR10B.TTF', 16)

        self.scale = 1.2
        self.bb_offset_y = 40
        self.bb_offset_x = -10

        self.if_timer = 0.0
        self.Hit = Hit(self)

        self.foot_idle_adj = 36
        self.foot_run_adj = 36

        self.x, self.y = 500, 340
        self.base_ground_y = self.y
        self.in_air = False

        self.frame = 0
        self.face_dir = 1
        self.dir = 0
        self.velocity = 0
        self.size = 1.0
        self.image = load_image('사진수집/character/캐릭터 3.png')
        self.camera = None
        self.up_pressed = False
        self.left_pressed = False
        self.right_pressed = False

        def land_to_run(e, boy=self):
            return (e[0] == 'LAND') and (boy.left_pressed or boy.right_pressed)

        def land_to_idle(e, boy=self):
            return (e[0] == 'LAND') and (not boy.left_pressed and not boy.right_pressed)

        def left_up_to_idle(e, boy=self):
            return left_up(e) and (not boy.right_pressed)

        def left_up_to_run(e, boy=self):
            return left_up(e) and boy.right_pressed

        def right_up_to_idle(e, boy=self):
            return right_up(e) and (not boy.left_pressed)

        def right_up_to_run(e, boy=self):
            return right_up(e) and boy.left_pressed

        self.IDLE = Idle(self)
        self.Run = Run(self)
        self.Jump = Jump(self)
        self.state_machine = StateMachine(
            self.IDLE,
            {
                self.IDLE: {
                    left_down: self.Run,
                    right_down: self.Run,
                    jump_key: self.Jump,
                    (lambda e: e[0] == 'TAKE_HIT'): self.Hit
                },
                self.Run: {
                    # 방향키를 누르면 계속 Run 유지 (방향만 변경)
                    left_down: self.Run,
                    right_down: self.Run,

                    # 키를 뗐을 때: 다른 쪽 키 상태에 따라 Idle/Run 결정
                    left_up_to_idle: self.IDLE,
                    right_up_to_idle: self.IDLE,
                    left_up_to_run: self.Run,
                    right_up_to_run: self.Run,

                    jump_key: self.Jump,
                    (lambda e: e[0] == 'TAKE_HIT'): self.Hit
                },
                self.Hit: {
                    (lambda e: e[0] == 'END_HIT'): self.IDLE
                },

                self.Jump: {
                    land_to_run: self.Run,
                    land_to_idle: self.IDLE,
                    (lambda e: e[0] == 'TAKE_HIT'): self.Hit,
                    (lambda e: e[0] == 'LAND'): self.IDLE
                },

            }
        )




    def screen_xy(self):
        if self.camera:
            return self.camera.world_to_screen(self.x, self.y)
        return self.x, self.y


    def update(self):
        self.state_machine.update()
        if self.camera and hasattr(self.camera, 'ground_y'):
            if not self.in_air:
                ground = self.camera.ground_y(self.x)
                self.y = ground
        else:
            if not self.in_air:
                self.y = self.base_ground_y

        if self.if_timer > 0:
            self.if_timer -= game_framework.frame_time
            if self.if_timer < 0:
                self.if_timer = 0.0

    def handle_event(self, event):
        self.state_machine.handle_state_event(('INPUT', event))
        if event.type == SDL_KEYDOWN:
            if event.key == SDLK_LEFT:
                self.left_pressed = True
                self.dir = -1
                self.face_dir = -1
            elif event.key == SDLK_RIGHT:
                self.right_pressed = True
                self.dir = 1
                self.face_dir = 1
            elif event.key == SDLK_UP:
                self.up_pressed = True
        elif event.type == SDL_KEYUP:
            if event.key == SDLK_LEFT:
                self.left_pressed = False
                if self.right_pressed:
                    self.dir = 1
                    self.face_dir = 1
                else:
                    self.dir = 0
            elif event.key == SDLK_RIGHT:
                self.right_pressed = False
                if self.left_pressed:
                    self.dir = -1
                    self.face_dir = -1
                else:
                    self.dir = 0
            elif event.key == SDLK_UP:
                self.up_pressed = False


    def draw(self):
        flicker = (self.if_timer > 0.0) and ((int(get_time() * 10) % 2) == 0)

        if flicker:
            try:
                self.image.opacify(0.35)
            except:
                pass

        self.state_machine.draw()

        if flicker:
            try:
                self.image.opacify(1.0)
            except:
                pass


    def set_camera(self, cam):
        self.camera = cam

    def screen_xy(self):
        if self.camera:
            return self.camera.world_to_screen(self.x, self.y)
        return self.x, self.y

    def get_bb(self):
        W, H = 35, 60
        S = getattr(self, 'scale', 1.0)


        hw = int(W * S) // 2
        hh = int(H * S) // 2

        shift = -7
        offset_x = shift * self.face_dir

        cx = self.x + offset_x
        cy = self.y - self.bb_offset_y

        return (cx - hw, cy - hh, cx + hw, cy + hh)


    def take_hit(self, from_dir: int):
        if self.if_timer > 0:
            return

        self.if_timer = 0.5
        IMPULSE = 20
        knock_dir = -1 if from_dir > 0 else 1
        self.x += knock_dir * IMPULSE

        self.state_machine.handle_state_event(('TAKE_HIT', from_dir))