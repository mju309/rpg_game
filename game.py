import pygame
import random
import string
import sys
import os
import json
from quest_data import QUEST_DB
from quest import QuestManager
import math # math 모듈 추가

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
    {"name": "마왕성", "min_lv": 90, "color": (30, 0, 0)}, # 최종 지역
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
    0: {"name": "킹 슬라임", "hp": 500, "atk": 25, "def": 15, "agi": 10, "crit": 5, "exp": 200, "patterns": ["점프 프레스", "자가 회복"]},
    1: {"name": "고대 설괴", "hp": 1200, "atk": 45, "def": 30, "agi": 15, "crit": 8, "exp": 600, "patterns": ["눈보라", "얼음 방벽"]},
    2: {"name": "데저트 드래곤", "hp": 2500, "atk": 70, "def": 45, "agi": 25, "crit": 12, "exp": 1500, "patterns": ["화염 숨결", "모래 폭풍"]},
    3: {"name": "맹독 히드라", "hp": 4000, "atk": 90, "def": 50, "agi": 30, "crit": 10, "exp": 2500, "patterns": ["맹독 브레스", "트리플 바이트"]},
    4: {"name": "심해의 크라켄", "hp": 6000, "atk": 110, "def": 70, "agi": 20, "crit": 15, "exp": 3500, "patterns": ["먹물 발사", "촉수 휩쓸기"]},
    5: {"name": "지옥의 켈베로스", "hp": 10000, "atk": 160, "def": 40, "agi": 50, "crit": 20, "exp": 6000, "patterns": ["삼연격 지옥화염", "광폭화"]},
    6: {"name": "심연의 수호자", "hp": 15000, "atk": 200, "def": 120, "agi": 40, "crit": 25, "exp": 10000, "patterns": ["어둠의 고리", "멸망의 주문"]},
    7: {"name": "마왕", "hp": 50000, "atk": 450, "def": 200, "agi": 60, "crit": 35, "exp": 0, "patterns": ["심연의 불꽃", "차원 붕괴", "종말의 예고"], "is_last": True},
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
STATE_QUEST_LOG = "quest_log"
STATE_ENDING = "ending" # 엔딩 화면 추가
STATE_SAVE_LOAD = "save_load" # 세이브/로드 선택 화면
STATE_TITLE = "title" # 타이틀 화면
STATE_ESC_MENU = "esc_menu" # ESC 메뉴
STATE_HIDDEN_JOB = "hidden_job" # AI 히든 직업 결정 화면

# 전투 시퀀스 전술 단계
BATTLE_STEP_CRITICAL = 100 # 크리티컬 바 단계
BATTLE_STEP_DEATH = 200 # 사망 연출 단계

state = STATE_TITLE
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
quest_btn_rect = pygame.Rect(10, 10, 130, 40)
quest_log_scroll = 0
state_before_quest_log = STATE_TOWN
state_before_levelup = STATE_TOWN
state_before_save_load = STATE_TOWN
save_load_mode = "save" # "save" 또는 "load"
save_slot_index = 0
title_select_idx = 0 # 타이틀 메뉴 선택 인덱스
esc_menu_idx = 0 # ESC 메뉴 선택 인덱스
state_before_settings = STATE_TOWN # 설정 전 상태 저장용
state_before_esc = STATE_TITLE # ESC 메뉴 진입 전 상태 저장용

# 소울 싱크로나이즈 (크리티컬 시스템) 관련 변수
crit_ring_radius = 200 # 시작 반경
crit_target_radius = 40 # 목표 반경 (중앙 코어 크기)
crit_ring_speed = 6 # 축소 속도
crit_result = None
crit_multiplier = 1.0

damage_labels = []
particles = [] # 이펙트 파티클 리스트

# 연출 효과 변수
screen_shake_time = 0
screen_shake_intensity = 0
hit_flash_time = 0
hit_flash_color = WHITE

# 상점 및 인벤토리
player_gold = 200
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
player_size = 40 # 기본 논리 사이즈
player_start_pos = (400, 520) # 남쪽 도로 입구
player_town_pos = (400, 520)
player_field_pos = (600, HEIGHT - 80)
player = pygame.Rect(player_start_pos[0], player_start_pos[1], player_size, player_size)
player_level = 1
player_exp = 0
player_move_timer = 0
PLAYER_MOVE_INTERVAL = 150 # 그리드 이동 딜레이
player_speed = 40 # 이동 거리
player_facing = "right" # 캐릭터가 보는 방향

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

# ----------------------------------------
# 이미지 스프라이트 설정 (40x40)
# ----------------------------------------
# 아래 파일들을 프로젝트 폴더에 넣으면 자동으로 적용됩니다.
# - player.png, chief.png, job.png, store.png, blacksmith.png, guard.png, recruit.png
# - slime.png, mushroom.png, goblin.png 등
SPRITES = {}

def load_sprite(name, filename, color_fallback):
    path = os.path.join(os.getcwd(), filename)
    if os.path.exists(path):
        try:
            img = pygame.image.load(path).convert_alpha()
            SPRITES[name] = pygame.transform.scale(img, (80, 80))
            return True
        except: pass
    # 파일이 없거나 로드 실패 시 색상 정보 저장
    SPRITES[name] = color_fallback
    return False

# 초기 이미지 로드 (파일이 없으면 설정된 색깔로 대체됨)
load_sprite("player", "player.png", BLUE)
load_sprite("chief", "chief.png", GREEN)
load_sprite("job", "job.png", (150, 0, 150))
load_sprite("store", "store.png", (200, 200, 0))
load_sprite("blacksmith", "blacksmith.png", (60, 60, 65))
load_sprite("guard", "guard.png", (50, 50, 200))
load_sprite("recruit", "recruit.png", (100, 50, 150))

# 몬스터 스프라이트 (이미지 파일 없을 때의 기본 색상)
load_sprite("slime", "slime.png", (0, 255, 150))
load_sprite("mushroom", "mushroom.png", (255, 100, 100))
load_sprite("goblin", "goblin.png", (50, 150, 50))
load_sprite("demon_king", "demon_king.png", (100, 0, 100)) # 마왕

def draw_sprite(screen, name, rect, facing="right"):
    sprite = SPRITES.get(name)
    if isinstance(sprite, pygame.Surface):
        # 이미지 파일이 있는 경우 2배(80x80)로 출력, 논리적 Rect 중앙에 배치
        # logic rect is offset by -20, -20 to center the 80x80 visual
        draw_surf = sprite
        if facing == "left":
            draw_surf = pygame.transform.flip(sprite, True, False)
        
        screen.blit(draw_surf, (rect.x - 20, rect.y - 20))
    else:
        # Fallback: 원래 사이즈(40x40) 사각형
        pygame.draw.rect(screen, sprite if sprite else WHITE, rect)

# 퀘스트 및 대화
# 퀘스트 관리자 인스턴스 생성
quest_manager = QuestManager()

class AnalyticsManager:
    def __init__(self):
        self.data = {
            "skill_type_counts": {"physical": 0, "magic": 0, "buff": 0, "utility": 0},
            "total_turns": 0,
            "total_battles": 0,
            "flee_count": 0,
            "death_count": 0,
            "low_hp_attack_count": 0, # HP 20% 이하 공격
            "high_lv_challenge_count": 0, # 본인보다 높은 렙 지역 전투
            "potion_emergency": 0, # 20% 미만 사용
            "potion_habitual": 0,  # 70% 이상 사용
            "blacksmith_attempts": 0,
            "companion_skill_usage": 0,
            "perfect_hits": 0,
            "miss_hits": 0,
            "last_death_time": 0,
            "retry_speed_sum": 0, # 사망 후 복귀 시간 합산
            "retry_count": 0
        }

    def log(self, category, key, value=1):
        if category in self.data:
            if isinstance(self.data[category], dict):
                self.data[category][key] = self.data[category].get(key, 0) + value
            else:
                 # category 자체가 key인 경우 (단순 필드)
                 pass 
        if key in self.data:
            self.data[key] += value

    def get_state(self):
        return self.data

    def load_state(self, state_data):
        if state_data:
            self.data.update(state_data)

analytics = AnalyticsManager()

