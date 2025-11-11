from pico2d import load_image, draw_line

class Field:
    VIEW_W = 1000
    VIEW_H = 550

    def __init__(self, image_path='사진수집/background/헤네시스.png', lerp=0.15):
        try:
            self.image = load_image(image_path)
            self.bg_w, self.bg_h = int(self.image.w), int(self.image.h)
        except Exception:
            self.image = None
            self.bg_w, self.bg_h = 5000, 1000

        self.target = None
        self.cam_x = self.bg_w / 2
        self.cam_y = self.bg_h / 2
        self.lerp = float(lerp)

    def draw(self):
        if not self.image:
            draw_line(0, 30, 800, 30)
            return


        left = int(self.cam_x - self.VIEW_W // 2)
        bottom = int(self.cam_y - self.VIEW_H // 2)

        left = max(0, min(left, self.bg_w - self.VIEW_W))
        bottom = max(0, min(bottom, self.bg_h - self.VIEW_H))


        # clip_draw(src_left, src_bottom, src_w, src_h, dest_center_x, dest_center_y)
        self.image.clip_draw(left, bottom, self.VIEW_W, self.VIEW_H,
                             self.VIEW_W // 2, self.VIEW_H // 2)

    def update(self):
        if not self.target:
            return

        tx = getattr(self.target, 'x', self.bg_w / 2)
        ty = getattr(self.target, 'y', self.bg_h / 2)

        half_w = self.VIEW_W / 2
        half_h = self.VIEW_H / 2
        min_cx = half_w
        max_cx = max(self.bg_w - half_w, half_w)
        min_cy = half_h
        max_cy = max(self.bg_h - half_h, half_h)

        desired_cx = max(min_cx, min(tx, max_cx))
        desired_cy = max(min_cy, min(ty, max_cy))


        self.cam_x += (desired_cx - self.cam_x) * self.lerp
        self.cam_y += (desired_cy - self.cam_y) * self.lerp

