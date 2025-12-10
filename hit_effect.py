from pico2d import *
import game_framework

class HitEffect:
    def __init__(self, x, y, field=None):
        self.x, self.y = x, y          # 월드 좌표(몬스터 위치 기준)
        self.image = load_image('사진수집/etc/hiteffect.png')
        self.camera = field            # Field (카메라 변환용)
        self.life = 0.15               # 0.15초 정도만 보이게
        self.scale = 1.0
        self.dead = False              # 다 쓰면 True 로 바꿔서 제거

    def set_camera(self, cam):
        self.camera = cam

    def update(self):
        dt = game_framework.frame_time
        self.life -= dt
        if self.life <= 0:
            self.dead = True

    def draw(self):
        # 카메라 기준 화면 좌표로 변환
        if self.camera:
            sx, sy = self.camera.world_to_screen(self.x, self.y)
        else:
            sx, sy = self.x, self.y

        w = int(self.image.w * self.scale)
        h = int(self.image.h * self.scale)
        self.image.draw(sx, sy, w, h)
