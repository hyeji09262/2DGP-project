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

    for layer in game_world.world:
        layer[:] = [o for o in layer if not isinstance(o, Mushroom)]
    monsters.clear()

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
    event_list = get_events()
    for event in event_list:
        if event.type == SDL_QUIT:
            game_framework.quit()
        elif event.type == SDL_KEYDOWN and event.key == SDLK_ESCAPE:
            game_framework.quit()
        else:
            boy.handle_event(event)

def init():
    load_map("henesys", "default")


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
        for o in list(layer):
            if isinstance(o, Mushroom) and getattr(o, 'dead', False):

                if random.random() < 0.7:  # 70% 확률로만 드랍, 30%는 그냥 안 줌
                    drop_x = o.x
                    drop_y = o.y + 20

                    kind = _choose_drop_kind()  # ← 여기서 확률로 10원/100원/1000원... 뽑힘
                    item = DropItem(drop_x, drop_y, field=field, kind=kind)
                    game_world.add_object(item, 1)
                    items.append(item)

                game_world.remove_object(o)


def draw():
    clear_canvas()
    game_world.render()
    _draw_portals_debug()

    if DRAW_HITBOX and field:
        # 캐릭터 박스
        l, b, r, t = boy.get_bb()
        sx0, sy0 = field.world_to_screen(l, b)
        sx1, sy1 = field.world_to_screen(r, t)
        draw_rectangle(sx0, sy0, sx1, sy1)  # 보통 빨간색으로 그려짐

        # 몬스터 박스
        for m in _gather_monsters():
            l, b, r, t = m.get_bb()
            sx0, sy0 = field.world_to_screen(l, b)
            sx1, sy1 = field.world_to_screen(r, t)
            draw_rectangle(sx0, sy0, sx1, sy1)

        for it in _gather_items():
            l, b, r, t = it.get_bb()
            sx0, sy0 = field.world_to_screen(l, b)
            sx1, sy1 = field.world_to_screen(r, t)
            draw_rectangle(sx0, sy0, sx1, sy1)

    update_canvas()


def finish():
    game_world.clear()

def pause(): pass
def resume(): pass

