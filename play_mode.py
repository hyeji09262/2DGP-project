import random
from pico2d import *

import game_framework
import game_world

from boy import Boy
from field import Field
from monster import Mushroom
from item import DropItem, ITEM_IMAGES

field = None
boy = None
current_map = None
_transition_cooldown = 0.0
monsters = []
items = []
DRAW_HITBOX = True
_collision_grace = 0.0
COLLIDE_IGNORE_PROB = 0.8
enchant_msg_img = None


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
DRAW_MENU_BOUNDS = True

char_x_rect = None
inven_x_rect = None
hotkey_x_rect = None
weapon_x_rect = None

# 각 서브창(다음 화면) 열림 여부
ui_char_open = False       # U
ui_inven_open = False      # I
ui_hotkey_open = False     # O
ui_weapon_open = False     # P

char_panel_img = None
CHAR_PANEL_SCALE = 0.5

inven_panel_img = None
INVEN_PANEL_SCALE = 0.5
inv_item_images = {}

INV_ICON_SCALES = {
    '주황버섯의 갓': 0.1,
    '빨간포션' : 0.25,
    '파란포션' : 0.25
    # 나중에 아이템 더 생기면 여기 계속 추가하면 됨
}
DEFAULT_INV_ICON_SCALE = 0.1

hotkey_panel_img = None
HOTKEY_PANEL_SCALE = 0.5

weapon_panel_img = None
WEAPON_PANEL_SCALE = 0.37

last_enchant_msg = ""
last_enchant_timer = 0.0

potion_bar_img = None
POTION_BAR_SCALE = 0.15

potion_icon_imgs = {}


#-----------------------------

