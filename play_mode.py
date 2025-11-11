import random
from pico2d import *

import game_framework
import game_world

from boy import Boy
from field import Field

field = None
boy = None

def handle_events():
    event_list = get_events()
    for event in event_list:
        if event.type == SDL_QUIT:
            game_framework.quit()
        elif event.type == SDL_KEYDOWN and event.key == SDLK_ESCAPE:
            game_framework.quit()
        else:
            boy.handle_event(event)

def init():
    global boy, field

    field = Field('사진수집/background/헤네시스.png', lerp=1.0)
    field.VIEW_W, field.VIEW_H = get_canvas_width(), get_canvas_height()
    game_world.add_object(field, 0)

    boy = Boy()
    boy.set_camera(field)
    game_world.add_object(boy, 1)


    field.target = boy

   

def update():
    game_world.update()
    field.update()


def draw():
    clear_canvas()
    game_world.render()
    update_canvas()


def finish():
    game_world.clear()

def pause(): pass
def resume(): pass

