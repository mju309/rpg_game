
import pygame
import random
import math

# 전투 시퀀스 전술 단계
BATTLE_STEP_CRITICAL = 100 
BATTLE_STEP_DEATH = 200

# 부유하는 데미지 수치
damage_labels = [] 
particles = [] # 이펙트 파티클 리스트

# 연출 효과 변수
screen_shake_time = 0
screen_shake_intensity = 0
hit_flash_time = 0
hit_flash_color = (255, 255, 255)

# 소울 싱크로나이즈 (크리티컬 시스템) 관련 변수
crit_ring_radius = 200 # 시작 반경
crit_target_radius = 40 # 목표 반경 (중앙 코어 크기)
crit_ring_speed = 6 # 축소 속도
crit_result = None
crit_multiplier = 1.0

# ----------------------------------------------------
# 데미지 라벨 시스템
# ----------------------------------------------------
def add_damage_label(text, x, y, color=(255, 60, 60), is_crit=False):
    global damage_labels, screen_shake_time, screen_shake_intensity, hit_flash_time
    # 약간의 위치 랜덤성
    rx = x + random.randint(-30, 30)
    ry = y + random.randint(-20, 20)
    
    # 임팩트 효과 트리거
    screen_shake_time = 10 # 프레임 수
    screen_shake_intensity = 6 if is_crit else 3 # 강도 조절
    
    # 공격 이펙트 추가 (Procedural Effect)
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

def draw_effects(screen, off_x, off_y):
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
            
            pygame.draw.line(screen, (255, 255, 255), p1, p2, 5) # Core styling
            pygame.draw.line(screen, p["color"], p1, p2, 3) # Inner color

        elif p["type"] == "particle":
            p["x"] += p["vx"]
            p["y"] += p["vy"]
            pygame.draw.circle(screen, p["color"], (int(p["x"] + off_x), int(p["y"] + off_y)), p["size"])

def draw_damage_labels(screen, font):
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
        
        # 폰트 크기 혹은 스케일링 처리
        # 여기서는 단순히 render 후 transform.scale
        
        # 텍스트 렌더링
        txt_surf = font.render(label["text"], True, label["color"])
        # 크기 확대 (1.5배) - 여기서는 단순히 기본 폰트를 키우는 로직 대신 스케일로 처리
        # 만약 font 객체 자체를 큰 걸 쓰려면 매개변수로 큰 폰트를 받아야 함
        # 여기서는 스케일링 사용
        scale = 2.0 if label["is_crit"] else 1.5
        w = int(txt_surf.get_width() * scale)
        h = int(txt_surf.get_height() * scale)
        scaled_surf = pygame.transform.scale(txt_surf, (w, h))
        
        # 외곽선 (검은색 그림자 효과)
        shadow_surf = font.render(label["text"], True, (0, 0, 0))
        shadow_scaled = pygame.transform.scale(shadow_surf, (w, h))
        
        # 위치
        draw_x = label["x"] - w//2
        draw_y = curr_y - h//2
        
        # 외곽선 그리기 (4방향)
        for dx, dy in [(-2,0), (2,0), (0,-2), (0,2)]:
            screen.blit(shadow_scaled, (draw_x + dx, draw_y + dy))
            
        screen.blit(scaled_surf, (draw_x, draw_y))

# ----------------------------------------------------
# 소울 싱크(크리티컬 바) 그리기
# ----------------------------------------------------
def draw_soul_sync(screen, WIDTH, HEIGHT):
    global crit_ring_radius, crit_ring_speed, crit_target_radius
    
    # 화면 중앙
    cx, cy = WIDTH//2, HEIGHT//2 - 50
    
    # 1. 중앙 가이드 라인 (타겟 코어)
    pygame.draw.circle(screen, (60, 60, 60), (cx, cy), crit_target_radius + 15, 2) # Outer Guide
    pygame.draw.circle(screen, (255, 255, 0), (cx, cy), crit_target_radius, 3) # Perfect Core (YELLOW)
    
    # 2. 수축하는 링 (Soul Ring)
    # 시간에 따라 반경 감소
    crit_ring_radius -= crit_ring_speed
    
    # 링이 코어보다 작아지면 다시 크게 (실패 방지 루프 - 실제로는 도중에 누름)
    if crit_ring_radius < 10:
        crit_ring_radius = 220
        
    # 링 색상 결정 (목표에 가까워질수록 밝아짐)
    dist = abs(crit_ring_radius - crit_target_radius)
    ring_color = (255, 255, 255)
    if dist < 10: ring_color = (255, 255, 0) # YELLOW
    elif dist < 30: ring_color = (0, 255, 0) # GREEN
    
    pygame.draw.circle(screen, ring_color, (cx, cy), int(crit_ring_radius), 4)
    
    # 사이버네틱 효과 (십자 가이드)
    pygame.draw.line(screen, (100, 100, 100), (cx - 10, cy), (cx + 10, cy), 2)
    pygame.draw.line(screen, (100, 100, 100), (cx, cy - 10), (cx, cy + 10), 2)

