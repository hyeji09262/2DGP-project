from pico2d import (load_image, get_time, load_font, SDL_KEYDOWN, SDLK_RIGHT, SDL_KEYUP,
                    SDLK_LEFT , SDLK_LCTRL, SDLK_UP, SDLK_z,SDLK_LALT, get_canvas_width, get_canvas_height, draw_rectangle)

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
    return e[0] == 'INPUT' and e[1].type == SDL_KEYDOWN and e[1].key == SDLK_LALT
def attack_key(e):
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
    HIT_TIME = 0.1
    IF_TIME = 2.0
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
    GRAVITY_PPS = 2000.0
    JUMP_SPEED_PPS = 700.0
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
        if isinstance(e, tuple) and e[0] == 'LAND':
            self.boy.in_air = False
            self.vy = 0.0

    def do(self):
        dt = game_framework.frame_time
        self.vy -= self.GRAVITY_PPS * dt
        self.boy.y += self.vy * dt
        self.boy.air_vy = self.vy
        self.boy.x += self.hdir * RUN_SPEED_PPS * self.MOVE_RATIO * dt
        self.boy.frame = (self.boy.frame + 1) % 1

        if self.boy.camera and hasattr(self.boy.camera, 'ground_y'):
            ground_y = self.boy.camera.ground_y(self.boy.x)
        else:
            ground_y = self.boy.base_ground_y

        if self.boy.y <= ground_y:
            self.boy.y = ground_y
            self.boy.in_air = False
            self.vy = 0.0
            self.boy.air_vy = 0.0
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

ATTACK_A_FRAMES = [
    (0,   470, 90, 80),
    (95,  460, 65, 100),
    (158, 470, 90, 80),
    (252, 470, 90, 80),
    (345, 470, 90, 80),
    (434, 470, 91, 80),
]

ATTACK_B_FRAMES = [
    (0,   280, 60, 100),
    (65,  280, 60, 100),
    (130, 280, 84, 100),
    (213, 280, 84, 100),
    (296, 280, 84, 100),
    (379, 280, 85, 100),
]

class Attack:

    DURATION = 1.0  # 전체 공격 모션 시간
    HIT_START = 0.10  # 이 시점부터
    HIT_END = 0.25  # 이 시점까지 공격 판정 활성

    FPS = 6
    FRAMES_A = len(ATTACK_A_FRAMES)
    FRAMES_B = len(ATTACK_B_FRAMES)


    def __init__(self, boy):
        self.boy = boy
        self.t = 0.0
        self.acc = 0.0
        self.f = 0
        self.style = 0
        self.air_attack = False
        self.vy = 0.0

    def enter(self, e):
        self.t = 0.0
        self.acc = 0.0
        self.f = 0
        self.boy.attack_active = False  # 공격 판정 OFF
        self.style = self.boy.attack_style
        self.boy.attack_style ^= 1

        self.air_attack = self.boy.in_air

        if self.air_attack:
            self.vy = 0.0
        else:
            self.vy = 0.0


    def exit(self, e):
        self.boy.attack_active = False  # 상태 나갈 때 항상 OFF

    def do(self):
        dt = game_framework.frame_time
        self.t += dt

        if self.air_attack:
            self.vy -= Jump.GRAVITY_PPS * dt
            self.boy.y += self.vy * dt

            self.boy.air_vy = self.vy

            if self.boy.camera and hasattr(self.boy.camera, 'ground_y'):
                ground_y = self.boy.camera.ground_y(self.boy.x)
            else:
                ground_y = self.boy.base_ground_y

            if self.boy.y <= ground_y:
                self.boy.y = ground_y
                self.boy.in_air = False
                self.air_attack = False
                self.vy = 0.0
                self.boy.air_vy = 0.0

        if self.HIT_START <= self.t <= self.HIT_END:
            self.boy.attack_active = True
        else:
            self.boy.attack_active = False

        self.boy.x += self.boy.face_dir * RUN_SPEED_PPS * 0.0 * dt

        self.acc += dt
        step = 1.0 / self.FPS
        while self.acc >= step:
            self.acc -= step
            if self.style == 0:
                self.f = (self.f + 1) % self.FRAMES_A
            else:
                self.f = (self.f + 1) % self.FRAMES_B

        if self.t >= self.DURATION:
            self.boy.attack_active = False
            self.boy.state_machine.handle_state_event(('END_ATTACK', 0))

    def draw(self):

        if self.style == 0:
            frames = ATTACK_A_FRAMES
        else:
            frames = ATTACK_B_FRAMES

        left_tex, bottom_tex, W, H,  = frames[self.f]

        sx, sy = self.boy.screen_xy()

        S = self.boy.scale
        DW, DH = int(W * S), int(H * S)
        foot_fix = (DH - H) // 2
        base_y = sy - foot_fix - self.boy.foot_run_adj

        if self.style == 0:  # A 모션
            y = base_y - self.boy.foot_attack_a_adj
        else:  # B 모션
            y = base_y - self.boy.foot_attack_b_adj

        flip = '' if self.boy.face_dir == -1 else 'h'
        self.boy.image.clip_composite_draw(left_tex, bottom_tex, W, H, 0, flip, sx, y, DW, DH)
        half_w = DW // 2
        half_h = DH // 2
        lx = sx - half_w  # left
        bx = y - half_h  # bottom
        rx = sx + half_w  # right
        tx = y + half_h  # top

        draw_rectangle(lx, bx, rx, tx)

