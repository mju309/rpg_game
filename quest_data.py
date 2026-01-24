
# 퀘스트 데이터 베이스
# type: MAIN 또는 SUB
# start_npc: 퀘스트 시작 NPC 이름 (촌장, 경비병 등)
# end_npc: 퀘스트 완료 NPC 이름 (촌장, 경비병, 대장장이, 상점, 전직관, 용병단장 등)
# req_level: 퀘스트 시작 최소 레벨
# req_quest: 선행 퀘스트 ID (없으면 None)
# objective: {"type": "kill"|"collect"|"talk"|"equip"|"level", "target": "...", "count": N}
# rewards: {"gold": N, "exp": N, "item": "..."}

QUEST_DB = {
    # ---------------------------------------------------------
    # 1부: 모험의 시작 (Lv.1 ~ 20)
    # ---------------------------------------------------------
    1: {
        "name": "마을의 골칫거리",
        "type": "MAIN",
        "desc": "마을 주변의 슬라임을 처치하여 안전을 확보하세요.",
        "start_npc": "촌장",
        "end_npc": "촌장",
        "req_level": 1,
        "req_quest": None,
        "objective": {"type": "kill", "target": "슬라임", "count": 1},
        "rewards": {"gold": 1000, "exp": 100}
    },
    2: {
        "name": "모험 준비",
        "type": "MAIN",
        "desc": "상점에서 기본 장비를 구매하고 장착하여 모험 준비를 하세요.",
        "start_npc": "촌장",
        "end_npc": "촌장",
        "req_level": 1,
        "req_quest": 1,
        "objective": {"type": "equip", "target": "any_weapon_armor", "count": 1}, # 로직에서 장착 여부 확인
        "rewards": {"gold": 500, "exp": 200}
    },
    3: {
        "name": "약초꾼의 의뢰",
        "type": "SUB",
        "desc": "상점 주인이 포션 재료인 새싹을 구하고 있습니다.",
        "start_npc": "경비병",
        "end_npc": "상점",
        "req_level": 2,
        "req_quest": 2,
        "objective": {"type": "kill", "target": "새싹", "count": 5},
        "rewards": {"gold": 100, "exp": 300, "item": "red_potion", "item_count": 5}
    },
    4: {
        "name": "대장장이의 부탁",
        "type": "SUB",
        "desc": "대장장이가 연구 재료로 슬라임 방울을 필요로 합니다.",
        "start_npc": "경비병",
        "end_npc": "대장장이",
        "req_level": 2,
        "req_quest": 2,
        "objective": {"type": "collect", "target": "슬라임 방울", "count": 5},
        "rewards": {"gold": 200, "exp": 300, "item": "iron_necklace", "item_count": 1}
    },
    5: {
        "name": "숲의 평화",
        "type": "MAIN",
        "desc": "마을 주변 숲의 버섯들을 처치하여 생태계를 안정시키세요.",
        "start_npc": "촌장",
        "end_npc": "촌장",
        "req_level": 5,
        "req_quest": 2,
        "objective": {"type": "kill", "target": "버섯", "count": 3},
        "rewards": {"gold": 1000, "exp": 500}
    },
    6: {
        "name": "늑대의 위협",
        "type": "SUB",
        "desc": "용병단장이 신입 훈련용으로 늑대 사냥을 의뢰했습니다.",
        "start_npc": "경비병",
        "end_npc": "용병단장",
        "req_level": 8,
        "req_quest": 5,
        "objective": {"type": "kill", "target": "늑대", "count": 5},
        "rewards": {"gold": 300, "exp": 800, "item": "old_glove", "item_count": 1} # old_glove (가죽 장갑 가칭)
    },
    7: {
        "name": "겨울나기 준비",
        "type": "SUB",
        "desc": "상점 주인이 겨울 옷 제작을 위해 늑대 가죽을 찾습니다.",
        "start_npc": "경비병",
        "end_npc": "상점",
        "req_level": 10,
        "req_quest": 6,
        "objective": {"type": "collect", "target": "늑대 가죽", "count": 5},
        "rewards": {"gold": 500, "exp": 1000, "item": "enhancement_stone", "item_count": 2} # 강화석
    },
    8: {
        "name": "자격 증명",
        "type": "MAIN",
        "desc": "더 큰 모험을 위해 레벨 20을 달성하고 전직을 완료하세요.",
        "start_npc": "촌장",
        "end_npc": "전직관",
        "req_level": 15,
        "req_quest": 5,
        "objective": {"type": "level_job", "target": 20, "count": 1}, # 레벨 20 + 전직후 대화
        "rewards": {"gold": 2000, "exp": 3000, "item": "job_weapon_box", "item_count": 1} # 직업 무기 상자
    },

    # ---------------------------------------------------------
    # 2부: 오크 군단과 숲 (Lv.21 ~ 50)
    # ---------------------------------------------------------
    9: {
        "name": "난폭해진 오크",
        "type": "MAIN",
        "desc": "숲의 평화를 위협하는 오크들을 처치하세요.",
        "start_npc": "촌장",
        "end_npc": "촌장",
        "req_level": 20,
        "req_quest": 8,
        "objective": {"type": "kill", "target": "오크", "count": 15},
        "rewards": {"gold": 3000, "exp": 5000}
    },
    10: {
        "name": "오크의 부적",
        "type": "SUB",
        "desc": "전직관이 오크들의 주술력을 조사하기 위해 부적을 수집해달라고 합니다.",
        "start_npc": "경비병",
        "end_npc": "전직관",
        "req_level": 22,
        "req_quest": 9,
        "objective": {"type": "collect", "target": "오크의 부적", "count": 10},
        "rewards": {"gold": 1000, "exp": 6000, "item": "enhancement_stone", "item_count": 3}
    },
    11: {
        "name": "생태계 교란",
        "type": "SUB",
        "desc": "멧돼지들이 무분별하게 번식하여 숲을 망치고 있습니다.",
        "start_npc": "경비병",
        "end_npc": "경비병",
        "req_level": 25,
        "req_quest": 9,
        "objective": {"type": "kill", "target": "멧돼지", "count": 15},
        "rewards": {"gold": 1500, "exp": 7000, "item": "reinforced_leather", "item_count": 1}
    },
    12: {
        "name": "사막 원정",
        "type": "SUB",
        "desc": "용병단장이 사막 루트 개척을 위해 독사 처치를 의뢰했습니다.",
        "start_npc": "경비병",
        "end_npc": "용병단장",
        "req_level": 30,
        "req_quest": 11,
        "objective": {"type": "kill", "target": "독사", "count": 10},
        "rewards": {"gold": 5000, "exp": 8000}
    },
    13: {
        "name": "사막의 가시",
        "type": "SUB",
        "desc": "대장장이가 튼튼한 무기 재료로 선인장 가시가 필요하다고 합니다.",
        "start_npc": "경비병",
        "end_npc": "대장장이",
        "req_level": 35,
        "req_quest": 12,
        "objective": {"type": "collect", "target": "선인장 가시", "count": 15}, # 몬스터 DB 수정 필요할수도
        "rewards": {"gold": 2000, "exp": 9000, "item": "elixir", "item_count": 3}
    },
    14: {
        "name": "숲의 오염원",
        "type": "MAIN",
        "desc": "오크들의 배후에 있는 숲의 오염원, 킹 슬라임을 처치하세요.",
        "start_npc": "촌장",
        "end_npc": "촌장",
        "req_level": 40,
        "req_quest": 9,
        "objective": {"type": "kill_boss", "target": "킹 슬라임", "count": 1},
        "rewards": {"gold": 10000, "exp": 20000, "item": "hero_medal", "item_count": 1} # 용사의 훈장
    },

    # ---------------------------------------------------------
    # 3부: 사천왕 토벌 (Lv.51 ~ 100)
    # ---------------------------------------------------------
    15: {
        "name": "설원 정리",
        "type": "MAIN",
        "desc": "북쪽 설원을 점거한 예티 무리를 몰아내세요.",
        "start_npc": "촌장",
        "end_npc": "촌장",
        "req_level": 50,
        "req_quest": 14,
        "objective": {"type": "kill", "target": "예티", "count": 20},
        "rewards": {"gold": 20000, "exp": 30000}
    },
    16: {
        "name": "추위와의 싸움",
        "type": "SUB",
        "desc": "상점 주인이 귀족들에게 팔 예티 털뭉치를 대량으로 구하고 있습니다.",
        "start_npc": "경비병",
        "end_npc": "상점",
        "req_level": 55,
        "req_quest": 15,
        "objective": {"type": "collect", "target": "예티의 털뭉치", "count": 20},
        "rewards": {"gold": 30000, "exp": 40000}
    },
    17: {
        "name": "동굴의 언데드",
        "type": "SUB",
        "desc": "전직관이 사악한 기운을 정화하기 위해 스켈레톤 토벌을 요청했습니다.",
        "start_npc": "경비병",
        "end_npc": "전직관",
        "req_level": 60,
        "req_quest": 16,
        "objective": {"type": "kill", "target": "스켈레톤", "count": 30},
        "rewards": {"gold": 5000, "exp": 50000, "item": "holy_water", "item_count": 10} # 성수
    },
    18: {
        "name": "거미줄 제거",
        "type": "SUB",
        "desc": "용병단원들이 동굴 탐사 중 거미줄에 갇혔습니다. 거대거미를 처치하세요.",
        "start_npc": "경비병",
        "end_npc": "용병단장",
        "req_level": 65,
        "req_quest": 17,
        "objective": {"type": "kill", "target": "거대거미", "count": 25},
        "rewards": {"gold": 10000, "exp": 60000, "item": "elixir", "item_count": 5}
    },
    19: {
        "name": "동쪽의 재앙",
        "type": "MAIN",
        "desc": "동쪽 바다를 지배하는 크라켄을 처치하고 평화를 되찾으세요.",
        "start_npc": "촌장",
        "end_npc": "촌장",
        "req_level": 70,
        "req_quest": 15,
        "objective": {"type": "kill_boss", "target": "심해의 크라켄", "count": 1},
        "rewards": {"gold": 50000, "exp": 100000, "item": "hero_armor", "item_count": 1} # 영웅 갑옷
    },
    20: {
        "name": "전설의 재료",
        "type": "SUB",
        "desc": "대장장이가 전설의 무기를 만들기 위해 크라켄의 다리를 원합니다.",
        "start_npc": "경비병",
        "end_npc": "대장장이",
        "req_level": 80,
        "req_quest": 19,
        "objective": {"type": "collect", "target": "크라켄 다리", "count": 1},
        "rewards": {"gold": 0, "exp": 120000, "item": "legendary_weapon_scroll", "item_count": 1} # 전설 무기 제작권/재료
    },
    21: {
        "name": "서쪽의 재앙",
        "type": "MAIN",
        "desc": "서쪽 화산 지대의 문지기 켈베로스를 처치하세요.",
        "start_npc": "촌장",
        "end_npc": "촌장",
        "req_level": 85,
        "req_quest": 19,
        "objective": {"type": "kill_boss", "target": "지옥의 켈베로스", "count": 1},
        "rewards": {"gold": 50000, "exp": 150000, "item": "hero_helm", "item_count": 1} # 영웅 투구
    },

    # ---------------------------------------------------------
    # 4부: 최후의 결전 (Lv.90 ~ )
    # ---------------------------------------------------------
    22: {
        "name": "결전의 시간",
        "type": "MAIN",
        "desc": "모든 준비가 끝났습니다. 마왕성으로 진입하여 최후의 결전을 준비하세요.",
        "start_npc": "촌장",
        "end_npc": "촌장", # 대화 후 맵 이동 트리거
        "req_level": 90,
        "req_quest": 21,
        "objective": {"type": "talk", "target": "촌장", "count": 1},
        "rewards": {"gold": 0, "exp": 0}
    },
    23: {
        "name": "마왕 토벌",
        "type": "MAIN",
        "desc": "이 세계를 위협하는 마왕을 처치하고 영원한 평화를 가져오세요.",
        "start_npc": "시스템", # 자동 시작
        "end_npc": "시스템", # 보스 처치 시 자동 완료 및 엔딩
        "req_level": 90,
        "req_quest": 22,
        "objective": {"type": "kill_boss", "target": "마왕", "count": 1},
        "rewards": {"gold": 1000000, "exp": 1000000}
    }
}
