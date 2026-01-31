import random
import json
import dynamic_quest_data as data
import ai_module

def has_batchim(text):
    if not text: return False
    last_char = text[-1]
    if 0xAC00 <= ord(last_char) <= 0xD7A3:
        return (ord(last_char) - 0xAC00) % 28 > 0
    return False

def get_josa(text, type):
    if type == "이/가":
        return text + ("이" if has_batchim(text) else "가")
    if type == "을/를":
        return text + ("을" if has_batchim(text) else "를")
    return text

def weighted_pick(choices, weights):
    """가중치 기반 랜덤 선택 함수"""
    total_weight = sum(weights)
    pick = random.uniform(0, total_weight)
    current = 0
    for i, weight in enumerate(weights):
        current += weight
        if current >= pick:
            return choices[i]
    return choices[-1]

def get_player_needs_weights(player_gold, analytics_data):
    """플레이어 상태에 따른 보상 및 난이도 가중치 계산"""
    weights = {"gold": 1.0, "exp": 1.0, "easy": 1.0, "hard": 1.0}
    
    # 골드 가중치: 돈이 적을수록 골드 퀘스트 선호 (최대 1.5배)
    if player_gold < 2000:
        weights["gold"] = 1.5
    elif player_gold > 10000:
        weights["gold"] = 0.7 # 돈이 많으면 골드 의뢰 축소
        
    # 난이도 성향: 도전적인 플레이어는 어려운 퀘스트 선호
    slayer_score = analytics_data.get('high_lv_challenge_count', 0)
    if slayer_score > 5:
        weights["hard"] = 1.3
    
    return weights

def generate_dynamic_quests(player_level, analytics_data, monster_db, map_data, player_gold, player_name="Adventurer"):
    """
    AI 하이브리드 로직을 이용한 동적 퀘스트 생성.
    AI가 있으면 DNA 기반 큐레이션을 수행하고, 없으면 기본 확률 엔진으로 작동합니다.
    """
    generated_quests = []
    
    # 1. AI DNA 큐레이션 시도
    ai_curation = ai_module.get_quest_curation(
        player_name, 
        analytics_data, 
        data.QUEST_TEMPLATES, 
        data.MODIFIER_POOL
    )
    
    # 2. 이용 가능한 몬스터 필터링
    available_monsters = []
    for m_id, m_info in monster_db.items():
        m_map_idx = m_info.get("map_idx", 0)
        map_lv = map_data[m_map_idx].get("min_lv", 0)
        if map_lv <= player_level + 10:
            available_monsters.append((m_id, m_info, map_lv))
            
    if not available_monsters:
        return []

    needs = get_player_needs_weights(player_gold, analytics_data)

    # 3. 퀘스트 생성 (AI 결과가 있으면 활용, 없으면 로직 엔진)
    if ai_curation and "curated_quests" in ai_curation:
        raw_list = ai_curation["curated_quests"]
    else:
        # 로직 엔진용 가짜(모의) 큐레이션 생성
        raw_list = []
        for _ in range(3):
            # 난이도 결정 (가중치 반영)
            possible_stars = []
            star_weights = []
            for star, rules in data.DIFFICULTY_RULES.items():
                req = rules["unlock_req"]
                if req:
                    if "min_level" in req and player_level < req["min_level"]: continue
                    if "special" in req and req["special"] == "boss_slayer":
                        if analytics_data.get('high_lv_challenge_count', 0) < 10: continue
                possible_stars.append(star)
                base_w = (6 - star); 
                if star >= 4: base_w *= needs["hard"]
                star_weights.append(base_w)
            
            sel_star = weighted_pick(possible_stars, star_weights)
            sel_tpl = random.choice(list(data.QUEST_TEMPLATES.keys()))
            
            sel_mods = []
            rule = data.DIFFICULTY_RULES[sel_star]
            if random.random() < rule["modifier_chance"]:
                pm = [k for k, v in data.MODIFIER_POOL.items() if sel_star in v["allowed_stars"]]
                if pm: sel_mods.append(random.choice(pm))
                
            raw_list.append({"template_id": sel_tpl, "star": sel_star, "modifiers": sel_mods})

    # 최종 퀘스트 객체 조립
    for i, item in enumerate(raw_list):
        star = item.get("star", 1)
        tpl_key = item.get("template_id", "extermination")
        tpl = data.QUEST_TEMPLATES.get(tpl_key, data.QUEST_TEMPLATES["extermination"])
        rule = data.DIFFICULTY_RULES.get(star, data.DIFFICULTY_RULES[1])
        
        # 대상 몬스터 선택 (별점에 따른 가중치 시스템 동일하게 사용)
        monster_candidates = []
        for m in available_monsters:
            lv_diff = m[2] - player_level
            m_weight = 1.0
            if star == 1: m_weight = 1.0 if lv_diff <= 0 else 0.1
            if star >= 4: m_weight = 1.0 if lv_diff > 0 else 0.5
            monster_candidates.append((m, m_weight))
            
        target_tuple = weighted_pick([c[0] for c in monster_candidates], [c[1] for c in monster_candidates])
        target_id, target_info, target_lv = target_tuple
        
        # 보상 및 텍스트 완성 로직 동일 적용
        modifiers = item.get("modifiers", [])
        base_gold = (target_lv * 50 + 200) * rule["reward_mult"]
        base_exp = (target_lv * 30 + 100) * rule["reward_mult"]
        
        gold_mult, exp_mult = 1.0, 1.0
        for m_key in modifiers:
            if m_key in data.MODIFIER_POOL:
                m_info = data.MODIFIER_POOL[m_key]
                gold_mult *= m_info.get("reward_bonus", {}).get("gold", 1.0)
                exp_mult *= m_info.get("reward_bonus", {}).get("exp", 1.0)
            
        final_gold = int(base_gold * gold_mult * needs["gold"])
        final_exp = int(base_exp * exp_mult * needs["exp"])
        
        count = random.randint(3 + star, 10 + star * 2)
        target_original_name = target_info["name"]
        if tpl["type"] == "collect":
            target_original_name = target_info.get("loot_item", f"{target_original_name}의 흔적")
            
        name = tpl['name_format'].format(target=target_original_name)
        
        # 조사(Josa) 처리 적용
        if "{target}가" in tpl["desc_format"] or "{target}이" in tpl["desc_format"]:
            target_with_josa = get_josa(target_original_name, "이/가")
            desc = tpl["desc_format"].replace("{target}가", "{target}").replace("{target}이", "{target}").format(target=target_with_josa, count=count)
        elif "{target}를" in tpl["desc_format"] or "{target}을" in tpl["desc_format"]:
            target_with_josa = get_josa(target_original_name, "을/를")
            desc = tpl["desc_format"].replace("{target}를", "{target}").replace("{target}을", "{target}").format(target=target_with_josa, count=count)
        else:
            desc = tpl["desc_format"].format(target=target_original_name, count=count)
            
        mod_objects = []
        for m_key in modifiers:
            if m_key in data.MODIFIER_POOL:
                m_obj = data.MODIFIER_POOL[m_key].copy()
                m_obj["name"] = m_key
                mod_objects.append(m_obj)
            
        generated_quests.append({
            "id": 2000 + i + random.randint(1, 9999),
            "name": name, "desc": desc, "type": "DYNAMIC",
            "objective": {"type": tpl["type"], "target": target_original_name, "count": count},
            "rewards": {"gold": final_gold, "exp": final_exp},
            "star": star, "modifiers": mod_objects
        })
        
    return generated_quests