def save_game(slot):
    global player_name, player_level, player_exp, player_gold, player_job, player_stats
    global player_inventory, player_equipment, player_stat_points, skill_points
    global current_map_index, owned_companions, player_party, quest_manager

    party_indices = []
    for member in player_party:
        found = False
        for i, owned in enumerate(owned_companions):
            if member is owned:
                party_indices.append(i); found = True; break
        if not found:
             for i, owned in enumerate(owned_companions):
                if member['name'] == owned['name']:
                    party_indices.append(i); break

    save_data = {
        "player": {
            "name": player_name, "level": player_level, "exp": player_exp,
            "gold": player_gold, "job": player_job, "stats": player_stats,
            "stat_points": player_stat_points, "skill_points": skill_points
        },
        "inventory": player_inventory,
        "equipment": player_equipment,
        "world": { "map_index": current_map_index, "player_pos": (player.x, player.y) },
        "companions": { "owned": owned_companions, "party_indices": party_indices },
        "quests": quest_manager.get_state(),
        "analytics": analytics.get_state(),
        "save_time": pygame.time.get_ticks() 
    }

    try:
        filename = f"savegame_{slot}.json"
        with open(filename, "w", encoding="utf-8") as f:
            json.dump(save_data, f, ensure_ascii=False, indent=4)
        return True
    except Exception as e:
        print(f"저장 오류: {e}")
        return False

def load_game(slot):
    global player_name, player_level, player_exp, player_gold, player_job, player_stats
    global player_inventory, player_equipment, player_stat_points, skill_points
    global current_map_index, owned_companions, player_party, quest_manager, state, player

    filename = f"savegame_{slot}.json"
    if not os.path.exists(filename):
        return False

    try:
        with open(filename, "r", encoding="utf-8") as f:
            save_data = json.load(f)

        p = save_data["player"]
        player_name = p["name"]
        player_level = p["level"]
        player_exp = p["exp"]
        player_gold = p["gold"]
        player_job = p["job"]
        player_stats = p["stats"]
        player_stat_points = p.get("stat_points", 0)
        skill_points = p.get("skill_points", 0)

        player_inventory = save_data["inventory"]
        player_equipment = save_data["equipment"]
        
        current_map_index = save_data["world"]["map_index"]
        pos = save_data["world"].get("player_pos", player_start_pos)
        player.x, player.y = pos

        c = save_data["companions"]
        owned_companions[:] = c["owned"]
        player_party[:] = []
        for idx in c["party_indices"]:
            if idx < len(owned_companions):
                player_party.append(owned_companions[idx])

        quest_manager.load_state(save_data["quests"])
        
        # 분석 정보 복구
        if "analytics" in save_data:
            analytics.load_state(save_data["analytics"])
        
        for k, d in COMPANION_DB.items():
            if 'desc' in d:
                d['desc'] = d['desc'].replace("주인공", player_name).replace("플레이어", player_name)
        
        return True
    except Exception as e:
        print(f"불러오기 오류: {e}")
        return False

def get_slot_info(slot):
    filename = f"savegame_{slot}.json"
    if not os.path.exists(filename):
        return "비어 있음"
    try:
        with open(filename, "r", encoding="utf-8") as f:
            data = json.load(f)
            p = data["player"]
            return f"Lv.{p['level']} {p['name']} ({p['job']})"
    except:
        return "데이터 손상"

# 저장 메시지 관리
save_msg_timer = 0
save_msg_text = ""
def trigger_save(slot):
    global save_msg_timer, save_msg_text
    if save_game(slot):
        save_msg_text = f"{slot}번 슬롯에 저장되었습니다!"
    else:
        save_msg_text = "저장 실패!"
    save_msg_timer = pygame.time.get_ticks()
# 초기 퀘스트(1번) 강제 시작 제거 (대화로 시작)
# quest_manager.start_quest(1) 

current_dialog = []

current_dialog = []