class Die:
    FPS = 6.0
    DURATION = 1.0


    def __init__(self, boy):
        self.boy = boy
        self.acc = 0.0
        self.t = 0.0
        self.f = 0

    def enter(self, e):
        # 죽을 때는 움직임 정지
        self.boy.dir = 0
        self.acc = 0.0
        self.t = 0.0
        self.f = 0

    def exit(self, e):
        pass

    def do(self):
        dt = game_framework.frame_time
        self.t += dt
        self.acc += dt

        # 프레임 넘기기
        step = 1.0 / self.FPS
        while self.acc >= step:
            self.acc -= step
            if self.f < len(self.FRAMES) - 1:
                self.f += 1

        if self.t >= self.DURATION:
            self.boy.alive = False  # 이 뒤로는 입력/업데이트 안 받게 쓸 수 있음

    def draw(self):
        if not self.FRAMES:
            return  # 아직 프레임 숫자 안 채웠으면 그냥 안 그림

        left, bottom, W, H = self.FRAMES[self.f]

        sx, sy = self.boy.screen_xy()
        S = self.boy.scale
        DW, DH = int(W * S), int(H * S)

        foot_fix = (DH - H) // 2
        y = sy - foot_fix - self.boy.foot_idle_adj

        flip = '' if self.boy.face_dir == -1 else 'h'
        self.boy.die_image.clip_composite_draw(
            left, bottom, W, H,0, flip,sx, y, DW, DH)


