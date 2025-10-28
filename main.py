from pico2d import *
from boy import Boy
from field import Field


# Game object class here


def handle_events():
    global running

    event_list = get_events()
    for event in event_list:
        if event.type == SDL_QUIT:
            running = False
        elif event.type == SDL_KEYDOWN and event.key == SDLK_ESCAPE:
            running = False
        else:
            boy.handle_event(event)


def reset_world():
    global world
    global boy

    world = []

    field = Field()
    world.append(field)

    boy = Boy()
    world.append(boy)



def update_world():
    for o in world:
        o.update()
    pass


def render_world():
    clear_canvas()
    for o in world:
        o.draw()
    update_canvas()


running = True



open_canvas(1000,580)
reset_world()
# game loop
while running:
    handle_events()
    update_world()
    render_world()
    delay(1)
# finalization code
close_canvas()
