from pico2d import *
import game_framework

GRAVITY_PPS = 1500.0

ITEM_IMAGES = {
    '10원':   '사진수집/etc/동.png',
    '100원': '사진수집/etc/금.png',
    '1000원':    '사진수집/etc/지페.png',
    '5000원':    '사진수집/etc/다발.png',
    '주황버섯의 갓':   '사진수집/etc/주황버섯의 갓.png',
}


class DropItem:
    def __init__(self, x, y, field=None, kind='주황버섯의 갓'):
        self.x, self.y = x, y
        self.vy = 300.0          # 처음 위로 살짝 튀어오르게
        self.kind = kind
        self.scale = 1.0
        self.collected = False

        self.scale = 0.2

        path = ITEM_IMAGES.get(kind, ITEM_IMAGES['주황버섯의 갓'])
        self.image = load_image(path)

        base = max(self.image.w, self.image.h) * self.scale
        self.bb_r = int(base * 0.3)

        self.camera = None
        if field:
            self.set_camera(field)

        self.bb_r = 16

    def set_camera(self, cam):
        self.camera = cam

    def screen_xy(self):
        if self.camera:
            return self.camera.world_to_screen(self.x, self.y)
        return self.x, self.y

    def update(self):
        dt = game_framework.frame_time

        # 중력
        self.vy -= GRAVITY_PPS * dt
        self.y += self.vy * dt

        # 바닥에 닿으면 멈추기
        if self.camera and hasattr(self.camera, 'ground_y'):
            ground = self.camera.ground_y(self.x)
            if self.y < ground:
                self.y = ground
                self.vy = 0

    def draw(self):
        sx, sy = self.screen_xy()
        S = self.scale

        w = int(self.image.w * S)
        h = int(self.image.h * S)

        self.image.draw(sx, sy, w, h)

        print("DRAW ITEM", self.kind, "scale=", self.scale)

    def get_bb(self):
        r = self.bb_r
        return (self.x - r, self.y - r, self.x + r, self.y + r)
