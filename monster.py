from pico2d import*
import random
import game_framework


PIXEL_PER_METER = (10.0 / 0.3) # 10 pixel 30 cm
RUN_SPEED_KMPH = 20.0 # Km / Hour
RUN_SPEED_MPM = (RUN_SPEED_KMPH * 1000.0 / 60.0)
RUN_SPEED_MPS = (RUN_SPEED_MPM / 60.0)
RUN_SPEED_PPS = (RUN_SPEED_MPS * PIXEL_PER_METER)

SHEET_PATH = '사진수집/monster/주황버섯.png'


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
        (380, 25, 120, 100),
        (480, 25, 120, 100),
    ]
    FPS_DIE = 8.0

    FRAME_SCALE = 0.8
    FRAME_FOOT_ADJ = 45
    FRAME_BB_OFFSET_Y = 30

    def __init__(self, x, y, field=None):
        self.x, self.y = x, y
        self.dir = random.choice([-1, 1])   # -1: 왼쪽, 1: 오른쪽

        self.frame = 0
        self.acc = 0.0
        self.state_t = 0.0

        self.scale = self.FRAME_SCALE
        self.foot_adj = self.FRAME_FOOT_ADJ
        self.bb_offset_y = self.FRAME_BB_OFFSET_Y

        self.image = load_image(SHEET_PATH)
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
        if self.dead or self.state == 'die':
            return

        print("MUSHROOM HIT! hp before =", self.hp)  # 디버그용

        self.hp -= damage
        self.hit_dir = -from_dir   # 공격자 반대 방향으로 넉백

        if self.hp <= 0:
            print("MUSHROOM DIE START")
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

        # ----------------- run 상태 -----------------
        if self.state == 'run':
            # 걷기 이동
            self.x += self.dir * RUN_SPEED_PPS * dt

            if self.x < self.world_min_x:
                self.x = self.world_min_x
                self.dir = 1
            elif self.x > self.world_max_x:
                self.x = self.world_max_x
                self.dir = -1

            # 지면에 붙이기
            if self.camera and hasattr(self.camera, 'ground_y'):
                self.y = self.camera.ground_y(self.x)

            # 걷기 애니메이션
            self.acc += dt
            step = 1.0 / self.FPS_RUN
            while self.acc >= step:
                self.acc -= step
                self.frame = (self.frame + 1) % len(self.RUN_FRAMES)

        # ----------------- hit 상태 -----------------
        elif self.state == 'hit':
            # 넉백
            self.x += self.hit_dir * self.hit_back_speed * dt

            # 지면
            if self.camera and hasattr(self.camera, 'ground_y'):
                self.y = self.camera.ground_y(self.x)

            # 피격 애니
            self.acc += dt
            step = 1.0 / self.FPS_HIT
            while self.acc >= step:
                self.acc -= step
                if len(self.HIT_FRAMES) > 1:
                    self.frame = (self.frame + 1) % len(self.HIT_FRAMES)
                else:
                    self.frame = 0

            # 피격 유지 시간 지나면 다시 run
            if self.state_t >= 0.25:
                self.state = 'run'
                self.state_t = 0.0
                self.frame = 0

        # ----------------- die 상태 -----------------
        elif self.state == 'die':
                # 지면 고정(원하면)
            if self.camera and hasattr(self.camera, 'ground_y'):
                self.y = self.camera.ground_y(self.x)

                # 경과 시간 기반으로 프레임 계산
                # FPS_DIE 속도로 0,1,2,... 증가
            index = int(self.state_t * self.FPS_DIE)

            if index >= len(self.DIE_FRAMES):
                    # 마지막 프레임에서 멈추고 dead 처리
                self.frame = len(self.DIE_FRAMES) - 1
                self.dead = True
                return
            else:
                self.frame = index

                # 지면 고정
            if self.camera and hasattr(self.camera, 'ground_y'):
                self.y = self.camera.ground_y(self.x)

    def draw(self):
        if self.dead:
            return

        sx, sy = self.screen_xy()
        flip = '' if self.dir == -1 else 'h'

        if self.state == 'run':
            i = self.frame % len(self.RUN_FRAMES)
            left, bottom, width, height = self.RUN_FRAMES[i]
        elif self.state == 'hit':
            i = min(self.frame, len(self.HIT_FRAMES) - 1)
            left, bottom, width, height = self.HIT_FRAMES[i]
        elif self.state == 'die':
            i = min(self.frame, len(self.DIE_FRAMES) - 1)
            left, bottom, width, height = self.DIE_FRAMES[i]

        DW, DH = int(width * self.scale), int(height * self.scale)
        y = sy - (DH - height) // 2 - self.foot_adj

        self.image.clip_composite_draw(left, bottom, width, height,
                                       0, flip, sx, y, DW, DH)

    def get_bb(self):
        # 죽는 중이거나 죽었으면 히트박스 제거
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
