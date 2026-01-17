import pygame
import random
import string
import sys
import os

pygame.init()

# 화면 설정
# 화면 설정 (전체 화면 및 스케일링)
# 화면 설정 (전체 화면 및 스케일링)
WIDTH, HEIGHT = 800, 600

# 해상도 목록 정의
RESOLUTIONS = [
    (800, 600),
    (1024, 768),
    (1280, 720),
    (1920, 1080),
    "Fullscreen"
]
current_res_idx = 0 # 기본값을 800x600으로 설정

real_screen = None
screen_width = 0
screen_height = 0
scale_factor = 1
scaled_width = WIDTH
scaled_height = HEIGHT
offset_x = 0
offset_y = 0

def set_display_mode(idx):
    global real_screen, screen_width, screen_height, scale_factor, scaled_width, scaled_height, offset_x, offset_y, current_res_idx
    
    current_res_idx = idx
    mode = RESOLUTIONS[current_res_idx]
    
    if mode == "Fullscreen":
        real_screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
        info = pygame.display.Info()
        screen_width, screen_height = info.current_w, info.current_h
    else:
        screen_width, screen_height = mode
        os.environ['SDL_VIDEO_CENTERED'] = '1'
        real_screen = pygame.display.set_mode((screen_width, screen_height))
        
    scale_factor = min(screen_width / WIDTH, screen_height / HEIGHT)
    scaled_width = int(WIDTH * scale_factor)
    scaled_height = int(HEIGHT * scale_factor)
    offset_x = (screen_width - scaled_width) // 2
    offset_y = (screen_height - scaled_height) // 2

# 초기 화면 설정
set_display_mode(current_res_idx)

screen = pygame.Surface((WIDTH, HEIGHT)) # 게임 로직용 가상 스크린
pygame.display.set_caption("RPG")
clock = pygame.time.Clock()

# 폰트
font = pygame.font.Font("PF스타더스트.ttf", 24)
font_small = pygame.font.Font("PF스타더스트.ttf", 18)

# 색상
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
BLUE = (0, 150, 255)
GREEN = (0, 255, 100)
RED = (255, 60, 60)
YELLOW = (255, 255, 0)
GREY = (70, 70, 70)

BG_NAME = BLACK
BG_TOWN = (139, 69, 19)
BG_FOREST = (50, 140, 60)
BG_BATTLE = (20, 20, 20)
BG_LEVELUP = (40, 40, 80)
BG_SELECT = (20, 20, 40)

# 희귀도 색상
COLOR_COMMON = (240, 240, 240)
COLOR_UNCOMMON = (100, 255, 100)
COLOR_RARE = (100, 180, 255)
COLOR_UNIQUE = (220, 100, 255)
COLOR_LEGENDARY = (255, 220, 0)
COLOR_MYTHIC = (255, 50, 50)

# 크리티컬 스크립트
CRIT_SCRIPTS = [
    "치명적인 피해를 입혔습니다!",
    "효과가 굉장했습니다!",
    "급소에 맞았습니다!"
]

RARITY_COLORS = {
    "커먼": COLOR_COMMON,
    "언커먼": COLOR_UNCOMMON,
    "레어": COLOR_RARE
}

def get_rarity_color(rarity_name):
    return RARITY_COLORS.get(rarity_name, WHITE)

# 맵 데이터
MAP_DATA = [
    {"name": "초심자의 숲", "min_lv": 1, "color": BG_FOREST},
    {"name": "험준한 산맥", "min_lv": 10, "color": (101, 67, 33)},
    {"name": "메마른 사막", "min_lv": 20, "color": (210, 180, 140)},
    {"name": "혹한의 설원", "min_lv": 30, "color": (200, 240, 255)},
    {"name": "심연의 동굴", "min_lv": 40, "color": (50, 0, 50)},
    {"name": "바람의 평원", "min_lv": 50, "color": (100, 200, 100)},
    {"name": "황혼의 유적", "min_lv": 60, "color": (100, 100, 80)},
]

# 몬스터 데이터 베이스 (map_idx: 등장 맵 인덱스)
MONSTER_DB = {
    # 0: 숲
    "slime": {"name": "슬라임", "hp": 20, "atk": 10, "def": 5, "agi": 5, "crit": 0, "exp": 10, "pos": (100, 100), "map_idx": 0, "loot_price": 20, "loot_item": "슬라임 방울", "rare_loot": "농축된 액체", "rare_price": 100},
    "sprout": {"name": "새싹", "hp": 15, "atk": 5, "def": 2, "agi": 10, "crit": 0, "exp": 5, "pos": (200, 200), "map_idx": 0, "loot_price": 10, "loot_item": "푸른 잎사귀", "rare_loot": "세계수의 가지", "rare_price": 80},
    "mushroom": {"name": "버섯", "hp": 25, "atk": 12, "def": 8, "agi": 3, "crit": 5, "exp": 15, "pos": (300, 300), "map_idx": 0, "loot_price": 30, "loot_item": "버섯 포자", "rare_loot": "환각 가루", "rare_price": 120},
    
    # 1: 산맥
    "wolf": {"name": "늑대", "hp": 50, "atk": 25, "def": 10, "agi": 15, "crit": 10, "exp": 30, "pos": (200, 200), "map_idx": 1, "loot_price": 60, "loot_item": "늑대 가죽", "rare_loot": "빛나는 송곳니", "rare_price": 300},
    "bear": {"name": "곰", "hp": 80, "atk": 30, "def": 20, "agi": 5, "crit": 5, "exp": 50, "pos": (400, 200), "map_idx": 1, "loot_price": 100, "loot_item": "곰의 발바닥", "rare_loot": "웅담", "rare_price": 500},
    "eagle": {"name": "독수리", "hp": 40, "atk": 35, "def": 5, "agi": 25, "crit": 15, "exp": 40, "pos": (100, 100), "map_idx": 1, "loot_price": 80, "loot_item": "날카로운 깃털", "rare_loot": "질풍의 깃", "rare_price": 400},
    
    # 2: 사막
    "snake": {"name": "독사", "hp": 40, "atk": 20, "def": 5, "agi": 20, "crit": 15, "exp": 25, "pos": (150, 150), "map_idx": 2, "loot_price": 50, "loot_item": "뱀의 허물", "rare_loot": "맹독 주머니", "rare_price": 250},
    "scorpion": {"name": "전갈", "hp": 60, "atk": 25, "def": 25, "agi": 10, "crit": 20, "exp": 45, "pos": (300, 300), "map_idx": 2, "loot_price": 90, "loot_item": "전갈의 독침", "rare_loot": "단단한 껍질", "rare_price": 450},
    "cactus": {"name": "선인장", "hp": 100, "atk": 15, "def": 10, "agi": 5, "crit": 0, "exp": 35, "pos": (500, 200), "map_idx": 2, "loot_price": 70, "loot_item": "선인장 가시", "rare_loot": "사막의 오아시스", "rare_price": 350},

    # 3: 설원
    "yeti": {"name": "예티", "hp": 150, "atk": 35, "def": 20, "agi": 10, "crit": 5, "exp": 80, "pos": (300, 300), "map_idx": 3, "loot_price": 160, "loot_item": "예티의 털뭉치", "rare_loot": "예티의 심장", "rare_price": 800},
    "ice_wolf": {"name": "설원늑대", "hp": 120, "atk": 30, "def": 15, "agi": 20, "crit": 15, "exp": 70, "pos": (200, 400), "map_idx": 3, "loot_price": 140, "loot_item": "얼어붙은 어금니", "rare_loot": "만년빙", "rare_price": 700},
    "snowman": {"name": "눈사람", "hp": 200, "atk": 20, "def": 30, "agi": 5, "crit": 0, "exp": 60, "pos": (400, 100), "map_idx": 3, "loot_price": 120, "loot_item": "단단한 눈사탕", "rare_loot": "수정 눈코", "rare_price": 600},

    # 4: 동굴
    "skeleton": {"name": "스켈레톤", "hp": 80, "atk": 35, "def": 5, "agi": 12, "crit": 10, "exp": 45, "pos": (200, 400), "map_idx": 4, "loot_price": 100, "loot_item": "오래된 유골", "rare_loot": "저주받은 뼛가루", "rare_price": 500},
    "bat": {"name": "박쥐", "hp": 50, "atk": 25, "def": 0, "agi": 30, "crit": 20, "exp": 30, "pos": (100, 100), "map_idx": 4, "loot_price": 60, "loot_item": "박쥐의 날개뼈", "rare_loot": "흡혈 어금니", "rare_price": 300},
    "spider": {"name": "거대거미", "hp": 100, "atk": 30, "def": 10, "agi": 15, "crit": 15, "exp": 55, "pos": (300, 200), "map_idx": 4, "loot_price": 120, "loot_item": "끈적한 거미줄", "rare_loot": "거미의 눈", "rare_price": 600},

    # 5: 평원
    "orc": {"name": "오크", "hp": 140, "atk": 45, "def": 25, "agi": 12, "crit": 5, "exp": 80, "map_idx": 5, "loot_price": 110, "loot_item": "오크의 부적"},
    "goblin": {"name": "고블린", "hp": 100, "atk": 35, "def": 15, "agi": 25, "crit": 10, "exp": 70, "map_idx": 5, "loot_price": 80, "loot_item": "고블린 금화"},
    "boar": {"name": "멧돼지", "hp": 180, "atk": 50, "def": 30, "agi": 15, "crit": 5, "exp": 100, "map_idx": 5, "loot_price": 130, "loot_item": "멧돼지 상아"},

    # 6: 유적
    "golem": {"name": "골렘", "hp": 300, "atk": 60, "def": 80, "agi": 2, "crit": 0, "exp": 250, "map_idx": 6, "loot_price": 250, "loot_item": "고대 석판 조각"},
    "gargoyle": {"name": "가고일", "hp": 250, "atk": 70, "def": 50, "agi": 20, "crit": 15, "exp": 300, "map_idx": 6, "loot_price": 300, "loot_item": "석조 날개 파편"},
    "mimic": {"name": "미믹", "hp": 400, "atk": 80, "def": 40, "agi": 25, "crit": 25, "exp": 500, "map_idx": 6, "loot_price": 500, "loot_item": "순금 보물 상자"},
}

# 직업 및 동료 이름
JOBS = ["전사", "도적", "마법사", "사수"]
# 용병 데이터 및 대열 정보
owned_companions = [] # 소환한 모든 동료 {name, power_lv, ...}
player_party = []     # 현재 전투 참여 중인 동료
gacha_list = []       # 현재 소환 결과 목록
gacha_view_idx = 0    # 소환 결과 보기 인덱스

COMPANION_DB = {
    # N 등급 (스탯이 낮고 스킬 없음)
    "마을 병사": {"rarity": "N", "role": "탱커", "atk_rate": 0.1, "hp_rate": 0.8, "desc": "튼튼한 몸 하나는 자신 있는 병사입니다.", "skills": []},
    "수습 수도사": {"rarity": "N", "role": "힐러", "atk_rate": 0.02, "hp_rate": 0.2, "desc": "약초 지식만 조금 있는 수습생입니다.", "skills": []},
    "연습생": {"rarity": "N", "role": "버퍼", "atk_rate": 0.05, "hp_rate": 0.25, "desc": "옆에서 박수로 응원을 보냅니다.", "skills": []},
    "떠돌이 검사": {"rarity": "N", "role": "딜러", "atk_rate": 0.15, "hp_rate": 0.4, "desc": "실력은 없지만 의욕은 넘칩니다.", "skills": []},
    
    # R 등급 (안정적인 역할 수행)
    "루카": {"rarity": "R", "role": "탱커", "atk_rate": 0.15, "hp_rate": 0.9, "desc": "용병단 출신의 단단한 방패잡이입니다.", "skills": ["도발 함성"]},
    "리사": {"rarity": "R", "role": "힐러", "atk_rate": 0.05, "hp_rate": 0.25, "desc": "치유의 기도로 큰 부상을 막아줍니다.", "skills": ["그레이터 힐"]},
    "카이": {"rarity": "R", "role": "디버퍼", "atk_rate": 0.2, "hp_rate": 0.35, "desc": "함정을 설치해 적을 위협합니다.", "skills": ["발목 걸기"]},
    
    # SR 등급 (강력한 유틸리티)
    "아서": {"rarity": "SR", "role": "성기사", "atk_rate": 0.25, "hp_rate": 1.0, "desc": "주인공만큼 튼튼한 성스러운 기사입니다.", "skills": ["신의 도발", "홀리 라이트"]},
    "셀레나": {"rarity": "SR", "role": "버퍼", "atk_rate": 0.3, "hp_rate": 0.35, "desc": "정령의 힘으로 주인공의 한계를 높입니다.", "skills": ["질풍의 가속", "정령의 분노"]},
    "에스텔": {"rarity": "SR", "role": "성녀", "atk_rate": 0.1, "hp_rate": 0.3, "desc": "기적을 일으켜 보호를 제공합니다.", "skills": ["마나 링크", "천상의 축복"]},
    
    # SSR 등급 (전략적 핵심 지원)
    "레오": {"rarity": "SSR", "role": "검성", "atk_rate": 0.5, "hp_rate": 0.5, "desc": "가장 강력한 지원 공격을 퍼붓습니다.", "skills": ["심검 사참", "투기 방출", "방어해체"]},
    "메이": {"rarity": "SSR", "role": "대마법사", "atk_rate": 0.45, "hp_rate": 0.45, "desc": "전설적인 대규모 보조 지술을 펼칩니다.", "skills": ["시공의 왜곡", "마력 증폭", "절대영도"]},
    "크로우": {"rarity": "SSR", "role": "암살자", "atk_rate": 0.55, "hp_rate": 0.4, "desc": "치명적인 습격으로 전황을 바꿉니다.", "skills": ["그림자 습격", "연막탄", "독니"]},
    "미다스": {"rarity": "SSR", "role": "연금술사", "atk_rate": 0.2, "hp_rate": 0.45, "desc": "금전술과 연금술의 달인입니다.", "skills": ["황금 강탈", "미지의 물약", "연금술적 지원"]},
}
GACHA_COST_1 = 5000
GACHA_COST_11 = 50000

# 퀘스트 처치 카운트
monster_kills = {"goblin": 0, "orc": 0, "king_slime": 0}

# 보서 데이터 베이스
BOSS_DB = {
    0: {"name": "킹 슬라임", "hp": 500, "atk": 25, "def": 15, "agi": 10, "exp": 200, "patterns": ["점프 프레스", "자가 회복"]},
    1: {"name": "고대 설괴", "hp": 1200, "atk": 45, "def": 30, "agi": 15, "exp": 600, "patterns": ["눈보라", "얼음 방벽"]},
    2: {"name": "데저트 드래곤", "hp": 2500, "atk": 70, "def": 45, "agi": 25, "exp": 1500, "patterns": ["화염 숨결", "모래 폭풍"]},
    3: {"name": "맹독 히드라", "hp": 4000, "atk": 90, "def": 50, "agi": 30, "exp": 2500, "patterns": ["맹독 브레스", "트리플 바이트"]},
    4: {"name": "심해의 크라켄", "hp": 6000, "atk": 110, "def": 70, "agi": 20, "exp": 3500, "patterns": ["먹물 발사", "촉수 휩쓸기"]},
    5: {"name": "지옥의 켈베로스", "hp": 10000, "atk": 160, "def": 40, "agi": 50, "exp": 6000, "patterns": ["삼연격 지옥화염", "광폭화"]},
    6: {"name": "심연의 수호자", "hp": 15000, "atk": 200, "def": 120, "agi": 40, "exp": 10000, "patterns": ["어둠의 고리", "멸망의 주문"]},
}

# 게임 상태
STATE_NAME = "name"
STATE_TOWN = "town"
STATE_DIALOG = "dialog"
STATE_SELECT_MAP = "select_map"
STATE_FIELD = "field" # 기존 forest 대체
STATE_BATTLE = "battle"
STATE_LEVELUP = "levelup"
STATE_STATS = "stats"
STATE_JOB_SELECT = "job_select"
STATE_STORE = "store"
STATE_SETTINGS = "settings"
STATE_BLACKSMITH = "blacksmith"
STATE_RECRUIT = "recruit"
STATE_PARTY = "party"

state = STATE_NAME
dialog_page = 0
quest_text = ""
player_name = ""

# 키 설정 (Global Variables)
KEY_UP = pygame.K_UP
KEY_DOWN = pygame.K_DOWN
KEY_LEFT = pygame.K_LEFT
KEY_RIGHT = pygame.K_RIGHT
KEY_ACTION_1 = pygame.K_z # 확인/공격/상호작용
KEY_ACTION_2 = pygame.K_x # 취소/스킬
KEY_ACTION_3 = pygame.K_c # 메뉴/아이템
KEY_ACTION_4 = pygame.K_v # 도망
KEY_TAB_L = pygame.K_q # 탭 왼쪽
KEY_TAB_R = pygame.K_w # 탭 오른쪽
KEY_MENU_OPEN = pygame.K_c # 스탠창
KEY_ESC = pygame.K_ESCAPE # 설정 메뉴

player_speed = 4
current_map_index = 0
select_map_index = 0

# 상점 및 인벤토리
player_gold = 0
player_inventory = [] # {"name": "...", "type": "...", "stat": ...}
player_equipment = {"weapon": None, "armor": None, "accessory": None}
player_party = [] # 동료 목록
skill_levels = {} # 각 스킬의 레벨 (기본 1)
skill_points = 0  # 스킬 강화를 위한 포인트

