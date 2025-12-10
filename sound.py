from pico2d import load_music, load_wav

# ==== 전역 ====
_bgm_dict = {}        # 맵/상황 이름 -> 배경음악 객체
_sfx_dict = {}        # 효과음 이름 -> 효과음 객체
_current_bgm = None
_initialized = False


def _safe_load_music(key, path, volume=64):
    global _bgm_dict
    try:
        m = load_music(path)
        m.set_volume(volume)
        _bgm_dict[key] = m
        print(f"[SOUND] BGM loaded: {key} <- {path}")
    except Exception as e:
        _bgm_dict[key] = None
        print(f"[SOUND] !!! FAIL to load BGM: {path} ({e})")


def _safe_load_sfx(key, path, volume=64):
    global _sfx_dict
    try:
        s = load_wav(path)
        s.set_volume(volume)
        _sfx_dict[key] = s
        print(f"[SOUND] SFX loaded: {key} <- {path}")
    except Exception as e:
        _sfx_dict[key] = None
        print(f"[SOUND] !!! FAIL to load SFX: {path} ({e})")


def init():
    """게임 시작 시 한 번만 불리면 됨."""
    global _initialized
    if _initialized:
        return
    _initialized = True

    # ==== BGM 로드 ====
    _safe_load_music('henesys', 'sound/헤네시스.mp3', 60)
    _safe_load_music('map2',    'sound/헤네필드.mp3', 60)
    _safe_load_music('map3',    'sound/헤네필드.mp3', 60)
    _safe_load_music('title',   'sound/타이틀.mp3',  60)

    # ==== 효과음 로드 ====
    _safe_load_sfx('attack',      'sound/타격.wav',   80)
    _safe_load_sfx('hit',         'sound/피격.mp3',   80)
    _safe_load_sfx('die',         'sound/죽음.mp3',   80)
    _safe_load_sfx('monster_die', 'sound/죽음.mp3',   80)
    _safe_load_sfx('levelup',     'sound/레벨업.mp3', 80)
    _safe_load_sfx('portal',      'sound/포탈.mp3',   80)
    _safe_load_sfx('ui_click',    'sound/클릭.wav',   60)
    _safe_load_sfx('quest',       'sound/보상.wav',   60)
    _safe_load_sfx('jump',        'sound/점프.mp3', 60)
    _safe_load_sfx('pickup', 'sound/줍기.mp3', 60)



def play_bgm(name, repeat=True):
    """키 이름으로 배경음 재생."""
    global _current_bgm

    # 혹시라도 init() 안 불렀으면 여기서 한 번 호출
    if not _initialized:
        init()

    m = _bgm_dict.get(name, None)
    if m is None:
        print(f"[SOUND] No BGM for '{name}' (not loaded)")
        return

    # 이전 BGM 끄기
    if _current_bgm and _current_bgm is not m:
        try:
            _current_bgm.stop()
        except Exception:
            pass

    _current_bgm = m
    try:
        if repeat:
            m.repeat_play()
        else:
            m.play()
        print(f"[SOUND] play BGM: {name}")
    except Exception as e:
        print(f"[SOUND] !!! FAIL to play BGM '{name}': {e}")


def stop_bgm():
    global _current_bgm
    if _current_bgm:
        try:
            _current_bgm.stop()
        except Exception:
            pass
        _current_bgm = None
        print("[SOUND] stop BGM")


def play_sfx(name):
    s = _sfx_dict.get(name, None)
    if s is None:
        print(f"[SOUND] No SFX for '{name}'")
        return
    try:
        s.play()
    except Exception as e:
        print(f"[SOUND] !!! FAIL to play SFX '{name}': {e}")


# ==== 자주 쓸 것들 편의 함수 ====

def play_attack():      play_sfx('attack')
def play_hit():         play_sfx('hit')
def play_die():         play_sfx('die')
def play_monster_die(): play_sfx('monster_die')
def play_levelup():     play_sfx('levelup')
def play_portal():      play_sfx('portal')
def play_ui_click():    play_sfx('ui_click')
def play_quest():       play_sfx('quest')
def play_jump():        play_sfx('jump')
def play_pickup():      play_sfx('pickup')
