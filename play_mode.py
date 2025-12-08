import random
from pico2d import *

import game_framework
import game_world

from boy import Boy
from field import Field
from monster import Mushroom
from item import DropItem

field = None
boy = None
current_map = None
_transition_cooldown = 0.0
monsters = []
items = []
DRAW_HITBOX = True
_collision_grace = 0.0
COLLIDE_IGNORE_PROB = 0.8

# ==== ESC 메뉴 상태 ====
menu_open = False          # 메뉴가 열려 있는지
menu_img = None
MENU_SCALE = 0.5
# 메뉴 PNG 이미지

# 메뉴 버튼 영역(마우스 클릭용)
menu_rect_main = None
menu_rect_close = None
menu_rect_char = None      # U : 캐릭터 정보
menu_rect_inven = None     # I : 인벤토리
menu_rect_hotkey = None    # O : 단축키 정보
menu_rect_weapon = None    # P : 무기 강화
menu_rect_exit = None      # 종료 버튼

# 각 서브창(다음 화면) 열림 여부
ui_char_open = False       # U
ui_inven_open = False      # I
ui_hotkey_open = False     # O
ui_weapon_open = False     # P

char_panel_img = None
CHAR_PANEL_SCALE = 0.5

DROP_TABLE = [
    ('10원',   0.3),
    ('100원', 0.2),
    ('1000원',    0.15),
    ('5000원',    0.05),
    ('주황버섯의 갓',   0.3),
]

MAPS = {
    "henesys": {
        "image": "사진수집/background/헤네시스.png",
        "width": 5000,
         "ground": [
            (0, 400),
            (470, 400),
            (550, 340),
            (2550, 340),
            (2630, 280),
            (2700, 280),
            (2780, 220),
            (5000, 220)
        ],
        "spawn": {
            "default":   (250, 400),
            "from_left": (70, 400),
            "from_right":(4850, 220),
        },
        # 맨 왼쪽 세로 전체를 포털로 설정 → map2의 오른쪽에서 들어오게
        "portals": [
            {"rect": (50, 300, 100, 400), "to": "map2", "entry": "from_right", "require_up": True}
        ],
        "spawn_monsters": False
    },
    "map2": {
        "image": "사진수집/background/헤네필드/헤네필드2.png",
        "width": 1000,
        "ground": [
            (0, 167),
            (240, 167),
            (350, 227),
            (725, 227),
            (825, 167),
            (1000, 167)
        ],
        "spawn": {
            "default":   (275, 40),
            "from_left": (120, 40),
            "from_right":(970, 450),
        },
        # 맨 오른쪽 포털 → henesys의 왼쪽으로 들어감
        "portals": [
            {"rect": (950, 100, 1000, 200), "to": "henesys", "entry": "from_left",  "require_up": True}
        ],
        "spawn_monsters": True
    },
}

def _fmt_num(n, max_digits=6):
    try:
        v = int(n)
    except:
        return str(n)
    s = str(v)
    if len(s) > max_digits:
        # 예: 1234567 -> 12345+
        return s[:max_digits - 1] + '+'
    return s

def _init_menu_layout():
    global menu_rect_main, menu_rect_close
    global menu_rect_char, menu_rect_inven, menu_rect_hotkey, menu_rect_weapon, menu_rect_exit

    if menu_img is None:
        return

    cw, ch = get_canvas_width(), get_canvas_height()

    # 실제 화면에 그릴 크기(축소 적용)
    w = int(menu_img.w * MENU_SCALE)
    h = int(menu_img.h * MENU_SCALE)

    # 메뉴 전체를 화면 중앙에 배치
    cx = cw // 2
    cy = ch // 2
    x0 = cx - w // 2
    y0 = cy - h // 2
    x1 = x0 + w
    y1 = y0 + h
    menu_rect_main = (x0, y0, x1, y1)

    close_w = int(w * 0.09)  # 대략적인 비율
    close_h = close_w
    cx1 = x1 - int(w * 0.06)
    cy1 = y1 - int(h * 0.06)
    cx0 = cx1 - close_w
    cy0 = cy1 - close_h
    menu_rect_close = (cx0, cy0, cx1, cy1)

    # 네 개 큰 버튼(캐릭터/U, 인벤/I, 단축키/O, 무기강화/P)
    btn_w = int(w * 0.36)
    btn_h = int(h * 0.22)

    # 좌우 열 중심
    left_cx = x0 + int(w * 0.30)
    right_cx = x0 + int(w * 0.70)

    top_cy = y0 + int(h * 0.63)
    bottom_cy = y0 + int(h * 0.35)

    def make_rect(cx, cy):
        hw = btn_w // 2
        hh = btn_h // 2
        return (cx - hw, cy - hh, cx + hw, cy + hh)

    menu_rect_char = make_rect(left_cx, top_cy)  # U : 캐릭터 정보
    menu_rect_inven = make_rect(right_cx, top_cy)  # I : 인벤토리
    menu_rect_hotkey = make_rect(left_cx, bottom_cy)  # O : 단축키 정보
    menu_rect_weapon = make_rect(right_cx, bottom_cy)  # P : 무기 강화

    # 게임 종료 버튼 (오른쪽 아래)
    exit_w = int(w * 0.22)
    exit_h = int(h * 0.15)
    ex1 = x1 - int(w * 0.06)
    ey0 = y0 + int(h * 0.08)
    ex0 = ex1 - exit_w
    ey1 = ey0 + exit_h
    menu_rect_exit = (ex0, ey0, ex1, ey1)