ITEM_DB = {
    # 소모품 (Potions)
    "red_potion": {"name": "빨간 포션", "type": "potion", "rarity": "커먼", "effect": "hp", "value": 50, "price": 50, "desc": "체력 50 회복", "min_lv": 1},
    "blue_potion": {"name": "파란 포션", "type": "potion", "rarity": "커먼", "effect": "mana", "value": 30, "price": 50, "desc": "마나 30 회복", "min_lv": 1},
    "elixir": {"name": "엘릭서", "type": "potion", "rarity": "레어", "effect": "hp_mana", "value": 500, "price": 1000, "desc": "HP/MP 500 회복", "min_lv": 40},

    # --- 전사 무기 ---
    "rusty_greatsword": {"name": "녹슨 대검", "type": "weapon", "rarity": "커먼", "atk": 8, "price": 100, "desc": "전사 전용. 무겁다. 공격 +8", "min_lv": 1, "job": "전사"},
    "steel_longsword": {"name": "강철 롱소드", "type": "weapon", "rarity": "언커먼", "atk": 22, "price": 800, "desc": "전사 전용. 단단하다. 공격 +22", "min_lv": 12, "job": "전사"},
    "knights_blade": {"name": "기사의 검", "type": "weapon", "rarity": "레어", "atk": 45, "price": 5000, "desc": "전사 전용. 명예로운 검. 공격 +45", "min_lv": 30, "job": "전사"},

    # --- 도적 무기 ---
    "rusty_dagger": {"name": "녹슨 단검", "type": "weapon", "rarity": "커먼", "atk": 6, "price": 50, "desc": "도적 전용. 매우 낡았다. 공격 +6", "min_lv": 1, "job": "도적"},
    "sharp_dagger": {"name": "날카로운 단검", "type": "weapon", "rarity": "언커먼", "atk": 18, "price": 600, "desc": "도적 전용. 날카롭다. 공격 +18", "min_lv": 10, "job": "도적"},
    "assassins_shiv": {"name": "암살자의 비수", "type": "weapon", "rarity": "레어", "atk": 38, "crit": 12, "price": 4500, "desc": "도적 전용. 암살에 적합. 공격 +38, 크리 +12", "min_lv": 28, "job": "도적"},

    # --- 마법사 무기 ---
    "cracked_staff": {"name": "금이 간 지팡이", "type": "weapon", "rarity": "커먼", "atk": 10, "mana": 30, "price": 120, "desc": "마법사 전용. 약한 마력. 공격 +10, 마나 +30", "min_lv": 1, "job": "마법사"},
    "oak_wand": {"name": "오크 나무 완드", "type": "weapon", "rarity": "언커먼", "atk": 28, "mana": 80, "price": 900, "desc": "마법사 전용. 집중이 잘 된다. 공격 +28, 마나 +80", "min_lv": 15, "job": "마법사"},
    "archmages_staff": {"name": "대마도사의 지팡이", "type": "weapon", "rarity": "레어", "atk": 55, "mana": 250, "price": 6000, "desc": "마법사 전용. 강력한 마력. 공격 +55, 마나 +250", "min_lv": 35, "job": "마법사"},

    # --- 사수 무기 ---
    "practice_bow": {"name": "연습용 활", "type": "weapon", "rarity": "커먼", "atk": 7, "price": 90, "desc": "사수 전용. 연습용이다. 공격 +7", "min_lv": 1, "job": "사수"},
    "composite_bow": {"name": "컴포짓 보우", "type": "weapon", "rarity": "언커먼", "atk": 20, "price": 750, "desc": "사수 전용. 사거리가 길다. 공격 +20", "min_lv": 12, "job": "사수"},
    "hunters_longbow": {"name": "사냥꾼의 롱보우", "type": "weapon", "rarity": "레어", "atk": 42, "crit": 8, "price": 5500, "desc": "사수 전용. 정교한 활. 공격 +42, 크리 +8", "min_lv": 32, "job": "사수"},

    # --- 공용 무기 ---
    "common_club": {"name": "공용 몽둥이", "type": "weapon", "rarity": "커먼", "atk": 6, "price": 80, "desc": "누구나 사용 가능. 투박하다. 공격 +6", "min_lv": 1},
    "iron_mace": {"name": "철제 메이스", "type": "weapon", "rarity": "언커먼", "atk": 18, "price": 700, "desc": "누구나 사용 가능. 묵직하다. 공격 +18", "min_lv": 10},
    "heros_blade": {"name": "영웅의 검", "type": "weapon", "rarity": "레어", "atk": 36, "crit": 6, "price": 5200, "desc": "누구나 사용 가능. 빛이 난다. 공격 +36, 크리 +6", "min_lv": 25},

    # --- 방어구 ---
    "old_vest": {"name": "낡은 조끼", "type": "armor", "rarity": "커먼", "def": 1, "price": 40, "desc": "낡았다. 방어 +1", "min_lv": 1},
    "leather_armor": {"name": "가죽 갑옷", "type": "armor", "rarity": "커먼", "def": 3, "hp": 20, "price": 300, "desc": "기본 갑옷. 방어 +3, HP +20", "min_lv": 1},
    "reinforced_leather": {"name": "강화 가죽 조끼", "type": "armor", "rarity": "언커먼", "def": 6, "hp": 40, "price": 800, "desc": "강화되었다. 방어 +6, HP +40", "min_lv": 10},
    "silver_chestplate": {"name": "은색 판금 조끼", "type": "armor", "rarity": "레어", "def": 20, "hp": 150, "price": 6000, "desc": "단단하다. 방어 +20, HP +150", "min_lv": 25},
    
    # 재료 아이템
    "slime_bubble": {"name": "슬라임 방울", "type": "misc", "rarity": "커먼", "price": 20, "desc": "끈적이는 슬라임의 잔해."},

    # 퀘스트용
    "wooden_sword": {"name": "목검", "type": "weapon", "rarity": "커먼", "atk": 5, "price": 200, "desc": "누구나 사용 가능. 기본 무기. 공격 +5", "min_lv": 1, "upgrade_material": "슬라임 방울"},
}


# 플레이어
player_size = 40
player_start_pos = (400, 520) # 남쪽 도로 입구
player_town_pos = (400, 520)
player_field_pos = (600, HEIGHT - 80)
player = pygame.Rect(player_start_pos[0], player_start_pos[1], player_size, player_size)
player_level = 1
player_exp = 0
player_move_timer = 0
PLAYER_MOVE_INTERVAL = 150 # 그리드 이동 딜레이
player_speed = player_size # 한 칸씩 이동

STAT_CONFIG = {
    "hp": {"label": "체력", "base": 100, "max": 1000, "increment": 10},
    "atk": {"label": "공격력", "base": 10, "max": 100, "increment": 1},
    "def": {"label": "방어력", "base": 10, "max": 100, "increment": 1},
    "mana": {"label": "마나", "base": 100, "max": 1000, "increment": 10},
    "agi": {"label": "민첩", "base": 10, "max": 100, "increment": 1},
    "crit": {"label": "크리티컬", "base": 10, "max": 100, "increment": 1},
}

STAT_ORDER = ["hp", "atk", "def", "mana", "agi", "crit"]

# 직업 데이터
# 직업 데이터 (이름 한글화, 감소 스탯 반영된 베이스)
# 레벨업 시 자동 상승 없음 (growth 삭제), 스탯 포인트만 지급
JOB_DB = {
    "초보자": {
        "base": {"hp": 100, "atk": 10, "def": 10, "mana": 50, "agi": 10, "crit": 10},
        "skills": ["강한 공격"]
    },
    "전사": {
        "base": {"hp": 300, "atk": 26, "def": 30, "mana": 100, "agi": 5, "crit": 5},
        "skills": ["파워 스트라이크", "배쉬", "아이언 바디", "가드 브레이크", "휠윈드", "워 크라이"]
    },
    "도적": {
        "base": {"hp": 150, "atk": 28, "def": 15, "mana": 150, "agi": 30, "crit": 32},
        "skills": ["기습", "더블 어택", "헤이스트", "다크 사이트", "독 바르기", "암살"]
    },
    "마법사": {
        "base": {"hp": 120, "atk": 32, "def": 5, "mana": 300, "agi": 10, "crit": 15},
        "skills": ["파이어볼", "에너지 볼트", "매직 실드", "콜드 빔", "블리자드", "메테오"]
    },
    "사수": {
        "base": {"hp": 180, "atk": 28, "def": 15, "mana": 200, "agi": 25, "crit": 22},
        "skills": ["애로우 블로우", "더블 샷", "크리티컬 샷", "포커스", "에로우 샤워", "스나이핑"]
    }

}

SKILLS = {
    "강한 공격": {"mana": 10, "dmg_rate": 1.2, "name": "강한 공격"},
    "배쉬": {"mana": 25, "dmg_rate": 1.3, "name": "배쉬", "stun_chance": 0.2},
    "파워 스트라이크": {"mana": 20, "dmg_rate": 1.5, "name": "파워 스트라이크"},
    "더블 어택": {"mana": 25, "dmg_rate": 0.8, "name": "더블 어택", "hits": 2}, 
    "파이어볼": {"mana": 40, "dmg_rate": 2.5, "name": "파이어볼"},
    "애로우 블로우": {"mana": 30, "dmg_rate": 1.7, "name": "애로우 블로우"},
    "기습": {"mana": 25, "dmg_rate": 1.3, "crit_bonus": 20, "name": "기습"},
    "에너지 볼트": {"mana": 20, "dmg_rate": 1.8, "name": "에너지 볼트"},
    "더블 샷": {"mana": 25, "dmg_rate": 1.6, "name": "더블 샷"},
    # 전사 스킬
    "아이언 바디": {"mana": 30, "dmg_rate": 0, "name": "아이언 바디", "desc": "방어력 일시 대폭 상승"},
    "가드 브레이크": {"mana": 35, "dmg_rate": 2.0, "name": "가드 브레이크", "desc": "적의 방어를 무시하고 타격"},
    "휠윈드": {"mana": 50, "dmg_rate": 2.4, "name": "휠윈드", "desc": "무기를 크게 휘둘러 타격"},
    "워 크라이": {"mana": 40, "dmg_rate": 0, "name": "워 크라이", "desc": "공격력 일시 상승"},
    # 도적 스킬
    "헤이스트": {"mana": 40, "dmg_rate": 0, "name": "헤이스트", "desc": "민첩 대폭 상승"},
    "다크 사이트": {"mana": 50, "dmg_rate": 2.8, "name": "다크 사이트", "desc": "은신 후 기습 타격"},
    "독 바르기": {"mana": 30, "dmg_rate": 1.5, "name": "독 바르기", "desc": "중독 데미지 추가"},
    "암살": {"mana": 60, "dmg_rate": 3.8, "name": "암살", "crit_bonus": 50},
    # 마법사 스킬
    "매직 실드": {"mana": 45, "dmg_rate": 0, "name": "매직 실드", "desc": "마나로 피해 흡수"},
    "콜드 빔": {"mana": 35, "dmg_rate": 1.8, "name": "콜드 빔", "desc": "적을 얼려 속도 저하"},
    "블리자드": {"mana": 70, "dmg_rate": 3.2, "name": "블리자드", "desc": "강력한 얼음 마법"},
    "메테오": {"mana": 120, "dmg_rate": 6.5, "name": "메테오", "desc": "궁극의 화염 마법"},
    # 사수 스킬
    "크리티컬 샷": {"mana": 30, "dmg_rate": 1.5, "crit_bonus": 55, "name": "크리티컬 샷"},
    "포커스": {"mana": 25, "dmg_rate": 0, "name": "포커스", "desc": "명중률 및 공격력 상승"},
    "에로우 샤워": {"mana": 55, "dmg_rate": 2.5, "name": "에로우 샤워", "desc": "화살 비를 퍼부음"},
}
# 동료 전용 스킬 데이터베이스
COMPANION_SKILL_DB = {
    # 탱커 스킬
    "도발 함성": {"desc": "적의 공격을 자신에게 집중시킵니다.", "type": "taunt", "power": 0},
    "철벽 방어": {"desc": "플레이어의 방어력을 대폭 높입니다.", "type": "buff", "target": "def", "power": 2},
    "신의 도발": {"desc": "신성한 권능으로 모든 공격을 받아냅니다.", "type": "taunt", "power": 0},
    
    # 힐러/성녀 스킬
    "그레이터 힐": {"desc": "플레이어의 HP를 50 회복합니다.", "type": "heal", "power": 50},
    "홀리 라이트": {"desc": "플레이어의 HP를 100 회복합니다.", "type": "heal", "power": 100},
    "마나 링크": {"desc": "플레이어의 마나를 50 회복합니다.", "type": "mana", "power": 50},
    "정화의 빛": {"desc": "HP/MP 풀회복 및 모든 상태이상 해제", "type": "special_full_heal", "power": 0},
    "천상의 축복": {"desc": "플레이어의 공/방을 2배로 높입니다.", "type": "buff_all", "power": 2},
    
    # 버퍼 스킬
    "질풍의 가속": {"desc": "플레이어의 민첩성을 높입니다.", "type": "buff", "target": "agi", "power": 3},
    "정령의 분노": {"desc": "플레이어의 크리티컬 확률을 높입니다.", "type": "buff", "target": "crit", "power": 50},
    "마력 증폭": {"desc": "플레이어의 다음 마법 공격력을 증폭합니다.", "type": "buff", "target": "atk", "power": 2},
    
    # 디버퍼 스킬
    "발목 걸기": {"desc": "적을 둔화시킵니다.", "type": "debuff", "target": "slow", "power": 3},
    "한기 전달": {"desc": "적을 2턴간 기절시킵니다.", "type": "debuff", "target": "stun", "power": 2},
    "절대영도": {"desc": "적을 영구적으로 약화시킵니다.", "type": "debuff", "target": "weak", "power": 0},
    
    # 딜러/특종 스킬
    "심검 사참": {"desc": "방어력을 무시하는 치명적인 일격", "type": "damage", "power": 2.5},
    "방어해체": {"desc": "적의 방어력을 영구적으로 깎습니다.", "type": "debuff", "target": "def_down", "power": 20},
    "그림자 습격": {"desc": "체력이 낮은 적을 즉사시킵니다.", "type": "execute", "power": 0.15},
    "연막탄": {"desc": "일시적으로 플레이어의 회피를 극대화합니다.", "type": "buff", "target": "def", "power": 5},
    "황금 강탈": {"desc": "적에게서 골드를 훔쳐옵니다.", "type": "gold", "power": 0},
    "미지의 물약": {"desc": "무작위 능력치를 극대화합니다.", "type": "buff", "target": "atk", "power": 3},
    "시공의 왜곡": {"desc": "시간을 멈춰 적을 마비시킵니다.", "type": "debuff", "target": "stun", "power": 2},
}

# 보서 데이터 베이스

player_job = "초보자"
player_stats = {key: JOB_DB[player_job]["base"][key] for key in STAT_ORDER}


player_max_hp = player_stats["hp"]
player_hp = player_max_hp
player_max_mana = player_stats["mana"]
player_mana = player_max_mana
player_stat_points = 0
levelup_selected_stat = 0
levelup_allocations = {stat: 0 for stat in STAT_ORDER}
stat_menu_points = 0
state_before_stats = STATE_TOWN

# NPC (40 단위 좌표 - 동선 방해 최소화)
# NPC 위치 재배치 (도로 구역 피해서 배치)
# 가로 도로: Y 240~360, 세로 도로: X 340~460
npc = pygame.Rect(120, 120, 40, 40) # 촌장 (좌상단 구역)
npc_job = pygame.Rect(640, 120, 40, 40) # 전직관 (우상단 구역)
npc_store = pygame.Rect(120, 480, 40, 40) # 상점 (좌하단 구역)
npc_blacksmith = pygame.Rect(640, 480, 40, 40) # 대장장이 (우하단 구역)
npc_recruit = pygame.Rect(520, 480, 40, 40) # 용병단장 (우하단 구역)
npc_guard = pygame.Rect(280, 80, 40, 40)  # 경비병 (북쪽 입구 근처)

# 퀘스트 및 대화
quest_step = 0  # 0:시작전, 1:퀘스트수락, 2:목표달성, 3:완료
current_dialog = []

dialog_map = {
    0: [
        "반갑네, {name}.",
        "숲 속에 슬라임이 나타났다네.",
        "가서 슬라임과 싸워주게!"
    ],
    1: [
        "아직 슬라임을 처치하지 못했나?",
        "숲은 마을 북쪽에 있다네."
    ],
    2: [
        "오오, 무사히 돌아왔군!",
        "슬라임을 처치하다니 대단해.",
        "이제 자네도 어엿한 모험가야.",
        "레벨업을 했다면 C키를 눌러 스탯을 올려보게.",
        "이제 더 넓은 세상으로 나갈 준비가 된 것 같구만."
    ],
    3: [
        "마을 밖은 위험하니 조심하게.",
        "더 강한 몬스터들이 기다리고 있을걸세."
    ],
    7: [
        "오, 경비병의 훈련을 마치고 왔군!",
        "자네 실력이 정말 일취월장하고 있어.",
        "이제 마을 사람들도 자네를 든든하게 생각한다네."
    ]
}

# 몬스터 관리 (리스트로 변경)
field_monsters = [] # [{"rect": Rect, "data": dict, "dir": [x,y], "timer": 0, "name": str}, ...]
monster_respawn_timer = 0
MONSTER_MOVE_INTERVAL = 500 # 몬스터 이동 간격 (조금 느리게)
menu_nav_timer = 0 # 메뉴 네비게이션 타이머
battle_cooldown_timer = 0 # 전투 종료 후 무적 시간
BATTLE_COOLDOWN_TIME = 2000 # 2초 동안 전투 발생 안 함

# 전투 관련
battle_select = 0
menu_list = ["공격", "스킬", "아이템", "도망"]
battle_messages = []
battle_step = 0  # 0: 메뉴선택, 1:플레이어공격, 2:슬라임공격, 3:전투종료, 4:적선공
battle_timer = 0
BATTLE_DELAY = 1000  # 1초
battle_enemy = {} # 현재 전투 중인 적 정보

def draw_text_box(text, x, y, w, h, color_bg=GREY, color_text=WHITE, small=False):
    f = font_small if small else font
    
    # 줄바꿈 처리 및 필요한 높이 사전 계산
    words = text.split(' ')
    lines = []
    current_line = ""
    for word in words:
        test_line = current_line + (" " if current_line else "") + word
        test_w = f.size(test_line)[0]
        
        if test_w > w - 30: # 좌우 패딩 15씩 제외
            if current_line:
                lines.append(current_line)
            current_line = word
        else:
            current_line = test_line
    if current_line:
        lines.append(current_line)
    
    # 줄 높이 계산 (폰트 높이 + 간격)
    line_h = f.get_height() + 5
    # 최소 높이(h)와 텍스트 내용에 필요한 높이 중 큰 쪽을 선택
    actual_h = max(h, len(lines) * line_h + 30) # 상하 패딩 15씩 추가
    
    # 박스 그리기
    pygame.draw.rect(screen, color_bg, (x, y, w, actual_h))
    pygame.draw.rect(screen, WHITE, (x, y, w, actual_h), 2) # 테두리
    
    # 텍스트 그리기
    for i, line in enumerate(lines):
        img = f.render(line, True, color_text)
        screen.blit(img, (x + 15, y + 15 + i * line_h))
    
    return actual_h # 필요한 경우 늘어난 높이 반환

def draw_text(text, x, y, color=WHITE, center=False, small=False):
    f = font_small if small else font
    img = f.render(text, True, color)
    if center:
        rect = img.get_rect(center=(x, y))
        screen.blit(img, rect)
    else:
        screen.blit(img, (x, y))


def reset_battle(enemy_data=None):
    global battle_select, battle_timer, battle_messages, battle_step, battle_turn_count
    global player_battle_buffs, enemy_battle_debuffs, battle_mana_shield, battle_companion_idx, battle_taunt_target
    global battle_enemy, is_boss_battle
    battle_select = 0
    battle_timer = 0
    battle_messages = []
    battle_step = 0
    battle_turn_count = 0
    battle_companion_idx = 0
    battle_taunt_target = -1 # 도발 대상 초기화
    player_battle_buffs = {}
    enemy_battle_debuffs = {}
    battle_mana_shield = False
    battle_turn_count = 1
    
    # 버프/디버프 초기화 (효과명: 지속턴수)
    player_battle_buffs = {}
    enemy_battle_debuffs = {}
    
    if enemy_data:
        battle_enemy = enemy_data.copy()
        battle_enemy["max_hp"] = battle_enemy["hp"]
        is_boss_battle = enemy_data.get("is_boss", False)
        # 선공 결정 (민첩 비교)
        battle_step = 0 if player_stats["agi"] >= battle_enemy["agi"] else 4
    else:
        # 기본값 (안전장치)
        battle_enemy = {"name": "Unknown", "hp": 10, "max_hp": 10, "atk": 1, "def": 0, "agi": 0, "crit": 0, "exp": 0}
        battle_step = 0
        is_boss_battle = False

def handle_companion_attack():
    global battle_messages
    if player_party:
        for member in player_party:
            help_atk = player_stats["atk"] * member["atk_rate"]
            hd, hc = calculate_damage(help_atk, battle_enemy["def"], 10)
            battle_enemy["hp"] = max(0, battle_enemy["hp"] - hd)
            battle_messages.append(f"{member['name']}의 지원 공격! {hd} 데미지!")

def update_quest(text):
    global quest_text
    quest_text = text

