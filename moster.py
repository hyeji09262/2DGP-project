from pico2d import*
import random
import game_framework


PIXEL_PER_METER = (10.0 / 0.3) # 10 pixel 30 cm
RUN_SPEED_KMPH = 25.0 # Km / Hour
RUN_SPEED_MPM = (RUN_SPEED_KMPH * 1000.0 / 60.0)
RUN_SPEED_MPS = (RUN_SPEED_MPM / 60.0)
RUN_SPEED_PPS = (RUN_SPEED_MPS * PIXEL_PER_METER)


SHEET_PATH = '사진수집/monster/주황버섯.png'
W, H    = 64, 64      # 프레임 크기
PITCH   = 64          # 다음 프레임까지 이동량(여백 없으면 W와 동일)
START_X = 0           # 첫 프레임 left
START_Y = 0           # 프레임 줄 bottom
FRAMES  = 4           # 달리기 프레임 수
FPS     = 8.0         # 애니 속도(프레임/초)

class Mushroom:
    def __init__(self, x, y, field=None):
        self.x, self.y = x, y
        self.dir = random.choice([-1, 1])   # -1: 왼쪽, 1: 오른쪽
        self.frame = 0
        self.acc = 0.0
        self.scale = 0.9
        self.foot_adj = 0

        self.image = load_image(SHEET_PATH)
        self.camera = None
        if field: self.set_camera(field)

        # 월드 경계 (기본값 — playmode에서 맵 폭으로 덮어써줄 것)
        self.world_min_x = 0
        self.world_max_x = 5000

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

    def update(self):
        # 이동
        self.x += self.dir * RUN_SPEED_PPS * game_framework.frame_time

        # 경계 반전
        if self.x < self.world_min_x:
            self.x = self.world_min_x; self.dir = 1
        elif self.x > self.world_max_x:
            self.x = self.world_max_x; self.dir = -1

        # 지면에 붙이기
        if self.camera and hasattr(self.camera, 'ground_y'):
            self.y = self.camera.ground_y(self.x)

        # 애니메이션
        self.acc += game_framework.frame_time
        step = 1.0 / FPS
        while self.acc >= step:
            self.acc -= step
            self.frame = (self.frame + 1) % FRAMES

    def draw(self):
        sx, sy = self.screen_xy()

        DW, DH = int(W * self.scale), int(H * self.scale)
        y = sy - (DH - H)//2 - self.foot_adj

        left = START_X + (self.frame % FRAMES) * PITCH
        bottom = START_Y

        # 기본 시트가 '왼쪽'을 보게 그려져 있다고 가정
        flip = '' if self.dir == -1 else 'h'
        self.image.clip_composite_draw(left, bottom, W, H, 0, flip, sx, y, DW, DH)

    # 충돌 박스(원하면 숫자만 다듬어도 됨)
    def get_bb(self):
        hw = int(W * self.scale) // 2 - 6
        hh = int(H * self.scale) // 2 - 6
        return (self.x - hw, self.y - hh, self.x + hw, self.y + hh)