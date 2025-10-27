from pico2d import load_image


class field:
    def __init__(self):
        self.image = load_image('사진수집','background','헤네필드','헤네필드2.png')

    def draw(self):
        self.image.draw(400, 30)

    def update(self):
        pass