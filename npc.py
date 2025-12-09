from pico2d import load_image, draw_rectangle
import math

NPC_IMG_PATH = '사진수집/npc/밍밍.png'

class NPC:
    def __init__(self, x, y, field=None):
        self.x, self.y = x, y
        self.image = load_image(NPC_IMG_PATH)
        self.field = field

        self.scale = 1.0     # NPC 크기 조절
        self.talk_range = 80 # 이 거리 안에서만 대화 가능

    def set_camera(self, cam):
        self.field = cam

    def screen_xy(self):
        if self.field:
            return self.field.world_to_screen(self.x, self.y)
        return self.x, self.y

    def update(self):
        # 나중에 idle 애니 만들고 싶으면 여기에서 프레임 돌리면 됨
        pass

    def draw(self):
        sx, sy = self.screen_xy()
        w = int(self.image.w * self.scale)
        h = int(self.image.h * self.scale)
        self.image.draw(sx, sy, w, h)

        # 디버그용 히트박스/범위 보고 싶으면 주석 풀기
        # l, b, r, t = self.get_bb()
        # if self.field:
        #     l, b = self.field.world_to_screen(l, b)
        #     r, t = self.field.world_to_screen(r, t)
        # draw_rectangle(l, b, r, t)

    def get_bb(self):
        w = int(self.image.w * self.scale)
        h = int(self.image.h * self.scale)
        hw, hh = w // 2, h // 2
        return (self.x - hw, self.y - hh,
                self.x + hw, self.y + hh)

    def is_near(self, boy):
        bx0, by0, bx1, by1 = boy.get_bb()
        bc_x = (bx0 + bx1) / 2
        bc_y = (by0 + by1) / 2

        dx = bc_x - self.x
        dy = bc_y - self.y
        dist2 = dx * dx + dy * dy
        return dist2 <= (self.talk_range ** 2)
