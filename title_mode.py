from pico2d import *
import game_framework

image = None

def init():
     global image
     image = load_image('사진수집/메인 화면.jpg')
def finish():
     global image
     del image
def handle_events():
     event_list = get_events()
     for event in event_list:
         if event.type == SDL_QUIT:
             game_framework.quit()
         elif event.type == SDL_KEYDOWN and event.key == SDLK_ESCAPE:
             game_framework.quit()
def draw():
     clear_canvas()
     image.draw(400,300)
def update(): pass
def pause(): pass
def resume(): pass