def get_max_exp(level):
    # 경험치 요구량을 10 단위로 깔끔하게 처리 (0으로 끝남)
    raw_exp = 3 * level * level
    return max(10, (raw_exp // 10) * 10)

def level_up():
    global player_level, player_stat_points, player_hp, player_mana, state, skill_points
    player_level += 1
    player_stat_points += 3
    skill_points += 1 # 레벨업 시 스킬 포인트 1 획득
    
    # 레벨업 스탯 자동 상승 제거 (포인트만 지급)
    # 체력, 마나는 회복
    player_hp = player_max_hp
    player_mana = player_max_mana
    # 전투 종료 후 바로 호출되므로 상태 변경은 여기서 하지 않거나, 
    # 호출하는 쪽에서 제어. 여기서는 값만 변경.

def reset_levelup_allocations():
    global levelup_allocations, levelup_selected_stat
    levelup_allocations = {stat: 0 for stat in STAT_ORDER}
    levelup_selected_stat = 0

def commit_levelup_allocations():
    global player_stats, player_hp, player_max_hp, player_mana, player_max_mana
    for stat, count in levelup_allocations.items():
        if count <= 0:
            continue
        increment = STAT_CONFIG[stat]["increment"] * count
        player_stats[stat] = min(player_stats[stat] + increment, STAT_CONFIG[stat]["max"])
    player_max_hp = player_stats["hp"]
    player_hp = player_max_hp
    player_max_mana = player_stats["mana"]
    player_mana = player_max_mana
    reset_levelup_allocations()

# 아이템 추가 함수 (스택 기능)
def add_item_to_inventory(item_data, qty=1):
    global player_inventory
    # 무기(weapon)는 스택되지 않도록 처리
    is_stackable = item_data.get('type') not in ['weapon']
    
    target = None
    if is_stackable:
        for it in player_inventory:
            if it['name'] == item_data['name'] and it.get('enhancement', 0) == item_data.get('enhancement', 0):
                target = it
                break
    
    if target:
        target['count'] = target.get('count', 0) + qty
    else:
        # 무기의 경우 qty가 여러 개라도 개별 슬롯으로 추가
        if not is_stackable:
            for _ in range(qty):
                new_item = item_data.copy()
                new_item['count'] = 1
                player_inventory.append(new_item)
        else:
            new_item = item_data.copy()
            new_item['count'] = qty
            player_inventory.append(new_item)

def calculate_damage(attacker_atk, defender_def, attacker_crit, ignore_def=False):
    # 방어 무시 시 0으로 처리
    actual_def = 0 if ignore_def else defender_def

    # 기본 공격력 (소폭 랜덤)
    base = attacker_atk * random.uniform(0.9, 1.1)

    # 방어 감쇠 공식
    if attacker_atk + actual_def > 0:
        damage = base * (attacker_atk / (attacker_atk + actual_def))
    else:
        damage = 0

    final_damage = max(1, int(damage))
    
    # 크리티컬 로직 (기존 유지)
    crit_chance = attacker_crit * 0.001
    crit_multiplier = 1.5 + (attacker_crit * 0.005)
    
    is_crit = random.random() < crit_chance
    if is_crit:
        final_damage = int(final_damage * crit_multiplier)
        
    return final_damage, is_crit

def open_stat_menu(current_state):
    global state, state_before_stats, stat_menu_points, menu_nav_timer, stat_page, stat_inventory_idx, stat_adjust_mode
    state_before_stats = current_state
    stat_menu_points = player_stat_points
    reset_levelup_allocations()
    state = STATE_STATS
    menu_nav_timer = pygame.time.get_ticks()
    stat_page = 0 # 0: 스탯, 1: 장비/인벤토리
    stat_inventory_idx = 0 # 인벤토리 선택 커서
    stat_adjust_mode = False # 스탯 조절 모드 여부

def close_stat_menu(apply_changes):
    global state, player_stat_points
    if apply_changes:
        player_stat_points = stat_menu_points
        commit_levelup_allocations()
    else:
        reset_levelup_allocations()
    state = state_before_stats

def draw_town_objects():
    # 1. 마을 배경 및 도로 그리기
    screen.fill((120, 70, 40)) # 흙 바닥 (도로 외 구역)
    
    # 가로 도로 (중앙)
    pygame.draw.rect(screen, (150, 100, 60), (0, 240, WIDTH, 120))
    # 세로 도로 (중앙)
    pygame.draw.rect(screen, (150, 100, 60), (340, 0, 120, HEIGHT))
    
    # 플레이어 그리기
    pygame.draw.rect(screen, BLUE, player)
    
    # 헬퍼 함수: 인접 여부 확인
    def is_near(n):
        return abs(player.x - n.x) <= 40 and abs(player.y - n.y) <= 40

    # 촌장
    pygame.draw.rect(screen, GREEN, npc)
    if quest_step == 0:
        # 처음 튜토리얼: 멀리 있어도 표시
        draw_text("[Z] 촌장과 대화", npc.x - 20, npc.y - 30, YELLOW, small=True)
    elif quest_step == 12:
        # 퀘스트 완료 보고: 멀리 있어도 표시
        draw_text("[Z] 촌장에게 보고", npc.x - 20, npc.y - 30, YELLOW, small=True)
    elif is_near(npc):
        if quest_step == 2:
            # 목표 달성 후 보고: 가까이 갈 때만 표시
            draw_text("[Z] 촌장에게 보고", npc.x - 20, npc.y - 30, YELLOW, small=True)

    # 전직관
    # 전직관은 상시 대화 가능 (퀘스트 개념이 아니므로 일단 유지하거나 필요시 수정)
    pygame.draw.rect(screen, (150, 0, 150), npc_job)
    if is_near(npc_job):
        draw_text("[Z] 전직관", npc_job.x, npc_job.y - 30, YELLOW, small=True)

    # 상점 (상시 이용 가능)
    pygame.draw.rect(screen, (200, 200, 0), npc_store)
    if is_near(npc_store):
        draw_text("[Z] 상점", npc_store.x, npc_store.y - 30, YELLOW, small=True)

    # 대장장이
    pygame.draw.rect(screen, (60, 60, 65), npc_blacksmith)
    if is_near(npc_blacksmith):
        if quest_step == 4:
            draw_text("[Z] 대장장이와 대화", npc_blacksmith.x - 20, npc_blacksmith.y - 30, YELLOW, small=True)
        elif quest_step == 5:
            bubble_count = sum(it.get('count', 1) for it in player_inventory if it['name'] == "슬라임 방울")
            if bubble_count >= 5:
                draw_text("[Z] 재료 전달", npc_blacksmith.x - 10, npc_blacksmith.y - 30, YELLOW, small=True)
            else:
                draw_text("[Z] 대장장이", npc_blacksmith.x, npc_blacksmith.y - 30, YELLOW, small=True)
        else:
            draw_text("[Z] 대장장이", npc_blacksmith.x, npc_blacksmith.y - 30, YELLOW, small=True)

    # 경비병
    pygame.draw.rect(screen, (50, 50, 200), npc_guard)
    # 퀘스트 대기 중일 때는 멀리서도 텍스트 표시
    if quest_step in [3, 6]:
        label = "대장장이의 부탁" if quest_step == 3 else "고블린 소탕 훈련"
        draw_text(f"[Z] {label}", npc_guard.x - 40, npc_guard.y - 30, YELLOW, small=True)
    elif is_near(npc_guard):
        if quest_step == 7 and monster_kills["goblin"] >= 5:
             draw_text("[Z] 훈련 보고", npc_guard.x - 10, npc_guard.y - 30, YELLOW, small=True)
        else:
             draw_text("[Z] 경비병", npc_guard.x, npc_guard.y - 30, YELLOW, small=True)

    # 용병단장 (상시 이용 가능)
    pygame.draw.rect(screen, (100, 50, 150), npc_recruit)
    if is_near(npc_recruit):
        draw_text("[Z] 용병단", npc_recruit.x, npc_recruit.y - 30, YELLOW, small=True)



# ----------------------------------------
# 메인 루프
# ----------------------------------------
running = True
while running:
    dt = clock.tick(60)
    screen.fill(BLACK)
    keys = pygame.key.get_pressed()
    now = pygame.time.get_ticks()
    
    # 이벤트 처리 (상태 무관 공통)
    events = pygame.event.get()
    for event in events:
        if event.type == pygame.QUIT:
            running = False
        
        if event.type == pygame.KEYUP:
            # 스탯 메뉴 토글
            if event.key == KEY_MENU_OPEN:
                if state == STATE_STATS:
                    close_stat_menu(True) # 적용하며 닫기
                elif state in [STATE_TOWN, STATE_FIELD]: 
                    open_stat_menu(state)
            
            # 설정 메뉴 토글 (ESC)
            if event.key == KEY_ESC:
                if state == STATE_SETTINGS:
                    state = state_before_settings if 'state_before_settings' in globals() else STATE_TOWN
                else:
                    state_before_settings = state
                    state = STATE_SETTINGS


        if event.type == pygame.KEYDOWN:
            # X키로 메뉴 닫기 공통 (STATS, SETTINGS)
            if event.key == KEY_ACTION_2:
                if state == STATE_STATS:
                    close_stat_menu(True)
                elif state == STATE_SETTINGS and not globals().get('is_rebinding', False):
                    state = state_before_settings if 'state_before_settings' in globals() else STATE_TOWN
                # 상점은 키입력 직접 처리하므로 여기 없음.

    # ----------------------------------------
    # 이름 입력
    # ----------------------------------------
    if state == STATE_NAME:
        screen.fill(BG_NAME)
        draw_text_box("용사 이름을 입력하세요 (영어만)", 150, 150, 500, 50)
        draw_text_box("입력: " + player_name, 150, 220, 500, 50)
        draw_text_box("조작법: 방향키 이동, F키 상호작용, Z키 선택, 엔터 확정", 150, 290, 500, 50)

        for event in events:
            if event.type == pygame.KEYDOWN:
                if state == STATE_NAME:
                    if event.key == pygame.K_RETURN and player_name != "":
                        state = STATE_TOWN
                        # DB 내의 호칭 업데이트
                        for k, d in COMPANION_DB.items():
                            d['desc'] = d['desc'].replace("주인공", player_name).replace("플레이어", player_name)
                        for k, d in COMPANION_SKILL_DB.items():
                            d['desc'] = d['desc'].replace("주인공", player_name).replace("플레이어", player_name)
                    elif event.key == pygame.K_BACKSPACE:
                        player_name = player_name[:-1]
                    else:
                        if event.unicode in string.ascii_letters:
                            player_name += event.unicode


    # ----------------------------------------
    # 마을
    # ----------------------------------------
    elif state == STATE_TOWN:
        screen.fill(BG_TOWN)
        # draw_grid() # 격자 제거
        draw_town_objects()
        
        # 전직관 (레벨 10 이상이고 아직 Novice일 때만? 아니면 항상?)
        # 10레벨 이상일 때 표시
        if player_level >= 10 and player_job == "초보자":
             draw_text("[Z] 전직", npc_job.x, npc_job.y - 30, YELLOW)


        draw_text("↑사냥터", WIDTH//2, 20, WHITE, center=True, small=True)
        update_quest("퀘스트: 촌장과 대화하기")
        
        update_quest("퀘스트: 촌장과 대화하기")
        
        # 플레이어 이동 (그리드 방식)
        if now - player_move_timer > PLAYER_MOVE_INTERVAL:
            next_x, next_y = player.x, player.y
            moved = False
            
            if keys[KEY_UP]:
                next_y -= player_speed
                moved = True
            elif keys[KEY_DOWN]:
                next_y += player_speed
                moved = True
            elif keys[KEY_LEFT]:
                next_x -= player_speed
                moved = True
            elif keys[KEY_RIGHT]:
                next_x += player_speed
                moved = True
            
            if moved:
                # 충돌 체크 및 이동
                temp_rect = pygame.Rect(next_x, next_y, player_size, player_size)
                
                # 1. 화면 밖 (위쪽은 사냥터 이동을 위해 허용)
                # 아래, 좌, 우는 막힘
                if next_x < 0: next_x = 0
                if next_x > WIDTH - player_size: next_x = WIDTH - player_size
                if next_y > HEIGHT - player_size: next_y = HEIGHT - player_size
                # next_y < 0 은 허용 (맵 이동 트리거)

                temp_rect.x, temp_rect.y = next_x, next_y
                
                # 2. NPC 충돌
                if (not temp_rect.colliderect(npc) and 
                    not temp_rect.colliderect(npc_job) and 
                    not temp_rect.colliderect(npc_store) and 
                    not temp_rect.colliderect(npc_blacksmith) and 
                    not temp_rect.colliderect(npc_recruit) and 
                    not temp_rect.colliderect(npc_guard)):
                    player.x, player.y = next_x, next_y
                    player_move_timer = now

        # 촌장 대화 (Interaction)
        # 그리드니까 40 이하 거리면 인접
        if ((abs(player.x - npc.x) <= 40 and abs(player.y - npc.y) == 0) or 
            (abs(player.x - npc.x) == 0 and abs(player.y - npc.y) <= 40)):
            
            for event in events:
                if event.type == pygame.KEYDOWN and event.key == KEY_ACTION_1:
                    state = STATE_DIALOG
                    dialog_page = 0
                    current_dialog = dialog_map.get(quest_step, dialog_map[3])
                    menu_nav_timer = now # 타이머 초기화
                    break # 한 번만 처리
        
        # 상점 대화 (Interaction)
        if ((abs(player.x - npc_store.x) <= 40 and abs(player.y - npc_store.y) == 0) or 
            (abs(player.x - npc_store.x) == 0 and abs(player.y - npc_store.y) <= 40)):
            
            for event in events:
                if event.type == pygame.KEYDOWN and event.key == KEY_ACTION_1:
                    state = STATE_STORE
                    store_select_idx = 0
                    menu_nav_timer = now # 타이머 초기화 (입력 중복 방지)
                    break

        # 전직관 대화 (Interaction)
        if ((abs(player.x - npc_job.x) <= 40 and abs(player.y - npc_job.y) == 0) or 
            (abs(player.x - npc_job.x) == 0 and abs(player.y - npc_job.y) <= 40)):
            
            for event in events:
                if event.type == pygame.KEYDOWN and event.key == KEY_ACTION_1:
                    menu_nav_timer = now # 타이머 초기화
                    if player_level < 10:
                        # 10레벨 미만 대화
                        state = STATE_DIALOG
                        current_dialog = ["아직 전직할 준비가 되지 않았네.", "10레벨을 달성하고 오게."]
                        dialog_page = 0
                    elif player_job == "초보자":
                        state = STATE_JOB_SELECT
                    else:
                        state = STATE_DIALOG
                        current_dialog = [f"이미 {player_job}의 길을 걷고 있군."]
                        dialog_page = 0
                    break

        # 대장장이 대화 (Interaction)
        if ((abs(player.x - npc_blacksmith.x) <= 40 and abs(player.y - npc_blacksmith.y) == 0) or 
            (abs(player.x - npc_blacksmith.x) == 0 and abs(player.y - npc_blacksmith.y) <= 40)):
            
            # 퀘스트 알림 표시
            if quest_step == 4:
                draw_text("!", npc_blacksmith.x + 15, npc_blacksmith.y - 40, YELLOW)
            elif quest_step == 5:
                # 재료 확인
                bubble_count = sum(it.get('count', 1) for it in player_inventory if it['name'] == "슬라임 방울")
                if bubble_count >= 5:
                    draw_text("?", npc_blacksmith.x + 15, npc_blacksmith.y - 40, GREEN)
           
            for event in events:
                if event.type == pygame.KEYDOWN and event.key == KEY_ACTION_1:
                    if quest_step == 4:
                        state = STATE_DIALOG
                        current_dialog = ["어이, 거기 모험가!", "촌장님께 소식 들었네. 실력이 꽤 좋다며?", "내 부탁 하나만 들어주게. 슬라임 방울 5개만 구해다 줄 수 있나?", "연구 재료로 꼭 필요해서 말이야."]
                        dialog_page = 0
                        quest_step = 5
                        update_quest("퀘스트: 슬라임 방울 5개 수집")
                        menu_nav_timer = now
                    elif quest_step == 5:
                        bubble_count = sum(it.get('count', 1) for it in player_inventory if it['name'] == "슬라임 방울")
                        if bubble_count >= 5:
                            state = STATE_DIALOG
                            current_dialog = ["오! 정말 가져왔군. 고맙네!", "이건 내가 대충 만든 거지만 꽤 쓸만할 거야.", "철 목걸이를 받았다! 장비창에서 장착해보게."]
                            dialog_page = 0
                            quest_step = 6
                            update_quest("퀘스트 완료: 대장장이의 재료")
                            
                            # 재료 삭제
                            rem = 5
                            for it in player_inventory[:]:
                                if it['name'] == "슬라임 방울":
                                    if it.get('count',1) >= rem:
                                        it['count'] -= rem
                                        if it['count'] <= 0: player_inventory.remove(it)
                                        rem = 0
                                    else:
                                        rem -= it.get('count',1)
                                        player_inventory.remove(it)
                                if rem <= 0: break
                                
                            add_item_to_inventory(ITEM_DB["iron_necklace"])
                            menu_nav_timer = now
                        else:
                            state = STATE_BLACKSMITH
                            menu_nav_timer = now
                    else:
                        state = STATE_BLACKSMITH
                        menu_nav_timer = now
                    break

        # 경비병 대화 (Interaction)
        if ((abs(player.x - npc_guard.x) <= 40 and abs(player.y - npc_guard.y) == 0) or 
            (abs(player.x - npc_guard.x) == 0 and abs(player.y - npc_guard.y) <= 40)):
            
            for event in events:
                if event.type == pygame.KEYDOWN and event.key == KEY_ACTION_1:
                    if quest_step == 3:
                        state = STATE_DIALOG
                        current_dialog = ["어이, 모험가! 마을 대장장이가 급하게 사람을 찾고 있더군.", "슬라임들을 잡으면서 '슬라임 방울' 5개만 모아다 주게.", "전부 모으면 대장장이에게 가져다주면 될 거야."]
                        dialog_page = 0
                        quest_step = 4
                        update_quest("퀘스트: 슬라임 방울 5개 수집")
                        menu_nav_timer = now
                    elif quest_step == 6:
                        state = STATE_DIALOG
                        current_dialog = ["실력이 꽤 늘었군! 이제 정식 훈련을 시작하지.", "바람의 평원에 가서 고블린 5마리를 퇴치해오게.", "자네의 실력을 증명할 때다!"]
                        dialog_page = 0
                        quest_step = 7
                        update_quest("퀘스트: 고블린 5마리 퇴치 (0/5)")
                        menu_nav_timer = now
                    elif quest_step == 7:
                        if monster_kills["goblin"] >= 5:
                            state = STATE_DIALOG
                            current_dialog = ["훌륭하군! 고블린들을 완벽히 제압했어.", "이건 자네의 노력에 대한 보상일세. 은반지를 받게.", "앞으로도 마을의 안전을 위해 힘써주게!"]
                            dialog_page = 0
                            quest_step = 8
                            update_quest("퀘스트 완료: 경비병의 인정")
                            add_item_to_inventory(ITEM_DB["silver_ring"])
                            player_gold += 1000
                        else:
                            state = STATE_DIALOG
                            current_dialog = [f"아직 고블린 소탕이 끝나지 않았네! ({monster_kills['goblin']}/5)"]
                            dialog_page = 0
                        menu_nav_timer = now
                    else:
                        state = STATE_DIALOG
                        current_dialog = ["마을의 평화는 내가 지킨다!"]
                        dialog_page = 0
                    break

        # 용병단장 대화 (Interaction)
        if ((abs(player.x - npc_recruit.x) <= 40 and abs(player.y - npc_recruit.y) == 0) or 
            (abs(player.x - npc_recruit.x) == 0 and abs(player.y - npc_recruit.y) <= 40)):
            
            for event in events:
                if event.type == pygame.KEYDOWN and event.key == KEY_ACTION_1:
                    state = STATE_RECRUIT
                    menu_nav_timer = now

        # 위로 나가면 사냥터 선택 이동
        if player.y < 0:
            state = STATE_SELECT_MAP
            select_map_index = 0
            player.x, player.y = player_town_pos # 살짝 아래로 조정하여 바로 다시 나가지 않게? 아니면 그냥 위치 리셋
            # 여기서는 플레이어 위치를 마을 상단에 유지하되, 상태만 바꿈. 
            # 실제로 필드로 이동할때 좌표를 player_field_pos로 바꿈.

    # ----------------------------------------
    # 대화
    # ----------------------------------------
    elif state == STATE_DIALOG:
        screen.fill(BG_TOWN)
        draw_town_objects()
        
        # 현재 대화 목록이 비어있으면 기본값 처리 (안전장치)
        if not current_dialog:
            current_dialog = dialog_map[0]

        text = current_dialog[dialog_page].replace("{name}", player_name)
        draw_text_box(text, 50, 400, 700, 150)
        draw_text_box("[Z] 다음", 600, 500, 135, 50, color_bg=BLACK, color_text=YELLOW)


        # 키 누르고 있는 상태(keys)가 아니라, 눌렀을 때 이벤트(KEYDOWN)로 처리
        for event in events:
            if event.type == pygame.KEYDOWN and event.key == KEY_ACTION_1:
                dialog_page += 1
                if dialog_page >= len(current_dialog):
                    state = STATE_TOWN
                    # 대화 종료 후 퀘스트 상태 업데이트
                    if quest_step == 0:
                        quest_step = 1
                        update_quest("퀘스트: 슬라임을 물리치기")
                    elif quest_step == 2:
                        quest_step = 10
                        update_quest("퀘스트: 장비 마련하기")
                        player_gold += 1000

                        # 안내 메시지 추가
                        current_dialog = [
                            "슬라임을 물리쳤군! 정말 훌륭하네.",
                            "하지만 그 빈손으로는 다음 모험이 위험할 걸세.",
                            "자, 여기 1000G를 줄 테니 상점에 가서 장비를 사게.",
                            "가장 기본적인 '목검'과 '가죽 갑옷'이면 충분할 걸세.",
                            "준비가 되면 다시 나에게 오게나."
                        ]
                        dialog_page = 0
                        state = STATE_DIALOG 
                    elif quest_step == 10:
                        quest_step = 11
                        update_quest("퀘스트: 목검과 가죽 갑옷 구매 (상점)")
                    elif quest_step == 12:
                        quest_step = 13
                        current_dialog = [
                            "오! 이제야 좀 모험가다운 모습이군.",
                            "이제 마을 북쪽 입구의 '경비병'을 찾아가게.",
                            "그가 자네의 실력을 더 단련시켜 줄 걸세."
                        ]
                        dialog_page = 0
                        state = STATE_DIALOG
                        quest_step = 3 # 기존 경비병 퀘스트 트리거 단계로 이동

    # ----------------------------------------
    # 사냥터 선택
    # ----------------------------------------
    elif state == STATE_SELECT_MAP:
        screen.fill(BG_LEVELUP)
        draw_text("사냥터를 선택하세요", WIDTH//2, 100, WHITE, center=True)
        draw_text("[← / →] 이동, [Z] 입장, [X] 취소", WIDTH//2, HEIGHT - 100, WHITE, center=True, small=True)

        # 선택된 맵 정보 표시
        selected_map = MAP_DATA[select_map_index]
        map_name = selected_map["name"]
        min_lv = selected_map["min_lv"]
        bg_color = selected_map["color"]
        
        # 메시지 타이머 (레벨 부족 등)
        if 'msg_timer' not in globals(): msg_timer = 0
        if 'msg_text' not in globals(): msg_text = ""

        # 중앙에 맵 이름과 박스 표시
        box_width, box_height = 300, 200
        box_x, box_y = WIDTH//2 - box_width//2, HEIGHT//2 - box_height//2
        
        # 배경색 미리보기
        pygame.draw.rect(screen, bg_color, (box_x, box_y, box_width, box_height))
        pygame.draw.rect(screen, WHITE, (box_x, box_y, box_width, box_height), 3)

        draw_text(map_name, WIDTH//2, box_y + 80, WHITE, center=True)
        
        info_color = GREEN if player_level >= min_lv else RED
        draw_text(f"권장 레벨: {min_lv}", WIDTH//2, box_y + 120, info_color, center=True, small=True)

        if now - menu_nav_timer > 150:
            if keys[KEY_LEFT]:
                select_map_index = (select_map_index - 1) % len(MAP_DATA)
                menu_nav_timer = now
            elif keys[KEY_RIGHT]:
                select_map_index = (select_map_index + 1) % len(MAP_DATA)
                menu_nav_timer = now
        
        if keys[KEY_ACTION_2]: # 마을로 돌아가기
            if now - menu_nav_timer > 200:
                state = STATE_TOWN
                player.y = 10  # 마을 상단으로 다시 배치
                menu_nav_timer = now

        if keys[KEY_ACTION_1]:
            if now - menu_nav_timer > 200:
                menu_nav_timer = now
                if player_level >= min_lv:
                    state = STATE_FIELD
                    current_map_index = select_map_index
                    player.x, player.y = player_field_pos
                    
                    # 몬스터 생성 (1~3마리)
                    # 이전 몬스터 초기화
                    field_monsters = [] 
                    
                    available_monsters = [k for k, v in MONSTER_DB.items() if v.get("map_idx") == current_map_index]
                    
                    spawn_count_min = 1
                    spawn_count_max = 4

                    # 튜토리얼(퀘스트 2단계 이하)에서는 숲에서 슬라임만 나오도록 강제
                    if current_map_index == 0 and quest_step < 3:
                         available_monsters = ["slime"]
                         spawn_count_max = 1 # 튜토리얼은 1마리만
                    
                    if available_monsters:
                        count = random.randint(spawn_count_min, spawn_count_max)
                        for _ in range(count):
                            mob_key = random.choice(available_monsters)
                            mob_data = MONSTER_DB[mob_key].copy() # 복사해서 사용
                            
                            # 위치 랜덤 (그리드 정렬 - WIDTH는 800, HEIGHT는 600. 둘다 40배수)
                            # UI영역 (상단20, 하단20 등) 제외하고 40~560, 40~760 정도?
                            rx = random.randrange(40, WIDTH - 40, 40)
                            ry = random.randrange(40, HEIGHT - 80, 40) # 하단 UI 고려 (좀 더 위로)
                            
                            # 몬스터 객체 생성 (사이즈 축소)
                            m_rect = pygame.Rect(rx, ry, 40, 40)
                            
                            monster_obj = {
                                "rect": m_rect,
                                "data": mob_data, # 스탯 포함
                                "name": mob_data["name"],
                                "dir": [0,0],
                                "timer": 0,
                                "key": mob_key
                            }
                            field_monsters.append(monster_obj)

                    if current_map_index == 0:
                        if quest_step == 0:
                             update_quest("퀘스트: 촌장에게 먼저 말을 거세요")
                        elif quest_step == 1:
                            update_quest("퀘스트: 슬라임 물리치기")
                        elif quest_step == 5:
                            update_quest("퀘스트: 슬라임 방울 5개 수집")
                        elif quest_step == 7:
                            update_quest(f"퀘스트: 고블린 퇴치 ({monster_kills['goblin']}/5)")
                        elif quest_step == 11:
                             # 아이템 보유 체크를 여기서 수행 (매 프레임)
                             has_sword = any(it['name'] == ITEM_DB["wooden_sword"]["name"] for it in player_inventory)
                             has_armor = any(it['name'] == ITEM_DB["leather_armor"]["name"] for it in player_inventory)
                             if has_sword and has_armor:
                                 quest_step = 12
                                 update_quest("퀘스트 완료: 장비 마련 (촌장 보고)")
                             else:
                                 update_quest("퀘스트: 목검과 가죽 갑옷 구매 (상점)")
                        elif quest_step == 12:
                             update_quest("퀘스트 완료: 장비 마련 (촌장 보고)")
                        else:
                            update_quest("자유롭게 사냥하세요")
                else:
                    msg_text = "레벨이 부족합니다!"
                    msg_timer = now
        
        if msg_text and now - msg_timer < 1000:
            draw_text(msg_text, WIDTH//2, HEIGHT - 150, RED, center=True)
        else:
            msg_text = ""

    # ----------------------------------------
    # 필드 (구 숲)
    # ----------------------------------------
    elif state == STATE_FIELD:
        # 현재 맵 배경색 사용
        screen.fill(MAP_DATA[current_map_index]["color"])
        # draw_grid() # 격자 제거
        pygame.draw.rect(screen, BLUE, player)
        
        # 맵 이름 표시 (상단 중앙)
        draw_text(MAP_DATA[current_map_index]["name"], WIDTH//2, 20, WHITE, center=True, small=True)

        if field_monsters:
            monster_respawn_timer = 0 # 몬스터가 있으면 리스폰 타이머 초기화 (확실하게)
            for mob in field_monsters:
                pygame.draw.rect(screen, RED, mob["rect"])
                draw_text(mob["name"], mob["rect"].x, mob["rect"].y - 25, RED, small=True)
                
                # 이동 로직 (추격 AI + 그리드)
                if now - mob["timer"] > MONSTER_MOVE_INTERVAL:
                    # 플레이어와 거리 계산
                    dist_x = player.x - mob["rect"].x
                    dist_y = player.y - mob["rect"].y
                    dist = (dist_x**2 + dist_y**2) ** 0.5
                    
                    if dist < 250: # 감지 범위
                        # 추격 (X축 우선 혹은 Y축 우선 랜덤)
                        if abs(dist_x) > abs(dist_y):
                            dx = 1 if dist_x > 0 else -1
                            dy = 0
                        else:
                            dx = 0
                            dy = 1 if dist_y > 0 else -1
                        mob["dir"] = [dx, dy]
                    else:
                        # 랜덤 배회
                        dx = random.choice([-1, 0, 1])
                        dy = random.choice([-1, 0, 1])
                        mob["dir"] = [dx, dy]
                    
                    mob["rect"].x += mob["dir"][0] * 40 # 그리드 단위 이동
                    mob["rect"].y += mob["dir"][1] * 40
                    
                    # 맵 밖으로 나가지 않게 (그리드 보정)
                    # WIDTH // 40 * 40 등으로 딱 떨어지게 할 수도 있음
                    mob["rect"].x = max(0, min(WIDTH - 40, mob["rect"].x))
                    mob["rect"].y = max(40, min(HEIGHT - 40, mob["rect"].y))
                    mob["timer"] = now
                
                # 충돌 체크 (근접 시 전투)
                # 플레이어와 몬스터가 1칸 이내(40px) 거리면 전투
                dist_x = abs(player.x - mob["rect"].x)
                dist_y = abs(player.y - mob["rect"].y)
                
                # 40px 이하 (딱 붙거나 겹칠 때)
                if dist_x <= 40 and dist_y <= 40:
                    if current_map_index == 0 and quest_step == 0:
                         draw_text("먼저 촌장에게 말을 거세요!", player.x, player.y - 30, RED, small=True)
                    else:
                        # 전투 시작
                        if now - battle_cooldown_timer > BATTLE_COOLDOWN_TIME:
                            reset_battle(mob["data"])
                            state = STATE_BATTLE
                            
                            # 전투 대상 설정
                            battle_target_mob = mob
        # 플레이어 이동 (그리드)
        if now - player_move_timer > PLAYER_MOVE_INTERVAL:
            next_x, next_y = player.x, player.y
            moved = False
            
            if keys[KEY_UP]:
                next_y -= player_speed
                moved = True
            elif keys[KEY_DOWN]:
                next_y += player_speed
                moved = True
            elif keys[KEY_LEFT]:
                next_x -= player_speed
                moved = True
            elif keys[KEY_RIGHT]:
                next_x += player_speed
                moved = True
            
            if moved:
                # 필드 경계 체크
                # 상단: 0보다 작으면 막힘 (더 갈 곳 없음)
                if next_y < 0: next_y = 0
                
                # 좌우: 화면 밖으로 못 나감
                if next_x < 0: next_x = 0
                if next_x > WIDTH - player_size: next_x = WIDTH - player_size
                
                # 하단: 화면 밖으로 나가면 마을로 이동 (아래 로직에서 처리하므로 여기선 제한 없음)
                # 단, 너무 멀리 가지 않게 적당히 제한하거나, 아래 로직에 맡김.
                # 여기서는 업데이트만 함.
                
                player.x, player.y = next_x, next_y
                player_move_timer = now

        # 숲 아래로 가면 마을로
        if player.y >= HEIGHT:
            state = STATE_TOWN
            player.x, player.y = player_town_pos
            # 퀘스트 완료 상태로 복귀했다면 자동 대화 X, 촌장에게 가야함
            if quest_step == 2:
                # update_quest("퀘스트: 촌장에게 완료 보고") # 이미 되어있음
                pass
            elif quest_step == 1:
                update_quest("퀘스트: 촌장과 대화하기") # ?? 사냥 중단?
                pass
            
            monster_respawn_timer = 0
            
        else:
             # 몹이 없으면 리스폰 타이머 작동
            if current_map_index == 0 and quest_step < 3:
                pass # 튜토리얼 중 리스폰 X
            else:
                if monster_respawn_timer == 0:
                    monster_respawn_timer = now
                elif now - monster_respawn_timer > 1000:
                    # 리스폰 1~3마리
                    available_monsters = [k for k, v in MONSTER_DB.items() if v.get("map_idx") == current_map_index]
                    
                    # 튜토리얼 몬스터 제한 (리스폰 시에도 적용)
                    if current_map_index == 0: # 튜토리얼 맵
                        if quest_step == 2: # 이미 잡았고 보고 전이면 리스폰 안 함
                            available_monsters = []
                        elif quest_step < 2: # 아직 안 잡았거나 퀘스트 중이면 1마리 유지
                            available_monsters = ["slime"]
                            spawn_count_max = 1
                        else:
                            spawn_count_max = 4
                    else:
                        spawn_count_max = 4

                    if available_monsters:
                        count = random.randint(1, spawn_count_max)
                        for _ in range(count):
                            # 보스 인카운터 확률 (5%)
                            if random.random() < 0.05 and current_map_index in BOSS_DB:
                                mob_data = BOSS_DB[current_map_index].copy()
                                mob_data["is_boss"] = True
                            else:
                                mob_key = random.choice(available_monsters)
                                mob_data = MONSTER_DB[mob_key].copy()
                                mob_data["is_boss"] = False

                            # 리스폰 위치도 그리드 정렬
                            rx = random.randrange(0, WIDTH, 40)
                            ry = random.randrange(40, HEIGHT, 40)
                            m_rect = pygame.Rect(rx, ry, 40, 40)
                            monster_obj = {
                                "rect": m_rect,
                                "data": mob_data,
                                "name": mob_data["name"],
                                "dir": [0,0],
                                "timer": 0,
                                "key": "boss" if mob_data.get("is_boss") else mob_key
                            }
                            field_monsters.append(monster_obj)
                    monster_respawn_timer = 0

    # ----------------------------------------
    # 전투
    # ----------------------------------------
    elif state == STATE_BATTLE:
        screen.fill(BG_BATTLE)
        # 전투 UI
        slime_rect = pygame.Rect(50, 50, 80, 80)
        player_rect = pygame.Rect(600, 300, 80, 80)
        pygame.draw.rect(screen, RED, slime_rect)
        pygame.draw.rect(screen, BLUE, player_rect)
        
        draw_text(f"{battle_enemy['name']} HP: {battle_enemy['hp']}/{battle_enemy['max_hp']}", slime_rect.x, slime_rect.y - 25)
        draw_text(f"{player_name} HP: {player_hp}", player_rect.x, player_rect.y - 25)

        msg_box_y = 400
        pygame.draw.rect(screen, BLACK, (50, msg_box_y, 700, 100))
        pygame.draw.rect(screen, WHITE, (50, msg_box_y, 700, 100), 1)
        
        # 메시지 시퀀스 연출
        if battle_messages:
            # 첫 번째 메시지 (기본 공격/스킬명)
            draw_text(battle_messages[0], 70, msg_box_y + 15, WHITE)
            
            # 0.5초(500ms) 뒤 두 번째 메시지(급소/효과 등) 출력
            if len(battle_messages) > 1 and now - battle_timer > 500:
                draw_text(battle_messages[1], 70, msg_box_y + 45, YELLOW, small=True)
            
            # 1.0초(1000ms) 뒤 세 번째 메시지 출력 (있는 경우)
            if len(battle_messages) > 2 and now - battle_timer > 1000:
                draw_text(battle_messages[2], 70, msg_box_y + 70, YELLOW, small=True)
        
        # 용병 사용 안내
        if player_party and battle_step == 0:
            draw_text("Tip: 내 턴이 끝나면 영입한 용병들의 명령을 내릴 수 있습니다.", WIDTH//2, 385, GREEN, center=True, small=True)

        # 메뉴
        for i, m in enumerate(menu_list):
            x = 50 + i * 180
            y = 520
            color = WHITE
            border = WHITE
            if i == battle_select:
                color = YELLOW
                border = YELLOW
            pygame.draw.rect(screen, border, (x-10, y-10, 150, 60), 2)
            draw_text(m, x, y, color)

        # 전투 로직
        # 전투 로직
        if battle_step == 0:  # 메뉴 선택
            if now - menu_nav_timer > 150: # 150ms 간격
                if keys[KEY_LEFT]:
                    battle_select = max(0, battle_select - 1)
                    menu_nav_timer = now
                elif keys[KEY_RIGHT]:
                    battle_select = min(3, battle_select + 1)
                    menu_nav_timer = now

            for event in events:
                if event.type == pygame.KEYDOWN and event.key == KEY_ACTION_1:
                    if now - menu_nav_timer > 300:
                        menu_nav_timer = now
                        if battle_select == 0: # 공격
                            atk_bonus = 1.3 if "공격력" in player_battle_buffs else 1.0
                            crit_bonus = 20 if "크리티컬" in player_battle_buffs else 0
                            
                            # 공격 시퀀스 시작
                            hd, hc = calculate_damage(player_stats["atk"] * atk_bonus, battle_enemy["def"], player_stats["crit"] + crit_bonus)
                            battle_enemy["hp"] = max(0, battle_enemy["hp"] - hd)
                            
                            battle_messages = [f"{player_name}의 공격! {hd} 데미지!"]
                            if hc: battle_messages.append(random.choice(CRIT_SCRIPTS))
                            
                            battle_step = 1 # 메시지 연출 단계로
                            battle_timer = now
                            menu_nav_timer = now
                        elif battle_select == 1: # 스킬 (메뉴 진입)
                            battle_step = 10 # 스킬 선택 모드
                            battle_skill_select_idx = 0
                            menu_nav_timer = now 
                        
                        elif battle_select == 2: # 아이템
                             battle_step = 20 # 아이템 선택 모드
                             battle_item_select_idx = 0
                             menu_nav_timer = now

                        elif battle_select == 3: # 도망
                            if random.random() < 0.5:
                                battle_messages = ["도망에 성공했다!"]
                                battle_step = 5 # 도망 성공 대기 상태
                                battle_timer = now
                            else:
                                battle_messages = ["도망에 실패했다!"]
                                battle_step = 1 # 적 턴으로 넘어감
                                battle_timer = now

        elif battle_step == 10: # 스킬 선택 화면
            pygame.draw.rect(screen, BLACK, (50, HEIGHT - 150, WIDTH - 100, 140))
            draw_text(f"스킬 선택 (MP: {player_mana}/{player_max_mana}) (X: 취소)", 70, HEIGHT - 140, GREY, small=True)
            
            my_skills = JOB_DB[player_job]["skills"]
            
            # 스킬 목록 표시
            for i, s_name in enumerate(my_skills):
                s_data = SKILLS.get(s_name, {"mana": 0, "name": s_name})
                color = YELLOW if i == battle_skill_select_idx else WHITE
                draw_text(f"{s_name} (MP {s_data['mana']})", 80, HEIGHT - 110 + i * 30, color)
            
            if now - menu_nav_timer > 150:
                if keys[KEY_UP]:
                    battle_skill_select_idx = (battle_skill_select_idx - 1) % len(my_skills)
                    menu_nav_timer = now
                elif keys[KEY_DOWN]:
                    battle_skill_select_idx = (battle_skill_select_idx + 1) % len(my_skills)
                    menu_nav_timer = now
            
            for event in events:
                if event.type == pygame.KEYDOWN:
                    if event.key == KEY_ACTION_2: # 취소
                        if now - menu_nav_timer > 200:
                            battle_step = 0
                            menu_nav_timer = now
                    
                    if event.key == KEY_ACTION_1: # 선택
                        if now - menu_nav_timer > 300:
                            menu_nav_timer = now
                            skill_name = my_skills[battle_skill_select_idx]
                            skill_data = SKILLS.get(skill_name)
                            
                            if player_mana >= skill_data["mana"]:
                                player_mana -= skill_data["mana"]
                                
                                # 공통 효과 처리
                                effect_msgs = []
                                
                                # 1. 버프/특수 효과 적용 (공격 전)
                                if skill_name == "아이언 바디":
                                    player_battle_buffs["방어력"] = 4
                                    effect_msgs.append("방어력이 대폭 상승했습니다!")
                                elif skill_name == "워 크라이":
                                    player_battle_buffs["공격력"] = 4
                                    effect_msgs.append("전투 의지가 솟구칩니다! (공격력 상승)")
                                elif skill_name == "헤이스트":
                                    player_battle_buffs["민첩"] = 5
                                    effect_msgs.append("몸이 가벼워졌습니다! (민첩 상승)")
                                elif skill_name == "매직 실드":
                                    battle_mana_shield = True
                                    effect_msgs.append("마나의 장벽이 생성되었습니다!")
                                elif skill_name == "포커스":
                                    player_battle_buffs["공격력"] = 3
                                    player_battle_buffs["크리티컬"] = 3
                                    effect_msgs.append("집중력이 높아집니다!")
                                elif skill_name == "독 바르기":
                                    player_battle_buffs["독무기"] = 5
                                    effect_msgs.append("무기에 독을 발랐습니다!")

                                # 2. 공격 처리
                                dmg_rate = skill_data.get("dmg_rate", 0)
                                if dmg_rate > 0:
                                    hits = skill_data.get("hits", 1)
                                    total_dmg = 0
                                    any_crit = False
                                    
                                    # 버프 적용된 공격력/크리
                                    atk_bonus = 1.3 if "공격력" in player_battle_buffs else 1.0
                                    crit_bonus = skill_data.get("crit_bonus", 0)
                                    if "크리티컬" in player_battle_buffs: crit_bonus += 20
                                    
                                    ignore_def = skill_name == "가드 브레이크"
                                    
                                    for _ in range(hits):
                                        lv = skill_levels.get(skill_name, 1)
                                        lv_bonus = (lv - 1) * 0.1
                                        
                                        d, c = calculate_damage(player_stats["atk"] * (dmg_rate + lv_bonus) * atk_bonus, 
                                                               battle_enemy["def"], 
                                                               player_stats["crit"] + crit_bonus,
                                                               ignore_def=ignore_def)
                                        total_dmg += d
                                        if c: any_crit = True
                                    
                                    battle_enemy["hp"] = max(0, battle_enemy["hp"] - total_dmg)
                                    msg = f"{skill_name}! {total_dmg} 데미지!"
                                    if hits > 1: msg = f"{skill_name}({hits}연타)! " + msg
                                    effect_msgs.append(msg)
                                    
                                    if any_crit:
                                        effect_msgs.append(random.choice(CRIT_SCRIPTS))
                                    
                                    # 공격 후 부가 효과
                                    if skill_data.get("stun_chance", 0) > random.random():
                                        enemy_battle_debuffs["기절"] = 1
                                        effect_msgs.append(f"{battle_enemy['name']}이(가) 기절했습니다!")
                                    
                                    if "독무기" in player_battle_buffs:
                                        enemy_battle_debuffs["중독"] = 3
                                        effect_msgs.append("적을 중독시켰습니다!")
                                    
                                    if skill_name == "콜드 빔":
                                        enemy_battle_debuffs["둔화"] = 2
                                        effect_msgs.append("적이 얼어붙어 느려졌습니다!")

                        # 용병 동시 공격 제거 (이제 용병이 직접행동함)
                                # if dmg_rate > 0:
                                #    handle_companion_attack()

                                battle_messages = effect_msgs if effect_msgs else ["스킬 사용!"]
                                battle_step = 1 # 결과 연출 단계로 이동
                                battle_timer = now # 타이머 시작 (0.5초/1초 연출용)
                                menu_nav_timer = now
                            else:
                                battle_messages = ["마나가 부족합니다!"]

        elif battle_step == 1: # 내 메시지 연출
            if now - battle_timer > 1500:
                if battle_enemy["hp"] <= 0:
                    battle_messages = [f"{battle_enemy['name']}을(를) 쓰러트렸다!"]
                    battle_step = 3
                    battle_timer = now
                else:
                    battle_messages = []
                    battle_step = 30
                    battle_companion_idx = 0
                    battle_timer = now

        elif battle_step == 30: # 동료 행동 메뉴
            if not player_party or battle_companion_idx >= len(player_party):
                battle_step = 40 # 적 턴 계산 단계로
                battle_timer = now
            else:
                member = player_party[battle_companion_idx]
                if member.get("hp", 0) <= 0:
                    battle_companion_idx += 1
                    continue # 루프 다음 프레임에서 재진입

                m_data = COMPANION_DB.get(member["name"], {})
                m_skills = m_data.get("skills", [])
                
                pygame.draw.rect(screen, BLACK, (50, HEIGHT - 180, WIDTH - 100, 170))
                draw_text(f"[ {member['name']} ] 의 차례", 70, HEIGHT - 170, YELLOW, small=True)
                
                actions = ["기본 공격"] + m_skills
                if 'battle_comp_select' not in globals(): globals()['battle_comp_select'] = 0
                
                for i, act in enumerate(actions):
                    color = YELLOW if i == battle_comp_select else WHITE
                    draw_text(act, 80, HEIGHT - 130 + i * 30, color)

                if now - menu_nav_timer > 150:
                    if keys[KEY_UP]:
                        globals()['battle_comp_select'] = (battle_comp_select - 1) % len(actions)
                        menu_nav_timer = now
                    elif keys[KEY_DOWN]:
                        globals()['battle_comp_select'] = (battle_comp_select + 1) % len(actions)
                        menu_nav_timer = now

                for event in events:
                    if event.type == pygame.KEYDOWN and event.key == KEY_ACTION_1:
                        sel_action = actions[battle_comp_select]
                        atk_val = player_stats["atk"] * member["atk_rate"]
                        
                        if sel_action == "기본 공격":
                            hd, hc = calculate_damage(atk_val, battle_enemy["def"], 10)
                            battle_enemy["hp"] = max(0, battle_enemy["hp"] - hd)
                            battle_messages = [f"{member['name']}의 공격! {hd} 데미지!"]
                            if hc: battle_messages.append(random.choice(CRIT_SCRIPTS))
                        else:
                            s_data = COMPANION_SKILL_DB.get(sel_action, {})
                            s_type = s_data.get("type", "")
                            s_power = s_data.get("power", 0)
                            msg = f"{member['name']}의 {sel_action}!"
                            sub_msg = ""

                            if s_type == "taunt":
                                globals()['battle_taunt_target'] = battle_companion_idx
                                sub_msg = "적들의 주의를 자신에게 고정시켰습니다!"
                            elif s_type == "heal":
                                player_hp = min(player_max_hp, player_hp + s_power)
                                sub_msg = f"{player_name}님의 HP가 {s_power} 회복되었습니다."
                            elif s_type == "mana":
                                player_mana = min(player_max_mana, player_mana + s_power)
                                sub_msg = f"{player_name}님의 MP가 {s_power} 회복되었습니다."
                            elif s_type == "damage":
                                hd, _ = calculate_damage(atk_val * s_power, battle_enemy["def"], 20)
                                battle_enemy["hp"] = max(0, battle_enemy["hp"] - hd)
                                sub_msg = f"{hd}의 피해를 입혔습니다!"
                            
                            battle_messages = [msg]
                            if sub_msg: battle_messages.append(sub_msg)
                        
                        battle_step = 31 # 동료 메시지 연출 단계
                        battle_timer = now

        elif battle_step == 31: # 동료 메시지 연출
            if now - battle_timer > 1500:
                battle_messages = []
                battle_companion_idx += 1
                if battle_companion_idx >= len(player_party):
                    battle_step = 40 # 모든 동료 종료 후 적 턴 준비
                else:
                    battle_step = 30 # 다음 동료
                battle_timer = now

        elif battle_step == 40: # 적 턴 계산 및 메시지 세팅
            if battle_enemy["hp"] <= 0:
                battle_step = 1 # 승리 체크하러
                continue

            # 적 턴 처리 전 상태 효과 확인
            if "기절" in enemy_battle_debuffs:
                battle_messages = [f"{battle_enemy['name']}은(는) 기절하여 움직일 수 없다!"]
                enemy_battle_debuffs["기절"] -= 1
                if enemy_battle_debuffs["기절"] <= 0: del enemy_battle_debuffs["기절"]
                battle_step = 2 # 바로 연출 단계로
                battle_timer = now
                continue

            boss_skill_used = False
            # (기존 보스 스킬 로직 통합 생략 - 핵심 흐름 위주)
            # 여기서는 편의상 일반 공격 로직만 먼저 정리
            target = "player"
            if battle_taunt_target != -1 and player_party[battle_taunt_target].get("hp",0) > 0:
                target = f"comp{battle_taunt_target}"
            else:
                target_pool = ["player"]
                for i, c in enumerate(player_party):
                    if c.get("hp",0) > 0: target_pool.append(f"comp{i}")
                target = random.choice(target_pool) if random.random() < 0.4 else "player"

            enemy_atk = battle_enemy["atk"]
            if target == "player":
                damage, crit = calculate_damage(enemy_atk, player_stats["def"], battle_enemy["crit"])
                player_hp = max(0, player_hp - damage)
                battle_messages = [f"{battle_enemy['name']}의 공격! {player_name}에게 {damage} 데미지!"]
                if crit: battle_messages.append("치명타를 입었습니다!")
            else:
                c_idx = int(target[-1])
                comp = player_party[c_idx]
                damage, crit = calculate_damage(enemy_atk, player_stats["def"]*0.7, battle_enemy["crit"])
                comp["hp"] = max(0, comp["hp"] - damage)
                battle_messages = [f"{battle_enemy['name']}의 공격! {comp['name']}에게 {damage} 데미지!"]
                if comp["hp"] <= 0: battle_messages.append(f"{comp['name']}이(가) 쓰러졌습니다!")

            battle_step = 2
            battle_timer = now

        elif battle_step == 2: # 적 메시지 연출 및 턴 종료
            if now - battle_timer > 1500:
                battle_messages = []
                battle_turn_count += 1
                battle_step = 0 # 다시 플레이어 메뉴로
                battle_timer = now

        elif battle_step == 20: # 아이템 선택 화면
            pygame.draw.rect(screen, BLACK, (50, HEIGHT - 150, WIDTH - 100, 140))
            draw_text(f"아이템 선택 (X: 취소)", 70, HEIGHT - 140, GREY, small=True)
            
            potions = [item for item in player_inventory if item["type"] == "potion"]
            
            if not potions:
                draw_text("사용할 수 있는 포션이 없습니다.", 80, HEIGHT - 100, WHITE)
            else:
                # 목록 표시
                for i, item in enumerate(potions):
                    color = YELLOW if i == battle_item_select_idx else WHITE
                    draw_text(f"{item['name']} x{item.get('count', 1)} ({item.get('desc', '')})", 80, HEIGHT - 110 + i * 30, color, small=True)
            
            if now - menu_nav_timer > 150:
                if keys[KEY_UP] and potions:
                    battle_item_select_idx = (battle_item_select_idx - 1) % len(potions)
                    menu_nav_timer = now
                elif keys[KEY_DOWN] and potions:
                    battle_item_select_idx = (battle_item_select_idx + 1) % len(potions)
                    menu_nav_timer = now
            
            for event in events:
                if event.type == pygame.KEYDOWN:
                    if event.key == KEY_ACTION_2: # 취소
                        battle_step = 0
                        menu_nav_timer = now
                    
                    if event.key == KEY_ACTION_1 and potions: # 사용
                        item = potions[battle_item_select_idx]
                        eff = item.get("effect")
                        val = item.get("value", 0)
                        
                        if eff == "hp":
                            player_hp = min(player_max_hp, player_hp + val)
                            battle_messages = [f"{item['name']}을(를) 사용하여 체력을 {val} 회복했습니다!"]
                        elif eff == "mana":
                            player_mana = min(player_max_mana, player_mana + val)
                            battle_messages = [f"{item['name']}을(를) 사용하여 마나를 {val} 회복했습니다!"]
                        elif eff == "hp_mana":
                            player_hp = min(player_max_hp, player_hp + val)
                            player_mana = min(player_max_mana, player_mana + val)
                            battle_messages = [f"{item['name']}을(를) 사용하여 HP/MP를 {val} 회복했습니다!"]
                        
                        # 소모
                        item['count'] -= 1
                        if item['count'] <= 0:
                            player_inventory.remove(item)
                        
                        battle_step = 30 # 동료 행동 단계로 이동
                        battle_companion_idx = 0
                        battle_timer = now
                        menu_nav_timer = now

        elif battle_step == 30: # 동료 행동 메뉴
            if not player_party or battle_companion_idx >= len(player_party):
                battle_step = 1 # 적 턴으로
                battle_timer = now
            else:
                member = player_party[battle_companion_idx]
                # 쓰러진 동료는 건너뜀
                if member.get("hp", 1) <= 0:
                    battle_companion_idx += 1
                    continue
                
                m_data = COMPANION_DB.get(member["name"], {})
                m_skills = m_data.get("skills", [])
                
                pygame.draw.rect(screen, BLACK, (50, HEIGHT - 180, WIDTH - 100, 170))
                draw_text(f"[ {member['name']} ] 의 차례 (상태: {m_data['rarity']})", 70, HEIGHT - 170, YELLOW, small=True)
                
                # 행동 리스트 생성
                actions = ["기본 공격"] + m_skills
                if 'battle_comp_select' not in globals(): globals()['battle_comp_select'] = 0
                
                for i, act in enumerate(actions):
                    color = YELLOW if i == battle_comp_select else WHITE
                    draw_text(act, 80, HEIGHT - 130 + i * 30, color)

                if now - menu_nav_timer > 150:
                    if keys[KEY_UP]:
                        globals()['battle_comp_select'] = (battle_comp_select - 1) % len(actions)
                        menu_nav_timer = now
                    elif keys[KEY_DOWN]:
                        globals()['battle_comp_select'] = (battle_comp_select + 1) % len(actions)
                        menu_nav_timer = now

                for event in events:
                    if event.type == pygame.KEYDOWN and event.key == KEY_ACTION_1:
                        if now - menu_nav_timer > 200:
                            sel_action = actions[battle_comp_select]
                            atk_val = player_stats["atk"] * m_data.get("atk_rate", 0.5)
                            
                            if sel_action == "기본 공격":
                                hd, hc = calculate_damage(atk_val, battle_enemy["def"], 10)
                                battle_enemy["hp"] = max(0, battle_enemy["hp"] - hd)
                                battle_messages.append(f"{member['name']}의 공격! {hd} 데미지!")
                            else:
                                # COMPANION_SKILL_DB 참조
                                s_data = COMPANION_SKILL_DB.get(sel_action, {})
                                s_type = s_data.get("type", "")
                                s_power = s_data.get("power", 0)
                                msg = f"{member['name']}의 {sel_action}!"

                                if s_type == "taunt":
                                    globals()['battle_taunt_target'] = battle_companion_idx
                                    msg += " 적들을 자신에게 고정시켰습니다!"
                                elif s_type == "heal":
                                    player_hp = min(player_max_hp, player_hp + s_power)
                                    msg += f" {player_name}님의 HP가 {s_power} 회복되었습니다."
                                elif s_type == "mana":
                                    player_mana = min(player_max_mana, player_mana + s_power)
                                    msg += f" {player_name}님의 MP가 {s_power} 회복되었습니다."
                                elif s_type == "buff":
                                    target_stat = s_data.get("target", "atk")
                                    player_battle_buffs[target_stat if target_stat != "atk" else "공격력"] = s_power
                                    msg += f" {player_name}님의 {target_stat} 능력이 강화되었습니다."
                                elif s_type == "debuff":
                                    target_stat = s_data.get("target", "")
                                    if target_stat == "stun": enemy_battle_debuffs["기절"] = s_power
                                    elif target_stat == "slow": enemy_battle_debuffs["둔화"] = s_power
                                    elif target_stat == "def_down": battle_enemy["def"] = max(0, battle_enemy["def"] - s_power)
                                    msg += " 적에게 상태이상을 부여했습니다."
                                elif s_type == "damage":
                                    hd, _ = calculate_damage(atk_val * s_power, battle_enemy["def"], 20)
                                    battle_enemy["hp"] = max(0, battle_enemy["hp"] - hd)
                                    msg += f" {hd}의 피해를 입혔습니다!"
                                elif s_type == "execute":
                                    if battle_enemy["hp"] < battle_enemy["max_hp"] * s_power and not is_boss_battle:
                                        battle_enemy["hp"] = 0
                                        msg += " 적을 즉시 처형했습니다!"
                                    else:
                                        hd, _ = calculate_damage(atk_val * 2.0, battle_enemy["def"], 20)
                                        battle_enemy["hp"] = max(0, battle_enemy["hp"] - hd)
                                        msg += f" {hd}의 피해를 입혔습니다!"
                                elif s_type == "gold":
                                    stolen = random.randint(50, 200) * (player_level + 1)
                                    player_gold += stolen
                                    msg += f" {stolen}G를 획득했습니다!"
                                elif s_type == "special_full_heal":
                                    player_hp = player_max_hp
                                    player_mana = player_max_mana
                                    player_battle_buffs = {}
                                    msg += " 기적으로 모든 상처를 치유했습니다!"
                                elif s_type == "buff_all":
                                    player_battle_buffs["공격력"] = s_power
                                    player_battle_buffs["방어력"] = s_power
                                    msg += " 전능한 기운으로 공방을 강화합니다."
                                
                                battle_messages.append(msg)
                            
                            battle_step = 31 # 동료 결과 메시지 대기 단계
                            menu_nav_timer = now
                            battle_timer = now

        elif battle_step == 31: # 동료 행동 메시지 연출 대기
            if now - battle_timer > 1500:
                battle_companion_idx += 1
                battle_messages = []
                if battle_companion_idx >= len(player_party):
                    battle_step = 2 # 적 턴으로
                else:
                    battle_step = 30 # 다음 동료
                battle_timer = now
                globals()['battle_comp_select'] = 0
                menu_nav_timer = now

        elif battle_step == 2:
            can_skip = False
            for event in events:
                if event.type == pygame.KEYDOWN and event.key == KEY_ACTION_1:
                    can_skip = True

            if now - battle_timer > 1000 or can_skip:
                # 턴 종료 처리 (독 데미지 등)
                battle_turn_count += 1
                
                # 플레이어 독 데미지 추가
                if "중독" in player_battle_buffs:
                    p_dmg = int(player_max_hp * 0.05)
                    player_hp = max(1, player_hp - p_dmg)
                    battle_messages = [f"중독 상태! HP가 {p_dmg} 감소했습니다."]
                    player_battle_buffs["중독"] -= 1
                    if player_battle_buffs["중독"] <= 0: del player_battle_buffs["중독"]
                    battle_timer = now
                    battle_step = 11
                    continue

                if "중독" in enemy_battle_debuffs:
                    poison_dmg = int(battle_enemy["max_hp"] * 0.05)
                    battle_enemy["hp"] = max(1, battle_enemy["hp"] - poison_dmg) 
                    battle_messages = [f"독 데미지! {battle_enemy['name']}의 HP가 {poison_dmg} 감소했습니다."]
                    enemy_battle_debuffs["중독"] -= 1
                    if enemy_battle_debuffs["중독"] <= 0: del enemy_battle_debuffs["중독"]
                    battle_timer = now
                
                # 버프 기간 감소
                for k in list(player_battle_buffs.keys()):
                    if k == "중독": continue
                    player_battle_buffs[k] -= 1
                    if player_battle_buffs[k] <= 0: del player_battle_buffs[k]
                
                for k in list(enemy_battle_debuffs.keys()):
                    if k not in ["중독", "기절", "둔화"]: 
                        enemy_battle_debuffs[k] -= 1
                        if enemy_battle_debuffs[k] <= 0: del enemy_battle_debuffs[k]

                if not battle_messages or (len(battle_messages)==1 and "공격!" in battle_messages[0]): 
                    battle_messages = []
                    battle_step = 0
                else:
                    battle_step = 11 
                    battle_timer = now

        elif battle_step == 11: # 턴 종료 메시지 출력 후 플레이어 턴
            if now - battle_timer > BATTLE_DELAY:
                battle_messages = []
                battle_step = 0

        elif battle_step == 3:
            if now - battle_timer > BATTLE_DELAY:
                # 경험치 및 보상 획득
                exp_gain = battle_enemy["exp"]
                gold_gain = int(exp_gain * 1.5) + random.randint(0, 5)
                
                player_exp += exp_gain
                player_gold += gold_gain
                
                # 퀘스트 카운트
                if battle_enemy["name"] == "고블린":
                    monster_kills["goblin"] += 1
                elif battle_enemy["name"] == "오크":
                    monster_kills["orc"] += 1
                elif battle_enemy["name"] == "킹 슬라임":
                    monster_kills["king_slime"] += 1
                
                msg = f"승리! 경험치 {exp_gain}, {gold_gain}G 획득"
                
                # 전리품 획득 (30% 확률)
                if random.random() < 0.3:
                    loot_name = battle_enemy.get('loot_item', f"{battle_enemy['name']}의 전리품")
                    loot_price = battle_enemy.get('loot_price', int(exp_gain * 2))
                    add_item_to_inventory({"name": loot_name, "type": "misc", "price": loot_price, "desc": "상점에 판매 가능"})
                    msg += f", {loot_name} 획득!"

                # 희귀 전리품 획득 (5% 확률)
                if random.random() < 0.05 and 'rare_loot' in battle_enemy:
                    rare_name = battle_enemy['rare_loot']
                    rare_price = battle_enemy.get('rare_price', 1000)
                    add_item_to_inventory({"name": rare_name, "type": "misc", "price": rare_price, "desc": "매우 귀한 전리품"})
                    msg += f", {rare_name} 획득!!!"

                
                battle_messages = [msg] # 메시지 설정
                battle_step = 6 # 승리 대기 상태로 이동
                battle_timer = now

        elif battle_step == 6: # 승리 메시지 대기
             if now - battle_timer > 1500: # 1.5초 대기
                # 몬스터 제거 (전투 승리 시)
                if 'battle_target_mob' in globals() and battle_target_mob in field_monsters:
                    field_monsters.remove(battle_target_mob)
                    # battle_target_mob 변수 제거는 밑에서 자동 처리 (여기서는 리스트에서만 제거)

                # 레벨업 체크
                max_exp = get_max_exp(player_level)
                if player_exp >= max_exp:
                    player_exp -= max_exp
                    level_up()
                    state = STATE_LEVELUP
                else:
                    state = STATE_FIELD # 필드 복귀
                    battle_cooldown_timer = now 

                # 퀘스트 목표 달성
                if quest_step == 1 and current_map_index == 0:
                    quest_step = 2
                    update_quest("퀘스트: 촌장에게 돌아가기")
                
                battle_messages = []
        
        elif battle_step == 5: # 도망 성공 대기
            if now - battle_timer > 1000: # 1초 대기
                state = STATE_FIELD
                battle_cooldown_timer = now # 무적 시간 적용
                battle_messages = []
                # 도망 시 몬스터가 사라지지 않게 하려면 battle_target_mob 제거 로직을 건너뛰어야 함
                # 하지만 여기서는 그냥 유지. 만약 사라지게 하려면 remove 호출.
                # 보통 도망치면 몬스터는 그대로 있거나 (다시 싸우면 체력 리셋?), 아니면 사라짐.
                # 편의상 제거하지 않음. 대신 전투 종료 시 battle_target_mob 관련 처리가 3번 단계 뒤에 있음.
                # 5번 단계에서는 그냥 필드로 복귀.

            battle_timer = now

        elif battle_step == 4:
            damage, _ = calculate_damage(battle_enemy["atk"], player_stats["def"], battle_enemy["crit"])
            player_hp = max(0, player_hp - damage)
            battle_messages = [f"{battle_enemy['name']}의 선공! {damage} 데미지!"]
            battle_step = 2
            battle_timer = now

    # ----------------------------------------
    # 레벨업 화면
    # ----------------------------------------
    elif state == STATE_LEVELUP:
        screen.fill(BG_LEVELUP)
        draw_text(f"레벨업! 현재 레벨: {player_level}", WIDTH//2, HEIGHT//2 - 60, YELLOW, center=True)
        draw_text(f"보유 스탯 포인트: {player_stat_points}", WIDTH//2, HEIGHT//2 - 20, WHITE, center=True)
        draw_text("[C]키로 스탯 메뉴를 열어 분배하세요.", WIDTH//2, HEIGHT//2 + 20, WHITE, center=True, small=True)
        draw_text_box("[Z] 계속", WIDTH//2 - 67, HEIGHT//2 + 60, 135, 50, color_bg=BLACK, color_text=YELLOW)
        if keys[KEY_ACTION_1]:
            pygame.time.delay(150)
            state = STATE_FIELD # 마을이 아닌 필드로 복귀
            # 위치는 그대로 유지 (전투 전 위치)

    elif state == STATE_STATS:
        screen.fill(BG_LEVELUP)
        
        # 탭 메뉴
        color_p0 = YELLOW if stat_page == 0 else GREY
        color_p1 = YELLOW if stat_page == 1 else GREY
        color_p2 = YELLOW if stat_page == 2 else GREY
        draw_text("스탯", WIDTH//2 - 120, 30, color_p0, center=True, small=True)
        draw_text("|", WIDTH//2 - 60, 30, WHITE, center=True, small=True)
        draw_text("인벤토리", WIDTH//2, 30, color_p1, center=True, small=True)
        draw_text("|", WIDTH//2 + 60, 30, WHITE, center=True, small=True)
        draw_text("스킬", WIDTH//2 + 120, 30, color_p2, center=True, small=True)

        # 탭 전환
        if not globals().get('stat_adjust_mode', False):
            if now - menu_nav_timer > 150:
                if keys[KEY_LEFT]:
                    stat_page = (stat_page - 1) % 3
                    menu_nav_timer = now
                elif keys[KEY_RIGHT]:
                    stat_page = (stat_page + 1) % 3
                    menu_nav_timer = now

        if stat_page == 0:
            # 스탯 페이지
            draw_text(f"Lv.{player_level} {player_job}", WIDTH//2, 75, YELLOW, center=True)
            max_exp = get_max_exp(player_level)
            draw_text(f"EXP: {player_exp} / {max_exp}", WIDTH//2, 105, (50, 255, 50), center=True)
            draw_text(f"남은 포인트: {stat_menu_points}", WIDTH//2, 135, WHITE, center=True, small=True)

            list_start_y = 175
            for idx, stat_key in enumerate(STAT_ORDER):
                label = STAT_CONFIG[stat_key]["label"]
                base_value = player_stats[stat_key]
                bonus = levelup_allocations[stat_key] * STAT_CONFIG[stat_key]["increment"]
                total_value = base_value + bonus
                text = f"{label}: {total_value}"
                if bonus: text += f" (+{bonus})"
                
                color = WHITE
                if idx == levelup_selected_stat:
                    color = RED if globals().get('stat_adjust_mode', False) else YELLOW
                draw_text(text, WIDTH//2, list_start_y + idx * 40, color, center=True)

            if now - menu_nav_timer > 150:
                if not globals().get('stat_adjust_mode', False):
                    if keys[KEY_UP]:
                        globals()['levelup_selected_stat'] = (levelup_selected_stat - 1) % len(STAT_ORDER)
                        menu_nav_timer = now
                    elif keys[KEY_DOWN]:
                        globals()['levelup_selected_stat'] = (levelup_selected_stat + 1) % len(STAT_ORDER)
                        menu_nav_timer = now
                    for event in events:
                        if event.type == pygame.KEYDOWN and event.key == KEY_ACTION_1:
                            globals()['stat_adjust_mode'] = True
                            menu_nav_timer = now
                else:
                    selected_stat = STAT_ORDER[levelup_selected_stat]
                    stat_info = STAT_CONFIG[selected_stat]
                    if keys[KEY_RIGHT]:
                        if stat_menu_points > 0:
                            levelup_allocations[selected_stat] += 1
                            globals()['stat_menu_points'] -= 1
                            menu_nav_timer = now
                    elif keys[KEY_LEFT]:
                        if levelup_allocations[selected_stat] > 0:
                            levelup_allocations[selected_stat] -= 1
                            globals()['stat_menu_points'] += 1
                            menu_nav_timer = now
                    for event in events:
                        if event.type == pygame.KEYDOWN and event.key == KEY_ACTION_1:
                            globals()['stat_adjust_mode'] = False
                            menu_nav_timer = now

        elif stat_page == 1:
            # 장비/인벤토리 페이지
            draw_text("장비 및 인벤토리", WIDTH//2, 70, YELLOW, center=True)
            
            eq_y = 110
            w_name = player_equipment["weapon"]["name"] if player_equipment["weapon"] else "없음"
            a_name = player_equipment["armor"]["name"] if player_equipment["armor"] else "없음"
            acc_name = player_equipment["accessory"]["name"] if player_equipment["accessory"] else "없음"
            
            draw_text(f"무기: {w_name}", WIDTH//2 - 200, eq_y, WHITE, center=True, small=True)
            draw_text(f"방어구: {a_name}", WIDTH//2, eq_y, WHITE, center=True, small=True)
            draw_text(f"장신구: {acc_name}", WIDTH//2 + 200, eq_y, WHITE, center=True, small=True)
            draw_text(f"소지금: {player_gold}G", WIDTH//2, eq_y + 30, YELLOW, center=True, small=True)
            
            inv_start_y = 180
            if not player_inventory:
                draw_text("비어있음", WIDTH//2, inv_start_y + 40, GREY, center=True)
            else:
                for i, item in enumerate(player_inventory):
                    color = YELLOW if i == stat_inventory_idx else WHITE
                    draw_text(f"{item['name']} x{item.get('count', 1)}", WIDTH//2, inv_start_y + i * 30, color, center=True, small=True)

            if now - menu_nav_timer > 150:
                if keys[KEY_UP]:
                    stat_inventory_idx = max(0, stat_inventory_idx - 1)
                    menu_nav_timer = now
                elif keys[KEY_DOWN]:
                    if player_inventory:
                        stat_inventory_idx = min(len(player_inventory) - 1, stat_inventory_idx + 1)
                    menu_nav_timer = now
            
            for event in events:
                if event.type == pygame.KEYDOWN and event.key == KEY_ACTION_1 and player_inventory:
                    if stat_inventory_idx >= len(player_inventory):
                        stat_inventory_idx = max(0, len(player_inventory) - 1)
                    
                    item = player_inventory[stat_inventory_idx]
                    if item["type"] in ["weapon", "armor", "accessory"]:
                        if "job" in item and item["job"] != player_job and player_job != "초보자":
                             pass # 직업 제한
                        else:
                            eq_type = item["type"]
                            current = player_equipment[eq_type]
                            
                            # 기존 장비 해제 (스탯 감소)
                            if current:
                                for s_key in STAT_ORDER:
                                    if s_key in current:
                                        player_stats[s_key] -= current[s_key]
                                add_item_to_inventory(current)
                            
                            # 새 장비 장착 (스탯 증가)
                            player_equipment[eq_type] = item.copy()
                            player_equipment[eq_type]['count'] = 1
                            for s_key in STAT_ORDER:
                                if s_key in item:
                                    player_stats[s_key] += item[s_key]
                            
                            # HP/MP 최대치 업데이트
                            player_max_hp = player_stats["hp"]
                            player_max_mana = player_stats["mana"]
                            
                            item['count'] -= 1
                            if item['count'] <= 0: 
                                player_inventory.pop(stat_inventory_idx)
                                stat_inventory_idx = max(0, stat_inventory_idx - 1)
                            menu_nav_timer = now
                    elif item["type"] == "potion":
                        # 포션 사용
                        if item.get("effect") == "hp": player_hp = min(player_max_hp, player_hp + item.get("value", 0))
                        item['count'] -= 1
                        if item['count'] <= 0: 
                            player_inventory.pop(stat_inventory_idx)
                            stat_inventory_idx = max(0, stat_inventory_idx - 1)
                        menu_nav_timer = now

        elif stat_page == 2:
            # 스킬 페이지
            draw_text(f"스킬 포인트: {skill_points}", WIDTH//2, 80, YELLOW, center=True)
            my_skills = JOB_DB[player_job]["skills"]
            if 'skill_selected_idx' not in globals(): globals()['skill_selected_idx'] = 0
            
            for idx, s_name in enumerate(my_skills):
                lv = skill_levels.get(s_name, 1)
                color = YELLOW if idx == skill_selected_idx else WHITE
                draw_text(f"{s_name} (Lv.{lv})", 100, 150 + idx * 40, color)
            
            sel_skill = my_skills[skill_selected_idx]
            s_data = SKILLS.get(sel_skill, {})
            lv = skill_levels.get(sel_skill, 1)
            
            # 수치 정보 추가
            dmg_base = s_data.get('dmg_rate', 0)
            curr_dmg = dmg_base + (lv-1)*0.1
            next_dmg = dmg_base + lv*0.1
            
            info_text = f"[{sel_skill}] Lv.{lv}\n{s_data.get('desc', '기본 공격 스킬')}\n"
            if dmg_base > 0:
                info_text += f"현재 위력: {curr_dmg:.1f}x -> 진화: {next_dmg:.1f}x"
                
            draw_text_box(info_text, 400, 150, 350, 200)

            for event in events:
                if event.type == pygame.KEYDOWN:
                    if event.key == KEY_ACTION_1 and skill_points > 0:
                        skill_points -= 1
                        skill_levels[sel_skill] = lv + 1
                        menu_nav_timer = now
                    elif event.key == pygame.K_UP:
                        globals()['skill_selected_idx'] = (skill_selected_idx - 1) % len(my_skills)
                        menu_nav_timer = now
                    elif event.key == pygame.K_DOWN:
                        globals()['skill_selected_idx'] = (skill_selected_idx + 1) % len(my_skills)
                        menu_nav_timer = now

    elif state == STATE_RECRUIT:
        screen.fill(BG_SELECT)
        draw_text("용병 모집 (N/R/SR/SSR)", WIDTH//2, 55, YELLOW, center=True)
        draw_text(f"보유 골드: {player_gold}G", WIDTH//2, 95, WHITE, center=True, small=True)
        
        # 상단 탭
        color_r = YELLOW
        color_p = GREY
        draw_text(" [ 고용 ] ", WIDTH//2 - 80, 25, color_r, center=True, small=True)
        draw_text("   대열   ", WIDTH//2 + 80, 25, color_p, center=True, small=True)
        
        if not gacha_list:
            draw_text(f"[1] 1회 소환: {GACHA_COST_1}G", WIDTH//2 - 150, 150, WHITE, center=True, small=True)
            draw_text(f"[2] 11회 소환: {GACHA_COST_11}G (SR확정)", WIDTH//2 + 150, 150, YELLOW, center=True, small=True)
            draw_text("( → 방향키: 대열 관리 )", WIDTH//2, HEIGHT - 50, GREY, center=True, small=True)

        if gacha_list:
            res_name = gacha_list[gacha_view_idx]
            data = COMPANION_DB[res_name]
            rarity = data['rarity']
            color = get_rarity_color(rarity)
            
            draw_text(f"결과 ({gacha_view_idx+1}/{len(gacha_list)})", WIDTH//2, 210, GREY, center=True, small=True)
            draw_text(f"!!! {rarity} 등급 !!!", WIDTH//2, 260, color, center=True)
            draw_text(f"[{res_name}]", WIDTH//2, 310, WHITE, center=True)
            draw_text(data['desc'], WIDTH//2, 360, GREY, center=True, small=True)
            
            draw_text("[Z] 다음 결과 보기  [X] 대화 종료", WIDTH//2, HEIGHT - 80, WHITE, center=True, small=True)
        else:
            draw_text("모험의 동반자를 찾으십니까?", WIDTH//2, HEIGHT//2, WHITE, center=True)
            draw_text("[1] 1회 소환  [2] 11회 소환  [X] 대화 종료", WIDTH//2, HEIGHT - 100, WHITE, center=True, small=True)
        
        def perform_gacha(guaranteed_sr=False):
            r = random.randint(1, 100)
            target_rarities = ["N", "R", "SR", "SSR"]
            
            if guaranteed_sr:
                r = random.randint(1, 13) # SR(10) + SSR(2) 확률 근사치
                if r <= 2: tr = "SSR"
                else: tr = "SR"
            else:
                if r <= 2: tr = "SSR"
                elif r <= 12: tr = "SR"
                elif r <= 42: tr = "R"
                else: tr = "N"
            
            pool = [name for name, d in COMPANION_DB.items() if d['rarity'] == tr]
            res = random.choice(pool)
            return res

        for event in events:
            if event.type == pygame.KEYDOWN:
                if gacha_list:
                    if event.key == KEY_ACTION_1: # 다음 결과
                        gacha_view_idx += 1
                        if gacha_view_idx >= len(gacha_list):
                            gacha_list = []
                            gacha_view_idx = 0
                    elif event.key == KEY_ACTION_2: # 종료
                        gacha_list = []
                        gacha_view_idx = 0
                        state = STATE_TOWN
                else:
                    if event.key == pygame.K_1: # 1회
                        if player_gold >= GACHA_COST_1:
                            player_gold -= GACHA_COST_1
                            res = perform_gacha()
                            gacha_list = [res]
                            
                            # 파티 관리 로직 (보유 용병고에 추가)
                            existing = next((m for m in owned_companions if m['name'] == res), None)
                            if existing:
                                # 중복 획득 시 강화
                                existing["power_lv"] = existing.get("power_lv", 0) + 1
                                existing["atk_rate"] += 0.05
                            else:
                                m_data = COMPANION_DB[res]
                                new_comp = {
                                    "name": res, 
                                    "atk_rate": m_data['atk_rate'],
                                    "hp": int(player_max_hp * m_data["hp_rate"]),
                                    "max_hp": int(player_max_hp * m_data["hp_rate"]),
                                    "power_lv": 0,
                                    "rarity": m_data["rarity"]
                                }
                                owned_companions.append(new_comp)
                                # 파티가 비어있으면 자동 참여 (최대 2명)
                                if len(player_party) < 2:
                                    player_party.append(new_comp)
                        menu_nav_timer = now
                    elif event.key == pygame.K_2: # 11회
                        if player_gold >= GACHA_COST_11:
                            player_gold -= GACHA_COST_11
                            results = []
                            for i in range(10): results.append(perform_gacha())
                            results.append(perform_gacha(guaranteed_sr=True))
                            gacha_list = results
                            
                            for res in results:
                                existing = next((m for m in owned_companions if m['name'] == res), None)
                                if existing:
                                    existing["power_lv"] = existing.get("power_lv", 0) + 1
                                    existing["atk_rate"] += 0.02
                                else:
                                    m_data = COMPANION_DB[res]
                                    new_comp = {
                                        "name": res, 
                                        "atk_rate": m_data['atk_rate'],
                                        "hp": int(player_max_hp * m_data["hp_rate"]),
                                        "max_hp": int(player_max_hp * m_data["hp_rate"]),
                                        "power_lv": 0,
                                        "rarity": m_data["rarity"]
                                    }
                                    owned_companions.append(new_comp)
                                    if len(player_party) < 2:
                                        player_party.append(new_comp)
                        menu_nav_timer = now
                    elif event.key == pygame.K_RIGHT and not gacha_list:
                        state = STATE_PARTY
                        menu_nav_timer = now
                    elif event.key == KEY_ACTION_2: # 종료
                        gacha_list = []
                        gacha_view_idx = 0
                        state = STATE_TOWN
                        menu_nav_timer = now

    elif state == STATE_PARTY:
        screen.fill(BG_SELECT)
        # 상단 탭
        color_r = GREY
        color_p = YELLOW
        draw_text("   고용   ", WIDTH//2 - 80, 25, color_r, center=True, small=True)
        draw_text(" [ 대열 ] ", WIDTH//2 + 80, 25, color_p, center=True, small=True)
        draw_text("( ← 방향키로 고용 화면 이동 )", WIDTH//2, HEIGHT - 30, GREY, center=True, small=True)

        draw_text("대열 관리 (최대 2명 편성)", WIDTH//2, 65, YELLOW, center=True)
        draw_text(f"보유 동료 수: {len(owned_companions)}명", WIDTH//2, 100, WHITE, center=True, small=True)
        
        if 'party_scroll_idx' not in globals(): globals()['party_scroll_idx'] = 0
        
        # 보유 용병 리스트 출력 (한 페이지에 8명)
        start_y = 150
        for i, comp in enumerate(owned_companions[party_scroll_idx:party_scroll_idx+8]):
            idx = party_scroll_idx + i
            is_active = comp in player_party
            color = GREEN if is_active else WHITE
            y_pos = start_y + i * 45
            
            p_indicator = "[참전]" if is_active else "[대기]"
            text = f"{p_indicator} {comp['name']} (Lv.{comp['power_lv']}) - {comp['rarity']}"
            
            draw_text(text, 100, y_pos, color, small=True)
            draw_text(f"[{i+1}]", 60, y_pos, YELLOW, small=True)

        draw_text("[1~8] 편성/해제  [X] 마을로 돌아가기", WIDTH//2, HEIGHT - 50, WHITE, center=True, small=True)

        for event in events:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LEFT:
                    state = STATE_RECRUIT
                    menu_nav_timer = now
                elif event.key == KEY_ACTION_2:
                    state = STATE_TOWN
                elif pygame.K_1 <= event.key <= pygame.K_8:
                    rel_idx = event.key - pygame.K_1
                    abs_idx = party_scroll_idx + rel_idx
                    if abs_idx < len(owned_companions):
                        comp = owned_companions[abs_idx]
                        if comp in player_party:
                            player_party.remove(comp)
                        else:
                            if len(player_party) < 2:
                                player_party.append(comp)
                            else:
                                # 이미 2명이면 교체 등 처리는 나중에 더 고도화 가능
                                pass
    elif state == STATE_STORE:
        screen.fill(BG_LEVELUP)
        
        if 'store_mode' not in globals():
            store_mode = 0 # 0: 구매, 1: 판매
        if 'store_select_idx' not in globals():
            store_select_idx = 0
        if 'store_scroll_offset' not in globals():
            store_scroll_offset = 0
        if 'store_msg' not in globals():
            store_msg = ""
            store_msg_timer = 0
        if 'store_adjust_mode' not in globals():
            store_adjust_mode = False
            store_sell_qty = 1
            
        # 탭 메뉴
        color_buy = YELLOW if store_mode == 0 else GREY
        color_sell = YELLOW if store_mode == 1 else GREY
        draw_text("구매", WIDTH//2 - 60, 25, color_buy, center=True, small=True)
        draw_text("|", WIDTH//2, 25, WHITE, center=True, small=True)
        draw_text("판매", WIDTH//2 + 60, 25, color_sell, center=True, small=True)
        draw_text("[←/→] 탭 전환", WIDTH//2, 45, GREY, center=True, small=True)

        draw_text("상점", WIDTH//2, 60, YELLOW, center=True)
        draw_text(f"보유 골드: {player_gold}G", WIDTH//2, 90, WHITE, center=True)
        
        # 탭 전환 (조절 모드 아닐 때 방향키로도 가능)
        if not store_adjust_mode:
            if keys[KEY_TAB_L] and store_mode != 0: 
                store_mode = 0
                store_select_idx = 0
                store_scroll_offset = 0
                store_msg = ""
            if keys[KEY_TAB_R] and store_mode != 1: 
                store_mode = 1
                store_select_idx = 0
                store_scroll_offset = 0
                store_msg = ""
            if now - menu_nav_timer > 150:
                if keys[KEY_LEFT] and store_mode == 1:
                    store_mode = 0
                    store_select_idx = 0
                    store_scroll_offset = 0
                    menu_nav_timer = now
                elif keys[KEY_RIGHT] and store_mode == 0:
                    store_mode = 1
                    store_select_idx = 0
                    store_scroll_offset = 0
                    menu_nav_timer = now

        MAX_DISPLAY = 7

        if store_mode == 0: # 구매
             # 레벨 및 직업별 아이템 필터링
            allowed_items = [
                (k, v) for k, v in ITEM_DB.items() 
                if player_level >= v.get("min_lv", 1) and (v.get("job") == player_job or "job" not in v)
            ]
            
            # 튜토리얼 퀘스트 2 필터링
            if quest_step == 11:
                allowed_items = [(k, v) for k, v in allowed_items if k in ["wooden_sword", "leather_armor"]]
            
            target_list = allowed_items
        else: # 판매
            target_list = player_inventory
        
        # 인덱스 안전 장치
        if target_list:
            store_select_idx = max(0, min(store_select_idx, len(target_list) - 1))
        
        # 스크롤 로직
        if store_select_idx < store_scroll_offset:
            store_scroll_offset = store_select_idx
        elif store_select_idx >= store_scroll_offset + MAX_DISPLAY:
            store_scroll_offset = store_select_idx - MAX_DISPLAY + 1
        
        visible_items = target_list[store_scroll_offset : store_scroll_offset + MAX_DISPLAY]

        # 목록 표시
        if not target_list:
            msg = "구매 가능한 아이템이 없습니다." if store_mode == 0 else "판매할 아이템이 없습니다."
            draw_text(msg, WIDTH//2, 200, GREY, center=True)
        else:
            for i, item_data in enumerate(visible_items):
                # 데이터 정규화 (구매: (key, dict), 판매: dict)
                if store_mode == 0:
                    current_item = item_data[1]
                else:
                    current_item = item_data
                    
                abs_idx = store_scroll_offset + i
                rarity = current_item.get("rarity", "커먼")
                item_color = get_rarity_color(rarity)
                if abs_idx == store_select_idx:
                    item_color = YELLOW # 선택 강조

                
                name_to_draw = current_item["name"]
                y_pos = 150 + i * 30
                if store_mode == 0:
                    price = current_item['price']
                    draw_text(f"[{rarity}] {name_to_draw}", 150, y_pos, item_color, small=True)
                    draw_text(f"{price}G", 550, y_pos, WHITE, small=True)
                else: 
                    price = int(current_item.get('price', 0) * 0.5)
                    count = current_item.get("count", 1)
                    text = f"[{rarity}] {name_to_draw}"
                    if count > 1: text += f" * {count}"
                    draw_text(text, 150, y_pos, item_color, small=True)
                    draw_text(f"{price}G", 550, y_pos, WHITE, small=True)


                
                # 선택된 아이템 설명 및 가격 정보
                if abs_idx == store_select_idx:
                    if store_adjust_mode:
                        desc = f"▶ 판매 수량 조절: {store_sell_qty}개 (총 {price * store_sell_qty}G)"
                    else:
                        desc = f"▷ {current_item.get('desc', '설명 없음')}"
                        if store_mode == 0 and current_item.get("min_lv", 1) > 1 and current_item.get("min_lv", 1) != 999:
                            desc += f" (Lv.{current_item['min_lv']} 필요)"
                    
                    # 툴팁 위치를 목록 하단으로 이동하여 가격과 겹치지 않게 함
                    pygame.draw.rect(screen, (40, 40, 45), (145, 370, 510, 50))
                    pygame.draw.rect(screen, WHITE, (145, 370, 510, 50), 1)
                    draw_text(desc, 155, 385, GREEN if not store_adjust_mode else RED, small=True)

        # 하단 도움말
        if store_adjust_mode:
            help_text = "[←/→] 수량 조절  [Z] 판매 확정"
        else:
            action_label = "구매" if store_mode == 0 else "판매 시작"
            help_text = f"[↑/↓] 선택  [←/→] 탭 전환  [Z] {action_label}  [X] 나가기"
        draw_text(help_text, WIDTH//2, HEIGHT - 50, WHITE, center=True, small=True)

        if store_msg and now - store_msg_timer < 1500:
             draw_text(store_msg, WIDTH//2, HEIGHT - 100, RED if "부족" in store_msg else BLUE, center=True)

        # 키 입력 (방향키는 keysPolling 유지하여 연속 이동 가능)
        if now - menu_nav_timer > 150:
            if not store_adjust_mode:
                if keys[KEY_UP]:
                    if target_list:
                        store_select_idx = (store_select_idx - 1) % len(target_list)
                        menu_nav_timer = now
                elif keys[KEY_DOWN]:
                    if target_list:
                        store_select_idx = (store_select_idx + 1) % len(target_list)
                        menu_nav_timer = now
            else:
                # 수량 조절 모드
                current_data = target_list[store_select_idx]
                
                if store_mode == 0: # 구매
                    # current_data는 (key, dict) 튜플
                    item_info = current_data[1]
                    price = item_info.get('price', 999999)
                    max_buy_possible = max(1, player_gold // price) if price > 0 else 1
                    
                    if keys[KEY_RIGHT]:
                        store_buy_qty = min(max_buy_possible, store_buy_qty + 1)
                        menu_nav_timer = now - 50
                    elif keys[KEY_LEFT]:
                        store_buy_qty = max(1, store_buy_qty - 1)
                        menu_nav_timer = now - 50
                
                else: # 판매
                    # current_data는 dict
                    item_info = current_data
                    max_sell_possible = item_info.get('count', 1)

                    if keys[KEY_RIGHT]:
                        store_sell_qty = min(max_sell_possible, store_sell_qty + 1)
                        menu_nav_timer = now - 50
                    elif keys[KEY_LEFT]:
                        store_sell_qty = max(1, store_sell_qty - 1)
                        menu_nav_timer = now - 50

        # 선택 및 확정 액션 [KEYDOWN으로 통일]
        for event in events:
            if event.type == pygame.KEYDOWN and event.key == KEY_ACTION_1:
                if now - menu_nav_timer > 300 and target_list:
                    if not store_adjust_mode:
                        if store_mode == 0: # 구매 모드 진입
                            store_adjust_mode = True
                            store_buy_qty = 1
                            menu_nav_timer = now
                        else: # 판매 모드 진입
                            store_adjust_mode = True
                            store_sell_qty = 1
                            menu_nav_timer = now
                    else: # 수량 조절 후 확정
                        if store_mode == 0: # 구매 확정
                            item_key, current_item = target_list[store_select_idx]
                            total_price = current_item["price"] * store_buy_qty
                            if player_gold >= total_price:
                                player_gold -= total_price
                                new_item_data = current_item.copy()
                                new_item_data["key"] = item_key
                                add_item_to_inventory(new_item_data, store_buy_qty)
                                store_msg = f"{current_item['name']} {store_buy_qty}개 구매 완료!"
                                store_msg_timer = now
                                menu_nav_timer = now + 150
                                store_adjust_mode = False # 구매 후 조절 모드 해제
                            else:
                                store_msg = "골드가 부족합니다."
                                store_msg_timer = now
                                menu_nav_timer = now
                        else: # 판매 확정
                            removed_item = target_list[store_select_idx]
                            sell_price = int(removed_item.get('price', 0) * 0.5)
                            total_gold = sell_price * store_sell_qty
                            player_gold += total_gold
                            
                            removed_item['count'] -= store_sell_qty
                            if removed_item['count'] <= 0:
                                player_inventory.remove(removed_item)

                            store_msg = f"{removed_item['name']} {store_sell_qty}개 판매 완료!"
                            store_msg_timer = now
                            store_adjust_mode = False
                            menu_nav_timer = now + 200
                            # 판매 후 인덱스 조정
                            if store_select_idx >= len(player_inventory):
                                store_select_idx = max(0, len(player_inventory) - 1)
        
        if keys[KEY_ACTION_2]: # X키
            if now - menu_nav_timer > 200:
                if store_adjust_mode:
                    store_adjust_mode = False
                else:
                    state = STATE_TOWN
                menu_nav_timer = now
                store_msg = ""

    # ----------------------------------------
    # 직업 선택 (Redesigned)
    # ----------------------------------------
    elif state == STATE_JOB_SELECT:
        screen.fill((20, 20, 30)) # 전용 어두운 배경
        
        # 상단 헤더
        pygame.draw.rect(screen, (40, 40, 60), (0, 0, WIDTH, 80))
        pygame.draw.line(screen, YELLOW, (0, 80), (WIDTH, 80), 2)
        draw_text("모험의 길을 선택하세요", WIDTH//2, 40, YELLOW, center=True)

        jobs = ["전사", "도적", "마법사", "사수"]
        job_descs = {
            "전사": "강인한 생존력과 방어 기술을 통해 안정적으로 전투를 이끌어갑니다.",
            "도적": "빠른 행동력과 높은 치명타 확률로 전투의 흐름을 빠르게 가져옵니다.",
            "마법사": "강력한 주문 공격과 마나 효율을 바탕으로 적에게 치명적인 일격을 가합니다.",
            "사수": "정교한 명중률과 균형 잡힌 성장을 통해 다재다능한 전투가 가능합니다."
        }
        
        if 'job_select_idx' not in globals():
            job_select_idx = 0
            
        # 왼쪽: 직업 목록
        list_x = 50
        list_y = 120
        for i, job in enumerate(jobs):
            is_sel = (i == job_select_idx)
            box_color = (60, 60, 80) if is_sel else (40, 40, 50)
            text_color = YELLOW if is_sel else WHITE
            
            # 버튼 형태 박스
            pygame.draw.rect(screen, box_color, (list_x, list_y + i*70, 200, 60))
            if is_sel:
                pygame.draw.rect(screen, YELLOW, (list_x, list_y + i*70, 200, 60), 2)
            
            draw_text(f"{job}", list_x + 100, list_y + i*70 + 30, text_color, center=True)

        # 오른쪽: 상세 정보
        detail_x = 280
        detail_y = 120
        detail_w = 470
        detail_h = 400
        
        pygame.draw.rect(screen, (30, 30, 45), (detail_x, detail_y, detail_w, detail_h))
        pygame.draw.rect(screen, GREY, (detail_x, detail_y, detail_w, detail_h), 2)

        selected_job_name = jobs[job_select_idx]
        job_data = JOB_DB[selected_job_name]
        
        # 직업 타이틀 및 설명
        draw_text(f"[{selected_job_name}]", detail_x + 20, detail_y + 20, YELLOW)
        
        # 설명 (텍스트 박스 활용)
        desc_h = draw_text_box(job_descs[selected_job_name], detail_x + 20, detail_y + 60, detail_w - 40, 60, color_bg=(30, 30, 45), small=True)
        
        # 기본 스탯 표시
        stat_y = detail_y + 140
        draw_text("- 초기 능력치 -", detail_x + 20, stat_y, WHITE, small=True)
        
        base_stats = job_data["base"]
        for j, s_key in enumerate(STAT_ORDER):
            s_label = STAT_CONFIG[s_key]["label"]
            s_val = base_stats[s_key]
            
            # 스탯 바 배경
            bar_x = detail_x + 120
            bar_y = stat_y + 30 + j*25
            pygame.draw.rect(screen, (50, 50, 50), (bar_x, bar_y, 250, 15))
            
            # 스탯별 가중치 적용 (HP/Mana는 350 기준, 나머지는 35 기준 하도록 조정하여 바 길이를 체감있게 만듦)
            max_val = 350 if s_key in ["hp", "mana"] else 35
            bar_w = min(250, int((s_val / max_val) * 250))
            
            bar_color = GREEN if s_key in ["hp", "def"] else (100, 150, 255) if s_key in ["mana", "atk"] else YELLOW
            pygame.draw.rect(screen, bar_color, (bar_x, bar_y, bar_w, 15))
            
            draw_text(f"{s_label}", detail_x + 30, bar_y + 7, WHITE, small=True)
            draw_text(f"{s_val}", bar_x + 260, bar_y + 7, WHITE, small=True)

        # 보유 스킬 맛보기
        skill_y = stat_y + 200
        draw_text("- 주요 스킬 -", detail_x + 20, skill_y, WHITE, small=True)
        skills_str = ", ".join(job_data["skills"][:3]) + " 등"
        draw_text(skills_str, detail_x + 30, skill_y + 30, (200, 200, 200), small=True)

        # 하단 안내
        draw_text("[↑/↓] 직업 탐색  [Z] 전직 결정", WIDTH//2, HEIGHT - 40, WHITE, center=True, small=True)
        
        # 키 입력 처리
        if now - menu_nav_timer > 300:
            if keys[KEY_UP]:
                job_select_idx = (job_select_idx - 1) % len(jobs)
                menu_nav_timer = now
            elif keys[KEY_DOWN]:
                job_select_idx = (job_select_idx + 1) % len(jobs)
                menu_nav_timer = now
                
            for event in events:
                if event.type == pygame.KEYDOWN and event.key == KEY_ACTION_1:
                    selected_job = jobs[job_select_idx]
                    old_base = JOB_DB["초보자"]["base"]
                    new_base = JOB_DB[selected_job]["base"]
                    
                    # 스탯 보정 (기존 베이스와 새 베이스 차이 더하기)
                    for key in STAT_ORDER:
                        player_stats[key] += (new_base[key] - old_base[key])
                        
                    player_job = selected_job
                    player_max_hp = player_stats["hp"]
                    player_hp = player_max_hp
                    player_max_mana = player_stats["mana"]
                    player_mana = player_max_mana
                    
                    state = STATE_TOWN
                    menu_nav_timer = now


    # ----------------------------------------
    # 설정 (키 설정)
    # ----------------------------------------
    # ----------------------------------------
    # 설정 (키 설정)
    # ----------------------------------------
    elif state == STATE_SETTINGS:
        screen.fill(BG_LEVELUP)
        draw_text("환경 설정", WIDTH//2, 30, YELLOW, center=True)
        draw_text("방향키로 선택/조절, [Z]키로 키변경, [Esc] 저장 후 닫기", WIDTH//2, 60, WHITE, center=True, small=True)

        if 'settings_select_idx' not in globals():
            settings_select_idx = 0
        if 'is_rebinding' not in globals():
            is_rebinding = False

        # --- 메뉴 목록 구성 ---
        # 1. 해상도 (별도 처리)
        # 2. 키 설정 리스트
        
        # 키 목록 정의
        key_config_list = [
            ("위쪽 이동", "KEY_UP"),
            ("아래 이동", "KEY_DOWN"),
            ("왼쪽 이동", "KEY_LEFT"),
            ("오른쪽 이동", "KEY_RIGHT"),
            ("확인/공격 (Z)", "KEY_ACTION_1"),
            ("취소/스킬 (X)", "KEY_ACTION_2"),
            ("메뉴/아이템 (C)", "KEY_ACTION_3"),
            ("도망 (V)", "KEY_ACTION_4"),
            ("탭 왼쪽 (Q)", "KEY_TAB_L"),
            ("탭 오른쪽 (W)", "KEY_TAB_R"),
            ("스탯메뉴 (C)", "KEY_MENU_OPEN")
        ]
        
        total_items = 1 + len(key_config_list) # 해상도 + 키 설정들

        # 1. 해상도 표시
        res_y = 100
        is_res_sel = (settings_select_idx == 0)
        res_col = YELLOW if is_res_sel else WHITE
        
        mode_str = RESOLUTIONS[current_res_idx]
        if mode_str != "Fullscreen":
            mode_str = f"{mode_str[0]} x {mode_str[1]}"
            
        draw_text(f"해상도: < {mode_str} >", 150, res_y, res_col)
        if is_res_sel:
            draw_text("◀ ▶ 키로 조절", 500, res_y, GREEN, small=True)

        # 2. 키 설정 표시
        start_y = 150
        for i, (label, var_name) in enumerate(key_config_list):
            is_sel = (settings_select_idx == i + 1)
            col = YELLOW if is_sel else WHITE
            
            # 현재 키 값 가져오기
            current_key_code = globals()[var_name]
            key_name = pygame.key.name(current_key_code)
            
            # 리바인딩 중이면 표시
            val_text = key_name
            if is_sel and is_rebinding:
                val_text = "입력 대기 중..."
                col = GREEN
            
            draw_text(f"{label}", 150, start_y + i * 35, col, small=True)
            draw_text(f": {val_text}", 400, start_y + i * 35, col, small=True)

        # 키 입력 처리
        if not is_rebinding:
            if now - menu_nav_timer > 150:
                if keys[KEY_UP]:
                    settings_select_idx = (settings_select_idx - 1) % total_items
                    menu_nav_timer = now
                elif keys[KEY_DOWN]:
                    settings_select_idx = (settings_select_idx + 1) % total_items
                    menu_nav_timer = now
                
                # 해상도 조절 (인덱스 0일 때)
                if settings_select_idx == 0:
                    if keys[KEY_LEFT]:
                        new_idx = (current_res_idx - 1) % len(RESOLUTIONS)
                        set_display_mode(new_idx)
                        menu_nav_timer = now + 100 # 반동 방지
                    elif keys[KEY_RIGHT]:
                        new_idx = (current_res_idx + 1) % len(RESOLUTIONS)
                        set_display_mode(new_idx)
                        menu_nav_timer = now + 100

            for event in events:
                if event.type == pygame.KEYDOWN:
                    if event.key == KEY_ACTION_1:
                        # 키 설정 항목인 경우에만 리바인딩 모드 진입
                        if settings_select_idx > 0:
                            is_rebinding = True
                            
        else: # 리바인딩 중
            for event in events:
                if event.type == pygame.KEYDOWN:
                    # ESC는 취소
                    if event.key == pygame.K_ESCAPE:
                        is_rebinding = False
                    else:
                        # 키 적용 (인덱스 보정 -1)
                        target_var_name = key_config_list[settings_select_idx - 1][1]
                        globals()[target_var_name] = event.key
                        is_rebinding = False
                val_text = "입력 대기..."
            else:
                val = globals()[var_name]
                val_text = pygame.key.name(val)
            
            y_pos = 100 + i * 40
            draw_text(f"{label}: {val_text}", WIDTH//2, y_pos, color, center=True)

        # 키 입력 처리
        # 리바인딩 중일 때는 공통 이벤트 루프에서 처리하기 어려울 수 있으므로
        # 여기서 events 를 참조하여 처리 (상단 루프에서 events 변수 가져옴)
        # 단, events 는 매 프레임 초기화되므로 여기서도 접근 가능
        
        if is_rebinding:
            # 리바인딩 중: 키 입력 대기
            for event in events:
                if event.type == pygame.KEYDOWN:
                    # 키 변경
                    target_var_name = key_config_list[settings_select_idx][1]
                    globals()[target_var_name] = event.key
                    is_rebinding = False
                    # 약간의 딜레이
                    menu_nav_timer = now
        else:
            # 메뉴 이동
            if now - menu_nav_timer > 150:
                if keys[KEY_UP]:
                    settings_select_idx = max(0, settings_select_idx - 1)
                    if settings_select_idx < settings_scroll_offset:
                        settings_scroll_offset = settings_select_idx
                    menu_nav_timer = now
                elif keys[KEY_DOWN]:
                    settings_select_idx = min(len(key_config_list) - 1, settings_select_idx + 1)
                    if settings_select_idx >= settings_scroll_offset + MAX_SHOW:
                        settings_scroll_offset = settings_select_idx - MAX_SHOW + 1
                    menu_nav_timer = now
            
            if keys[KEY_ACTION_1]: # 변경 모드 진입
                if now - menu_nav_timer > 200:
                    is_rebinding = True
                    menu_nav_timer = now

    # ----------------------------------------
    # 대장간 (Blacksmith)
    # ----------------------------------------
    elif state == STATE_BLACKSMITH:
        screen.fill(BG_LEVELUP)
        draw_text("대장간 - 장비 강화", WIDTH//2, 40, YELLOW, center=True)
        
        # 보유 중인 장비만 필터링 (장착 중인 장비 제외, 인벤토리에 있는 것만)
        upgradeable_items = [it for it in player_inventory if it['type'] in ['weapon', 'armor']]
        
        if not upgradeable_items:
            draw_text("강화할 수 있는 장비가 인벤토리에 없습니다.", WIDTH//2, HEIGHT//2 - 20, GREY, center=True)
            draw_text("(장착 중인 장비는 해제 후 강화 가능합니다)", WIDTH//2, HEIGHT//2 + 20, GREY, center=True, small=True)
            draw_text("[X] 나가기", WIDTH//2, HEIGHT - 50, WHITE, center=True)
        else:
            # 목록 표시
            draw_text("강화할 장비를 선택하세요", 100, 80, WHITE, small=True)
            for i, item in enumerate(upgradeable_items):
                rarity = item.get("rarity", "커먼")
                color = get_rarity_color(rarity)
                if i == blacksmith_select_idx: color = YELLOW

                
                enh = item.get("enhancement", 0)
                text = f"[{rarity}] {item['name']} (+{enh})"
                draw_text(text, 100, 110 + i * 35, color)

            
            # 선택된 아이템 정보
            if 'blacksmith_select_idx' not in globals(): blacksmith_select_idx = 0
            if blacksmith_select_idx >= len(upgradeable_items): blacksmith_select_idx = 0
            
            sel_item = upgradeable_items[blacksmith_select_idx]
            enh = sel_item.get("enhancement", 0)
            
            # 비용 및 확률 설정 (아이템 가격 비례)
            base_price = sel_item.get("price", 1000)
            gold_cost = int(base_price * (1.5 ** (enh/2))) # 비용도 비싸짐
            loot_required = (enh // 4) + 1 
            
            # 최대 강화 제한
            MAX_ENH = 20
            
            # 확률: 계속 낮아짐 (0.85 하락 곡선)
            prob = max(1, int(100 * (0.85 ** enh)))
            
            # 파괴 확률 (삭제됨: 무조건 0)
            destruct_prob = 0

            
            # 우측 상세 창
            pygame.draw.rect(screen, (30, 30, 30), (450, 100, 300, 350))
            pygame.draw.rect(screen, WHITE, (450, 100, 300, 350), 2)
            
            draw_text("강화 상세", 600, 120, YELLOW, center=True)
            draw_text(f"아이템: {sel_item['name']}", 470, 160, WHITE, small=True)
            draw_text(f"현재 강화: +{enh}", 470, 190, WHITE, small=True)
            
            # 기하급수적 성능 향상 예측
            stat_type = "공격력" if sel_item['type'] == 'weapon' else "방어력"
            stat_key = "atk" if sel_item['type'] == 'weapon' else "def"
            current_stat = sel_item.get(stat_key, 0)
            
            # 기하급수적 공식: 기본 성장의 2% + 고정치(1.45배씩 증가)
            # 처음엔 미미하다가 나중엔 엄청나짐
            bonus = int(current_stat * 0.02) + int(3 * (1.45 ** enh))

            

            
            draw_text(f"현재 {stat_type}: {current_stat}", 470, 220, WHITE, small=True)
            draw_text(f"강화 시 {stat_type}: {current_stat + bonus}", 470, 250, GREEN, small=True)

            
            draw_text(f"성공 확률: {prob}%", 470, 290, YELLOW, small=True)
            
            draw_text(f"필요 골드: {gold_cost}G", 470, 345, WHITE, small=True)
            
            # 재료 체크 (해당 아이템에 설정된 전리품)
            target_material = sel_item.get("upgrade_material", "전리품")
            # 스택 시스템 대응: 해당 이름을 가진 모든 아이템의 count 합산
            matched_items = [it for it in player_inventory if it['name'] == target_material]
            current_loot_count = sum(it.get('count', 1) for it in matched_items)
            loot_color = GREEN if current_loot_count >= loot_required else RED
            draw_text(f"재료: {target_material} ({current_loot_count}/{loot_required})", 470, 375, loot_color, small=True)




            
            draw_text("[Z] 강화 시도  [X] 나가기", WIDTH//2, HEIGHT - 50, WHITE, center=True, small=True)

            # 결과 메시지
            if 'blacksmith_msg' in globals() and blacksmith_msg and now - blacksmith_msg_timer < 2000:
                color = GREEN if "성공" in blacksmith_msg else RED
                draw_text(blacksmith_msg, WIDTH//2, HEIGHT - 100, color, center=True)

            # 조작
            if now - menu_nav_timer > 150:
                if keys[KEY_UP]:
                    blacksmith_select_idx = (blacksmith_select_idx - 1) % len(upgradeable_items)
                    menu_nav_timer = now
                elif keys[KEY_DOWN]:
                    blacksmith_select_idx = (blacksmith_select_idx + 1) % len(upgradeable_items)
                    menu_nav_timer = now

            for event in events:
                if event.type == pygame.KEYDOWN and event.key == KEY_ACTION_1:
                    if now - menu_nav_timer > 300:
                        if enh >= MAX_ENH:
                            blacksmith_msg = "이미 최대 강화 단계입니다."
                        elif player_gold >= gold_cost and current_loot_count >= loot_required:
                            # 강화 진행
                            player_gold -= gold_cost
                            # 특정 전리품 소모 (스택 대응)
                            needed = loot_required
                            for it in player_inventory[:]: # 전체 리스트 복사본으로 순회
                                if it['name'] == target_material:
                                    if it.get('count', 1) >= needed:
                                        it['count'] = it.get('count', 1) - needed
                                        if it['count'] <= 0: player_inventory.remove(it)
                                        needed = 0
                                        break
                                    else:
                                        needed -= it.get('count', 1)
                                        player_inventory.remove(it)
                                if needed <= 0: break
                            
                            # 확률 판정
                            rand_val = random.randint(1, 100)
                            if rand_val <= prob:
                                sel_item["enhancement"] = enh + 1
                                sel_item[stat_key] += bonus
                                # 이름에 + 표시 업데이트
                                if " (+" in sel_item["name"]:
                                    sel_item["name"] = sel_item["name"].split(" (+")[0] + f" (+{enh+1})"
                                else:
                                    sel_item["name"] += f" (+{enh+1})"
                                blacksmith_msg = f"강화 성공! (+{enh+1})"
                            else:
                                # 실패 (파괴 없음)
                                blacksmith_msg = "강화 실패... (등급 유지)"

                            
                            blacksmith_msg_timer = now
                            menu_nav_timer = now
                        else:
                            if player_gold < gold_cost:
                                blacksmith_msg = "골드가 부족합니다."
                            else:
                                blacksmith_msg = "전리품이 부족합니다."
                            blacksmith_msg_timer = now
                            menu_nav_timer = now

        if keys[KEY_ACTION_2]: # 나가기
            if now - menu_nav_timer > 200:
                state = STATE_TOWN
                menu_nav_timer = now
                blacksmith_msg = ""

    # ----------------------------------------
    # 치트 메뉴 (Cheat Menu)
    # ----------------------------------------
    elif state == STATE_CHEAT:
        screen.fill(BG_LEVELUP)
        draw_text("★ 치트 메뉴 ★", WIDTH//2, 50, YELLOW, center=True)
        
        cheat_options = [
            ("레벨", "player_level", 1),
            ("스탯 포인트", "player_stat_points", 5),
            ("소지금", "player_gold", 1000),
            ("아이템 생성", "item_spawn", 1),
            ("전리품 생성", "loot_spawn", 1),
            ("생성 수량", "cheat_spawn_qty", 1),
            ("공격력", "atk", 10),
            ("방어력", "def", 10),
            ("최대체력", "hp", 100),
            ("최대마나", "mana", 100)
        ]
        
        # 입력 모드 초기화
        if 'cheat_input_mode' not in globals(): globals()['cheat_input_mode'] = False
        if 'cheat_input_buffer' not in globals(): globals()['cheat_input_buffer'] = ""
        if 'cheat_spawn_qty' not in globals(): globals()['cheat_spawn_qty'] = 1
        
        # 목록 준비
        item_keys = list(ITEM_DB.keys())
        if 'cheat_item_idx' not in globals(): globals()['cheat_item_idx'] = 0
        
        all_loots = []
        for m in MONSTER_DB.values():
            if m['loot_item'] not in [x['name'] for x in all_loots]:
                all_loots.append({"name": m['loot_item'], "price": m['loot_price'], "desc": "상점에 판매 가능"})
            if 'rare_loot' in m and m['rare_loot'] not in [x['name'] for x in all_loots]:
                all_loots.append({"name": m['rare_loot'], "price": m.get('rare_price', 1000), "desc": "매우 귀한 전리품"})
        if 'cheat_loot_idx' not in globals(): globals()['cheat_loot_idx'] = 0
        
        # UI 배치 설정
        start_x = 100
        start_y = 120
        line_h = 40
        
        for i, (label, var, inc) in enumerate(cheat_options):
            color = WHITE
            is_selected = (i == cheat_select_idx)
            
            if is_selected:
                color = YELLOW
                draw_text(">", start_x - 30, start_y + i * line_h, YELLOW)
            
            if var == "item_spawn":
                item_data = ITEM_DB[item_keys[cheat_item_idx]]
                rarity = item_data.get("rarity", "커먼")
                rarity_color = get_rarity_color(rarity)
                val_text = f"[{rarity}] {item_data['name']} (Z획득)"
                if is_selected: color = rarity_color if not cheat_input_mode else RED
            elif var == "loot_spawn":
                loot_data = all_loots[cheat_loot_idx]
                rarity = "언커먼" if "귀한" in loot_data['desc'] else "커먼"
                val_text = f"[{rarity}] {loot_data['name']} (Z획득)"
                if is_selected: color = get_rarity_color(rarity) if not cheat_input_mode else RED
            else:
                if is_selected and cheat_input_mode:
                    val_text = f"입력 중: {cheat_input_buffer}_"
                    color = RED
                else:
                    if var in ["player_level", "player_gold", "player_stat_points", "cheat_spawn_qty"]:
                        val_text = str(globals()[var])
                    else:
                        val_text = str(player_stats[var])
            
            draw_text(f"{label}: {val_text}", start_x, start_y + i * line_h, color)

        guide = "[↑/↓] 이동 [←/→] 조절 [Z] 생성 [Enter] 직접입력 [F1] 닫기"
        draw_text(guide, WIDTH//2, HEIGHT - 50, GREY, center=True, small=True)

        if cheat_input_mode:
            # 직접 입력 처리
            for event in events:
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_RETURN: # 확정
                        if cheat_input_buffer.isdigit():
                            new_val = int(cheat_input_buffer)
                            opt = cheat_options[cheat_select_idx]
                            var = opt[1]
                            if var in ["player_level", "player_gold", "player_stat_points", "cheat_spawn_qty"]:
                                globals()[var] = new_val
                            elif var in player_stats:
                                diff = new_val - player_stats[var]
                                player_stats[var] = new_val
                                if var == "hp": player_max_hp += diff; player_hp = min(player_hp, player_max_hp)
                                if var == "mana": player_max_mana += diff; player_mana = min(player_mana, player_max_mana)
                        cheat_input_mode = False
                        cheat_input_buffer = ""
                        menu_nav_timer = now
                    elif event.key == pygame.K_BACKSPACE:
                        cheat_input_buffer = cheat_input_buffer[:-1]
                    elif event.unicode.isdigit():
                        cheat_input_buffer += event.unicode
        else:
            # 일반 메뉴 조작
            if now - menu_nav_timer > 100:
                if keys[KEY_UP]:
                    cheat_select_idx = (cheat_select_idx - 1) % len(cheat_options)
                    menu_nav_timer = now
                elif keys[KEY_DOWN]:
                    cheat_select_idx = (cheat_select_idx + 1) % len(cheat_options)
                    menu_nav_timer = now
                
                opt = cheat_options[cheat_select_idx]
                var = opt[1]
                inc = opt[2]
                
                if keys[KEY_RIGHT]:
                    if var == "item_spawn": cheat_item_idx = (cheat_item_idx + 1) % len(item_keys)
                    elif var == "loot_spawn": cheat_loot_idx = (cheat_loot_idx + 1) % len(all_loots)
                    elif var in ["player_level", "player_gold", "player_stat_points", "cheat_spawn_qty"]:
                        globals()[var] += inc
                        if var == "player_level": globals()["player_stat_points"] += 3
                    else:
                        player_stats[var] += inc
                        if var == "hp": player_max_hp += inc; player_hp += inc
                        if var == "mana": player_max_mana += inc; player_mana += inc
                    menu_nav_timer = now
                elif keys[KEY_LEFT]:
                    if var == "item_spawn": cheat_item_idx = (cheat_item_idx - 1) % len(item_keys)
                    elif var == "loot_spawn": cheat_loot_idx = (cheat_loot_idx - 1) % len(all_loots)
                    elif var in ["player_level", "player_gold", "player_stat_points", "cheat_spawn_qty"]:
                        globals()[var] = max(1 if var=="cheat_spawn_qty" else 0, globals()[var] - inc)
                    else:
                        player_stats[var] = max(1, player_stats[var] - inc)
                        if var == "hp": player_max_hp = max(1, player_max_hp - inc); player_hp = min(player_hp, player_max_hp)
                        if var == "mana": player_max_mana = max(1, player_max_mana - inc); player_mana = min(player_mana, player_max_mana)
                    menu_nav_timer = now

            # 상호작용
            for event in events:
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_RETURN:
                        opt = cheat_options[cheat_select_idx]
                        if opt[1] not in ["item_spawn", "loot_spawn"]:
                            cheat_input_mode = True
                            cheat_input_buffer = ""
                            menu_nav_timer = now
                    elif event.key == KEY_ACTION_1:
                        opt = cheat_options[cheat_select_idx]
                        if opt[1] == "item_spawn":
                            item_key = item_keys[cheat_item_idx]
                            item_data = ITEM_DB[item_key].copy()
                            add_item_to_inventory(item_data, cheat_spawn_qty)
                            menu_nav_timer = now + 150
                        elif opt[1] == "loot_spawn":
                            loot_data = all_loots[cheat_loot_idx].copy()
                            loot_data["type"] = "misc"
                            add_item_to_inventory(loot_data, cheat_spawn_qty)
                            menu_nav_timer = now + 150



    # 퀘스트 표시 (전투 제외)
    if state in [STATE_TOWN, STATE_FIELD, STATE_DIALOG, STATE_SELECT_MAP]:
        draw_text(quest_text, 10, 10, WHITE)

    # 화면 스케일링 및 출력
    scaled_surface = pygame.transform.scale(screen, (scaled_width, scaled_height))
    real_screen.fill(BLACK) # 여백 클리어
    real_screen.blit(scaled_surface, (offset_x, offset_y))
    pygame.display.flip()

pygame.quit()
sys.exit()
