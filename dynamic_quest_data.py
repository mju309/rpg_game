# 동적 퀘스트 시스템을 위한 고도화된 데이터베이스

# 1. 난이도 정의 (Difficulty Rules)
# - stars: 1~5 난이도
# - prefix: 퀘스트 이름 앞에 붙을 수식어
# - modifier_chance: 특수 조건(Modifier)이 붙을 확률
# - modifier_count: 붙을 특수 조건의 개수
# - reward_mult: 기본 보상 배수
# - unlock_req: 전설 퀘스트 등을 위한 해금 조건 (플레이어 레벨, 특정 보스 처치 등)
DIFFICULTY_RULES = {
    1: {
        "label": "★☆☆☆☆ (초보)",
        "modifier_chance": 0.0,
        "modifier_count": 0,
        "reward_mult": 1.0,
        "unlock_req": None
    },
    2: {
        "label": "★★☆☆☆ (쉬움)",
        "modifier_chance": 0.3, # 30% 확률로 긍정적 변수
        "modifier_count": 1,
        "reward_mult": 1.2,
        "unlock_req": {"min_level": 5}
    },
    3: {
        "label": "★★★☆☆ (보통)",
        "modifier_chance": 1.0, # 100% 특수 조건 부여
        "modifier_count": 1,
        "reward_mult": 1.5,
        "unlock_req": {"min_level": 15}
    },
    4: {
        "label": "★★★★☆ (어려움)",
        "modifier_chance": 0.5, # 이미 목표가 어려우므로 변수는 적당히
        "modifier_count": 1,
        "reward_mult": 2.5,
        "unlock_req": {"min_level": 30, "min_main_quest": 8}
    },
    5: {
        "label": "★★★★★ (전설)",
        "modifier_chance": 0.0, # 순수 실력 대결, 변수 배제
        "modifier_count": 0,
        "reward_mult": 5.0,
        "unlock_req": {"min_level": 50, "special": "boss_slayer"} # Slayer DNA 혹은 보스 처치 기록
    }
}

# 2. 특수 조건 풀 (Modifier Pool)
# - type: 버프, 디버프, 환경, 제약
# - target: 영향을 주는 스탯이나 시스템
# - value: 보정치
# - reward_bonus: 이 조건이 붙었을 때 추가되는 보상 배수
MODIFIER_POOL = {
    "풍족": {
        "desc": "마을의 지원금이 넉넉합니다. (보상 골드 +20%)",
        "type": "buff",
        "reward_bonus": {"gold": 1.2},
        "allowed_stars": [2]
    },
    "긴급": {
        "desc": "긴급한 상황입니다. (각 전투당 5턴 제한, 보상 경험치 +50%)",
        "type": "constraint",
        "target": "turn_limit",
        "value": 5,
        "reward_bonus": {"exp": 1.5},
        "allowed_stars": [3, 4]
    },
    "위험": {
        "desc": "몬스터가 흥분 상태입니다. (몬스터 공격력 +50%, 보상 x2)",
        "type": "hazard",
        "target": "enemy_atk",
        "value": 1.5,
        "reward_bonus": {"gold": 2.0, "exp": 2.0},
        "allowed_stars": [3, 4]
    },
    "마력 역류": {
        "desc": "불안정한 마력이 흐릅니다. (마법 스킬 마나 소모량 2배, 보상 골드 +80%)",
        "type": "environment",
        "target": "mana_cost",
        "value": 2.0,
        "reward_bonus": {"gold": 1.8},
        "allowed_stars": [3]
    },
    "무뎌진 칼날": {
        "desc": "공기가 무겁습니다. (물리 데미지 -30%, 크리티컬 확률 +20%)",
        "type": "environment",
        "target": "phys_dmg",
        "value": 0.7,
        "reward_bonus": {"exp": 1.5},
        "allowed_stars": [3, 4]
    }
}

# 3. 퀘스트 베이스 템플릿
# - 몬스터 사냥, 재료 수집 핵심 로직
QUEST_TEMPLATES = {
    "extermination": {
        "name_format": "{target} 토벌",
        "desc_format": "마을 인근의 {target}가 평화를 위협하고 있습니다.\n총 {count}마리를 처치해주세요.",
        "type": "kill"
    },
    "collection": {
        "name_format": "{target} 수집",
        "desc_format": "연구를 위해 {target}가 급히 필요합니다.\n총 {count}개를 모아주세요.",
        "type": "collect"
    },
    "recon": {
        "name_format": "{target} 조사",
        "desc_format": "{target}들의 움직임이 이상합니다.\n총 {count}마리를 조사하며 상대해주세요.",
        "type": "kill"
    }
}

# 4. 가중치 매핑 (DNA Rolling Data)
# 플레이어 상태에 따라 어떤 유형의 퀘스트/보상 확률을 높일지 정의
WEIGHT_FACTORS = {
    "low_gold": {
        "condition": lambda p: p['gold'] < 2000,
        "boost": {"reward": "gold", "value": 1.5}
    },
    "high_slayer": {
        "condition": lambda p: p['analytics'].get('high_lv_challenge_count', 0) > 5,
        "boost": {"difficulty": "high", "value": 1.3}
    },
    "potion_lover": {
        "condition": lambda p: p['analytics'].get('potion_habitual', 0) > 20,
        "boost": {"reward_item": "potion", "value": 1.4}
    }
}
