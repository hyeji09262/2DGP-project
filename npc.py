# npc.py
from pico2d import *
import game_framework

class MingMing:
    # ==== 퀘스트 상태 상수 ====
    QUEST_NONE        = 0
    QUEST_AVAILABLE   = 1   # 수락 가능 (전구)
    QUEST_IN_PROGRESS = 2   # 진행중 (…) → 상호작용 막기
    QUEST_READY       = 3   # 완료 가능 (느낌표)
    QUEST_DONE        = 4   # 보상까지 다 받은 뒤

    # (left, bottom, w, h)
    IDLE_FRAMES = [
        (76,  1140, 202, 291),
        (356, 1140, 202, 291),
        (632, 1140, 202, 291),
        (917, 1140, 202, 291),
    ]
    FPS_IDLE = 4.0

    SCALE = 0.35
    FOOT_ADJ = 125
    TALK_RADIUS = 80

    def __init__(self, x, y, field=None):
        self.x, self.y = x, y
        self.image = load_image('사진수집/npc/밍밍.png')

        self.camera = None
        if field:
            self.set_camera(field)

        self.frame = 0
        self.acc = 0.0

        # 처음에는 퀘스트 “수락 가능”
        self.quest_state = self.QUEST_AVAILABLE

    # --- 카메라 세팅 ---
    def set_camera(self, cam):
        self.camera = cam

    # --- 월드좌표 → 화면좌표 ---
    def screen_xy(self):
        if self.camera:
            return self.camera.world_to_screen(self.x, self.y)
        return self.x, self.y

    # --- idle 애니메이션 프레임 진행 ---
    def update(self):
        dt = game_framework.frame_time
        self.acc += dt
        step = 1.0 / self.FPS_IDLE
        while self.acc >= step:
            self.acc -= step
            self.frame = (self.frame + 1) % len(self.IDLE_FRAMES)

    # --- 그리기 ---
    def draw(self):
        sx, sy = self.screen_xy()

        # 현재 프레임 선택
        i = self.frame % len(self.IDLE_FRAMES)
        left, bottom, w, h = self.IDLE_FRAMES[i]

        S = self.SCALE
        DW, DH = int(w * S), int(h * S)

        # 발 위치 맞추기:
        #   원본의 중심보다 커질수록 위로 늘어나니까 그만큼 내려줌
        foot_fix = (DH - h) // 2
        draw_y = sy - foot_fix - self.FOOT_ADJ

        # idle 애니메이션 프레임만 잘라서 그림
        self.image.clip_composite_draw(
            left, bottom, w, h,
            0, '',            # 회전 0, 반전 없음
            sx, draw_y, DW, DH
        )

        # === 디버그용 빨간 대화 박스 ===
        r = self.TALK_RADIUS
        box_bottom = sy -50
        box_top    = sy + 50  # 필요하면 높이 조절
        # draw_rectangle(sx - r, box_bottom, sx + r, box_top)

    # --- 플레이어와 근접 여부 ---
    def is_near(self, boy, radius=80):
        dx = boy.x - self.x
        dy = boy.y - self.y
        return (dx*dx + dy*dy) ** 0.5 <= radius

    # --- 지금 말 걸 수 있는 상태인지 ---
    def can_talk(self, boy):
        # 진행중이면 대화 막기
        if self.quest_state == self.QUEST_IN_PROGRESS:
            return False
        return self.is_near(boy)
