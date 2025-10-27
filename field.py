from pico2d import load_image, draw_line

class Field:
    def __init__(self):
        try:
            self.image = load_image('사진수집/background/헤네필드/헤네필드2.png')
        except:
            self.image = None

    def draw(self):
        if self.image:
            self.image.draw(500, 290)
        else:
            draw_line(0, 30, 800, 30)

    def update(self):
        pass
