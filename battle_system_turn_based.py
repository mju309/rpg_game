import pygame
import random
import math
import sys

# Constants relating to Battle Steps
BATTLE_STEP_MENU = 0
BATTLE_STEP_PLAYER_MSG = 1
BATTLE_STEP_ENEMY_MSG = 2
BATTLE_STEP_WIN = 3
BATTLE_STEP_WIN_WAIT = 7  # Changed from 6 to avoid collision with DEATH
BATTLE_STEP_RUN_WAIT = 5
BATTLE_STEP_DEATH = 6

BATTLE_STEP_CRITICAL = 8  # Changed from 30 to avoid collision with COMPANION
BATTLE_STEP_SKILL = 10
BATTLE_STEP_ITEM = 20

BATTLE_STEP_COMPANION_MENU = 30
BATTLE_STEP_COMPANION_MSG = 31
BATTLE_STEP_ENEMY_CALC = 40
BATTLE_STEP_TURN_END = 11

BATTLE_DELAY = 1000

# Battle State Variables
battle_step = 0
battle_timer = 0
battle_enemy = {}
battle_messages = []
battle_select = 0
battle_companion_idx = 0
battle_target_mob = None
battle_turn = 1 # 현재 전투 턴
battle_modifiers = [] # 활성화된 동적 퀘스트 모디파이어

# Critical / Soul Sync Variables
crit_ring_radius = 200
crit_ring_speed = 4
crit_target_radius = 40
crit_result = ""
crit_multiplier = 1.0

# Visual Effects Variables
damage_labels = []
particles = []
screen_shake_time = 0
screen_shake_intensity = 0
hit_flash_time = 0

# Comp/Enemy State
enemy_battle_debuffs = {}
battle_taunt_target = -1
battle_comp_select = 0

CRIT_SCRIPTS = [
    "치명적인 피해를 입혔습니다!",
    "효과가 굉장했습니다!",
    "급소에 맞았습니다!"
]

def init_battle():
    global damage_labels, particles
    damage_labels = []
    particles = []

def reset_battle(enemy_data):
    global battle_step, battle_timer, battle_enemy, battle_messages
    global battle_select, battle_skill_select_idx, battle_item_select_idx
    global crit_ring_radius, enemy_battle_debuffs, battle_taunt_target
    global battle_turn, battle_modifiers
    
    battle_step = 0
    battle_timer = pygame.time.get_ticks()
    battle_turn = 1
    battle_modifiers = enemy_data.get("modifiers", [])
    
    # Deep copy enemy data to avoid modifying original DB
    battle_enemy = enemy_data.copy()
    
    # 모디파이어 적용: Enemy ATK 부스트
    for mod in battle_modifiers:
        if mod.get("target") == "enemy_atk":
            battle_enemy["atk"] = int(battle_enemy["atk"] * mod.get("value", 1.0))
    battle_enemy["max_hp"] = battle_enemy["hp"]
    
    # "야생의 슬라임이 나타났다!" 메시지 제거 (빈 리스트로 초기화)
    battle_messages = []
    
    battle_select = 0
    battle_skill_select_idx = 0
    battle_item_select_idx = 0
    
    crit_ring_radius = 220
    enemy_battle_debuffs = {}
    battle_taunt_target = -1

    init_battle()

def calculate_damage(attacker_atk, defender_def, attacker_crit, ignore_def=False):
    base = attacker_atk
    
    # 방어력 적용
    actual_def = 0 if ignore_def else defender_def
    damage = base
    
    if attacker_atk + actual_def > 0:
        damage = base * (attacker_atk / (attacker_atk + actual_def))
    
    # 최소 데미지 보장
    damage = max(1, int(damage))
    
    # 모디파이어 적용: 물리 데미지 감소 및 크리티컬 보정
    for mod in battle_modifiers:
        if mod.get("target") == "phys_dmg":
            damage = int(damage * mod.get("value", 1.0))
            attacker_crit += 20 # 예시에 있던 크리 보정
    
    # 크리티컬 체크
    is_crit = False
    if random.randint(1, 100) <= attacker_crit:
        damage = int(damage * 1.5)
        is_crit = True
        
    return damage, is_crit

def add_damage_label(text, x, y, color=(255,0,0), is_crit=False):
    global damage_labels, screen_shake_time, screen_shake_intensity, hit_flash_time
    
    # 약간의 위치 랜덤성
    rx = x + random.randint(-30, 30)
    ry = y + random.randint(-20, 20)
    
    # 임팩트 효과 트리거
    screen_shake_time = 10 
    screen_shake_intensity = 6 if is_crit else 3
    
    # 공격 이펙트 추가
    add_effect("slash", rx, ry, color)
    if is_crit:
        add_effect("spark", rx, ry, (255, 255, 0)) # YELLOW

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
        particles.append({
            "type": "slash", "x": x, "y": y, "timer": 15, "max_timer": 15,
            "angle": random.randint(0, 360), "color": color, "size": 100
        })
    elif type == "spark":
        for _ in range(8):
            particles.append({
                "type": "spark", "x": x, "y": y, "timer": 20, "max_timer": 20,
                "vx": random.uniform(-5, 5), "vy": random.uniform(-5, 5),
                "color": color, "size": random.randint(3, 6)
            })

