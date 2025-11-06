import random
from pico2d import *

import game_framework
import game_world

from boy import Boy
from game_world import add_collision_pair
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
    game_world.add_collision_pair('field:ball', field,None)

    boy = Boy()
    game_world.add_object(boy, 1)

   

def update():
    game_world.update()
        #모든 객체가 업데이트가 끝나서 그에 따른 충돌 검사 필요
    game_world.handle_collision()


def draw():
    clear_canvas()
    game_world.render()
    update_canvas()


def finish():
    game_world.clear()

def pause(): pass
def resume(): pass