def init():
    global field, boy, current_map, _transition_cooldown, monsters, items
    global menu_open, menu_img
    global char_panel_img

    load_map("henesys", "default")

    menu_open = False

    menu_img = load_image('사진수집/etc/메뉴창.png')
    char_panel_img = load_image('사진수집/etc/캐릭터정보.png')

    print("[INIT] char_panel_img =", char_panel_img)
    print("[INIT] char_panel_img size =", char_panel_img.w, char_panel_img.h)

    _init_menu_layout()

def _handle_menu_event(event):
    global menu_open, ui_inven_open, ui_weapon_open

    if event.type == SDL_KEYDOWN and event.key == SDLK_ESCAPE:
        menu_open = False
        return

    if event.type == SDL_KEYDOWN:
        if event.key == SDLK_u:
            menu_open = False
            ui_char_open = True
            ui_inven_open = ui_hotkey_open = ui_weapon_open = False
            print("[MENU] 캐릭터 정보 (U)")
            return
        elif event.key == SDLK_i:
            menu_open = False
            ui_inven_open = True
            ui_char_open = ui_hotkey_open = ui_weapon_open = False
            print("[MENU] 인벤토리 (I)")
            return
        elif event.key == SDLK_o:
            menu_open = False
            ui_hotkey_open = True
            ui_char_open = ui_inven_open = ui_weapon_open = False
            print("[MENU] 단축키 정보 (O)")
            return

        elif event.key == SDLK_p:
            menu_open = False
            ui_weapon_open = True
            ui_char_open = ui_inven_open = ui_hotkey_open = False
            print("[MENU] 무기 강화 (P)")
            return

            # 마우스 왼쪽 클릭
        if event.type == SDL_MOUSEBUTTONDOWN and event.button == SDL_BUTTON_LEFT:
            mx, my = event.x, event.y

            # X 버튼
            if _in_rect(mx, my, menu_rect_close):
                menu_open = False
                print("[MENU] 닫기 버튼 클릭")
                return
            if _in_rect(mx, my, menu_rect_char):
                menu_open = False
                ui_char_open = True
                ui_inven_open = ui_hotkey_open = ui_weapon_open = False
                print("[MENU] 캐릭터 정보 클릭")
                return

                # 인벤토리
            if _in_rect(mx, my, menu_rect_inven):
                menu_open = False
                ui_inven_open = True
                ui_char_open = ui_hotkey_open = ui_weapon_open = False
                print("[MENU] 인벤토리 클릭")
                return

                # 단축키 정보
            if _in_rect(mx, my, menu_rect_hotkey):
                menu_open = False
                ui_hotkey_open = True
                ui_char_open = ui_inven_open = ui_weapon_open = False
                print("[MENU] 단축키 정보 클릭")
                return

                # 무기 강화
            if _in_rect(mx, my, menu_rect_weapon):
                menu_open = False
                ui_weapon_open = True
                ui_char_open = ui_inven_open = ui_hotkey_open = False
                print("[MENU] 무기 강화 클릭")
                return

                # 게임 종료
            if _in_rect(mx, my, menu_rect_exit):
                print("[MENU] 게임 종료 클릭")
                game_framework.quit()
                return


def _in_rect(x, y, rect): #esc 마우스 처리
    if rect is None:
        return False
    x0, y0, x1, y1 = rect
    return x0 <= x <= x1 and y0 <= y <= y1