dialog_map = {
    # 퀘스트 대화는 별도 관리 예정
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

def draw_soul_sync():
    global crit_ring_radius, crit_ring_speed, crit_target_radius
    
    # 화면 중앙
    cx, cy = WIDTH//2, HEIGHT//2 - 50
    
    # 1. 중앙 가이드 라인 (타겟 코어)
    pygame.draw.circle(screen, (60, 60, 60), (cx, cy), crit_target_radius + 15, 2) # Outer Guide
    pygame.draw.circle(screen, YELLOW, (cx, cy), crit_target_radius, 3) # Perfect Core
    
    # 2. 수축하는 링 (Soul Ring)
    # 시간에 따라 반경 감소
    crit_ring_radius -= crit_ring_speed
    
    # 링이 코어보다 작아지면 다시 크게 (실패 방지 루프 - 실제로는 도중에 누름)
    if crit_ring_radius < 10:
        crit_ring_radius = 220
        
    # 링 색상 결정 (목표에 가까워질수록 밝아짐)
    dist = abs(crit_ring_radius - crit_target_radius)
    ring_color = WHITE
    if dist < 10: ring_color = YELLOW
    elif dist < 30: ring_color = GREEN
    
    pygame.draw.circle(screen, ring_color, (cx, cy), int(crit_ring_radius), 4)
    
    # 사이버네틱 효과 (십자 가이드)
    pygame.draw.line(screen, (100, 100, 100), (cx - 10, cy), (cx + 10, cy), 2)
    pygame.draw.line(screen, (100, 100, 100), (cx, cy - 10), (cx, cy + 10), 2)



def add_damage_label(text, x, y, color=RED, is_crit=False):
    global damage_labels, screen_shake_time, screen_shake_intensity, hit_flash_time
    # 약간의 위치 랜덤성
    rx = x + random.randint(-30, 30)
    ry = y + random.randint(-20, 20)
    
    # 임팩트 효과 트리거
    screen_shake_time = 10 # 프레임 수 (조금 줄임)
    screen_shake_intensity = 6 if is_crit else 3 # 강도 조절
    
    # 공격 이펙트 추가 (Procedural Effect)
    add_effect("slash", rx, ry, color)
    if is_crit:
        add_effect("spark", rx, ry, YELLOW)

    damage_labels.append({
        "text": str(text),
        "x": rx,
        "y": ry,
        "start_y": ry,
        "timer": pygame.time.get_ticks(),
        "color": color,
        "is_crit": is_crit
    })

def add_effect(type, x, y, color):
    global particles
    if type == "slash":
        # 베기 이펙트 (선이 그어지는 연출)
        particles.append({
            "type": "slash", "x": x, "y": y, "timer": 15, "max_timer": 15,
            "angle": random.randint(0, 360), "color": color, "size": 100
        })
    elif type == "spark":
        # 튀는 불꽃
        for _ in range(8):
            particles.append({
                "type": "particle", 
                "x": x, "y": y, 
                "vx": random.uniform(-5, 5), "vy": random.uniform(-5, 5),
                "timer": 20, "color": color, "size": random.randint(3, 6)
            })

def draw_effects(off_x, off_y):
    global particles
    for p in particles[:]:
        p["timer"] -= 1
        if p["timer"] <= 0:
            particles.remove(p)
            continue
            
        if p["type"] == "slash":
            # 베기: 선이 빠르게 지나감
            progress = 1 - (p["timer"] / p["max_timer"])
            start_offset = -50 + progress * 100
            end_offset = start_offset + 40
            
            # 각도 적용
            rad = math.radians(p["angle"])
            c, s = math.cos(rad), math.sin(rad)
            
            p1 = (p["x"] + c * start_offset + off_x, p["y"] + s * start_offset + off_y)
            p2 = (p["x"] + c * end_offset + off_x,   p["y"] + s * end_offset + off_y)
            
            pygame.draw.line(screen, WHITE, p1, p2, 5) # Core styling
            pygame.draw.line(screen, p["color"], p1, p2, 3) # Inner color

        elif p["type"] == "particle":
            p["x"] += p["vx"]
            p["y"] += p["vy"]
            pygame.draw.circle(screen, p["color"], (int(p["x"] + off_x), int(p["y"] + off_y)), p["size"])

def draw_damage_labels():
    global damage_labels
    now = pygame.time.get_ticks()
    DURATION = 1200
    
    for label in damage_labels[:]:
        elapsed = now - label["timer"]
        if elapsed > DURATION:
            damage_labels.remove(label)
            continue
        
        offset_y = (elapsed / DURATION) * 80
        curr_y = label["start_y"] - offset_y
        
        # 폰트 크기 키우기 (메인 폰트보다 크게)
        font_to_use = font # 기본 폰트 사용하되, 스케일링으로 처리 or 그냥 큰 폰트 객체 생성
        
        # 텍스트 렌더링
        txt_surf = font_to_use.render(label["text"], True, label["color"])
        # 크기 확대 (1.5배)
        scale = 2.0 if label["is_crit"] else 1.5
        w = int(txt_surf.get_width() * scale)
        h = int(txt_surf.get_height() * scale)
        scaled_surf = pygame.transform.scale(txt_surf, (w, h))
        
        # 외곽선 (검은색 그림자 효과)
        shadow_surf = font_to_use.render(label["text"], True, BLACK)
        shadow_scaled = pygame.transform.scale(shadow_surf, (w, h))
        
        # 위치
        draw_x = label["x"] - w//2
        draw_y = curr_y - h//2
        
        # 외곽선 그리기 (4방향)
        for dx, dy in [(-2,0), (2,0), (0,-2), (0,2)]:
            screen.blit(shadow_scaled, (draw_x + dx, draw_y + dy))
            
        screen.blit(scaled_surf, (draw_x, draw_y))

def reset_battle(enemy_data=None):
    global battle_select, battle_timer, battle_messages, battle_step, battle_turn_count
    global player_battle_buffs, enemy_battle_debuffs, battle_mana_shield, battle_companion_idx, battle_taunt_target
    global battle_enemy, is_boss_battle, damage_labels
    damage_labels = [] # 이전 전투 잔상 제거
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
        # 치명타 확률이 데이터에 없으면 기본값 0 설정 (KeyError 방지)
        if "crit" not in battle_enemy:
            battle_enemy["crit"] = 0
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
    # 호환성 위해 남겨둠 (실제로는 매니저 사용 권장)
    pass

def get_max_exp(level):
    # 레벨업 요구량 곡선을 조금 더 가파르게 조정하여 밸런스 유지
    raw_exp = 5 * level * level + 10
    return (raw_exp // 10) * 10

def level_up():
    global player_level, player_stat_points, player_hp, player_mana, state, skill_points
    player_level += 1
    player_stat_points += 3
    skill_points += 1 # 레벨업 시 스킬 포인트 1 획득
    
    # 레벨업 시 체력, 마나는 최대치로 회복
    player_hp = player_max_hp
    player_mana = player_max_mana

def trigger_level_up_check():
    """XP가 증가했을 때 호출하여 레벨업 여부를 판단합니다."""
    global player_exp, player_level, state
    leveled = False
    while player_exp >= get_max_exp(player_level):
        player_exp -= get_max_exp(player_level)
        level_up()
        leveled = True
    
    if leveled:
        # 상태 전환은 호출한 곳에서 적절히(대화 종료 후 등) 처리하도록 할 수도 있음
        return True
    return False

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
    
    # 플레이어 그리기 (방향 반영)
    draw_sprite(screen, "player", player, facing=player_facing)
    
    # 헬퍼 함수: 인접 여부 확인 (이동 거리 40 기준 보정)
    def is_near(n):
        return abs(player.x - n.x) <= 40 and abs(player.y - n.y) <= 40

    # 촌장
    draw_sprite(screen, "chief", npc)
    
    # 메인 퀘스트 진행 중에는 항상 촌장에게 퀘스트 마커/텍스트를 띄워줌 (멀리 있어도)
    # 다만 너무 멀면 "촌장" 이라고만 뜨고, 가까우면 "[Z] 대화" 등이 뜨는게 자연스러움
    # 유저 요청: "원래 있었던것처럼 메인퀘스트를 할때는 촌장과 대화가 떠있게 해" -> 항상 표시
    
    main_q_id = quest_manager.main_quest_id
    q_data = QUEST_DB.get(main_q_id)
    
    label_text = "[Z] 촌장"
    is_main_active = q_data and q_data["type"] == "MAIN"
    
    # 완료 가능 상태 확인
    is_ready = False
    if is_main_active and q_data["end_npc"] == "촌장" and quest_manager.is_quest_active(main_q_id):
         obj = q_data["objective"]
         if obj["type"] in ["kill", "kill_boss", "collect"]:
              curr = quest_manager.active_quests.get(main_q_id, {"current_count": 0})["current_count"]
              if curr >= obj["count"]: is_ready = True
         elif obj["type"] == "equip":
              if player_equipment["weapon"] and player_equipment["armor"]: is_ready = True
         elif obj["type"] == "level_job":
              if player_level >= obj["target"] and player_job != "초보자": is_ready = True
         elif obj["type"] == "talk":
              is_ready = True

    # 퀘스트 수락 전(가이드 필요) 상태 확인
    needs_start = False
    if q_data and q_data["start_npc"] == "촌장":
        # 처치/수집 퀘스트인데 데이터가 없거나, 1번 퀘스트인 경우 (수락 전으로 판단)
        if main_q_id not in quest_manager.active_quests:
            if q_data["objective"]["type"] in ["kill", "collect", "kill_boss", "talk"] or main_q_id == 1:
                needs_start = True

    # 표시 조건: 보고 가능(Far) OR 새로운 퀘스트(Far) OR 진행 중(Far) OR 근처(Near)
    if is_ready:
        draw_text("[Z] 촌장에게 보고", npc.x - 20, npc.y - 30, YELLOW, small=True)
    elif needs_start:
        draw_text("[Z] 촌장과 대화", npc.x - 20, npc.y - 30, YELLOW, small=True)
    elif is_main_active: # 진행 중 상시 표시
        draw_text("[Z] 촌장", npc.x, npc.y - 30, YELLOW, small=True)
    elif is_near(npc):
        draw_text("[Z] 촌장", npc.x, npc.y - 30, YELLOW, small=True)

    # 전직관
    draw_sprite(screen, "job", npc_job)
    job_report = False
    for qid, progress in quest_manager.active_quests.items():
        q_data = QUEST_DB[qid]
        if q_data["end_npc"] == "전직관":
             obj = q_data["objective"]
             if obj["type"] == "kill" and progress["current_count"] >= obj["count"]:
                  job_report = True; break
             elif obj["type"] == "collect":
                  cnt = sum(it.get("count", 1) for it in player_inventory if it["name"] == obj["target"])
                  if cnt >= obj["count"]: job_report = True; break
             elif obj["type"] == "level_job":
                  if player_level >= obj["target"] and player_job != "초보자":
                       job_report = True; break

    # 전직관
    # 진행 중인 전직관 관련 퀘스트 확인
    job_active = any(QUEST_DB[qid]["end_npc"] == "전직관" or QUEST_DB[qid]["start_npc"] == "전직관" 
                     for qid in quest_manager.active_quests)
    
    if job_report:
        draw_text("[Z] 자격 보고", npc_job.x - 10, npc_job.y - 30, YELLOW, small=True)
    elif job_active:
        draw_text("[Z] 전직관", npc_job.x, npc_job.y - 30, YELLOW, small=True)
    elif is_near(npc_job):
        draw_text("[Z] 전직관", npc_job.x, npc_job.y - 30, YELLOW, small=True)

    # 상점 (상시 이용 가능)
    draw_sprite(screen, "store", npc_store)
    store_report = False
    for qid, progress in quest_manager.active_quests.items():
        if QUEST_DB[qid]["end_npc"] == "상점":
             obj = QUEST_DB[qid]["objective"]
             if obj["type"] == "kill" and progress["current_count"] >= obj["count"]:
                  store_report = True; break
             elif obj["type"] == "collect":
                  cnt = sum(it.get("count", 1) for it in player_inventory if it["name"] == obj["target"])
                  if cnt >= obj["count"]: store_report = True; break

    # 상점 진행 중 퀘스트 확인
    store_active = any(QUEST_DB[qid]["end_npc"] == "상점" or QUEST_DB[qid]["start_npc"] == "상점" 
                       for qid in quest_manager.active_quests)

    if store_report:
        draw_text("[Z] 의뢰 보고", npc_store.x - 10, npc_store.y - 30, YELLOW, small=True)
    elif store_active:
        draw_text("[Z] 상점", npc_store.x, npc_store.y - 30, YELLOW, small=True)
    elif is_near(npc_store):
        draw_text("[Z] 상점", npc_store.x, npc_store.y - 30, YELLOW, small=True)

    # 대장장이
    draw_sprite(screen, "blacksmith", npc_blacksmith)
    bs_report = False
    for qid, progress in quest_manager.active_quests.items():
        if QUEST_DB[qid]["end_npc"] == "대장장이":
             obj = QUEST_DB[qid]["objective"]
             if obj["type"] == "collect":
                  cnt = sum(it.get("count", 1) for it in player_inventory if it["name"] == obj["target"])
                  if cnt >= obj["count"]: bs_report = True; break
    
    # 대장장이 진행 중 퀘스트 확인
    bs_active = any(QUEST_DB[qid]["end_npc"] == "대장장이" or QUEST_DB[qid]["start_npc"] == "대장장이" 
                     for qid in quest_manager.active_quests)
    
    if bs_report:
        draw_text("[Z] 의뢰 보고", npc_blacksmith.x - 10, npc_blacksmith.y - 30, YELLOW, small=True)
    elif bs_active:
        draw_text("[Z] 대장장이", npc_blacksmith.x, npc_blacksmith.y - 30, YELLOW, small=True)
    elif is_near(npc_blacksmith):
        draw_text("[Z] 대장장이", npc_blacksmith.x, npc_blacksmith.y - 30, YELLOW, small=True)

    # 경비병 (퀘스트 중개소)
    draw_sprite(screen, "guard", npc_guard)
    
    # 1. 완료 가능한 퀘스트 확인 (보고 우선)
    guard_report = False
    for qid, progress in quest_manager.active_quests.items():
        if QUEST_DB[qid]["end_npc"] == "경비병":
             obj = QUEST_DB[qid]["objective"]
             if obj["type"] == "kill" and progress["current_count"] >= obj["count"]:
                 guard_report = True; break
    
    # 2. 새로 수락 가능한 서브 퀘스트 확인 (가이드)
    guard_new = False
    for qid, sq in QUEST_DB.items():
        if sq["start_npc"] == "경비병" and sq["type"] == "SUB":
             if not quest_manager.is_quest_completed(qid) and not quest_manager.is_quest_active(qid):
                  if player_level >= sq["req_level"]:
                       guard_new = True; break
    
    # 3. 진행 중인 퀘스트 확인
    guard_active = any(QUEST_DB[qid]["end_npc"] == "경비병" or QUEST_DB[qid]["start_npc"] == "경비병" 
                       for qid in quest_manager.active_quests)

    if guard_report:
        draw_text("[Z] 임무 보고", npc_guard.x - 10, npc_guard.y - 30, YELLOW, small=True)
    elif guard_new:
        draw_text("[Z] 새로운 임무", npc_guard.x - 10, npc_guard.y - 30, YELLOW, small=True)
    elif guard_active:
        draw_text("[Z] 경비병", npc_guard.x, npc_guard.y - 30, YELLOW, small=True)
    elif is_near(npc_guard):
        draw_text("[Z] 경비병", npc_guard.x, npc_guard.y - 30, YELLOW, small=True)

    # 용병단장 (상시 이용 가능)
    draw_sprite(screen, "recruit", npc_recruit)
    recruit_report = False
    for qid, progress in quest_manager.active_quests.items():
        if QUEST_DB[qid]["end_npc"] == "용병단장":
             obj = QUEST_DB[qid]["objective"]
             if obj["type"] == "kill" and progress["current_count"] >= obj["count"]:
                  recruit_report = True; break

    # 용병단 진행 중 퀘스트 확인
    recruit_active = any(QUEST_DB[qid]["end_npc"] == "용병단장" or QUEST_DB[qid]["start_npc"] == "용병단장" 
                         for qid in quest_manager.active_quests)

    if recruit_report:
        draw_text("[Z] 용병 보고", npc_recruit.x - 10, npc_recruit.y - 30, YELLOW, small=True)
    elif recruit_active:
        draw_text("[Z] 용병단", npc_recruit.x, npc_recruit.y - 30, YELLOW, small=True)
    elif is_near(npc_recruit):
        draw_text("[Z] 용병단", npc_recruit.x, npc_recruit.y - 30, YELLOW, small=True)



# ----------------------------------------
# 메인 루프
# ----------------------------------------
running = True
while running:
    dt = clock.tick(60)
    screen.fill(BLACK)
    keys = pygame.key.get_pressed()
    events = pygame.event.get()
    now = pygame.time.get_ticks()
    skip_esc_this_frame = False # 이번 프레임에서 ESC 메뉴를 열었는지 체크 (중복 처리 방지)
    
    # 이벤트 처리 (상태 무관 공통)
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
        
        # 설정/메뉴 (ESC)
        if event.type == pygame.KEYDOWN:
            if event.key == KEY_ESC:
                if state == STATE_ESC_MENU:
                    state = state_before_esc
                    menu_nav_timer = now
                elif state in [STATE_TOWN, STATE_FIELD, STATE_SELECT_MAP]: 
                    state_before_esc = state
                    state = STATE_ESC_MENU
                    esc_menu_idx = 0
                    menu_nav_timer = now
                    skip_esc_this_frame = True # 메뉴를 막 열었음
                elif state == STATE_SETTINGS:
                    state = STATE_ESC_MENU # 설정에서 ESC 누르면 메뉴로
                    menu_nav_timer = now
                    skip_esc_this_frame = True
        
        # 퀘스트 버튼 클릭 처리 (마우스)
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1: # 좌클릭
                mx, my = event.pos
                mx = (mx - offset_x) / scale_factor
                my = (my - offset_y) / scale_factor
                
                if state in [STATE_TOWN, STATE_FIELD] and quest_btn_rect.collidepoint(mx, my):
                    if quest_manager.active_quests:
                        state_before_quest_log = state
                        state = STATE_QUEST_LOG
                        menu_nav_timer = now

        if event.type == pygame.KEYDOWN:
            # X키로 메뉴 닫기 공통 (STATS, SETTINGS)
            if event.key == KEY_ACTION_2:
                if state == STATE_STATS:
                    close_stat_menu(True)
                elif state == STATE_SETTINGS and not globals().get('is_rebinding', False):
                    state = state_before_settings if 'state_before_settings' in globals() else STATE_TOWN
                # 상점은 키입력 직접 처리하므로 여기 없음.

    # ----------------------------------------
    # 타이틀 화면
    # ----------------------------------------
    if state == STATE_TITLE:
        screen.fill(BLACK)
        draw_text("★ RPG WORLD ★", WIDTH//2, 120, YELLOW, center=True)
        
        has_any_save = any(os.path.exists(f"savegame_{i}.json") for i in range(1, 4))
        
        menu_items = ["새로운 모험 시작"]
        if has_any_save:
            menu_items.append("모험 이어하기")
        menu_items.append("게임 종료")
        
        for i, item in enumerate(menu_items):
            color = YELLOW if i == title_select_idx else WHITE
            draw_text(item, WIDTH//2, 300 + i*60, color, center=True)
            if i == title_select_idx:
                draw_text("▶", WIDTH//2 - 120, 300 + i*60, YELLOW, center=True)

        for event in events:
            if event.type == pygame.KEYDOWN:
                if event.key == KEY_UP:
                    title_select_idx = (title_select_idx - 1) % len(menu_items)
                    menu_nav_timer = now
                elif event.key == KEY_DOWN:
                    title_select_idx = (title_select_idx + 1) % len(menu_items)
                    menu_nav_timer = now
                elif event.key == KEY_ACTION_1:
                    sel = menu_items[title_select_idx]
                    if sel == "새로운 모험 시작":
                        state = STATE_NAME
                    elif sel == "모험 이어하기":
                        state_before_save_load = STATE_TITLE
                        save_load_mode = "load"
                        state = STATE_SAVE_LOAD
                    elif sel == "게임 종료":
                        running = False
                    menu_nav_timer = now

    # ----------------------------------------
    # 이름 입력
    # ----------------------------------------
    elif state == STATE_NAME:
        screen.fill(BG_NAME)
        draw_text_box("용사 이름을 입력하세요 (영어만)", 150, 150, 500, 50)
        draw_text_box("입력: " + player_name, 150, 220, 500, 50)
        draw_text_box("조작법: 방향키 이동, Z 선택, X 뒤로", 150, 290, 500, 50)
        
        for event in events:
            if event.type == pygame.KEYDOWN:
                if state == STATE_NAME:
                    if event.key == KEY_ACTION_2: # 뒤로가기
                        state = STATE_TITLE
                        menu_nav_timer = now
                    elif event.key == pygame.K_RETURN and player_name != "":
                        state = STATE_TOWN
                        # [테스트 모드] 닉네임이 test인 경우 마왕 직전으로 점프
                        if player_name.lower() == "test":
                            player_level = 90
                            player_stats["atk"] = 999999
                            quest_manager.main_quest_id = 22
                            # 이전 퀘스트들 모두 완료 처리
                            for i in range(1, 22):
                                quest_manager.completed_quests.add(i)
                            if 22 in quest_manager.active_quests: del quest_manager.active_quests[22]
                        
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
        draw_text("[S] 저장", 10, HEIGHT - 30, GREY, small=True)
        
        # 저장 메시지 표시
        if save_msg_text and now - save_msg_timer < 2000:
            draw_text(save_msg_text, WIDTH//2, HEIGHT//2, YELLOW, center=True)
        else:
            save_msg_text = ""

        # S키 저장 단축키 (슬롯 선택 화면으로)
        if keys[pygame.K_s] and now - menu_nav_timer > 500:
            state_before_save_load = STATE_TOWN
            save_load_mode = "save"
            state = STATE_SAVE_LOAD
            menu_nav_timer = now

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
                player_facing = "left"
                moved = True
            elif keys[KEY_RIGHT]:
                next_x += player_speed
                player_facing = "right"
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
        if (abs(player.x - npc.x) <= 40 and abs(player.y - npc.y) <= 40):
            
            for event in events:
                if event.type == pygame.KEYDOWN and event.key == KEY_ACTION_1:
                    menu_nav_timer = now
                    # 퀘스트 대화 생성
                    d_lines, r_info = quest_manager.get_npc_dialog("촌장", player_name, player_level, player_job, player_inventory, player_equipment, ITEM_DB)
                    
                    # 보상 적용 (골드/경험치)
                    if r_info["gold"] > 0: player_gold += r_info["gold"]
                    if r_info["exp"] > 0: 
                        player_exp += r_info["exp"]
                        if trigger_level_up_check():
                            # 대화 중이면 대화 종료 후 레벨업 화면으로 가기 위해 플래그 설정
                            globals()['pending_levelup'] = True
                    
                    state = STATE_DIALOG
                    current_dialog = d_lines
                    dialog_page = 0
                    break
        
        # 상점 대화 (Interaction)
        if (abs(player.x - npc_store.x) <= 40 and abs(player.y - npc_store.y) <= 40):
            
            for event in events:
                if event.type == pygame.KEYDOWN and event.key == KEY_ACTION_1:
                    menu_nav_timer = now
                    d_lines, r_info = quest_manager.get_npc_dialog("상점", player_name, player_level, player_job, player_inventory, player_equipment, ITEM_DB)
                    
                    # 퀘스트 중요 이벤트(보상, 수락)가 있으면 대화 표시, 아니면 상점 열기
                    # "수락"은 판단하기 힘듦. 하지만 상점은 주로 완료/수집 퀘스트 관련이므로 보상 여부로 판단
                    # 혹은 dialog 내용이 기본 인사가 아니면 띄움
                    
                    has_event = (r_info["gold"] > 0 or r_info["exp"] > 0 or len(r_info["items_added"]) > 0 or 
                                 (len(d_lines) > 0 and "수락" in d_lines[-1]) or (len(d_lines) > 0 and "완료" in d_lines[-1]))

                    if has_event:
                         if r_info["gold"] > 0: player_gold += r_info["gold"]
                         if r_info["exp"] > 0: player_exp += r_info["exp"]
                         state = STATE_DIALOG
                         current_dialog = d_lines
                         dialog_page = 0
                    else:
                         state = STATE_STORE
                         store_select_idx = 0
                    break

        # 전직관 대화
        if (abs(player.x - npc_job.x) <= 40 and abs(player.y - npc_job.y) <= 40):
            
            for event in events:
                if event.type == pygame.KEYDOWN and event.key == KEY_ACTION_1:
                    menu_nav_timer = now
                    d_lines, r_info = quest_manager.get_npc_dialog("전직관", player_name, player_level, player_job, player_inventory, player_equipment, ITEM_DB)
                    
                    has_event = (r_info["gold"] > 0 or r_info["exp"] > 0 or len(r_info["items_added"]) > 0 or 
                                 (len(d_lines) > 0 and "수락" in d_lines[-1]) or (len(d_lines) > 0 and "완료" in d_lines[-1]))

                    if has_event:
                         if r_info["gold"] > 0: player_gold += r_info["gold"]
                         if r_info["exp"] > 0: player_exp += r_info["exp"]
                         state = STATE_DIALOG
                         current_dialog = d_lines
                         dialog_page = 0
                    else:
                         # 기존 전직 로직
                        if player_level < 10:
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

        # 대장장이 대화
        if (abs(player.x - npc_blacksmith.x) <= 40 and abs(player.y - npc_blacksmith.y) <= 40):
            
            for event in events:
                if event.type == pygame.KEYDOWN and event.key == KEY_ACTION_1:
                    menu_nav_timer = now
                    d_lines, r_info = quest_manager.get_npc_dialog("대장장이", player_name, player_level, player_job, player_inventory, player_equipment, ITEM_DB)
                    
                    has_event = (r_info["gold"] > 0 or r_info["exp"] > 0 or len(r_info["items_added"]) > 0 or 
                                 (len(d_lines) > 0 and "수락" in d_lines[-1]) or (len(d_lines) > 0 and "완료" in d_lines[-1]))

                    if has_event:
                         if r_info["gold"] > 0: player_gold += r_info["gold"]
                         if r_info["exp"] > 0: player_exp += r_info["exp"]
                         state = STATE_DIALOG
                         current_dialog = d_lines
                         dialog_page = 0
                    else:
                        state = STATE_BLACKSMITH
                        blacksmith_select_idx = 0
                    break

        # 경비병 대화
        if (abs(player.x - npc_guard.x) <= 40 and abs(player.y - npc_guard.y) <= 40):
            
            for event in events:
                if event.type == pygame.KEYDOWN and event.key == KEY_ACTION_1:
                    menu_nav_timer = now
                    d_lines, r_info = quest_manager.get_npc_dialog("경비병", player_name, player_level, player_job, player_inventory, player_equipment, ITEM_DB)
                    
                    if r_info["gold"] > 0: player_gold += r_info["gold"]
                    if r_info["exp"] > 0: player_exp += r_info["exp"]
                    
                    state = STATE_DIALOG
                    current_dialog = d_lines
                    dialog_page = 0
                    break

        # 용병단장 대화
        if (abs(player.x - npc_recruit.x) <= 40 and abs(player.y - npc_recruit.y) <= 40):
            
            for event in events:
                if event.type == pygame.KEYDOWN and event.key == KEY_ACTION_1:
                    menu_nav_timer = now
                    d_lines, r_info = quest_manager.get_npc_dialog("용병단장", player_name, player_level, player_job, player_inventory, player_equipment, ITEM_DB)
                    
                    has_event = (r_info["gold"] > 0 or r_info["exp"] > 0 or len(r_info["items_added"]) > 0 or 
                                 (len(d_lines) > 0 and "수락" in d_lines[-1]) or (len(d_lines) > 0 and "완료" in d_lines[-1]))

                    if has_event:
                         if r_info["gold"] > 0: player_gold += r_info["gold"]
                         if r_info["exp"] > 0: player_exp += r_info["exp"]
                         state = STATE_DIALOG
                         current_dialog = d_lines
                         dialog_page = 0
                    else:
                        state = STATE_RECRUIT
                        recruit_select_idx = 0
                    break

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
                    # 대화 종료 후 레벨업 대기 상태면 레벨업 화면으로, 아니면 마을로
                    if globals().get('pending_levelup', False):
                        state_before_levelup = STATE_TOWN
                        state = STATE_LEVELUP
                        globals()['pending_levelup'] = False
                    else:
                         state = STATE_TOWN

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

                    # 튜토리얼(초반 퀘스트)에서는 숲에서 슬라임만 나오도록 강제
                    # 퀘스트ID 1번이 슬라임 처치 퀘스트임
                    if current_map_index == 0 and quest_manager.main_quest_id <= 1:
                         available_monsters = ["slime"]
                         spawn_count_max = 1 # 튜토리얼은 1마리만
                    
                    if current_map_index == 7:
                        # 마왕성 특수 룰: 바로 마왕(최종 보스) 소환
                        mob_data = BOSS_DB[7].copy()
                        mob_data["is_boss"] = True
                        m_rect = pygame.Rect(WIDTH//2 - 20, HEIGHT//2 - 60, 40, 40)
                        field_monsters.append({
                            "rect": m_rect, "data": mob_data, "name": mob_data["name"],
                            "dir": [0,0], "timer": 0, "key": "demon_king" 
                        })
                    elif available_monsters:
                        count = random.randint(spawn_count_min, spawn_count_max)
                        for _ in range(count):
                            mob_key = random.choice(available_monsters)
                            mob_data = MONSTER_DB[mob_key].copy()
                            rx = random.randrange(40, WIDTH - 40, 40)
                            ry = random.randrange(40, HEIGHT - 80, 40)
                            m_rect = pygame.Rect(rx, ry, 40, 40)
                            monster_obj = {
                                "rect": m_rect, "data": mob_data, "name": mob_data["name"],
                                "dir": [0,0], "timer": 0, "key": mob_key
                            }
                            field_monsters.append(monster_obj)

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
        draw_sprite(screen, "player", player, facing=player_facing)
        
        # 맵 이름 표시 (상단 중앙)
        draw_text(MAP_DATA[current_map_index]["name"], WIDTH//2, 20, WHITE, center=True, small=True)
        draw_text("[S] 저장", 10, HEIGHT - 30, GREY, small=True)

        if save_msg_text and now - save_msg_timer < 2000:
            draw_text(save_msg_text, WIDTH//2, HEIGHT//2, YELLOW, center=True)

        if keys[pygame.K_s] and now - menu_nav_timer > 500:
            state_before_save_load = STATE_FIELD
            save_load_mode = "save"
            state = STATE_SAVE_LOAD
            menu_nav_timer = now

        if field_monsters:
            monster_respawn_timer = 0 # 몬스터가 있으면 리스폰 타이머 초기화 (확실하게)
            for mob in field_monsters:
                m_key = mob.get("key", "slime")
                draw_sprite(screen, m_key, mob["rect"])
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
                    if now - battle_cooldown_timer > BATTLE_COOLDOWN_TIME:
                        analytics.log("combat", "total_battles")
                        # 현재 맵의 권장 레벨보다 낮으면 챌린지 카운트
                        if player_level < MAP_DATA[current_map_index].get("min_lv", 0):
                            analytics.log("combat", "high_lv_challenge_count")
                            
                        reset_battle(mob["data"])
                        state = STATE_BATTLE
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
                player_facing = "left"
                moved = True
            elif keys[KEY_RIGHT]:
                next_x += player_speed
                player_facing = "right"
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
            player.x, player.y = 400, 10 # 마을 위쪽 입구에서 나타남
            # 퀘스트 완료 상태로 복귀했다면 자동 대화 X, 촌장에게 가야함
            pass
            
            monster_respawn_timer = 0
            
        else:
             # 몹이 없으면 리스폰 타이머 작동
            if current_map_index == 7:
                 # 마왕성에서는 리스폰 없음 (단판 승부)
                 pass
            elif current_map_index == 0 and quest_manager.main_quest_id <= 1:
                 pass # 튜토리얼 중인데... 일단 리스폰 허용하자? 아니면 유지?
                 # 기존 로직: quest_step < 3 (1, 2) 일때 pass (리스폰 X라는 뜻?)
                 # 아니 1328에 "몹이 없으면" 이니까...
                 # 튜토리얼때는 한마리 잡으면 끝이니까 리스폰 안하는게 맞을 수도.
                 pass 
            else:
                if monster_respawn_timer == 0:
                    monster_respawn_timer = now
                elif now - monster_respawn_timer > 1000:
                    # 리스폰 1~3마리
                    available_monsters = [k for k, v in MONSTER_DB.items() if v.get("map_idx") == current_map_index]
                    
                    # 튜토리얼 몬스터 제한 (리스폰 시에도 적용)
                    if current_map_index == 0: # 튜토리얼 맵
                        if quest_manager.main_quest_id <= 1:
                             # 튜토리얼 기간엔 슬라임만 1마리
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
        # global screen_shake_time, hit_flash_time # Removed to fix SyntaxError
        
        # 스크린 쉐이크 계산
        off_x, off_y = 0, 0
        if screen_shake_time > 0:
            off_x = random.randint(-screen_shake_intensity, screen_shake_intensity)
            off_y = random.randint(-screen_shake_intensity, screen_shake_intensity)
            screen_shake_time -= 1
            
        screen.fill(BG_BATTLE)
        
        # 모든 전투 오브젝트에 오프셋 적용
        slime_rect = pygame.Rect(50 + off_x, 50 + off_y, 80, 80)
        player_rect = pygame.Rect(600 + off_x, 300 + off_y, 80, 80)
        pygame.draw.rect(screen, RED, slime_rect)
        pygame.draw.rect(screen, BLUE, player_rect)
        
        # 이펙트 그리기 (캐릭터 위)
        draw_effects(off_x, off_y)
        
        draw_text(f"{battle_enemy['name']} HP: {battle_enemy['hp']}/{battle_enemy['max_hp']}", slime_rect.x, slime_rect.y - 25)
        draw_text(f"{player_name} HP: {player_hp}", player_rect.x, player_rect.y - 25)

        msg_box_y = 400
        pygame.draw.rect(screen, BLACK, (50, msg_box_y, 700, 100))
        pygame.draw.rect(screen, WHITE, (50, msg_box_y, 700, 100), 1)
        
        # 히트 플래시 (맞았을 때 흰색 반짝임)
        if hit_flash_time > 0:
            # 전체 화면 혹은 타격 부위에 플래시
            # 여기서는 연출 극대화를 위해 전체 박스 살짝 덮음
            flash_surf = pygame.Surface((WIDTH, HEIGHT))
            flash_surf.fill(WHITE)
            flash_surf.set_alpha(100)
            screen.blit(flash_surf, (0,0))
            hit_flash_time -= 1
        
        # 데미지 수치 출력
        draw_damage_labels()
        
        # 크리티컬 바 출력
        if battle_step == BATTLE_STEP_CRITICAL:
            draw_soul_sync()
        
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
                            # 소울 싱크 단계로 진입
                            battle_step = BATTLE_STEP_CRITICAL
                            crit_ring_radius = 220 # 원의 시작 크기
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

        elif battle_step == BATTLE_STEP_CRITICAL:
            for event in events:
                if event.type == pygame.KEYDOWN and event.key == KEY_ACTION_1:
                    # 거리 계산 (중앙 타겟 반경과의 차이)
                    dist = abs(crit_ring_radius - crit_target_radius)
                    
                    if dist <= 8:
                        crit_result = "PERFECT"
                        crit_multiplier = 2.2
                        analytics.log("action", "perfect_hits")
                    elif dist <= 25:
                        crit_result = "GREAT"
                        crit_multiplier = 1.6
                    elif dist <= 50:
                        crit_result = "GOOD"
                        crit_multiplier = 1.3
                    else:
                        crit_result = "MISSED"
                        crit_multiplier = 1.0
                        analytics.log("action", "miss_hits")

                    # 데미지 계산 및 적용
                    atk_bonus = 1.3 if "공격력" in player_battle_buffs else 1.0
                    crit_bonus = 20 if "크리티컬" in player_battle_buffs else 0
                    
                    # 빈사 상태 공격 체크
                    if player_hp / player_max_hp <= 0.2:
                        analytics.log("combat", "low_hp_attack_count")

                    hd, hc = calculate_damage(player_stats["atk"] * atk_bonus * crit_multiplier, 
                                           battle_enemy["def"], 
                                           player_stats["crit"] + crit_bonus)
                    battle_enemy["hp"] = max(0, battle_enemy["hp"] - hd)
                    
                    # 데미지 라벨 추가 (비주얼 강조)
                    is_p = (crit_result == "PERFECT")
                    add_damage_label(hd, 90, 80, YELLOW if is_p else RED, is_crit=is_p)
                    
                    battle_messages = [f"{crit_result}!"] # 데미지 텍스트 제거
                    if hc or crit_result == "PERFECT":
                         battle_messages.append(random.choice(CRIT_SCRIPTS))
                    
                    battle_step = 1
                    battle_timer = now
                    menu_nav_timer = now

        elif battle_step == BATTLE_STEP_DEATH:
            draw_text("전투에서 패배했습니다...", WIDTH//2, HEIGHT//2 - 20, RED, center=True)
            draw_text("[Z] 마을로 돌아가기", WIDTH//2, HEIGHT//2 + 20, WHITE, center=True, small=True)
            for event in events:
                if event.type == pygame.KEYDOWN and event.key == KEY_ACTION_1:
                    # 복귀 성능 측정 (사망 후 복귀까지 걸린 시간 합산)
                    death_time = analytics.data.get("last_death_time", now)
                    analytics.log("combat", "retry_speed_sum", now - death_time)
                    analytics.log("combat", "retry_count")
                    
                    # 상태 회복 및 강제 이동
                    player_hp = int(player_max_hp) # 100% 체력으로 부활
                    state = STATE_TOWN
                    player.x, player.y = player_start_pos
                    menu_nav_timer = now

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
                                
                                # 스킬 성향 로깅
                                if player_job == "마법사":
                                    analytics.log("skills", "magic")
                                elif player_job == "전사":
                                    analytics.log("skills", "physical")
                                elif player_job == "사수":
                                    analytics.log("skills", "physical")
                                else:
                                    analytics.log("skills", "physical") # 기본

                                # 빈사 상태 스킬 공격 체크
                                if player_hp / player_max_hp <= 0.2:
                                    analytics.log("combat", "low_hp_attack_count")
                                
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
                                add_damage_label(f"+{s_power}", 640, 330, GREEN) # Heal on player
                                sub_msg = f"{player_name}님의 HP가 {s_power} 회복되었습니다."
                            elif s_type == "mana":
                                player_mana = min(player_max_mana, player_mana + s_power)
                                add_damage_label(f"+{s_power}", 640, 330, BLUE) # Mana on player
                                sub_msg = f"{player_name}님의 MP가 {s_power} 회복되었습니다."
                            elif s_type == "damage":
                                hd, _ = calculate_damage(atk_val * s_power, battle_enemy["def"], 20)
                                battle_enemy["hp"] = max(0, battle_enemy["hp"] - hd)
                                add_damage_label(hd, 90, 80, RED) # Damage on enemy
                                sub_msg = f"{hd}의 피해를 입혔습니다!"
                            
                            battle_messages = [msg]
                            if sub_msg: battle_messages.append(sub_msg)
                            analytics.log("growth", "companion_skill_usage")
                        
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
                add_damage_label(damage, 640, 330, RED if crit else WHITE, is_crit=crit) # Damage on player
                battle_messages = ["위험합니다!"] if player_hp < player_max_hp * 0.2 else []
                if crit: battle_messages.append("치명타를 입었습니다!")
                
                if player_hp <= 0:
                    analytics.log("combat", "death_count")
                    analytics.data["last_death_time"] = pygame.time.get_ticks()
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
                analytics.log("combat", "total_turns")
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
                        
                        if eff == "hp" or eff == "hp_mana":
                            # 포션 사용 성향 로깅
                            hp_ratio = player_hp / player_max_hp
                            if hp_ratio <= 0.2:
                                analytics.log("growth", "potion_emergency")
                            elif hp_ratio >= 0.7:
                                analytics.log("growth", "potion_habitual")

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

                if player_hp <= 0:
                    battle_step = BATTLE_STEP_DEATH
                    battle_timer = now
                    continue

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
                # print(f"DEBUG: Monster killed: {battle_enemy['name']}")
                quest_manager.on_kill_monster(battle_enemy["name"])
                
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

                # 마왕(최종 보스) 토벌 체크
                if battle_enemy.get("is_last"):
                    state = STATE_ENDING
                # 레벨업 체크 (전투 승리 시)
                elif trigger_level_up_check():
                    state_before_levelup = STATE_FIELD
                    state = STATE_LEVELUP
                else:
                    state = STATE_FIELD # 필드 복귀
                    battle_cooldown_timer = now 

                # 퀘스트 목표 달성 (QuestManager가 처리하므로 삭제)
                # if quest_step == 1 ... (삭제됨)
                
                battle_messages = []
        
        elif battle_step == 5: # 도망 성공 대기
            if now - battle_timer > 1000: # 1초 대기
                analytics.log("combat", "flee_count")
                state = STATE_FIELD
                battle_cooldown_timer = now # 무적 시간 적용
                battle_messages = []
                # 도망 시 몬스터가 사라지지 않게 하려면 battle_target_mob 제거 로직을 건너뛰어야 함
                # 하지만 여기서는 그냥 유지. 만약 사라지게 하려면 remove 호출.
                # 보통 도망치면 몬스터는 그대로 있거나 (다시 싸우면 체력 리셋?), 아니면 사라짐.
                # 편의상 제거하지 않음. 대신 전투 종료 시 battle_target_mob 관련 처리가 3번 단계 뒤에 있음.
                # 5번 단계에서는 그냥 필드로 복귀.

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
            state = state_before_levelup
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
             # 현재 소유 중인 장비 이름 목록 (인벤토리 + 장착)
            owned_equips = [it["name"] for it in player_inventory if it["type"] in ["weapon", "armor", "accessory"]]
            for slot in player_equipment.values():
                if slot: owned_equips.append(slot["name"])

             # 레벨, 직업별 아이템 필터링 및 이미 소유한 장비 제외
            allowed_items = [
                (k, v) for k, v in ITEM_DB.items() 
                if player_level >= v.get("min_lv", 1) 
                and (v.get("job") == player_job or "job" not in v)
                and (v["type"] not in ["weapon", "armor", "accessory"] or v["name"] not in owned_equips)
            ]
            
            # 튜토리얼 퀘스트 2 필터링
            if quest_manager.main_quest_id == 2:
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
                        item_info = item_data[1] if store_mode == 0 else item_data
                        if item_info['type'] in ['potion', 'misc']:
                             desc = f"▶ {'구매' if store_mode == 0 else '판매'} 수량 조절: {store_buy_qty if store_mode == 0 else store_sell_qty}개 (총 {price * (store_buy_qty if store_mode == 0 else store_sell_qty)}G)"
                        else:
                             desc = f"▶ {item_info['name']}을(를) 정말로 {'구매' if store_mode == 0 else '판매'}하시겠습니까?"
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
                    if item_info['type'] in ['potion', 'misc']:
                        price = item_info.get('price', 999999)
                        max_buy_possible = max(1, player_gold // price) if price > 0 else 1
                        
                        if keys[KEY_RIGHT]:
                            store_buy_qty = min(max_buy_possible, store_buy_qty + 1)
                            menu_nav_timer = now - 50
                        elif keys[KEY_LEFT]:
                            store_buy_qty = max(1, store_buy_qty - 1)
                            menu_nav_timer = now - 50
                    else:
                        # 장비류는 수량 고정
                        store_buy_qty = 1
                
                else: # 판매
                    # current_data는 dict
                    item_info = current_data
                    if item_info['type'] in ['potion', 'misc']:
                        max_sell_possible = item_info.get('count', 1)

                        if keys[KEY_RIGHT]:
                            store_sell_qty = min(max_sell_possible, store_sell_qty + 1)
                            menu_nav_timer = now - 50
                        elif keys[KEY_LEFT]:
                            store_sell_qty = max(1, store_sell_qty - 1)
                            menu_nav_timer = now - 50
                    else:
                        store_sell_qty = 1

        # 선택 및 확정 액션 [KEYDOWN으로 통일]
        for event in events:
            if event.type == pygame.KEYDOWN and event.key == KEY_ACTION_1:
                if now - menu_nav_timer > 300 and target_list:
                    if not store_adjust_mode:
                        if store_mode == 0: # 구매 모드 진입
                            item_key, item_info = target_list[store_select_idx]
                            # 수량 조절 가능 여부 판단 (포션/재료만 가능)
                            if item_info['type'] in ['potion', 'misc']:
                                store_adjust_mode = True
                                store_buy_qty = 1
                            else:
                                # 장비류는 바로 1개 구매 진행 (구매 확인 질문 단계로 간주)
                                store_adjust_mode = True # 내부적으론 진입하되 수량 고정
                                store_buy_qty = 1
                            menu_nav_timer = now
                        else: # 판매 모드 진입
                            removed_item = target_list[store_select_idx]
                            if removed_item.get('count', 1) > 1:
                                store_adjust_mode = True
                                store_sell_qty = 1
                            else:
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
                            analytics.log("growth", "blacksmith_attempts")
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

    # 퀘스트 버튼 UI (전투 외)
    if state in [STATE_TOWN, STATE_FIELD] and quest_manager.active_quests:
        pygame.draw.rect(screen, (50, 50, 50), quest_btn_rect)
        pygame.draw.rect(screen, WHITE, quest_btn_rect, 2)
        draw_text("퀘스트 [Q]", quest_btn_rect.centerx, quest_btn_rect.centery, YELLOW, center=True, small=True)
    
    # 엔딩 화면
    elif state == STATE_ENDING:
        screen.fill(BLACK)
        draw_text("★ 게임 클리어 ★", WIDTH//2, 100, YELLOW, center=True)
        draw_text("세상의 평화를 되찾았습니다!", WIDTH//2, 160, WHITE, center=True)
        
        credits_lines = [
            "기획/개발: RPG Maker AI",
            "도움: Antigravity",
            "총괄 프로듀서: " + player_name,
            "",
            "플레이해주셔서 감사합니다!"
        ]
        for i, line in enumerate(credits_lines):
            draw_text(line, WIDTH//2, 250 + i*40, WHITE, center=True, small=True)
            
        draw_text("[Z] 처음으로 돌아가기", WIDTH//2, HEIGHT - 80, GREY, center=True, small=True)
        
        for event in events:
            if event.type == pygame.KEYDOWN and event.key == KEY_ACTION_1:
                player_level = 1
                player_exp = 0
                player_gold = 200
                player_job = "초보자"
                player_inventory = []
                player_equipment = {"weapon": None, "armor": None, "accessory": None}
                quest_manager = QuestManager()
                player.x, player.y = player_start_pos
                state = STATE_NAME
                player_name = ""

    # ----------------------------------------
    # ESC 메뉴
    # ----------------------------------------
    elif state == STATE_ESC_MENU:
        # 배경 약간 어둡게 (반투명 효과는 없으므로 검정 배경에 박스)
        pygame.draw.rect(screen, (20, 20, 30), (WIDTH//2 - 150, 100, 300, 400))
        pygame.draw.rect(screen, WHITE, (WIDTH//2 - 150, 100, 300, 400), 3)
        
        draw_text("메뉴", WIDTH//2, 130, YELLOW, center=True)
        
        esc_items = ["환경 설정", "게임 저장", "타이틀로", "게임 종료"]
        for i, item in enumerate(esc_items):
            color = YELLOW if i == esc_menu_idx else WHITE
            draw_text(item, WIDTH//2, 220 + i*60, color, center=True)
            if i == esc_menu_idx:
                draw_text("▶", WIDTH//2 - 100, 220 + i*60, YELLOW, center=True)

        draw_text("[Z] 선택  [X/ESC] 닫기", WIDTH//2, 460, GREY, center=True, small=True)

        for event in events:
            if event.type == pygame.KEYDOWN:
                if event.key == KEY_UP:
                    esc_menu_idx = (esc_menu_idx - 1) % len(esc_items)
                    menu_nav_timer = now
                elif event.key == KEY_DOWN:
                    esc_menu_idx = (esc_menu_idx + 1) % len(esc_items)
                    menu_nav_timer = now
                elif event.key == KEY_ACTION_1: # Z
                    sel = esc_items[esc_menu_idx]
                    if sel == "환경 설정":
                        state_before_settings = STATE_ESC_MENU
                        state = STATE_SETTINGS
                    elif sel == "게임 저장":
                        state_before_save_load = STATE_ESC_MENU
                        save_load_mode = "save"
                        state = STATE_SAVE_LOAD
                    elif sel == "타이틀로":
                        state = STATE_TITLE
                    elif sel == "게임 종료":
                        running = False
                    menu_nav_timer = now
                elif event.key in [KEY_ACTION_2, KEY_ESC] and not skip_esc_this_frame:
                    state = state_before_esc
                    menu_nav_timer = now

    # ----------------------------------------
    # 세이브/로드 슬롯 선택
    # ----------------------------------------
    elif state == STATE_SAVE_LOAD:
        screen.fill(BG_SELECT)
        title = "저장할 슬롯을 선택하세요" if save_load_mode == "save" else "불러올 슬롯을 선택하세요"
        draw_text(title, WIDTH//2, 80, YELLOW, center=True)
        
        for i in range(1, 4):
            rect = pygame.Rect(WIDTH//2 - 200, 150 + (i-1)*100, 400, 80)
            is_sel = (save_slot_index == i-1)
            color_bg = (60, 60, 80) if is_sel else (30, 30, 45)
            pygame.draw.rect(screen, color_bg, rect)
            pygame.draw.rect(screen, WHITE if is_sel else GREY, rect, 2)
            
            info = get_slot_info(i)
            draw_text(f"슬롯 {i}", rect.x + 20, rect.y + 15, YELLOW, small=True)
            draw_text(info, rect.x + 20, rect.y + 45, WHITE, small=True)

        draw_text("[방향키] 선택, [Z] 확정, [X] 취소", WIDTH//2, HEIGHT - 50, GREY, center=True, small=True)

        for event in events:
            if event.type == pygame.KEYDOWN and now - menu_nav_timer > 300:
                if event.key == KEY_UP:
                    save_slot_index = (save_slot_index - 1) % 3
                    # menu_nav_timer = now # 키다운 방식이므로 연속 입력 방지 타이머 불필요하지만, 입력 간격 조절 원하면 추가
                elif event.key == KEY_DOWN:
                    save_slot_index = (save_slot_index + 1) % 3
                elif event.key == KEY_ACTION_1: # 확정 (Z)
                    target_slot = save_slot_index + 1
                    if save_load_mode == "save":
                        trigger_save(target_slot)
                        state = state_before_save_load
                    else: # load
                        if load_game(target_slot):
                            state = STATE_TOWN
                        else:
                            # 로드 실패 알림 등
                            pass
                    menu_nav_timer = now
                elif event.key == KEY_ACTION_2: # 취소 (X)
                    state = state_before_save_load
                    menu_nav_timer = now

    # 퀘스트 로그 화면
    elif state == STATE_QUEST_LOG:
        screen.fill(BG_SELECT)
        draw_text("★ 퀘스트 목록 ★", WIDTH//2, 50, YELLOW, center=True)
        
        # 메인 퀘스트
        mq_id = quest_manager.main_quest_id
        q_data = QUEST_DB.get(mq_id)
        start_y = 120
        if q_data:
            draw_text("[메인 퀘스트]", 50, start_y, GREEN, small=True)
            draw_text(f"제목: {q_data['name']}", 70, start_y + 30, WHITE, small=True)
            draw_text(f"설명: {q_data['desc']}", 70, start_y + 60, (200, 200, 200), small=True)
            
            # 진행도
            status = "진행 중"
            if mq_id in quest_manager.active_quests:
                curr = quest_manager.active_quests[mq_id]["current_count"]
                req = q_data["objective"]["count"]
                status = f"진행도: {curr}/{req}"
                if curr >= req: status += " (완료 가능)"
            elif q_data["objective"]["type"] == "talk":
                status = "NPC와 대화하세요"
            
            draw_text(status, 70, start_y + 90, YELLOW, small=True)
            
        # 서브 퀘스트
        sub_y = start_y + 150
        draw_text("[서브 퀘스트]", 50, sub_y, (100, 200, 255), small=True)
        count = 0
        for qid, progress in quest_manager.active_quests.items():
            if QUEST_DB[qid]["type"] == "SUB":
                q_data = QUEST_DB[qid]
                draw_text(f"- {q_data['name']}: {progress['current_count']}/{q_data['objective']['count']}", 70, sub_y + 30 + count*30, WHITE, small=True)
                count += 1
        if count == 0:
            draw_text("진행 중인 서브 퀘스트가 없습니다.", 70, sub_y + 30, GREY, small=True)

        draw_text("[X] 닫기 [Q] 닫기", WIDTH//2, HEIGHT - 50, WHITE, center=True, small=True)
        
        for event in events:
            if event.type == pygame.KEYDOWN:
                if event.key in [KEY_ACTION_2, pygame.K_q]:
                    state = state_before_quest_log
                    menu_nav_timer = now
    
    # Q키 핫키 추가 (전역 이벤트 루프 루프 외부에서 처리하거나 내부에서 처리)
    # 이미 위에서 처리했으므로 중복 제거하거나 통합
    if state in [STATE_TOWN, STATE_FIELD, STATE_QUEST_LOG]:
        for event in events:
            if event.type == pygame.KEYDOWN and event.key == pygame.K_q:
                if state == STATE_QUEST_LOG:
                    state = state_before_quest_log
                else:
                    if quest_manager.active_quests:
                        state_before_quest_log = state
                        state = STATE_QUEST_LOG
                menu_nav_timer = now

    # 화면 스케일링 및 출력
    scaled_surface = pygame.transform.scale(screen, (scaled_width, scaled_height))
    real_screen.fill(BLACK) # 여백 클리어
    real_screen.blit(scaled_surface, (offset_x, offset_y))
    pygame.display.flip()

pygame.quit()
sys.exit()
