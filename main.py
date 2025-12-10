from pico2d import*
import game_framework
import logo_mode
import play_mode as start_mode
import sound

open_canvas (1000,550)
sound.init()

game_framework.run(start_mode)
close_canvas()