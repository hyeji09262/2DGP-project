from pico2d import *
import random
import game_framework


PIXEL_PER_METER = (10.0 / 0.3) # 10 pixel 30 cm
RUN_SPEED_KMPH = 20.0 # Km / Hour
RUN_SPEED_MPM = (RUN_SPEED_KMPH * 1000.0 / 60.0)
RUN_SPEED_MPS = (RUN_SPEED_MPM / 60.0)
RUN_SPEED_PPS = (RUN_SPEED_MPS * PIXEL_PER_METER)

SHEET_PATH_MUSH = '사진수집/monster/주황버섯.png'
SHEET_PATH_AXE  = '사진수집/monster/엑스텀프.png'


class Mushroom:
    RUN_FRAMES = [
        # (left, bottom, w, h)
        (235, 260, 145, 120),
        (381, 260, 113, 120),
        (490, 260, 145, 120),
    ]
    FPS_RUN = 6.0

    HIT_FRAMES = [
        (235, 140, 145, 120),
    ]
    FPS_HIT = 10.0
    HIT_DURATION = 0.25  # 피격 모션 유지 시간

    DIE_FRAMES = [
        (240, 25, 130, 102),
        (387, 25, 110, 100),
        (490, 25, 120, 100),
    ]
    FPS_DIE = 10

    FRAME_SCALE = 0.8
    FOOT_ADJ_RUN = 45
    FOOT_ADJ_DIE = 65
    FRAME_BB_OFFSET_Y = 30

    def __init__(self, x, y, field=None):
        self.x, self.y = x, y
        self.dir = random.choice([-1, 1])   # -1: 왼쪽, 1: 오른쪽

        self.frame = 0
        self.acc = 0.0
        self.state_t = 0.0

        self.scale = self.FRAME_SCALE
        self.foot_adj_run = self.FOOT_ADJ_RUN
        self.foot_adj_die = self.FOOT_ADJ_DIE
        self.bb_offset_y = self.FRAME_BB_OFFSET_Y

        self.image = load_image(SHEET_PATH_MUSH)

        self.camera = None
        if field:
            self.set_camera(field)

        # 월드 경계 (기본값 — playmode에서 맵 폭으로 덮어써줄 것)
        self.world_min_x = 0
        self.world_max_x = 5000

        # 상태 / 체력
        self.state = 'run'
        self.hp = 1
        self.dead = False

        # 피격 넉백
        self.hit_dir = 0
        self.hit_back_speed = 200.0
        self.hit_cool = 0.0

        self.contact_damage = 2

    # 카메라(필드) 연결
    def set_camera(self, cam):
        self.camera = cam
        if hasattr(cam, 'bg_w'):
            self.world_max_x = int(cam.bg_w)

    # (선택) 외부에서 경계 지정
    def set_world_bounds(self, x0, x1):
        self.world_min_x = x0
        self.world_max_x = x1

    def screen_xy(self):
        if self.camera:
            return self.camera.world_to_screen(self.x, self.y)
        return self.x, self.y

    def take_hit(self, damage=1, from_dir=1):
        # 이미 죽었거나 죽는 중이면 무시
        if self.dead or self.state == 'die':
            return

        dmg = max(1, int(damage))
        self.hp -= dmg
        self.hit_dir = -from_dir  # 공격 반대 방향으로 넉백

        print(f"[MUSHROOM] hit! dmg={dmg}, hp -> {self.hp}")

        if self.hp <= 0:
            self.state = 'die'
            self.state_t = 0.0
            self.frame = 0
        else:
            self.state = 'hit'
            self.state_t = 0.0
            self.frame = 0

    def update(self):
        dt = game_framework.frame_time
        if self.dead:
            return

        if self.hit_cool > 0:
            self.hit_cool -= dt
            if self.hit_cool < 0:
                self.hit_cool = 0

        self.state_t += dt

        # -------- run 상태 --------
        if self.state == 'run':
            self.x += self.dir * RUN_SPEED_PPS * dt

            if self.x < self.world_min_x:
                self.x = self.world_min_x
                self.dir = 1
            elif self.x > self.world_max_x:
                self.x = self.world_max_x
                self.dir = -1

            if self.camera and hasattr(self.camera, 'ground_y'):
                self.y = self.camera.ground_y(self.x)

            self.acc += dt
            step = 1.0 / self.FPS_RUN
            while self.acc >= step:
                self.acc -= step
                self.frame = (self.frame + 1) % len(self.RUN_FRAMES)

        # -------- hit 상태 --------
        elif self.state == 'hit':
            self.x += self.hit_dir * self.hit_back_speed * dt

            if self.camera and hasattr(self.camera, 'ground_y'):
                self.y = self.camera.ground_y(self.x)

            self.acc += dt
            step = 1.0 / self.FPS_HIT
            while self.acc >= step:
                self.acc -= step
                if len(self.HIT_FRAMES) > 1:
                    self.frame = (self.frame + 1) % len(self.HIT_FRAMES)
                else:
                    self.frame = 0

            if self.state_t >= self.HIT_DURATION:
                self.state = 'run'
                self.state_t = 0.0
                self.frame = 0

        # -------- die 상태 --------
        elif self.state == 'die':
            if self.camera and hasattr(self.camera, 'ground_y'):
                self.y = self.camera.ground_y(self.x)

            index = int(self.state_t * self.FPS_DIE)

            if index >= len(self.DIE_FRAMES):
                self.frame = len(self.DIE_FRAMES) - 1
                self.dead = True
                return
            else:
                self.frame = index

            if self.camera and hasattr(self.camera, 'ground_y'):
                self.y = self.camera.ground_y(self.x)

    def draw(self):
        if self.dead:
            return

        sx, sy = self.screen_xy()
        flip = '' if self.dir == -1 else 'h'

        if self.state == 'run':
            frames = self.RUN_FRAMES
            foot_adj = self.foot_adj_run
        elif self.state == 'hit':
            frames = self.HIT_FRAMES
            foot_adj = self.foot_adj_run
        elif self.state == 'die':
            frames = self.DIE_FRAMES
            foot_adj = self.foot_adj_die
        else:
            frames = self.RUN_FRAMES
            foot_adj = self.foot_adj_run

        i = min(self.frame, len(frames) - 1)
        left, bottom, width, height = frames[i]

        DW, DH = int(width * self.scale), int(height * self.scale)
        y = sy - (DW - width) // 2 - foot_adj
        y = sy - (DH - height) // 2 - foot_adj

        self.image.clip_composite_draw(left, bottom, width, height,
                                       0, flip, sx, y, DW, DH)

    def get_bb(self):
        if self.state == 'die' or self.dead:
            return (0, 0, 0, 0)

        i = self.frame % len(self.RUN_FRAMES)
        _, _, w, h = self.RUN_FRAMES[i]
        S = self.scale
        pad = 5

        hw = int(w * S) // 2 - pad
        hh = int(h * S) // 2 - pad
        cx, cy = self.x, self.y - self.bb_offset_y
        return (cx - hw, cy - hh, cx + hw, cy + hh)