def load_map(name: str, entry: str = "default"):
    """맵 로드 + 필드/보이 배치"""
    global field, boy, current_map, _collision_grace
    data = MAPS[name]
    current_map = name

    for layer in game_world.world:  # world = [[],[],[]]
        layer[:] = [o for o in layer if not isinstance(o, Boy)]

    # 이전 필드 제거
    if field:
        game_world.remove_object(field)

    # 새 필드 생성
    field = Field(data["image"], lerp=0.15)
    field.VIEW_W, field.VIEW_H = get_canvas_width(), get_canvas_height()
    field.ground_profile = data["ground"][:]  # 지면 포인트 주입
    game_world.add_object(field, 0)

    # 보이 생성/재사용
    if not boy:
        set_boy(Boy())
        game_world.add_object(boy, 1)  # depth 1
    else:
        # boy가 world에 없으면 다시 add (중복 방지)
        if all(boy not in layer for layer in game_world.world):
            game_world.add_object(boy, 1)
    # 스폰 배치
    sx, sy = data["spawn"].get(entry, data["spawn"]["default"])
    boy.x, boy.y = sx, sy
    if hasattr(field, "ground_y"):
        boy.y = field.ground_y(boy.x)

    if entry == "from_right":
        boy.x -= 40
    elif entry == "from_left":
        boy.x += 40

    _collision_grace = 0.35

    # 카메라 타겟 연결
    boy.set_camera(field)
    field.target = boy

    hw, hh = field.VIEW_W / 2, field.VIEW_H / 2
    max_cx = max(field.bg_w - hw, hw)
    max_cy = max(field.bg_h - hh, hh)
    field.cam_x = max(hw, min(boy.x, max_cx))
    field.cam_y = max(hh, min(boy.y, max_cy))

    if hasattr(boy, 'up_pressed'):
        boy.up_pressed = False

    field.update()
    monsters.clear()
    items.clear()

    for layer in game_world.world:
        layer[:] = [o for o in layer if not isinstance(o, Mushroom)]
    monsters.clear()

    for layer in game_world.world:
        layer[:] = [o for o in layer if not isinstance(o, DropItem)]
    items.clear()

    # 새 버섯 무작위 소환
    if data.get("spawn_monsters", False):
        width = data["width"]
        cnt = random.randint(5, 10)
        for _ in range(cnt):
            x = random.randint(0, width)
            y = field.ground_y(x) if hasattr(field, "ground_y") else 0
            m = Mushroom(x, y, field=field)
            m.set_world_bounds(0, width)
            # 방향 랜덤
            m.dir = random.choice([-1, 1])
            game_world.add_object(m, 1)
            monsters.append(m)

def set_boy(b: Boy):
    global boy
    boy = b

def _overlap(a, b):
    ax0, ay0, ax1, ay1 = a
    bx0, by0, bx1, by1 = b
    return (ax0 < bx1) and (ax1 > bx0) and (ay0 < by1) and (ay1 > by0)

def _gather_monsters():
    mons = []
    for layer in game_world.world:
        for o in layer:
            if o.__class__.__name__ == 'Mushroom':
                mons.append(o)
    return mons

def _gather_items():
    res = []
    for layer in game_world.world:
        for o in layer:
            if o.__class__.__name__ == 'DropItem':
                res.append(o)
    return res

def _choose_drop_kind():
    r = random.random()   # 0.0 ~ 1.0
    acc = 0.0
    for kind, p in DROP_TABLE:
        acc += p
        if r < acc:
            return kind
    # 혹시 합이 1.0이 안 맞아도 마지막 거 반환
    return DROP_TABLE[-1][0]

def _keep_boy_in_world():
    if not field:
        return

    world_w = getattr(field, "bg_w", MAPS.get(current_map, {}).get("width", 1000))

    l, b, r, t = boy.get_bb()
    if l < 0:
        boy.x += (0 - l)
    if r > world_w:
        boy.x += (world_w - r)

def _boy_bb():
    half_w, half_h = 100, 40
    return (boy.x - half_w, boy.y - half_h, boy.x + half_w, boy.y + half_h)

