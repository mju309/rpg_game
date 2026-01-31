
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
        "objective": {"type": "equip", "target": "any_weapon_armor", "count": 1},
        "rewards": {"gold": 500, "exp": 200}
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
    8: {
        "name": "자격 증명",
        "type": "MAIN",
        "desc": "더 큰 모험을 위해 레벨 20을 달성하고 전직을 완료하세요.",
        "start_npc": "촌장",
        "end_npc": "전직관",
        "req_level": 20,
        "req_quest": 5,
        "objective": {"type": "level_job", "target": 20, "count": 1},
        "rewards": {"gold": 2000, "exp": 3000, "item": "job_weapon_box", "item_count": 1}
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
    14: {
        "name": "숲의 오염원",
        "type": "MAIN",
        "desc": "오크들의 배후에 있는 숲의 오염원, 킹 슬라임을 처치하세요.",
        "start_npc": "촌장",
        "end_npc": "촌장",
        "req_level": 40,
        "req_quest": 9,
        "objective": {"type": "kill_boss", "target": "킹 슬라임", "count": 1},
        "rewards": {"gold": 10000, "exp": 20000, "item": "hero_medal", "item_count": 1}
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
    19: {
        "name": "동쪽의 재앙",
        "type": "MAIN",
        "desc": "동쪽 바다를 지배하는 크라켄을 처치하고 평화를 되찾으세요.",
        "start_npc": "촌장",
        "end_npc": "촌장",
        "req_level": 70,
        "req_quest": 15,
        "objective": {"type": "kill_boss", "target": "심해의 크라켄", "count": 1},
        "rewards": {"gold": 50000, "exp": 100000, "item": "hero_armor", "item_count": 1}
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
        "rewards": {"gold": 50000, "exp": 150000, "item": "hero_helm", "item_count": 1}
    },

    # ---------------------------------------------------------
    # 4부: 최후의 결전 (Lv.90 ~ )
    # ---------------------------------------------------------
    22: {
        "name": "결전의 시간",
        "type": "MAIN",
        "desc": "모든 준비가 끝났습니다. 마왕성으로 진입하여 최후의 결전을 준비하세요.",
        "start_npc": "촌장",
        "end_npc": "촌장",
        "req_level": 90,
        "req_quest": 21,
        "objective": {"type": "talk", "target": "촌장", "count": 1},
        "rewards": {"gold": 0, "exp": 0}
    },
    23: {
        "name": "마왕 토벌",
        "type": "MAIN",
        "desc": "이 세계를 위협하는 마왕을 처치하고 영원한 평화를 가져오세요.",
        "start_npc": "시스템",
        "end_npc": "시스템",
        "req_level": 90,
        "req_quest": 22,
        "objective": {"type": "kill_boss", "target": "마왕", "count": 1},
        "rewards": {"gold": 1000000, "exp": 1000000}
    }
}
