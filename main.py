from pico2d import*
import game_framework
import logo_mode
import play_mode as start_mode

open_canvas (1000,550)
logo_mode.init()
while logo_mode.running:
    logo_mode.handle_events()
    logo_mode.update()
    logo_mode.draw()
    delay(0.01)
logo_mode.finish()

game_framework.run(start_mode)
close_canvas()