def _check_portal_transition(dt):
    global _transition_cooldown
    if _transition_cooldown > 0:
        _transition_cooldown -= dt
        return

    portals = MAPS[current_map].get("portals", [])
    bb = _boy_bb()

    for p in portals:
        x0, y0, x1, y1 = p["rect"]
        need_up = p.get("require_up", False)
        if _overlap(bb, (x0, y0, x1, y1)) and (not need_up or getattr(boy, "up_pressed", False)):
            # print("PORTAL TRIGGER:", current_map, "->", p["to"])
            load_map(p["to"], entry=p.get("entry", "default"))
            _transition_cooldown = 0.25
            return

def _draw_portals_debug():
    for p in MAPS[current_map].get("portals", []):
        x0, y0, x1, y1 = p["rect"]
        sx0, sy0 = field.world_to_screen(x0, y0)
        sx1, sy1 = field.world_to_screen(x1, y1)
        draw_rectangle(min(sx0, sx1), min(sy0, sy1), max(sx0, sx1), max(sy0, sy1))

def handle_events():
    global menu_open
    global ui_char_open, ui_inven_open, ui_hotkey_open, ui_weapon_open

    event_list = get_events()
    for event in event_list:
        if event.type == SDL_QUIT:
            game_framework.quit()

        if event.type == SDL_KEYDOWN:
            if event.key == SDLK_u:
                ui_char_open = True
                ui_inven_open = ui_hotkey_open = ui_weapon_open = False
                menu_open = False
                print("[GLOBAL] 캐릭터 정보 (U)")
                continue
            elif event.key == SDLK_i:
                ui_inven_open = True
                ui_char_open = ui_hotkey_open = ui_weapon_open = False
                menu_open = False
                print("[GLOBAL] 인벤토리 (I)")
                continue
            elif event.key == SDLK_o:
                ui_hotkey_open = True
                ui_char_open = ui_inven_open = ui_weapon_open = False
                menu_open = False
                print("[GLOBAL] 단축키 정보 (O)")
                continue
            elif event.key == SDLK_p:
                ui_weapon_open = True
                ui_char_open = ui_inven_open = ui_hotkey_open = False
                menu_open = False
                print("[GLOBAL] 무기 강화 (P)")
                continue
        if ui_char_open or ui_inven_open or ui_hotkey_open or ui_weapon_open:
            if event.type == SDL_KEYDOWN and event.key == SDLK_ESCAPE:
                ui_char_open = ui_inven_open = ui_hotkey_open = ui_weapon_open = False
                print("[UI] 서브창 닫기 (ESC)")
            # 서브창 열려 있을 땐 다른 입력은 무시
            continue
        if event.type == SDL_KEYDOWN and event.key == SDLK_ESCAPE:
            menu_open = not menu_open
            print("ESC pressed, menu_open =", menu_open)
            continue

        if menu_open:
            _handle_menu_event(event)
            continue

        boy.handle_event(event)


def _handle_collisions():
    if hasattr(boy, 'alive') and not boy.alive:
        return

    # 1) 몬스터 → 플레이어 (플레이어가 맞는 쪽)
    if getattr(boy, 'if_timer', 0) <= 0:   # 무적 아닐 때만
        bb_b = boy.get_bb()
        for m in _gather_monsters():
            # 죽었거나 죽는 중인 몬스터는 무시
            if getattr(m, 'dead', False):
                continue
            if getattr(m, 'state', None) == 'die':
                continue

            if _overlap(bb_b, m.get_bb()):
                from_dir = 1 if (m.x > boy.x) else -1
                damage = getattr(m, 'contact_damage', 1)
                boy.take_hit(from_dir, damage=damage)
                return

    # 2) 플레이어 공격 → 몬스터 피격
    if getattr(boy, 'attack_active', False):
        atk_bb = boy.get_attack_bb()
        for m in _gather_monsters():
            if getattr(m, 'dead', False):
                continue

            # 🔥 방금 맞은 몬스터는 이번 프레임(또는 짧은 시간) 동안 무시
            if getattr(m, 'hit_cool', 0) > 0:
                continue

            if _overlap(atk_bb, m.get_bb()):
                m.take_hit(damage=1, from_dir=boy.face_dir)
                m.hit_cool = 0.3

def _handle_item_pickup():
    if not getattr(boy, 'pick_pressed', False):
        return

    bb_boy = boy.get_bb()

    for it in list(_gather_items()):
        if _overlap(bb_boy, it.get_bb()):
            boy.obtain_item(it.kind)

            for layer in game_world.world:
                if it in layer:
                    layer.remove(it)
            if it in items:
                items.remove(it)



