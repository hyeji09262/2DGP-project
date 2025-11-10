import random
from pico2d import *

import game_framework
import game_world

from boy import Boy
from field import Field

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
    global boy

    field = Field()
    game_world.add_object(field, 0)

    boy = Boy()
    game_world.add_object(boy, 1)

   

def update():
    game_world.update()


def draw():
    clear_canvas()
    game_world.render()
    update_canvas()


def finish():
    game_world.clear()
    pass

def pause(): pass
def resume(): pass

