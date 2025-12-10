# npc.py
from pico2d import *
import game_framework


class MingMing:

    IDLE_FRAMES = [
        (82, 1143, 202, 291),
        (345, 1143, 250, 291),
        (620, 1143, 250, 291),
        (905, 1143, 250, 291),
    ]
    FPS_IDLE = 4.0

    SCALE = 0.32    # 전체 크기 배율
    FOOT_ADJ = 190   # 발 위치 조정(캐릭터가 땅 위에 서 보이도록)

    def __init__(self, x, y, field=None):
        # 월드 좌표
        self.x, self.y = x, y

        # 시트 이미지
        self.image = load_image('사진수집/npc/밍밍.png')

        # 카메라
        self.camera = None
        if field:
            self.set_camera(field)

        # 애니메이션
        self.frame = 0
        self.acc = 0.0

    # --- 카메라 관련 ---
    def set_camera(self, cam):
        self.camera = cam

    def screen_xy(self):
        if self.camera:
            return self.camera.world_to_screen(self.x, self.y)
        return self.x, self.y

    # --- 애니메이션 업데이트 ---
    def update(self):
        dt = game_framework.frame_time
        self.acc += dt
        step = 1.0 / self.FPS_IDLE
        while self.acc >= step:
            self.acc -= step
            self.frame = (self.frame + 1) % len(self.IDLE_FRAMES)

    # --- 히트박스(대화 범위) ---
    def get_bb(self):
        w, h = 200, 250
        S = self.SCALE

        hw = int(w * S) // 2
        hh = int(h * S) // 2

        # y 쪽은 약간 아래로 내리기 (발 기준)
        cx = self.x
        cy = self.y -90

        return (cx - hw, cy - hh,
                cx + hw, cy + hh)

    # --- 그리기 ---
    def draw(self):
        sx, sy = self.screen_xy()

        i = self.frame % len(self.IDLE_FRAMES)
        left, bottom, w, h = self.IDLE_FRAMES[i]

        S = self.SCALE
        DW, DH = int(w * S), int(h * S)

        # 발 위치 맞추기
        foot_fix = (DH - h) // 2
        y = sy - foot_fix - self.FOOT_ADJ

        # NPC는 가만히 서 있으니 flip 없음
        self.image.clip_composite_draw(
            left, bottom, w, h,
            0, '',     # 회전 0, 반전 없음
            sx, y, DW, DH
        )

        # === 히트박스(빨간 네모) 표시 ===
        l, b, r, t = self.get_bb()
        if self.camera:
            l, b = self.camera.world_to_screen(l, b)
            r, t = self.camera.world_to_screen(r, t)
        draw_rectangle(l, b, r, t)

    # 플레이어와 근접했는지 (대화 가능 범위)
    def is_near(self, boy, radius=80):
        dx = boy.x - self.x
        dy = boy.y - self.y
        return (dx * dx + dy * dy) ** 0.5 <= radius