class Boy:
    def __init__(self):
        self.font = load_font('ENCR10B.TTF', 16)
        self.image = load_image('사진수집/character/캐릭터 3.png')
        self.die_image = load_image('사진수집/etc/무덤.png')

        self.scale = 1.2
        self.bb_offset_y = 40
        self.bb_offset_x = -10

        self.if_timer = 0.0
        self.Hit = Hit(self)

        self.foot_idle_adj = 36
        self.foot_run_adj = 36
        self.foot_attack_a_adj = -5
        self.foot_attack_b_adj = -10

        self.max_hp = 100  # 총 HP (원하면 숫자 조정)
        self.hp = self.max_hp
        self.alive = True

        self.x, self.y = 500, 340
        self.base_ground_y = self.y
        self.in_air = False

        self.frame = 0
        self.face_dir = 1
        self.dir = 0
        self.velocity = 0
        self.size = 1.0
        self.camera = None
        self.up_pressed = False
        self.left_pressed = False
        self.right_pressed = False
        self.pick_pressed = False
        self.attack_active = False
        self.attack_style = 0

        self.level = 1
        self.exp = 0
        self.exp_to_next = 100

        self.base_max_hp = 100
        self.max_hp = self.base_max_hp
        self.hp = self.max_hp
        self.alive = True


        self.inventory = {
            '10원': 0,
            '100원': 0,
            '1000원': 0,
            '5000원': 0,
            '주황버섯의 갓': 0,
        }

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

        def attack_end_to_run(e, boy=self):
            return (e[0] == 'END_ATTACK') and (boy.left_pressed or boy.right_pressed)

        def attack_end_to_idle(e, boy=self):
            return (e[0] == 'END_ATTACK') and (not boy.left_pressed and not boy.right_pressed)

        self.IDLE = Idle(self)
        self.Run = Run(self)
        self.Jump = Jump(self)
        self.Attack = Attack(self)
        self.Die = Die(self)

        self.state_machine = StateMachine(
            self.IDLE,
            {
                self.IDLE: {
                    left_down: self.Run,
                    right_down: self.Run,
                    jump_key: self.Jump,
                    attack_key: self.Attack,
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
                    attack_key: self.Attack,
                    (lambda e: e[0] == 'TAKE_HIT'): self.Hit
                },
                self.Hit: {
                    (lambda e: e[0] == 'END_HIT'): self.IDLE
                },

                self.Jump: {
                    land_to_run: self.Run,
                    land_to_idle: self.IDLE,
                    attack_key: self.Attack,
                    (lambda e: e[0] == 'TAKE_HIT'): self.Hit,
                    (lambda e: e[0] == 'LAND'): self.IDLE
                },
                self.Attack: {
                    attack_end_to_run: self.Run,  # 공격 끝 + 방향키 있음 → Run
                    attack_end_to_idle: self.IDLE,  # 공격 끝 + 방향키 없음 → Idle
                    (lambda e: e[0] == 'TAKE_HIT'): self.Hit
                },
                self.Die: {
                    # 죽은 상태에선 다른 상태로 안 돌아감
                }

            }
        )

    DIE_FRAMES = [
        (6, 56, 85, 43),
        (100, 54, 85, 47),
        (195, 54, 89, 44),
        (305, 54, 94, 44),
        (454, 54, 51, 43),
        (570, 54, 47, 44),
    ]
    DIE_FPS = 6.0  # 1초에 6프레임 정도
    DIE_LOOP = False



    def screen_xy(self):
        if self.camera:
            return self.camera.world_to_screen(self.x, self.y)
        return self.x, self.y


    def update(self):

        if not self.alive:
            dt = game_framework.frame_time
            self.dead_anim_t += dt

            if self.camera and hasattr(self.camera, 'ground_y'):
                self.y = self.camera.ground_y(self.x)

                # 죽는 애니 끝났는지 체크 (원하면 나중에 사용)
            total_frames = len(self.DIE_FRAMES)
            if not self.DIE_LOOP:
                max_t = total_frames / self.DIE_FPS
                if self.dead_anim_t >= max_t:
                    self.dead_anim_t = max_t
                    self.dead_anim_done = True

            return

        self.state_machine.update()

        if self.camera and hasattr(self.camera, 'ground_y'):
            if not getattr(self, 'in_air', False):
                ground = self.camera.ground_y(self.x)
                self.y = ground

        if self.if_timer > 0:
            self.if_timer -= game_framework.frame_time
            if self.if_timer < 0:
                self.if_timer = 0.0


    def handle_event(self, event):
        if not self.alive:
            return

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

            elif event.key == SDLK_z:
                self.pick_pressed = True

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

            elif event.key == SDLK_z:
                self.pick_pressed = False




    def draw(self):
        if not self.alive:
            sx, sy = self.screen_xy()

            # 죽는 애니 프레임 계산
            frames = self.DIE_FRAMES  # [(left,bottom,w,h), ...]
            if not frames:
                # 프레임 아직 안 잡았으면 일단 통짜로 그리기
                self.die_image.draw(sx, sy)
                return# 프레임 정의 아직 안 했으면 그냥 안 그림

            index = int(self.dead_anim_t * self.DIE_FPS)

            if self.DIE_LOOP:
                index = index % len(frames)
            else:
                if index >= len(frames):
                    index = len(frames) - 1

            left, bottom, W, H = frames[index]

            sx, sy = self.screen_xy()
            S = self.scale
            DW, DH = int(W * S), int(H * S)

            foot_fix = (DH - H) // 2
            y = sy - foot_fix - self.foot_idle_adj

            flip = '' if self.face_dir == -1 else 'h'

            self.die_image.clip_composite_draw(
                left, bottom, W, H,
                0, flip,
                sx, y, DW, DH
            )
            return

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

        self.font.draw(20, 560, f'HP: {self.hp}/{self.max_hp}', (255, 0, 0))


    def set_camera(self, cam):
        self.camera = cam

    def screen_xy(self):
        if self.camera:
            return self.camera.world_to_screen(self.x, self.y)
        return self.x, self.y

    def get_bb(self):
        if hasattr(self, 'alive') and not self.alive:
            return (0, 0, 0, 0)

        W, H = 35, 60
        S = getattr(self, 'scale', 1.0)


        hw = int(W * S) // 2
        hh = int(H * S) // 2

        shift = -7
        offset_x = shift * self.face_dir

        cx = self.x + offset_x
        cy = self.y - self.bb_offset_y

        return (cx - hw, cy - hh, cx + hw, cy + hh)

    def get_attack_bb(self):
        bx0, by0, bx1, by1 = self.get_bb()

        reach = 45
        h = by1 - by0
        ay0 = by0 + int(h * 0.3)
        ay1 = by1

        if self.face_dir == 1:
            return (bx1, ay0, bx1 + reach, ay1)
        else:
            return (bx0 - reach, ay0, bx0, ay1)

    def take_hit(self, from_dir: int, damage: int = 1):
        if not getattr(self, 'alive', True):
            return

        if self.if_timer > 0:
            return

        self.hp -= damage
        if self.hp <= 0:
            self.hp = 0
            self.alive = False
            print("[PLAYER] DEAD")

            self.dir = 0
            self.velocity = 0

            return

        self.if_timer = 0.5  # 0.5초 동안 무적

        IMPULSE = 20  # 한 번에 튕겨나가는 거리
        # 공격 반대 방향으로 넉백
        knock_dir = -1 if from_dir > 0 else 1
        self.x += knock_dir * IMPULSE

        # 피격 상태로 전환 (Hit 상태가 TAKE_HIT 이벤트를 받아서 처리)
        self.state_machine.handle_state_event(('TAKE_HIT', from_dir))

    def obtain_item(self, kind: str):
        """드랍템을 주웠을 때 호출 (인벤토리에 기록)"""
        if kind in self.inventory:
            self.inventory[kind] += 1
        else:
            self.inventory[kind] = 1

        print(f"OBTAIN ITEM: {kind}, now have {self.inventory[kind]}")

    def gain_exp(self, amount: int):
        """경험치 획득"""
        if not getattr(self, 'alive', True):
            return

        self.exp += amount
        print(f"[PLAYER] GET EXP {amount}, now {self.exp}/{self.exp_to_next}")

        while self.exp >= self.exp_to_next:
            self.exp -= self.exp_to_next
            self.level_up()

    def level_up(self):
        """레벨업 시 체력, 필요 경험치 증가"""
        self.level += 1
        print(f"[PLAYER] LEVEL UP! Lv.{self.level}")

        self.max_hp += 20  # 레벨당 +20

        # 체력 풀 회복
        self.hp = self.max_hp

        self.exp_to_next = int(self.exp_to_next * 1.5)
        if self.exp_to_next < 50:
            self.exp_to_next = 50

        print(f"[PLAYER] NEXT EXP = {self.exp_to_next}")

    def draw_ui(self):
        cw = get_canvas_width()
        ch = get_canvas_height()

        base_width = 200
        bar_height = 16

        width_ratio = self.max_hp / self.base_max_hp if self.base_max_hp > 0 else 1.0
        max_bar_width = int(base_width * width_ratio)

        # ✅ 화면 중앙 아래 정렬
        center_x = cw // 2
        bar_x0 = center_x - max_bar_width // 2
        hp_bar_y0 = 40  # 화면 아래에서 40픽셀 위
        hp_bar_y1 = hp_bar_y0 + bar_height

        # HP 비율
        hp_ratio = self.hp / self.max_hp if self.max_hp > 0 else 0.0
        hp_ratio = max(0.0, min(1.0, hp_ratio))
        cur_hp_width = int(max_bar_width * hp_ratio)

        draw_rectangle(bar_x0, hp_bar_y0, bar_x0 + max_bar_width, hp_bar_y1)
        # 현재 HP 바
        if cur_hp_width > 0:
            draw_rectangle(bar_x0, hp_bar_y0, bar_x0 + cur_hp_width, hp_bar_y1)

        # HP 글자 (HP / MaxHP / Lv)
        hp_text = f"HP {self.hp}/{self.max_hp}   Lv.{self.level}"
        self.font.draw(bar_x0, hp_bar_y1 + 5, hp_text, (255, 255, 255))

        exp_bar_y0 = hp_bar_y0 - 14
        exp_bar_y1 = exp_bar_y0 + 8

        if self.exp_to_next > 0:
            exp_ratio = self.exp / self.exp_to_next
        else:
            exp_ratio = 0.0
        exp_ratio = max(0.0, min(1.0, exp_ratio))

        # EXP 전체 바 테두리
        draw_rectangle(bar_x0, exp_bar_y0, bar_x0 + max_bar_width, exp_bar_y1)

        cur_exp_width = int(max_bar_width * exp_ratio)
        if cur_exp_width > 0:
            draw_rectangle(bar_x0, exp_bar_y0, bar_x0 + cur_exp_width, exp_bar_y1)

        exp_text = f"EXP {int(self.exp)}/{self.exp_to_next}"
        self.font.draw(bar_x0, exp_bar_y0 - 12, exp_text, (200, 200, 200))