def update():
    global _collision_grace
    game_world.update()
    if field and hasattr(field, "ground_y") and not getattr(boy, 'in_air', False):
        boy.y = field.ground_y(boy.x)

    field.update()

    _check_portal_transition(game_framework.frame_time)

    if _collision_grace > 0:
        _collision_grace -= game_framework.frame_time

    _keep_boy_in_world()
    _handle_collisions()
    _handle_item_pickup()

    for layer in game_world.world:
        for o in list(layer):  # 복사본 돌면서 제거
            # 몬스터 죽으면 드랍 생성 + 몬스터 제거
            if isinstance(o, Mushroom) and getattr(o, 'dead', False):
                # 드랍 확률 (원하면 수정)
                if random.random() < 0.7:
                    drop_x = o.x
                    drop_y = o.y + 20
                    kind = _choose_drop_kind()
                    print('[PLAYMODE] SPAWN DROP:', kind, 'at', drop_x, drop_y)
                    item = DropItem(drop_x, drop_y, field=field, kind=kind)
                    game_world.add_object(item, 1)
                    items.append(item)

                boy.gain_exp(10)

                game_world.remove_object(o)
                if o in monsters:
                    monsters.remove(o)

            if isinstance(o, DropItem) and getattr(o, 'expired', False):
                print('[PLAYMODE] REMOVE EXPIRED DROP:', o.kind)
                game_world.remove_object(o)
                if o in items:
                    items.remove(o)