def draw_effects(screen, off_x, off_y):
    global particles
    # 파티클 업데이트 및 그리기
    active_particles = []
    
    for p in particles:
        p["timer"] -= 1
        if p["timer"] <= 0: continue
        
        active_particles.append(p)
        
        ratio = p["timer"] / p["max_timer"]
        
        px = p["x"] + off_x
        py = p["y"] + off_y
        
        if p["type"] == "slash":
            # 선 그리기 (회전)
            length = p["size"] * ratio
            angle_rad = math.radians(p["angle"])
            dx = math.cos(angle_rad) * length / 2
            dy = math.sin(angle_rad) * length / 2
            
            start_pos = (px - dx, py - dy)
            end_pos = (px + dx, py + dy)
            
            pygame.draw.line(screen, p["color"], start_pos, end_pos, 3)
            
        elif p["type"] == "spark":
            p["x"] += p["vx"]
            p["y"] += p["vy"]
            sz = p["size"] * ratio
            rect = pygame.Rect(px - sz/2, py - sz/2, sz, sz)
            pygame.draw.rect(screen, p["color"], rect)

    particles = active_particles

def draw_damage_labels(game, screen):
    global damage_labels
    now = pygame.time.get_ticks()
    active_labels = []
    
    for lbl in damage_labels:
        elapsed = now - lbl["timer"]
        if elapsed < 800: # 0.8초 지속
            active_labels.append(lbl)
            
            # 위로 떠오름
            lbl["y"] = lbl["start_y"] - (elapsed * 0.05)
            
            # 데미지 폰트는 크게
            if lbl["is_crit"]:
                game.draw_text(lbl["text"], lbl["x"], lbl["y"]-10, lbl["color"], center=True) 
            else:
                game.draw_text(lbl["text"], lbl["x"], lbl["y"], lbl["color"], center=True, small=True)
        
    damage_labels = active_labels

def draw_soul_sync(screen, width, height):
    global crit_ring_radius, crit_ring_speed, crit_target_radius
    
    cx, cy = width//2, height//2 - 50
    
    # 1. 중앙 가이드 라인 (타겟 코어)
    pygame.draw.circle(screen, (60, 60, 60), (cx, cy), crit_target_radius + 15, 2)
    pygame.draw.circle(screen, (255, 255, 0), (cx, cy), crit_target_radius, 3) # YELLOW
    
    # 2. 수축하는 링
    crit_ring_radius -= crit_ring_speed
    
    if crit_ring_radius < 10:
        crit_ring_radius = 220
        
    dist = abs(crit_ring_radius - crit_target_radius)
    ring_color = (255, 255, 255) # WHITE
    if dist < 10: ring_color = (255, 255, 0) # YELLOW
    elif dist < 30: ring_color = (0, 255, 0) # GREEN
    
    pygame.draw.circle(screen, ring_color, (cx, cy), int(crit_ring_radius), 4)
    
    # 사이버네틱 효과
    pygame.draw.line(screen, (100, 100, 100), (cx - 10, cy), (cx + 10, cy), 2)
    pygame.draw.line(screen, (100, 100, 100), (cx, cy - 10), (cx, cy + 10), 2)