DROP_TABLE = [
    ('10원',   0.25),
    ('100원', 0.2),
    ('1000원',    0.1),
    ('5000원',    0.05),
    ('주황버섯의 갓',   0.2),
    ('빨간포션', 0.1),
    ('파란포션', 0.1),
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

    close_w = int(w *  0.06)  # 대략적인 비율
    close_h = close_w
    cx1 = x1 - int(w * 0.2)
    cy1 = y1 - int(h * 0.19)
    cx0 = cx1 - close_w
    cy0 = cy1 - close_h
    menu_rect_close = (cx0, cy0, cx1, cy1)

    # 네 개 큰 버튼(캐릭터/U, 인벤/I, 단축키/O, 무기강화/P)
    btn_w = int(w * 0.2)
    btn_h = int(h * 0.25)

    # 좌우 열 중심
    left_cx = x0 + int(w * 0.33)
    right_cx = x0 + int(w * 0.58)

    top_cy = y0 + int(h * 0.55)
    bottom_cy = y0 + int(h * 0.35)

    # 게임 종료 버튼 (오른쪽 아래)
    exit_w = int(w *0.1)
    exit_h = int(h * 0.1)
    ex1 = x1 - int(w * 0.2)
    ey0 = y0 + int(h * 0.2)
    ex0 = ex1 - exit_w
    ey1 = ey0 + exit_h
    menu_rect_exit = (ex0, ey0, ex1, ey1)

    def make_rect(cx, cy):
        hw = btn_w // 2
        hh = btn_h // 2
        return (cx - hw, cy - hh, cx + hw, cy + hh)

    menu_rect_char = make_rect(left_cx, top_cy)  # U : 캐릭터 정보
    menu_rect_inven = make_rect(right_cx, top_cy)  # I : 인벤토리
    menu_rect_hotkey = make_rect(left_cx, bottom_cy)  # O : 단축키 정보
    menu_rect_weapon = make_rect(right_cx, bottom_cy)  # P : 무기 강화



def init():
    global field, boy, current_map, _transition_cooldown, monsters, items
    global menu_open, menu_img
    global char_panel_img
    global inven_panel_img, inv_item_images
    global hotkey_panel_img
    global weapon_panel_img, last_enchant_msg, enchant_msg_img
    global potion_bar_img, potion_icons
    global  game_over_img

    load_map("henesys", "default")

    menu_open = False

    menu_img = load_image('사진수집/etc/메뉴창.png')
    char_panel_img = load_image('사진수집/etc/캐릭터정보.png')

    inven_panel_img = load_image('사진수집/etc/인벤2.png')

    hotkey_panel_img = load_image('사진수집/etc/단축키.png')

    inv_item_images = {}

    weapon_panel_img = load_image('사진수집/etc/무기.png')
    last_enchant_msg = ""

    enchant_msg_img = load_image('사진수집/etc/강화박스.png')

    potion_bar_img = load_image('사진수집/etc/포션바.png')
    potion_icon_imgs = {}

    game_over_img = load_image('사진수집/etc/부활키.png')

    _init_menu_layout()

def _canvas_mouse_xy(event):
    h = get_canvas_height()
    return event.x, h - event.y - 1

def _handle_menu_event(event):
    global menu_open, ui_char_open, ui_inven_open, ui_hotkey_open, ui_weapon_open

    # 마우스 왼쪽 클릭만 처리
    if event.type == SDL_MOUSEBUTTONDOWN and event.button == SDL_BUTTON_LEFT:
        mx, my = _canvas_mouse_xy(event)
        # print("[MENU] mouse click:", mx, my)

        # X 버튼 클릭 → 메뉴 닫기
        if _in_rect(mx, my, menu_rect_close):
            menu_open = False
            print("[MENU] X 버튼 클릭 → 메뉴 닫기")
            return

        # '캐릭터 정보' 버튼 (왼쪽 위)
        if _in_rect(mx, my, menu_rect_char):
            menu_open = False
            ui_char_open = True
            ui_inven_open = ui_hotkey_open = ui_weapon_open = False
            print("[MENU] 캐릭터 정보 클릭")
            return

        # '인벤토리' 버튼 (오른쪽 위)
        if _in_rect(mx, my, menu_rect_inven):
            menu_open = False
            ui_inven_open = True
            ui_char_open = ui_hotkey_open = ui_weapon_open = False
            print("[MENU] 인벤토리 클릭")
            return

        # '단축키 정보' 버튼 (왼쪽 아래)
        if _in_rect(mx, my, menu_rect_hotkey):
            menu_open = False
            ui_hotkey_open = True
            ui_char_open = ui_inven_open = ui_weapon_open = False
            print("[MENU] 단축키 정보 클릭")
            return

        # '무기 강화' 버튼 (오른쪽 아래)
        if _in_rect(mx, my, menu_rect_weapon):
            menu_open = False
            ui_weapon_open = True
            ui_char_open = ui_inven_open = ui_hotkey_open = False
            print("[MENU] 무기 강화 클릭")
            return

        # '게임 종료' 버튼 클릭
        if _in_rect(mx, my, menu_rect_exit):
            print("[MENU] 게임 종료 버튼 클릭 → game_framework.quit()")
            game_framework.quit()
            return



def _in_rect(x, y, rect): #esc 마우스 처리
    if rect is None:
        return False
    x0, y0, x1, y1 = rect
    return x0 <= x <= x1 and y0 <= y <= y1


def load_map(name: str, entry: str = "default"):
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
        # 창 닫기
        if event.type == SDL_QUIT:
            game_framework.quit()
            continue

        # ESC 키
        if event.type == SDL_KEYDOWN and event.key == SDLK_ESCAPE:
            # 서브창/메뉴 다 닫기
            if ui_char_open or ui_inven_open or ui_hotkey_open or ui_weapon_open:
                ui_char_open = ui_inven_open = ui_hotkey_open = ui_weapon_open = False
                print("[UI] 서브창 닫기 (ESC)")
            else:
                # 아무 서브창도 안 열려 있으면 메뉴 토글
                menu_open = not menu_open
                print("[UI] 메뉴 토글 =", menu_open)
            continue

        # ====== 서브창 단축키 ======
        if event.type == SDL_KEYDOWN:
            # 캐릭터 정보 (U)
            if event.key == SDLK_u:
                ui_char_open = True
                ui_inven_open = ui_hotkey_open = ui_weapon_open = False
                menu_open = False
                print("[GLOBAL] 캐릭터 정보 (U)")
                continue

            # 인벤토리 (I)
            if event.key == SDLK_i:
                ui_inven_open = True
                ui_char_open = ui_hotkey_open = ui_weapon_open = False
                menu_open = False
                print("[GLOBAL] 인벤토리 (I)")
                continue

            # 단축키 정보 (O)
            if event.key == SDLK_o:
                ui_hotkey_open = True
                ui_char_open = ui_inven_open = ui_weapon_open = False
                menu_open = False
                print("[GLOBAL] 단축키 정보 (O)")
                continue

            # 무기 강화 (P)
            if event.key == SDLK_p:
                ui_weapon_open = True
                ui_char_open = ui_inven_open = ui_hotkey_open = False
                menu_open = False
                print("[GLOBAL] 무기 강화 (P)")
                continue

            if event.type == SDL_KEYDOWN:
                if (not menu_open) and (not (ui_char_open or ui_inven_open or ui_hotkey_open or ui_weapon_open)):
                    if event.key == SDLK_1:
                        boy.use_red_potion()
                        continue
                    if event.key == SDLK_2:
                        boy.use_blue_potion()
                        continue

        if ui_weapon_open and event.type == SDL_KEYDOWN and event.key == SDLK_SPACE:
            _attempt_weapon_enchant()
                # boy.handle_event 로 넘기지 않음
            continue

        if ui_char_open or ui_inven_open or ui_hotkey_open or ui_weapon_open:
            _handle_subwindow_mouse(event)
            # 서브창이 열려 있으면 게임 조작(boy.handle_event)은 막음
            continue

        # ====== 메뉴가 열려 있을 때 마우스 처리 (나중에 버튼 클릭용) ======
        if menu_open:
            _handle_menu_event(event)
            continue

        if ui_char_open or ui_inven_open or ui_hotkey_open or ui_weapon_open:
            _handle_subwindow_mouse(event)
                # 여기서는 캐릭터 움직임 같은 건 막고 UI만 처리
            continue


            # ====== 평소 게임 조작(캐릭터 이동/점프/공격 등) ======
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

            if getattr(m, 'hit_cool', 0) > 0:
                continue

            if _overlap(atk_bb, m.get_bb()):
                dmg = _get_boy_attack()  # playmode.py 에 이미 만든 헬퍼
                m.take_hit(damage=dmg, from_dir=boy.face_dir)
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
    global _collision_grace, last_enchant_timer, last_enchant_msg
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

    if last_enchant_timer > 0:
        last_enchant_timer -= game_framework.frame_time
        if last_enchant_timer <= 0:
            last_enchant_timer = 0
            last_enchant_msg = ""

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


    if hasattr(boy, 'alive') and not boy.alive:
        GAME_OVER_SCALE = 0.3
        cw, ch = get_canvas_width(), get_canvas_height()
        w = int(game_over_img.w * GAME_OVER_SCALE)
        h = int(game_over_img.h * GAME_OVER_SCALE)
        game_over_img.draw(cw // 2, ch // 2 + 50, w, h)

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

    _draw_potion_bar()

    if menu_open and menu_img is not None:
        cw, ch = get_canvas_width(), get_canvas_height()
        scaled_w = int(menu_img.w * MENU_SCALE)
        scaled_h = int(menu_img.h * MENU_SCALE)
        menu_img.draw(cw // 2, ch // 2, scaled_w, scaled_h)
        _draw_menu_bounds()

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

    _draw_inventory_window()

    _draw_hotkey_window()

    _draw_weapon_window()

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
    global char_x_rect

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

    x1 = panel_left + w - int(w * 0.2)  # 오른쪽에서 4% 안쪽
    y1 = panel_bottom + h - int(h * 0.19)  # 위에서 5% 아래
    x0 = x1 - int(w * 0.06)  # X 버튼 폭 : w * 6%
    y0 = y1 - int(h * 0.10)  # X 버튼 높이 : h * 10%
    char_x_rect = (x0, y0, x1, y1)

    if DRAW_MENU_BOUNDS:
        draw_rectangle(*char_x_rect)

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

def _draw_inventory_window():

    global inven_x_rect

    if not ui_inven_open:
        return

    cw, ch = get_canvas_width(), get_canvas_height()

    if inven_panel_img is None:
            # 이미지 없으면 임시 박스
        w, h = 300, 500
        x0 = cw // 2 - w // 2
        y0 = ch // 2 - h // 2
        draw_rectangle(x0, y0, x0 + w, y0 + h)
        return

        # 패널 위치/크기
    w = int(inven_panel_img.w * INVEN_PANEL_SCALE)
    h = int(inven_panel_img.h * INVEN_PANEL_SCALE)
    cx, cy = cw // 2, ch // 2
    panel_left = cx - w // 2
    panel_bottom = cy - h // 2

        # 패널 이미지 그리기
    inven_panel_img.draw(cx, cy, w, h)

    x1 = panel_left + w - int(w * 0.15)
    y1 = panel_bottom + h - int(h * 0.08)
    x0 = x1 - int(w * 0.07)
    y0 = y1 - int(h * 0.05)
    inven_x_rect = (x0, y0, x1, y1)

    if DRAW_MENU_BOUNDS:
        draw_rectangle(*inven_x_rect)

        # ==========================
        # 1) 인벤 아이템 그리드
        #    (돈 제외한 아이템들만)
        # ==========================
    money_kinds = ('10원', '100원', '1000원', '5000원')

        # (kind, count) 리스트 만들기
    inv_list = []
    for kind, cnt in getattr(boy, 'inventory', {}).items():
        if cnt <= 0:
            continue
        if kind in money_kinds:
            continue
        inv_list.append((kind, cnt))
        # 4 x 5 슬롯 (위 그림 기준)
    cols, rows = 3, 5
    max_slots = cols * rows

        #내부 그리드 영역 (패널 비율로 계산)
    grid_left = panel_left + int(w * 0.2)
    grid_right = panel_left + int(w * 0.8)
    grid_bottom = panel_bottom + int(h * 0.16)
    grid_top = panel_bottom + int(h * 0.82)

    slot_w = (grid_right - grid_left) / cols
    slot_h = (grid_top - grid_bottom) / rows



    for idx in range(min(len(inv_list), max_slots)):
        kind, cnt = inv_list[idx]
        c = idx % cols  # 0 ~ 3
        r = idx // cols  # 0 ~ 4 (0이 맨 위)
            # 슬롯 중심 좌표
        cx_slot = grid_left + slot_w * (c + 0.5)
        cy_slot = grid_top - slot_h * (r + 0.5)

            # 아이콘 이미지 준비 (캐시 사용)
        if kind not in inv_item_images:
            path = ITEM_IMAGES.get(kind, None)
            if path:
                inv_item_images[kind] = load_image(path)
        img = inv_item_images.get(kind, None)
        if img is None:
            continue

        scale = INV_ICON_SCALES.get(kind, DEFAULT_INV_ICON_SCALE)

        iw = int(img.w * scale)
        ih = int(img.h * scale)
        if kind == '파란포션':  # ← 너가 ITEM_IMAGES에 쓴 키랑 똑같이!
            img.clip_composite_draw(
                0, 0, img.w, img.h,  # 원본 전체
                0, 'h',  # 회전 0, 수평 뒤집기
                int(cx_slot), int(cy_slot),
                iw, ih
            )
        else:
            img.draw(int(cx_slot), int(cy_slot), iw, ih)

            # 개수 숫자 (오른쪽 아래에 작게)
        count_str = str(cnt)
        font = boy.s_font
        font.draw(int(cx_slot + slot_w * 0.2),
                    int(cy_slot - slot_h * 0.23),
                    count_str, (0, 0, 0))

        # ==========================
        # 2) 누적 금액 표시 (맨 아래 흰 박스)
        # ==========================
    gold = getattr(boy, 'gold', 0)
    gold_str = f"{gold} G"

    font = boy.kr_font

        # 아래 하얀 바 중앙쯤
    gold_x = cx
    gold_y = panel_bottom + int(h * 0.105)

    font.draw(gold_x - len(gold_str) * 4, gold_y, gold_str, (255, 200, 0))

def _draw_hotkey_window():
    global hotkey_x_rect

    if not ui_hotkey_open:
        return

    cw, ch = get_canvas_width(), get_canvas_height()

    # 이미지가 없으면 임시 박스만
    if hotkey_panel_img is None:
        w, h = 500, 300
        x0 = cw // 2 - w // 2
        y0 = ch // 2 - h // 2
        draw_rectangle(x0, y0, x0 + w, y0 + h)
        return

    # 패널 위치/크기 (화면 중앙)
    w = int(hotkey_panel_img.w * HOTKEY_PANEL_SCALE)
    h = int(hotkey_panel_img.h * HOTKEY_PANEL_SCALE)
    cx, cy = cw // 2, ch // 2
    panel_left = cx - w // 2
    panel_bottom = cy - h // 2

    hotkey_panel_img.draw(cx, cy, w, h)

    x1 = panel_left + w - int(w * 0.2)
    y1 = panel_bottom + h - int(h * 0.18)
    x0 = x1 - int(w * 0.06)
    y0 = y1 - int(h * 0.12)
    hotkey_x_rect = (x0, y0, x1, y1)

    if DRAW_MENU_BOUNDS:
        draw_rectangle(*hotkey_x_rect)

# ----- 무기 강화 관련 헬퍼 -----

def _get_boy_attack():
    if hasattr(boy, 'attack'):
        return boy.attack
    if hasattr(boy, 'attack_power'):
        return boy.attack_power
    return 0

def _set_boy_attack(value):
    if hasattr(boy, 'attack'):
        boy.attack = value
    if hasattr(boy, 'attack_power'):
        boy.attack_power = value

def _get_enchant_info():

    cur_level = getattr(boy, 'weapon_level', 1)
    cur_atk = _get_boy_attack()

    start_rate = 1.0  # 100%
    step = 0.05  # 레벨당 5% 감소
    rate = start_rate - step * (cur_level - 1)
    rate = max(0.20, rate)  # 최소 20%

    # 골드 소비: 현재 무기 레벨 * 100
    cost = 10 * cur_level

    atk_before = cur_atk
    atk_after = cur_atk + 5  # 한 번 성공 시 +5

    return cur_level, rate, cost, atk_before, atk_after

def _attempt_weapon_enchant():
    global last_enchant_msg,  last_enchant_timer

    # boy가 죽어있으면 강화 불가
    if hasattr(boy, 'alive') and not boy.alive:
        last_enchant_msg = "강화 불가"
        last_enchant_timer = 0.8
        return

    level, rate, cost, atk_before, atk_after = _get_enchant_info()
    gold = getattr(boy, 'gold', 0)

    # 골드 부족
    if gold < cost:
        last_enchant_msg = f"골드 부족 ({gold}/{cost})"
        last_enchant_timer = 0.8
        print("[ENCHANT] 골드 부족:", gold, "/", cost)
        return

    # 골드 차감
    setattr(boy, 'gold', gold - cost)

    r = random.random()
    print(f"[ENCHANT] try: level={level}, rate={rate:.2f}, roll={r:.2f}")

    if r < rate:
        # 성공
        new_level = level + 1
        setattr(boy, 'weapon_level', new_level)
        _set_boy_attack(atk_after)
        last_enchant_msg = f"강화 성공! Lv.{new_level}"
        last_enchant_timer = 0.8
        print("[ENCHANT] SUCCESS -> level", new_level, "atk", atk_after)
    else:
        # 실패 (여기서는 하락/파괴 없음)
        last_enchant_msg = "강화 실패..."
        last_enchant_timer = 0.8
        print("[ENCHANT] FAIL")

def _draw_weapon_window():
    global weapon_x_rect
    if not ui_weapon_open:
        return

    cw, ch = get_canvas_width(), get_canvas_height()

    # 이미지 없을 때는 네모만
    if weapon_panel_img is None:
        w, h = 400, 600
        x0 = cw // 2 - w // 2
        y0 = ch // 2 - h // 2
        draw_rectangle(x0, y0, x0 + w, y0 + h)
        return

    # 패널 크기/위치
    w = int(weapon_panel_img.w * WEAPON_PANEL_SCALE)
    h = int(weapon_panel_img.h * WEAPON_PANEL_SCALE)
    cx, cy = cw // 2, ch // 2
    panel_left   = cx - w // 2
    panel_bottom = cy - h // 2

    # 배경 패널 이미지
    weapon_panel_img.draw(cx-10, cy+10, w, h)

    x1 = panel_left + w - int(w * 0.185)
    y1 = panel_bottom + h - int(h * 0.2)
    x0 = x1 - int(w * 0.06)
    y0 = y1 - int(h * 0.03)
    weapon_x_rect = (x0, y0, x1, y1)

    if DRAW_MENU_BOUNDS:
        draw_rectangle(*weapon_x_rect)

    # ======== 안에 들어갈 내용들 ========
    font = boy.font         # 숫자용
    big_font = boy.ui_font  # 조금 더 크게 쓰고 싶으면
    skr_font = boy.skr_font
    kr_font = boy.kr_font

    level, rate, cost, atk_before, atk_after = _get_enchant_info()
    gold = getattr(boy, 'gold', 0)

    # 1) 맨 위 "무기 레벨" 박스 안: 현재 무기 레벨 + 강화 확률
    level_x = panel_left + int(w * 0.44)
    level_y = panel_bottom + int(h * 0.64)
    big_font.draw(level_x, level_y, f"Lv.{level}", (0, 220, 0))

    chance_x = level_x
    chance_y = panel_bottom + int(h * 0.25)
    font.draw(chance_x, chance_y, f" {int(rate * 100)}%", (255, 80, 80))

    # 2) 가운데 "강화 전 / 강화 후" 박스: 공격력 값
    before_x = panel_left + int(w * 0.33)
    after_x  = panel_left + int(w * 0.62)
    atk_y    = panel_bottom + int(h * 0.44)

    font.draw(before_x, atk_y, str(atk_before), (0, 0, 0))
    font.draw(after_x,  atk_y, str(atk_after),  (0, 0, 0))

    # 3) 소모 골드 / 현재 골드
    cost_y = panel_bottom + int(h * 0.59)
    skr_font.draw(panel_left + int(w * 0.3), cost_y,
              f"비용     {cost} G", (0, 0, 0))
    skr_font.draw(panel_left + int(w * 0.3), cost_y-20,
              f"보유 골드   {gold} G", (0, 0, 0))

    # 4) 맨 아래에 최근 결과 메시지 (성공/실패/골드부족)
    if last_enchant_msg and last_enchant_timer > 0:
        msg_font = boy.kr_font
        msg = last_enchant_msg

        msg_cx = panel_left + int(w * 0.3)
        msg_cy = panel_bottom + int(h * 0.5)

        if enchant_msg_img:
            bw = int(enchant_msg_img.w * 0.35)
            bh = int(enchant_msg_img.h * 0.3)
            enchant_msg_img.draw(msg_cx, msg_cy, bw, bh)
        else:
            # 이미지 없으면 임시 네모 박스
            bw = int(w * 0.5)
            bh = int(h * 0.12)
            bx0 = msg_cx - bw // 2
            by0 = msg_cy - bh // 2
            bx1 = msg_cx + bw // 2
            by1 = msg_cy + bh // 2
            draw_rectangle(bx0, by0, bx1, by1)

            # 글자 위치 (말풍선 안 중앙 조금 위)
        text_x = msg_cx - len(msg) * 1 # 길이에 따라 살짝 왼쪽으로
        text_y = msg_cy +10

        # 테두리용 검정 + 본문 노란 글씨
        msg_font.draw(text_x + 1, text_y - 1, msg, (0, 0, 0))
        msg_font.draw(text_x, text_y, msg, (500, 0, 0))

def _draw_menu_bounds():
    if not menu_open:
        return
    if not DRAW_MENU_BOUNDS:
        return
    if menu_rect_main is None:
        return

    # 전체 메뉴 영역
    draw_rectangle(*menu_rect_main)

    # X 버튼
    if menu_rect_close:
        draw_rectangle(*menu_rect_close)

    # 캐릭터 / 인벤 / 단축키 / 무기강화
    for rect in [menu_rect_char, menu_rect_inven, menu_rect_hotkey, menu_rect_weapon]:
        if rect:
            draw_rectangle(*rect)

    # 게임 종료 버튼
    if menu_rect_exit:
        draw_rectangle(*menu_rect_exit)

def _handle_subwindow_mouse(event):
    global ui_char_open, ui_inven_open, ui_hotkey_open, ui_weapon_open
    global char_x_rect, inven_x_rect, hotkey_x_rect, weapon_x_rect

    if event.type != SDL_MOUSEBUTTONDOWN or event.button != SDL_BUTTON_LEFT:
        return

    mx, my = _canvas_mouse_xy(event)

    # 캐릭터 정보창 X
    if ui_char_open and _in_rect(mx, my, char_x_rect):
        ui_char_open = False
        print("[UI] 캐릭터창 X 클릭 → 닫기")
        return

    # 인벤창 X
    if ui_inven_open and _in_rect(mx, my, inven_x_rect):
        ui_inven_open = False
        print("[UI] 인벤창 X 클릭 → 닫기")
        return

    # 단축키창 X
    if ui_hotkey_open and _in_rect(mx, my, hotkey_x_rect):
        ui_hotkey_open = False
        print("[UI] 단축키창 X 클릭 → 닫기")
        return

    # 무기강화창 X
    if ui_weapon_open and _in_rect(mx, my, weapon_x_rect):
        ui_weapon_open = False
        print("[UI] 무기강화창 X 클릭 → 닫기")
        return

def _get_potion_icon(kind):
    if kind not in potion_icons:
        path = ITEM_IMAGES.get(kind, None)
        if path:
            try:
                potion_icons[kind] = load_image(path)
            except:
                potion_icons[kind] = None
    return potion_icons.get(kind, None)

def _get_potion_icon(kind):

    if kind not in potion_icons:
        path = ITEM_IMAGES.get(kind, None)
        if path:
            try:
                potion_icons[kind] = load_image(path)
            except:
                potion_icons[kind] = None
    return potion_icons.get(kind, None)


def _draw_potion_bar():
    global potion_bar_img, potion_icon_imgs

    if potion_bar_img is None:
        return
    if boy is None:
        return

    cw, ch = get_canvas_width(), get_canvas_height()

    # 바 크기
    w = int(potion_bar_img.w * POTION_BAR_SCALE)
    h = int(potion_bar_img.h * POTION_BAR_SCALE)

    base_x = -30  # ← 좌우 위치
    base_y = -20  # ← 위아래 위치

    cx = base_x + w // 2
    cy = base_y + h // 2


    potion_bar_img.draw(cx, cy, w, h)

    # 바의 실제 왼쪽/아래 좌표
    panel_left = cx - w // 2
    panel_bottom = cy - h // 2

    # 슬롯 두 개 중심 위치 (이미지 비율로 잡음)
    slot1_cx = panel_left + int(w * 0.38)
    slot2_cx = panel_left + int(w * 0.65)
    slot_cy = panel_bottom + int(h * 0.49)

    # 포션 종류 (이 이름은 inventory / ITEM_IMAGES 키랑 맞춰야 함!)
    kinds = ['빨간포션', '파란포션']
    centers = [(slot1_cx, slot_cy), (slot2_cx, slot_cy)]

    icon_scale = 0.28
    font = boy.font  # 숫자용 폰트

    for i, kind in enumerate(kinds):
        cx_slot, cy_slot = centers[i]

        # 아이콘 로드/캐시
        img = potion_icon_imgs.get(kind)
        if img is None:
            path = ITEM_IMAGES.get(kind, None)
            if path:
                img = load_image(path)
                potion_icon_imgs[kind] = img

        iw = ih = 0
        if img:
            iw = int(img.w * icon_scale)
            ih = int(img.h * icon_scale)

            if kind == '파란포션':
                # 파란 포션만 좌우 반전해서 그림
                img.clip_composite_draw(
                    0, 0, img.w, img.h, 0, 'h',
                    int(cx_slot), int(cy_slot),
                    iw, ih)
            else:
                img.draw(int(cx_slot), int(cy_slot), iw, ih)

        # 인벤토리에서 개수 가져오기 (없으면 0)
        cnt = getattr(boy, 'inventory', {}).get(kind, 0)
        cnt_str = str(cnt)

        # 숫자 위치 (아이콘 오른쪽 아래 느낌)
        text_x = int(cx_slot + (iw * 0.25))
        text_y = int(cy_slot - (ih * 0.3))

        font.draw(text_x, text_y, cnt_str, (0, 0, 0))


def finish():
    game_world.clear()

def pause(): pass
def resume(): pass

