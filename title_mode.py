from pico2d import *
import game_framework
import play_mode

image = None
font = None

def init(): # 타이틀 이미지를 로드
    global image, logo_start_time, font

    image = load_image('사진수집/메인 화면.jpg')
    font = load_font('ENCR10B.TTF', 30)

def update(): #시간 체크
    pass

def draw():#로고 이미지를 그림
    clear_canvas()
    image.draw(500,275)
    font.draw(300, 130, '< Press SPACE to Start >', (255, 255, 255))

    update_canvas()

def finish():
    global image, font
    del image
    del font

def handle_events():
    event_list = get_events() #현재까지 들어온 이벤트들을 받아온다
    # 그리고 아무처리도 하지 않는다
    for event in event_list:
        if event.type == SDL_QUIT:
            game_framework.quit()
        elif event.type == SDL_KEYDOWN and event.key == SDLK_ESCAPE:
            game_framework.quit()
        elif event.type == SDL_KEYDOWN and event.key == SDLK_SPACE:
            game_framework.change_mode(play_mode)

def pause():
    pass
def resume():
    pass