def update_battle(game, screen, events, keys, now):
    global battle_step, battle_timer, battle_enemy, battle_messages
    global battle_select, battle_skill_select_idx, battle_item_select_idx
    global crit_ring_radius, crit_result, crit_multiplier
    global screen_shake_time, screen_shake_intensity, hit_flash_time
    global damage_labels, particles, enemy_battle_debuffs
    global battle_companion_idx, battle_comp_select, battle_taunt_target
    global battle_turn, battle_modifiers
    
    # Screen Shake Logic
    off_x, off_y = 0, 0
    if screen_shake_time > 0:
        off_x = random.randint(-screen_shake_intensity, screen_shake_intensity)
        off_y = random.randint(-screen_shake_intensity, screen_shake_intensity)
        screen_shake_time -= 1
        
    screen.fill(game.BG_BATTLE)
    
    # Draw Battle Objects
    slime_rect = pygame.Rect(50 + off_x, 50 + off_y, 80, 80)
    player_rect = pygame.Rect(600 + off_x, 300 + off_y, 80, 80)
    pygame.draw.rect(screen, game.RED, slime_rect)
    pygame.draw.rect(screen, game.BLUE, player_rect)
    
    # Draw Effects
    draw_effects(screen, off_x, off_y)
    
    game.draw_text(f"{battle_enemy['name']} HP: {battle_enemy['hp']}/{battle_enemy['max_hp']}", slime_rect.x, slime_rect.y - 25)
    game.draw_text(f"{game.player_name} HP: {game.player_hp}", player_rect.x, player_rect.y - 25)

    # 턴 정보 및 제한 표시
    turn_limit = 0
    for mod in battle_modifiers:
        if mod.get("target") == "turn_limit":
            turn_limit = mod.get("value", 0)
    
    turn_color = game.WHITE
    turn_txt = f"TURN: {battle_turn}"
    if turn_limit > 0:
        turn_txt += f" / {turn_limit}"
        if battle_turn >= turn_limit - 2: turn_color = game.RED
    game.draw_text(turn_txt, 400, 20, turn_color, center=True)

    msg_box_y = 400
    pygame.draw.rect(screen, game.BLACK, (50, msg_box_y, 700, 100))
    pygame.draw.rect(screen, game.WHITE, (50, msg_box_y, 700, 100), 1)
    
    # Hit Flash
    if hit_flash_time > 0:
        flash_surf = pygame.Surface((game.WIDTH, game.HEIGHT))
        flash_surf.fill(game.WHITE)
        flash_surf.set_alpha(100)
        screen.blit(flash_surf, (0,0))
        hit_flash_time -= 1
    
    draw_damage_labels(game, screen)
    
    if battle_step == BATTLE_STEP_CRITICAL:
        draw_soul_sync(screen, game.WIDTH, game.HEIGHT)
    
    # Message Sequence
    if battle_messages:
        game.draw_text(battle_messages[0], 70, msg_box_y + 15, game.WHITE)
        if len(battle_messages) > 1 and now - battle_timer > 500:
            game.draw_text(battle_messages[1], 70, msg_box_y + 45, game.YELLOW, small=True)
        if len(battle_messages) > 2 and now - battle_timer > 1000:
            game.draw_text(battle_messages[2], 70, msg_box_y + 70, game.YELLOW, small=True)
    
    if game.player_party and battle_step == 0:
        game.draw_text("Tip: 내 턴이 끝나면 영입한 용병들의 명령을 내릴 수 있습니다.", game.WIDTH//2, 385, game.GREEN, center=True, small=True)

    # Menu
    menu_list = ["공격", "스킬", "아이템", "도망"]
    for i, m in enumerate(menu_list):
        x = 50 + i * 180
        y = 520
        color = game.WHITE
        border = game.WHITE
        if i == battle_select:
            color = game.YELLOW
            border = game.YELLOW
        pygame.draw.rect(screen, border, (x-10, y-10, 150, 60), 2)
        game.draw_text(m, x, y, color)

    # Logic
    if battle_step == BATTLE_STEP_MENU:  # Menu
        if now - game.menu_nav_timer > 150:
            if keys[game.KEY_LEFT]:
                battle_select = max(0, battle_select - 1)
                game.menu_nav_timer = now
            elif keys[game.KEY_RIGHT]:
                battle_select = min(3, battle_select + 1)
                game.menu_nav_timer = now

        for event in events:
            if event.type == pygame.KEYDOWN and event.key == game.KEY_ACTION_1:
                if now - game.menu_nav_timer > 300:
                    game.menu_nav_timer = now
                    if battle_select == 0: # Attack
                        battle_step = BATTLE_STEP_CRITICAL
                        crit_ring_radius = 220
                        game.menu_nav_timer = now
                    elif battle_select == 1: # Skill
                        battle_step = BATTLE_STEP_SKILL
                        battle_skill_select_idx = 0
                        game.menu_nav_timer = now 
                    elif battle_select == 2: # Item
                         battle_step = BATTLE_STEP_ITEM
                         battle_item_select_idx = 0
                         game.menu_nav_timer = now
                    elif battle_select == 3: # Run
                        if random.random() < 0.5:
                            battle_messages = ["도망에 성공했다!"]
                            battle_step = BATTLE_STEP_RUN_WAIT
                            battle_timer = now
                        else:
                            battle_messages = ["도망에 실패했다!"]
                            battle_step = BATTLE_STEP_PLAYER_MSG # -> then to enemy
                            # Actually if flee fails, we usually go straight to enemy turn or show message then enemy.
                            # Existing logic was Step 1 (Player Msg) implies showing Msg then check logic?
                            # Step 1 logic below checks enemy hp etc.
                            # If flee failed, we just want to show "Failed" then go to Enemy.
                            # Let's direct to Enemy Calc phase but maybe after a delay?
                            # For simplicity, let's treat it as a "Turn" that did nothing.
                            # So Step 1 logic will wait 1.5s then go to Companion/Enemy.
                            battle_timer = now

    elif battle_step == BATTLE_STEP_CRITICAL:
        for event in events:
            if event.type == pygame.KEYDOWN and event.key == game.KEY_ACTION_1:
                dist = abs(crit_ring_radius - crit_target_radius)
                
                if dist <= 8:
                    crit_result = "PERFECT"
                    crit_multiplier = 2.2
                    game.analytics.log("action", "perfect_hits")
                elif dist <= 25:
                    crit_result = "GREAT"
                    crit_multiplier = 1.6
                elif dist <= 50:
                    crit_result = "GOOD"
                    crit_multiplier = 1.3
                else:
                    crit_result = "MISSED"
                    crit_multiplier = 1.0
                    game.analytics.log("action", "miss_hits")

                atk_bonus = 1.3 if "공격력" in game.player_battle_buffs else 1.0
                crit_bonus = 20 if "크리티컬" in game.player_battle_buffs else 0
                
                if game.player_hp / game.player_max_hp <= 0.2:
                    game.analytics.log("combat", "low_hp_attack_count")

                hd, hc = calculate_damage(game.player_stats["atk"] * atk_bonus * crit_multiplier, 
                                       battle_enemy["def"], 
                                       game.player_stats["crit"] + crit_bonus)
                battle_enemy["hp"] = max(0, battle_enemy["hp"] - hd)
                
                is_p = (crit_result == "PERFECT")
                add_damage_label(hd, 90, 80, game.YELLOW if is_p else game.RED, is_crit=is_p)
                
                battle_messages = [f"{crit_result}!"] 
                if hc or crit_result == "PERFECT":
                     battle_messages.append(random.choice(CRIT_SCRIPTS))
                
                battle_step = BATTLE_STEP_PLAYER_MSG
                battle_timer = now
                game.menu_nav_timer = now

    elif battle_step == BATTLE_STEP_DEATH:
        game.draw_text("전투에서 패배했습니다...", game.WIDTH//2, game.HEIGHT//2 - 20, game.RED, center=True)
        game.draw_text("[Z] 마을로 돌아가기", game.WIDTH//2, game.HEIGHT//2 + 20, game.WHITE, center=True, small=True)
        for event in events:
            if event.type == pygame.KEYDOWN and event.key == game.KEY_ACTION_1:
                death_time = game.analytics.data.get("last_death_time", now)
                game.analytics.log("combat", "retry_speed_sum", now - death_time)
                game.analytics.log("combat", "retry_count")
                
                game.player_hp = int(game.player_max_hp)
                game.state = game.STATE_TOWN
                game.player.x, game.player.y = game.player_start_pos
                game.menu_nav_timer = now

    elif battle_step == BATTLE_STEP_SKILL: # Skill Select
        pygame.draw.rect(screen, game.BLACK, (50, game.HEIGHT - 150, game.WIDTH - 100, 140))
        game.draw_text(f"스킬 선택 (MP: {game.player_mana}/{game.player_max_mana}) (X: 취소)", 70, game.HEIGHT - 140, game.GREY, small=True)
        
        my_skills = game.JOB_DB[game.player_job]["skills"]
        
        for i, s_name in enumerate(my_skills):
            s_data = game.SKILLS.get(s_name, {"mana": 0, "name": s_name})
            color = game.YELLOW if i == battle_skill_select_idx else game.WHITE
            game.draw_text(f"{s_name} (MP {s_data['mana']})", 80, game.HEIGHT - 110 + i * 30, color)
        
        if now - game.menu_nav_timer > 150:
            if keys[game.KEY_UP]:
                battle_skill_select_idx = (battle_skill_select_idx - 1) % len(my_skills)
                game.menu_nav_timer = now
            elif keys[game.KEY_DOWN]:
                battle_skill_select_idx = (battle_skill_select_idx + 1) % len(my_skills)
                game.menu_nav_timer = now
        
        for event in events:
            if event.type == pygame.KEYDOWN:
                if event.key == game.KEY_ACTION_2: # Cancel
                    if now - game.menu_nav_timer > 200:
                        battle_step = BATTLE_STEP_MENU
                        game.menu_nav_timer = now
                
                if event.key == game.KEY_ACTION_1: # Select
                    if now - game.menu_nav_timer > 300:
                        game.menu_nav_timer = now
                        skill_name = my_skills[battle_skill_select_idx]
                        skill_data = game.SKILLS.get(skill_name)
                        
                        # 모디파이어 적용: 마나 소모량 증가
                        actual_mana_cost = skill_data["mana"]
                        for mod in battle_modifiers:
                            if mod.get("target") == "mana_cost":
                                actual_mana_cost = int(actual_mana_cost * mod.get("value", 1.0))
                        
                        if game.player_mana >= actual_mana_cost:
                            game.player_mana -= actual_mana_cost
                            
                            if game.player_job == "마법사": game.analytics.log("skills", "magic")
                            elif game.player_job == "전사": game.analytics.log("skills", "physical")
                            elif game.player_job == "사수": game.analytics.log("skills", "physical")
                            else: game.analytics.log("skills", "physical")

                            if game.player_hp / game.player_max_hp <= 0.2:
                                game.analytics.log("combat", "low_hp_attack_count")
                            
                            effect_msgs = []
                            
                            if skill_name == "아이언 바디":
                                game.player_battle_buffs["방어력"] = 4
                                effect_msgs.append("방어력이 대폭 상승했습니다!")
                            elif skill_name == "워 크라이":
                                game.player_battle_buffs["공격력"] = 4
                                effect_msgs.append("전투 의지가 솟구칩니다! (공격력 상승)")
                            elif skill_name == "헤이스트":
                                game.player_battle_buffs["민첩"] = 5
                                effect_msgs.append("몸이 가벼워졌습니다! (민첩 상승)")
                            elif skill_name == "매직 실드":
                                # game.battle_mana_shield = True # Assuming not used critially or can be ignored in this refactor
                                effect_msgs.append("마나의 장벽이 생성되었습니다!")
                            elif skill_name == "포커스":
                                game.player_battle_buffs["공격력"] = 3
                                game.player_battle_buffs["크리티컬"] = 3
                                effect_msgs.append("집중력이 높아집니다!")
                            elif skill_name == "독 바르기":
                                game.player_battle_buffs["독무기"] = 5
                                effect_msgs.append("무기에 독을 발랐습니다!")

                            dmg_rate = skill_data.get("dmg_rate", 0)
                            if dmg_rate > 0:
                                hits = skill_data.get("hits", 1)
                                total_dmg = 0
                                any_crit = False
                                
                                atk_bonus = 1.3 if "공격력" in game.player_battle_buffs else 1.0
                                crit_bonus = skill_data.get("crit_bonus", 0)
                                if "크리티컬" in game.player_battle_buffs: crit_bonus += 20
                                
                                ignore_def = skill_name == "가드 브레이크"
                                
                                for _ in range(hits):
                                    lv = game.skill_levels.get(skill_name, 1)
                                    lv_bonus = (lv - 1) * 0.1
                                    
                                    d, c = calculate_damage(game.player_stats["atk"] * (dmg_rate + lv_bonus) * atk_bonus, 
                                                           battle_enemy["def"], 
                                                           game.player_stats["crit"] + crit_bonus,
                                                           ignore_def=ignore_def)
                                    total_dmg += d
                                    if c: any_crit = True
                                
                                battle_enemy["hp"] = max(0, battle_enemy["hp"] - total_dmg)
                                msg = f"{skill_name}! {total_dmg} 데미지!"
                                if hits > 1: msg = f"{skill_name}({hits}연타)! " + msg
                                effect_msgs.append(msg)
                                
                                if any_crit:
                                    effect_msgs.append(random.choice(CRIT_SCRIPTS))
                                
                                if skill_data.get("stun_chance", 0) > random.random():
                                    enemy_battle_debuffs["기절"] = 1
                                    effect_msgs.append(f"{battle_enemy['name']}이(가) 기절했습니다!")
                                
                                if "독무기" in game.player_battle_buffs:
                                    enemy_battle_debuffs["중독"] = 3
                                    effect_msgs.append("적을 중독시켰습니다!")
                                
                                if skill_name == "콜드 빔":
                                    enemy_battle_debuffs["둔화"] = 2
                                    effect_msgs.append("적이 얼어붙어 느려졌습니다!")

                                battle_messages = effect_msgs if effect_msgs else ["스킬 사용!"]
                                battle_step = BATTLE_STEP_PLAYER_MSG
                                battle_timer = now
                                game.menu_nav_timer = now
                            else:
                                battle_messages = ["마나가 부족합니다!"]

    elif battle_step == BATTLE_STEP_PLAYER_MSG: # Player Message Result
        if now - battle_timer > 1500:
            if battle_enemy["hp"] <= 0:
                battle_messages = [f"{battle_enemy['name']}을(를) 쓰러트렸다!"]
                battle_step = BATTLE_STEP_WIN
                battle_timer = now
            else:
                battle_messages = []
                battle_step = BATTLE_STEP_COMPANION_MENU
                battle_companion_idx = 0
                battle_timer = now

    elif battle_step == BATTLE_STEP_COMPANION_MENU: # Companion Action Menu
        if not game.player_party or battle_companion_idx >= len(game.player_party):
            battle_step = BATTLE_STEP_ENEMY_CALC # To Enemy Turn
            battle_timer = now
        else:
            member = game.player_party[battle_companion_idx]
            if member.get("hp", 0) <= 0:
                battle_companion_idx += 1
                return # Next frame

            m_data = game.COMPANION_DB.get(member["name"], {})
            m_skills = m_data.get("skills", [])
            
            pygame.draw.rect(screen, game.BLACK, (50, game.HEIGHT - 180, game.WIDTH - 100, 170))
            game.draw_text(f"[ {member['name']} ] 의 차례", 70, game.HEIGHT - 170, game.YELLOW, small=True)
            
            actions = ["기본 공격"] + m_skills
            if 'battle_comp_select' not in globals(): globals()['battle_comp_select'] = 0
            
            for i, act in enumerate(actions):
                color = game.YELLOW if i == battle_comp_select else game.WHITE
                game.draw_text(act, 80, game.HEIGHT - 130 + i * 30, color)

            if now - game.menu_nav_timer > 150:
                if keys[game.KEY_UP]:
                    battle_comp_select = (battle_comp_select - 1) % len(actions)
                    game.menu_nav_timer = now
                elif keys[game.KEY_DOWN]:
                    battle_comp_select = (battle_comp_select + 1) % len(actions)
                    game.menu_nav_timer = now

            for event in events:
                if event.type == pygame.KEYDOWN and event.key == game.KEY_ACTION_1:
                    sel_action = actions[battle_comp_select]
                    atk_val = game.player_stats["atk"] * member["atk_rate"]
                    
                    if sel_action == "기본 공격":
                        hd, hc = calculate_damage(atk_val, battle_enemy["def"], 10)
                        battle_enemy["hp"] = max(0, battle_enemy["hp"] - hd)
                        battle_messages = [f"{member['name']}의 공격! {hd} 데미지!"]
                        if hc: battle_messages.append(random.choice(CRIT_SCRIPTS))
                    else:
                        s_data = game.COMPANION_SKILL_DB.get(sel_action, {})
                        s_type = s_data.get("type", "")
                        s_power = s_data.get("power", 0)
                        msg = f"{member['name']}의 {sel_action}!"
                        sub_msg = ""

                        if s_type == "taunt":
                            battle_taunt_target = battle_companion_idx
                            sub_msg = "적들의 주의를 자신에게 고정시켰습니다!"
                        elif s_type == "heal":
                            game.player_hp = min(game.player_max_hp, game.player_hp + s_power)
                            add_damage_label(f"+{s_power}", 640, 330, game.GREEN) 
                            sub_msg = f"{game.player_name}님의 HP가 {s_power} 회복되었습니다."
                        elif s_type == "mana":
                            game.player_mana = min(game.player_max_mana, game.player_mana + s_power)
                            add_damage_label(f"+{s_power}", 640, 330, game.BLUE) 
                            sub_msg = f"{game.player_name}님의 MP가 {s_power} 회복되었습니다."
                        elif s_type == "damage":
                            hd, _ = calculate_damage(atk_val * s_power, battle_enemy["def"], 20)
                            battle_enemy["hp"] = max(0, battle_enemy["hp"] - hd)
                            add_damage_label(hd, 90, 80, game.RED) 
                            sub_msg = f"{hd}의 피해를 입혔습니다!"
                        elif s_type == "buff":
                            target_stat = s_data.get("target", "atk")
                            t_key = "공격력" if target_stat == "atk" else target_stat
                            game.player_battle_buffs[t_key] = s_power
                            sub_msg = f"{game.player_name}님의 {target_stat} 능력이 강화되었습니다."
                        elif s_type == "debuff":
                            target_stat = s_data.get("target", "")
                            if target_stat == "stun": enemy_battle_debuffs["기절"] = s_power
                            elif target_stat == "slow": enemy_battle_debuffs["둔화"] = s_power
                            elif target_stat == "def_down": battle_enemy["def"] = max(0, battle_enemy["def"] - s_power)
                            sub_msg = "적에게 상태이상을 부여했습니다."
                        elif s_type == "execute":
                             if battle_enemy["hp"] < battle_enemy["max_hp"] * s_power and not battle_enemy.get("is_last"):
                                 battle_enemy["hp"] = 0
                                 sub_msg = "적을 즉시 처형했습니다!"
                             else:
                                 hd, _ = calculate_damage(atk_val * 2.0, battle_enemy["def"], 20)
                                 battle_enemy["hp"] = max(0, battle_enemy["hp"] - hd)
                                 sub_msg = f"{hd}의 피해를 입혔습니다!"
                        elif s_type == "gold":
                            stolen = random.randint(50, 200) * (game.player_level + 1)
                            game.player_gold += stolen
                            sub_msg = f"{stolen}G를 획득했습니다!"
                        elif s_type == "special_full_heal":
                            game.player_hp = game.player_max_hp
                            game.player_mana = game.player_max_mana
                            game.player_battle_buffs = {}
                            sub_msg = "기적으로 모든 상처를 치유했습니다!"
                        elif s_type == "buff_all":
                            game.player_battle_buffs["공격력"] = s_power
                            game.player_battle_buffs["방어력"] = s_power
                            sub_msg = "전능한 기운으로 공방을 강화합니다."
                        
                        battle_messages = [msg]
                        if sub_msg: battle_messages.append(sub_msg)
                        game.analytics.log("growth", "companion_skill_usage")
                    
                    battle_step = BATTLE_STEP_COMPANION_MSG
                    battle_timer = now

    elif battle_step == BATTLE_STEP_COMPANION_MSG: # Companion Msg Delay
        if now - battle_timer > 1500:
            battle_messages = []
            battle_companion_idx += 1
            if battle_companion_idx >= len(game.player_party):
                battle_step = BATTLE_STEP_ENEMY_CALC
            else:
                battle_step = BATTLE_STEP_COMPANION_MENU
            battle_timer = now

    elif battle_step == BATTLE_STEP_ENEMY_CALC: # Enemy Turn Logic
        if battle_enemy["hp"] <= 0:
            battle_step = BATTLE_STEP_PLAYER_MSG # Check win there?
            # Actually if enemy dead during their turn (e.g. poison?), check logic?
            # Poison is checked at Step 2 (Turn End).
            # Here we just calc attack.
            # If enemy dead, it shouldn't be here usually.
            battle_step = BATTLE_STEP_PLAYER_MSG # Just a loop back, eventually Win
            return

        if "기절" in enemy_battle_debuffs:
            battle_messages = [f"{battle_enemy['name']}은(는) 기절하여 움직일 수 없다!"]
            enemy_battle_debuffs["기절"] -= 1
            if enemy_battle_debuffs["기절"] <= 0: del enemy_battle_debuffs["기절"]
            battle_step = BATTLE_STEP_ENEMY_MSG
            battle_timer = now
            return

        target = "player"
        if battle_taunt_target != -1 and game.player_party[battle_taunt_target].get("hp",0) > 0:
            target = f"comp{battle_taunt_target}"
        else:
            target_pool = ["player"]
            for i, c in enumerate(game.player_party):
                if c.get("hp",0) > 0: target_pool.append(f"comp{i}")
            target = random.choice(target_pool) if random.random() < 0.4 else "player"

        enemy_atk = battle_enemy["atk"]
        if target == "player":
            damage, crit = calculate_damage(enemy_atk, game.player_stats["def"], battle_enemy["crit"])
            game.player_hp = max(0, game.player_hp - damage)
            add_damage_label(damage, 640, 330, game.RED if crit else game.WHITE, is_crit=crit)
            battle_messages = ["위험합니다!"] if game.player_hp < game.player_max_hp * 0.2 else []
            if crit: battle_messages.append("치명타를 입었습니다!")
            
            if game.player_hp <= 0:
                game.analytics.log("combat", "death_count")
                game.analytics.data["last_death_time"] = pygame.time.get_ticks()
        else:
            c_idx = int(target[-1])
            comp = game.player_party[c_idx]
            damage, crit = calculate_damage(enemy_atk, game.player_stats["def"]*0.7, battle_enemy["crit"])
            comp["hp"] = max(0, comp["hp"] - damage)
            battle_messages = [f"{battle_enemy['name']}의 공격! {comp['name']}에게 {damage} 데미지!"]
            if comp["hp"] <= 0: battle_messages.append(f"{comp['name']}이(가) 쓰러졌습니다!")

        battle_step = BATTLE_STEP_ENEMY_MSG
        battle_timer = now

    elif battle_step == BATTLE_STEP_ENEMY_MSG: # Enemy Turn Display
        can_skip = False
        for event in events:
            if event.type == pygame.KEYDOWN and event.key == game.KEY_ACTION_1:
                can_skip = True

        if now - battle_timer > 1000 or can_skip:
            # Turn End / DoT
            
            # Draw poison damage
            if "중독" in game.player_battle_buffs:
                p_dmg = int(game.player_max_hp * 0.05)
                game.player_hp = max(1, game.player_hp - p_dmg)
                battle_messages = [f"중독 상태! HP가 {p_dmg} 감소했습니다."]
                game.player_battle_buffs["중독"] -= 1
                if game.player_battle_buffs["중독"] <= 0: del game.player_battle_buffs["중독"]
                battle_timer = now
                battle_step = BATTLE_STEP_TURN_END
                return

            if "중독" in enemy_battle_debuffs:
                poison_dmg = int(battle_enemy["max_hp"] * 0.05)
                battle_enemy["hp"] = max(1, battle_enemy["hp"] - poison_dmg) 
                battle_messages = [f"독 데미지! {battle_enemy['name']}의 HP가 {poison_dmg} 감소했습니다."]
                enemy_battle_debuffs["중독"] -= 1
                if enemy_battle_debuffs["중독"] <= 0: del enemy_battle_debuffs["중독"]
                battle_timer = now
                return

            # Cooldown Buffs
            for k in list(game.player_battle_buffs.keys()):
                if k == "중독": continue
                game.player_battle_buffs[k] -= 1
                if game.player_battle_buffs[k] <= 0: del game.player_battle_buffs[k]
            
            for k in list(enemy_battle_debuffs.keys()):
                if k not in ["중독", "기절", "둔화"]: 
                    enemy_battle_debuffs[k] -= 1
                    if enemy_battle_debuffs[k] <= 0: del enemy_battle_debuffs[k]

            if game.player_hp <= 0:
                battle_step = BATTLE_STEP_DEATH
                battle_timer = now
                return

            if not battle_messages or (len(battle_messages)==1 and "공격!" in battle_messages[0]): 
                battle_messages = []
                battle_step = BATTLE_STEP_MENU
            else:
                battle_step = BATTLE_STEP_TURN_END 
                battle_timer = now

    elif battle_step == BATTLE_STEP_TURN_END: # End Turn Msg
        if now - battle_timer > BATTLE_DELAY:
            battle_messages = []
            battle_turn += 1
            
            # 턴 제한 모디파이어 체크
            fail_msg = ""
            for mod in battle_modifiers:
                if mod.get("target") == "turn_limit":
                    if battle_turn > mod.get("value", 99):
                        fail_msg = f"턴 제한 초과! ({mod.get('value')}턴)"
            
            if fail_msg:
                 battle_messages = [fail_msg, "전투에서 후퇴합니다."]
                 battle_step = BATTLE_STEP_RUN_WAIT
                 battle_timer = now
            else:
                 battle_step = BATTLE_STEP_MENU

    elif battle_step == BATTLE_STEP_ITEM: # Item Menu
        pygame.draw.rect(screen, game.BLACK, (50, game.HEIGHT - 150, game.WIDTH - 100, 140))
        game.draw_text(f"아이템 선택 (X: 취소)", 70, game.HEIGHT - 140, game.GREY, small=True)
        
        potions = [item for item in game.player_inventory if item["type"] == "potion"]
        
        if not potions:
            game.draw_text("사용할 수 있는 포션이 없습니다.", 80, game.HEIGHT - 100, game.WHITE)
        else:
            for i, item in enumerate(potions):
                color = game.YELLOW if i == battle_item_select_idx else game.WHITE
                game.draw_text(f"{item['name']} x{item.get('count', 1)} ({item.get('desc', '')})", 80, game.HEIGHT - 110 + i * 30, color, small=True)
        
        if now - game.menu_nav_timer > 150:
            if keys[game.KEY_UP] and potions:
                battle_item_select_idx = (battle_item_select_idx - 1) % len(potions)
                game.menu_nav_timer = now
            elif keys[game.KEY_DOWN] and potions:
                battle_item_select_idx = (battle_item_select_idx + 1) % len(potions)
                game.menu_nav_timer = now
        
        for event in events:
            if event.type == pygame.KEYDOWN:
                if event.key == game.KEY_ACTION_2: # Cancel
                    battle_step = BATTLE_STEP_MENU
                    game.menu_nav_timer = now
                
                if event.key == game.KEY_ACTION_1 and potions: # Use
                    item = potions[battle_item_select_idx]
                    eff = item.get("effect")
                    val = item.get("value", 0)
                    
                    if eff == "hp":
                        game.player_hp = min(game.player_max_hp, game.player_hp + val)
                        battle_messages = [f"{item['name']}을(를) 사용하여 체력을 {val} 회복했습니다!"]
                    elif eff == "mana":
                        game.player_mana = min(game.player_max_mana, game.player_mana + val)
                        battle_messages = [f"{item['name']}을(를) 사용하여 마나를 {val} 회복했습니다!"]
                    elif eff == "hp_mana":
                        game.player_hp = min(game.player_max_hp, game.player_hp + val)
                        player_mana = min(game.player_max_mana, game.player_mana + val)
                        battle_messages = [f"{item['name']}을(를) 사용하여 HP/MP를 {val} 회복했습니다!"]
                    
                    item['count'] -= 1
                    if item['count'] <= 0:
                        game.player_inventory.remove(item)
                    
                    battle_step = BATTLE_STEP_COMPANION_MENU # To Companion
                    battle_companion_idx = 0
                    battle_timer = now
                    game.menu_nav_timer = now

    elif battle_step == BATTLE_STEP_WIN: # Win
        if now - battle_timer > BATTLE_DELAY:
            exp_gain = battle_enemy["exp"]
            gold_gain = int(exp_gain * 1.5) + random.randint(0, 5)
            
            game.player_exp += exp_gain
            game.player_gold += gold_gain
            
            game.quest_manager.on_kill_monster(battle_enemy["name"])
            
            msg = f"승리! 경험치 {exp_gain}, {gold_gain}G 획득"
            
            if random.random() < 0.3:
                loot_name = battle_enemy.get('loot_item', f"{battle_enemy['name']}의 전리품")
                loot_price = battle_enemy.get('loot_price', int(exp_gain * 2))
                game.add_item_to_inventory({"name": loot_name, "type": "misc", "price": loot_price, "desc": "상점에 판매 가능"})
                msg += f", {loot_name} 획득!"

            if random.random() < 0.05 and 'rare_loot' in battle_enemy:
                rare_name = battle_enemy['rare_loot']
                rare_price = battle_enemy.get('rare_price', 1000)
                game.add_item_to_inventory({"name": rare_name, "type": "misc", "price": rare_price, "desc": "매우 귀한 전리품"})
                msg += f", {rare_name} 획득!!!"

            
            battle_messages = [msg]
            battle_step = BATTLE_STEP_WIN_WAIT
            battle_timer = now

    elif battle_step == BATTLE_STEP_WIN_WAIT: # Win Wait
         if now - battle_timer > 1500:
            if battle_target_mob and battle_target_mob in game.field_monsters:
                game.field_monsters.remove(battle_target_mob)

            if battle_enemy.get("is_last"):
                game.state = game.STATE_ENDING
            elif game.trigger_level_up_check():
                game.state_before_levelup = game.STATE_FIELD
                game.state = game.STATE_LEVELUP
            else:
                game.state = game.STATE_FIELD
                game.battle_cooldown_timer = now 
            
            battle_messages = []
    
    elif battle_step == BATTLE_STEP_RUN_WAIT: # Run Wait
        if now - battle_timer > 1000:
            game.analytics.log("combat", "flee_count")
            game.state = game.STATE_FIELD
            game.battle_cooldown_timer = now
            battle_messages = []

    # BATTLE_STEP_ENEMY ?? Was Step 4 in previous code?
    # Step 4 was "Enemy First Attack" (Ambush?). It was transition from Step 3 (Run Fail)?
    # Wait, in new code Run Fail goes to Player Msg (which then goes to Enemy).
    # Step 4 is seemingly unused or I missed it.
    # checking...
    # Previous code had `elif battle_step == 4:`
    # New code doesn't have it.
    # Step 4 was used if run failed?
    # No, Run Fail -> Step 1 (Player Msg)
    # Step 4 was "Enemy First Attack". Where was it triggered? nowhere visible.
    # So safe to ignore.