class Axe:
    SCALE = 1.3

    RUN_FRAMES = [
        (3,  210, 62, 80),
        (73, 210, 66, 80),
        (152, 210, 65, 80),
        (229, 210, 74, 80),
    ]
    FPS_RUN = 6.0

    HIT_FRAMES = [
        (5, 105, 59, 100),
    ]
    FPS_HIT = 10.0
    HIT_DURATION = 0.25

    DIE_FRAMES = [
        (4,   10, 61, 92),
        (82,  10, 58, 91),
        (156, 10, 61, 84),
        (232, 10, 61, 67),
    ]
    FPS_DIE = 10.0

    FRAME_SCALE = 1.0
    FOOT_ADJ_RUN = 26
    FOOT_ADJ_HIT = 20
    FOOT_ADJ_DIE = 26
    FRAME_BB_OFFSET_Y = 30

    def __init__(self, x, y, field=None):
        self.x, self.y = x, y
        self.dir = random.choice([-1, 1])

        self.frame = 0
        self.acc = 0.0
        self.state_t = 0.0

        self.scale = self.SCALE
        self.foot_adj_run = self.FOOT_ADJ_RUN
        self.foot_adj_die = self.FOOT_ADJ_DIE
        self.foot_adj_hit = self.FOOT_ADJ_HIT
        self.bb_offset_y = self.FRAME_BB_OFFSET_Y

        self.image = load_image(SHEET_PATH_AXE)

        self.camera = None
        if field:
            self.set_camera(field)

        self.world_min_x = 0
        self.world_max_x = 5000

        # 체력/상태 (버섯보다 쎄게)
        self.state = 'run'
        self.hp = 30
        self.max_hp = 3
        self.dead = False

        self.hit_dir = 0
        self.hit_back_speed = 220.0
        self.hit_cool = 0.0
        self.contact_damage = 4

    def set_camera(self, cam):
        self.camera = cam
        if hasattr(cam, 'bg_w'):
            self.world_max_x = int(cam.bg_w)

    def set_world_bounds(self, x0, x1):
        self.world_min_x = x0
        self.world_max_x = x1

    def screen_xy(self):
        if self.camera:
            return self.camera.world_to_screen(self.x, self.y)
        return self.x, self.y

    def take_hit(self, damage=1, from_dir=1):
        if self.dead or self.state == 'die':
            return

        dmg = max(1, int(damage))
        self.hp -= dmg
        self.hit_dir = -from_dir

        print(f"[AXE] hit! dmg={dmg}, hp -> {self.hp}")

        if self.hp <= 0:
            self.state = 'die'
            self.state_t = 0.0
            self.frame = 0
            self.dead = False
        else:
            self.state = 'hit'
            self.state_t = 0.0
            self.frame = 0

    def update(self):
        dt = game_framework.frame_time
        if self.dead:
            return

        if self.hit_cool > 0:
            self.hit_cool -= dt
            if self.hit_cool < 0:
                self.hit_cool = 0

        self.state_t += dt

        # run
        if self.state == 'run':
            self.x += self.dir * RUN_SPEED_PPS * 0.8 * dt  # 버섯보다 약간 느리게

            if self.x < self.world_min_x:
                self.x = self.world_min_x
                self.dir = 1
            elif self.x > self.world_max_x:
                self.x = self.world_max_x
                self.dir = -1

            if self.camera and hasattr(self.camera, 'ground_y'):
                self.y = self.camera.ground_y(self.x)

            self.acc += dt
            step = 1.0 / self.FPS_RUN
            while self.acc >= step:
                self.acc -= step
                self.frame = (self.frame + 1) % len(self.RUN_FRAMES)

        # hit
        elif self.state == 'hit':
            self.x += self.hit_dir * self.hit_back_speed * dt

            if self.camera and hasattr(self.camera, 'ground_y'):
                self.y = self.camera.ground_y(self.x)

            self.acc += dt
            step = 1.0 / self.FPS_HIT
            while self.acc >= step:
                self.acc -= step
                if len(self.HIT_FRAMES) > 1:
                    self.frame = (self.frame + 1) % len(self.HIT_FRAMES)
                else:
                    self.frame = 0

            if self.state_t >= self.HIT_DURATION:
                self.state = 'run'
                self.state_t = 0.0
                self.frame = 0

        # die
        elif self.state == 'die':
            if self.camera and hasattr(self.camera, 'ground_y'):
                self.y = self.camera.ground_y(self.x)

            index = int(self.state_t * self.FPS_DIE)

            if index >= len(self.DIE_FRAMES):
                self.frame = len(self.DIE_FRAMES) - 1
                self.dead = True
                return
            else:
                self.frame = index

            if self.camera and hasattr(self.camera, 'ground_y'):
                self.y = self.camera.ground_y(self.x)

    def draw(self):
        if self.dead:
            return


        sx, sy = self.screen_xy()
        flip = '' if self.dir == -1 else 'h'

        if self.state == 'run':
            frames = self.RUN_FRAMES
            foot_adj = self.foot_adj_run
        elif self.state == 'hit':
            frames = self.HIT_FRAMES
            foot_adj = self.foot_adj_hit
        elif self.state == 'die':
            frames = self.DIE_FRAMES
            foot_adj = self.foot_adj_die
        else:
            frames = self.RUN_FRAMES
            foot_adj = self.foot_adj_run

        i = min(self.frame, len(frames) - 1)
        left, bottom, width, height = frames[i]

        DW, DH = int(width * self.scale), int(height * self.scale)
        y = sy - (DH - height) // 2 - foot_adj

        self.image.clip_composite_draw(left, bottom, width, height,
                                       0, flip, sx, y, DW, DH)

    def get_bb(self):
        if self.state == 'die' or self.dead:
            return (0, 0, 0, 0)

        w, h = 80, 100
        S = self.SCALE

        bb_scale_w = 0.7
        bb_scale_h = 0.8

        half_w = int(w * S * bb_scale_w) // 2
        half_h = int(h * S * bb_scale_h) // 2

        cx = self.x
        cy = self.y - self.bb_offset_y  # ← 이거 중요

        return (cx - half_w, cy - half_h,
                cx + half_w, cy + half_h)