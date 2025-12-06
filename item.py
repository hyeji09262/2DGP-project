from pico2d import *
import game_framework

GRAVITY_PPS = 1500.0

ITEM_IMAGES = {
    '10원':   '사진수집/etc/동.png',
    '100원': '사진수집/etc/금.png',
    '1000원':    '사진수집/etc/지폐.png',
    '5000원':    '사진수집/etc/다발.png',
    '주황버섯의 갓':   '사진수집/etc/주황버섯의 갓.png',
    # 실제 파일 이름에 맞게 고쳐줘
}


class DropItem:
    def __init__(self, x, y, field=None, kind='coin'):
        self.x, self.y = x, y
        self.vy = 300.0          # 처음 위로 살짝 튀어오르게
        self.kind = kind
        self.scale = 1.0
        self.collected = False

        # TODO: 여기서 실제 아이템 이미지로 바꾸기
        self.image = load_image('사진수집/etc/돈.png')

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
        self.image.draw(sx, sy)

    def get_bb(self):
        r = self.bb_r
        return (self.x - r, self.y - r, self.x + r, self.y + r)