def draw():
    clear_canvas()
    game_world.render()
    _draw_portals_debug()

    if DRAW_HITBOX and field:
        # 캐릭터 박스
        l, b, r, t = boy.get_bb()
        sx0, sy0 = field.world_to_screen(l, b)
        sx1, sy1 = field.world_to_screen(r, t)
        draw_rectangle(sx0, sy0, sx1, sy1)

        # 몬스터 박스
        for m in _gather_monsters():
            l, b, r, t = m.get_bb()
            sx0, sy0 = field.world_to_screen(l, b)
            sx1, sy1 = field.world_to_screen(r, t)
            draw_rectangle(sx0, sy0, sx1, sy1)

        # 아이템 박스
        for it in _gather_items():
            l, b, r, t = it.get_bb()
            sx0, sy0 = field.world_to_screen(l, b)
            sx1, sy1 = field.world_to_screen(r, t)
            draw_rectangle(sx0, sy0, sx1, sy1)

    if boy:
        boy.draw_ui()

    if menu_open and menu_img is not None:
        cw, ch = get_canvas_width(), get_canvas_height()
        scaled_w = int(menu_img.w * MENU_SCALE)
        scaled_h = int(menu_img.h * MENU_SCALE)
        menu_img.draw(cw // 2, ch // 2, scaled_w, scaled_h)

        # 인벤토리 / 무기 강화 창
    _draw_subwindows()

    update_canvas()

def _draw_round_panel(rect):
    x0, y0, x1, y1 = rect
    draw_rectangle(x0, y0, x1, y1)

def _draw_menu():
    if not menu_open or menu_img is None:
        return

    if menu_img is None or menu_rect_main is None:
        # 혹시 이미지 로딩이 실패했는지 확인용
        x = get_canvas_width() // 2
        y = get_canvas_height() // 2
        draw_rectangle(x - 100, y - 50, x + 100, y + 50)
        return

    x0, y0, x1, y1 = menu_rect_main
    cx = (x0 + x1) // 2
    cy = (y0 + y1) // 2
    menu_img.draw(cx, cy)

    # 디버그: 클릭 영역이 어디인지 확인하고 싶으면 사각형 보여주기
    # if DRAW_MENU_BOUNDS:
    #     for rect in [menu_rect_close,
    #                  menu_rect_char, menu_rect_inven,
    #                  menu_rect_hotkey, menu_rect_weapon,
    #                  menu_rect_exit]:
    #         if rect:
    #             draw_rectangle(*rect)

def _draw_subwindows():
    cw, ch = get_canvas_width(), get_canvas_height()

    _draw_char_window()

    # 캐릭터 정보 (U)
    if ui_char_open:
        w, h = 500, 320
        x0 = cw // 2 - w // 2
        y0 = ch // 2 - h // 2
        x1 = x0 + w
        y1 = y0 + h
        draw_rectangle(x0, y0, x1, y1)

    # 인벤토리 (I)
    if ui_inven_open:
        w, h = 500, 320
        x0 = cw // 2 - w // 2
        y0 = ch // 2 - h // 2
        x1 = x0 + w
        y1 = y0 + h
        draw_rectangle(x0, y0, x1, y1)

    # 단축키 정보 (O)
    if ui_hotkey_open:
        w, h = 500, 240
        x0 = cw // 2 - w // 2
        y0 = ch // 2 - h // 2
        x1 = x0 + w
        y1 = y0 + h
        draw_rectangle(x0, y0, x1, y1)

    # 무기 강화 (P)
    if ui_weapon_open:
        w, h = 500, 320
        x0 = cw // 2 - w // 2
        y0 = ch // 2 - h // 2
        x1 = x0 + w
        y1 = y0 + h
        draw_rectangle(x0, y0, x1, y1)

def _draw_boy_portrait(px, py):
    if boy is None or boy.image is None:
        return

    # Idle 스프라이트 한 줄 기준 (boy.Idle.draw에서 쓰던 값)
    W, H = 56, 80
    PITCH = 58
    START_X = 0
    START_Y = 720

    frame_index = 0
    left = START_X + frame_index * PITCH
    bottom = START_Y

    S = 2.2  # 초상화 크기
    DW, DH = int(W * S), int(H * S)
    foot_fix = (DH - H) // 2
    y = py - foot_fix

    flip = 'h'

    boy.image.clip_composite_draw(left, bottom, W, H,
                                  0, flip,
                                  px, y, DW, DH)

def _draw_char_window():
    if not ui_char_open:
        return

    cw, ch = get_canvas_width(), get_canvas_height()

    if char_panel_img is None:
        # 이미지 없을 때 임시 박스
        w, h = 500, 320
        x0 = cw // 2 - w // 2
        y0 = ch // 2 - h // 2
        x1 = x0 + w
        y1 = y0 + h
        draw_rectangle(x0, y0, x1, y1)
        return

    # 패널 위치/크기
    w = int(char_panel_img.w * CHAR_PANEL_SCALE)
    h = int(char_panel_img.h * CHAR_PANEL_SCALE)
    cx, cy = cw // 2, ch // 2
    panel_left   = cx - w // 2
    panel_bottom = cy - h // 2

    # 패널 이미지 그리기
    char_panel_img.draw(cx, cy, w, h)

    # -----------------------
    # 1) 왼쪽 초상화 (그림 박스 안 중앙쯤)
    # -----------------------
    face_cx = panel_left + int(w * 0.35)
    face_cy = panel_bottom + int(h * 0.55)
    _draw_boy_portrait(face_cx, face_cy)

    # -----------------------
    # 2) 오른쪽 숫자들만 출력
    #    (라벨은 PNG 안에 이미 있음)
    # -----------------------
    lvl = getattr(boy, 'level', 1)
    exp = getattr(boy, 'exp', 0)
    exp_to_next = getattr(boy, 'exp_to_next', 1)
    wlv = getattr(boy, 'weapon_level', 1)
    atk = getattr(boy, 'attack', getattr(boy, 'attack_power', 0))

    # 너무 길면 잘라서 표시
    lvl_s = _fmt_num(lvl, max_digits=4)
    exp_s = _fmt_num(exp, max_digits=6)
    exp_next_s = _fmt_num(exp_to_next, max_digits=6)
    wlv_s = _fmt_num(wlv, max_digits=4)
    atk_s = _fmt_num(atk, max_digits=6)

    font = boy.ui_font

    # 숫자는 각 박스의 오른쪽 부분에 정렬되게
    num_x = panel_left + int(w * 0.58)  # 오른쪽으로 조금 붙이기

    # 위쪽 흰 박스(레벨/경험치) 안 y 좌표
    level_y = panel_bottom + int(h * 0.63)
    exp_y = panel_bottom + int(h * 0.53)

    # 아래 흰 박스(무기레벨/공격력) 안 y 좌표
    weapon_y = panel_bottom + int(h * 0.38)
    attack_y = panel_bottom + int(h * 0.295)

    # ---- 숫자만 출력 ----
    font.draw(num_x, level_y, lvl_s, (0, 0, 0))  # 레벨
    font.draw(num_x, exp_y, f'{exp_s}/{exp_next_s}', (0, 0, 0))  # 경험치
    font.draw(num_x, weapon_y, wlv_s, (0, 0, 0))  # 무기레벨
    font.draw(num_x, attack_y, atk_s, (0, 0, 0))



def finish():
    game_world.clear()

def pause(): pass
def resume(): pass

