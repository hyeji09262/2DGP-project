# item.py
from pico2d import *
import game_framework

GRAVITY_PPS = 1500.0  # 중력 (필요하면 조절)

# 드랍템 종류별 이미지 경로
ITEM_IMAGES = {
    '10원':        '사진수집/etc/동.png',
    '100원':       '사진수집/etc/금.png',
    '1000원':      '사진수집/etc/지페.png',
    '5000원':      '사진수집/etc/다발.png',
    '주황버섯의 갓': '사진수집/etc/주황버섯의 갓.png',
    '빨간포션' :    '사진수집/etc/빨간물약.png',
    '파란포션' :    '사진수집/etc/파란물약.png',
    '장작' :       '사진수집/etc/장작.png',
}


class DropItem:
    def __init__(self, x, y, field=None, kind='주황버섯의 갓'):
        # 월드 좌표
        self.x, self.y = x, y
        self.vy = 300.0              # 위로 살짝 튀어 오르는 속도
        self.kind = kind
        self.collected = False

        default_scale = 0.2

        if kind == '주황버섯의 갓':
            self.scale = 0.13  # 갓은 조금 더 크게
        elif kind == '빨간포션':
            self.scale = 0.3
        elif kind == '파란포션':
            self.scale = 0.3
        else:
            self.scale = default_scale

        self.ground_offset = -60

        self.flip_h = (kind == '파란포션')

        # 이미지 로드
        path = ITEM_IMAGES.get(kind, ITEM_IMAGES['주황버섯의 갓'])
        self.image = load_image(path)

        print('[DropItem] TRY LOAD:', kind, '=>', path)

        # 히트박스 반지름 (이미지+스케일 기준)
        base = max(self.image.w, self.image.h) * self.scale
        self.bb_r = int(base * 0.3)

        # 카메라
        self.camera = None
        if field:
            self.set_camera(field)

    def set_camera(self, cam):
        self.camera = cam

    def screen_xy(self):
        if self.camera:
            return self.camera.world_to_screen(self.x, self.y)
        return self.x, self.y

    def update(self):
        dt = game_framework.frame_time

        # 중력 적용
        self.vy -= GRAVITY_PPS * dt
        self.y += self.vy * dt

        # 바닥에 닿으면 멈추기
        if self.camera and hasattr(self.camera, 'ground_y'):
            ground = self.camera.ground_y(self.x)
            floor_y = ground + self.ground_offset

            if self.y < floor_y:
                self.y = floor_y
                self.vy = 0

    def draw(self):
        sx, sy = self.screen_xy()
        S = self.scale

        w = int(self.image.w * S)
        h = int(self.image.h * S)

        if self.flip_h:
            self.image.clip_composite_draw(
                0, 0, self.image.w, self.image.h,
                0, 'h',
                sx, sy, w, h
            )
        else:
            # 나머지 아이템은 그대로
            self.image.draw(sx, sy, w, h)

    def get_bb(self):
        r = self.bb_r
        return (self.x - r, self.y - r, self.x + r, self.y + r)
