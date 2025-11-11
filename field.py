from pico2d import load_image, draw_line

class Field:
    VIEW_W = 1000
    VIEW_H = 550

    def __init__(self, image_path='사진수집/background/헤네시스.png', lerp=0.1,
            start_x = None, start_y = None, draw_offset_x = 0, draw_offset_y = 0):
        try:
            self.image = load_image(image_path)
            self.bg_w, self.bg_h = int(self.image.w), int(self.image.h)
        except Exception:
            self.image = None
            self.bg_w, self.bg_h = 5000, 1000

        self.target = None
        self.lerp = float(lerp)


        half_w = self.VIEW_W / 2
        half_h = self.VIEW_H / 2
        max_cx = max(self.bg_w - half_w, half_w)
        max_cy = max(self.bg_h - half_h, half_h)

        init_x = self.bg_w / 2 if start_x is None else start_x
        init_y = self.bg_h / 2 if start_y is None else start_y
        self.cam_x = max(half_w, min(init_x, max_cx))
        self.cam_y = max(half_h, min(init_y, max_cy))

        self.draw_offset_x = int(draw_offset_x)
        self.draw_offset_y = int(draw_offset_y)

    def draw(self):
        if not self.image:
            draw_line(0, 30, 800, 30)
            return


        left = int(self.cam_x - self.VIEW_W // 2)
        bottom = int(self.cam_y - self.VIEW_H // 2)

        left = max(0, min(left, self.bg_w - self.VIEW_W))
        bottom = max(0, min(bottom, self.bg_h - self.VIEW_H))

        dest_x = self.VIEW_W // 2 + self.draw_offset_x
        dest_y = self.VIEW_H // 2 + self.draw_offset_y

        # clip_draw(src_left, src_bottom, src_w, src_h, dest_center_x, dest_center_y)
        self.image.clip_draw(left, bottom, self.VIEW_W, self.VIEW_H, dest_x, dest_y)

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

        self.cam_x = desired_cx
        self.cam_y = desired_cy

    def world_to_screen(self, x, y):
        sx = x - (self.cam_x - self.VIEW_W // 2) + self.draw_offset_x
        sy = y - (self.cam_y - self.VIEW_H // 2) + self.draw_offset_y
        return int(sx), int(sy)