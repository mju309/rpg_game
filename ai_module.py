import os
import json
from openai import OpenAI

try:
    from api_key import API_KEY
except ImportError:
    API_KEY = None

if API_KEY:
    client = OpenAI(api_key=API_KEY)
else:
    client = None

# 정해진 10종의 히든 직업 목록
VALID_HIDDEN_JOBS = [
    "버서커", "지휘관", "현자", "학살자", "연금술사", 
    "닌자", "대장장이", "수호자", "갬블러", "방랑가"
]

def get_hidden_job_analysis(player_name, analytics_data, player_level, player_stats):
    """
    사용자가 확정한 마스터 프롬프트를 사용하여 플레이어의 히든 직업을 판정합니다.
    """
    if not client:
        return mock_analysis(player_name, analytics_data)

    # 데이터를 DNA 카테고리로 구조화
    dna_data = {
        "Combat DNA": {
            "skill_type_counts": analytics_data.get("skill_type_counts", {}),
            "perfect_hits": analytics_data.get("perfect_hits", 0),
            "miss_hits": analytics_data.get("miss_hits", 0),
            "total_battles": analytics_data.get("total_battles", 0),
            "total_turns": analytics_data.get("total_turns", 0),
            "low_hp_attack_count": analytics_data.get("low_hp_attack_count", 0),
            "flee_count": analytics_data.get("flee_count", 0)
        },
        "Growth DNA": {
            "high_lv_challenge_count": analytics_data.get("high_lv_challenge_count", 0),
            "death_count": analytics_data.get("death_count", 0),
            "blacksmith_attempts": analytics_data.get("blacksmith_attempts", 0)
        },
        "World DNA": {
            "potion_habitual": analytics_data.get("potion_habitual", 0),
            "potion_emergency": analytics_data.get("potion_emergency", 0),
            "companion_skill_usage": analytics_data.get("companion_skill_usage", 0)
        },
        "Final Specs": {
            "level": player_level,
            "stats": player_stats
        }
    }

    # 사용자 최종 확정 프롬프트
    prompt = f"""
당신은 RPG 게임 시스템 보조 AI입니다.
당신의 역할은 플레이어 행동 데이터를 해석하여,
미리 정의된 직업 중 단 하나를 판정하는 것입니다.

[플레이어 DNA 데이터]
{json.dumps(dna_data, indent=2, ensure_ascii=False)}

[직업 선택 규칙]
1. 아래 목록 중 단 하나만 선택하라:
{", ".join(VALID_HIDDEN_JOBS)}

2. 절대 새로운 직업을 창작하거나 목록 밖의 이름을 사용하지 마라.

3. 점수 기반 판단을 수행하라.
- 전투 행동: 가중치 3
- 성장/투자 성향: 가중치 2
- 월드 상호작용: 가중치 1

선택된 직업은 최소 2개 이상의 행동 지표에서
명확한 근거가 있어야 한다.

4. 동률일 경우:
전투 행동 > 성장 성향 > 월드 상호작용 순서로 우선 판단하라.

[증거 작성 규칙]
- evidence는 반드시 플레이어 DNA 데이터의 실제 항목이나 수치를 직접 언급하라.
- 추상적 표현(공격적, 전략적 등)만으로는 근거가 될 수 없다.

[금지 사항]
- 새로운 직업 창작
- 밈, 농담, 캐주얼 별명 사용
- 플레이어에 대한 감정적 평가 또는 비난

[응답 포맷]
❗ 반드시 아래 JSON 형식만 출력하라.
❗ JSON 외의 텍스트를 출력하지 마라.

{{
  "job": "직업명",
  "evidence": [
    "행동 데이터 근거 1",
    "행동 데이터 근거 2",
    "행동 데이터 근거 3 (선택)"
  ],
  "ai_comment": "당신은 <행동 요약>한 플레이를 반복했습니다. 그 결과 <직업명>의 길이 열렸습니다.",
  "alternative": null
}}

alternative는 동률이거나 판단 신뢰도가 낮을 경우에만 작성하고,
그 외에는 반드시 null로 반환하라.
"""

    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "차분하고 중립적이며 논리적인 RPG 시스템 판정자 AI입니다."},
                {"role": "user", "content": prompt}
            ],
            response_format={ "type": "json_object" }
        )
        res_text = response.choices[0].message.content.strip()
        result = json.loads(res_text)
        
        # 유효성 검증
        if result.get("job") not in VALID_HIDDEN_JOBS:
             return mock_analysis(player_name, analytics_data)
             
        return result
    except Exception as e:
        print(f"AI Error: {e}")
        return mock_analysis(player_name, analytics_data)

def mock_analysis(player_name, analytics_data):
    """안전한 모의 분석 결과"""
    return {
        "job": "방랑가",
        "evidence": ["균형 잡힌 스탯 분배", "다양한 스킬의 고른 사용", "평범한 자원 관리 패턴"],
        "ai_comment": "당신은 모든 분야에서 고른 활약을 보여주었습니다. 그 결과 방랑가의 길이 열렸습니다.",
        "alternative": null
    }

def get_ai_behavior_comment(analytics_data):
    return ""

def get_quest_curation(player_name, dna_data, available_templates, modifier_pool):
    """
    플레이어 DNA를 분석하여 가장 흥미롭고 필요한 퀘스트 3개를 큐레이션합니다.
    """
    if not client:
        return None # 로직 엔진으로 폴백

    prompt = f"""
    당신은 RPG 게임의 '의뢰 게시판 관리 AI'입니다. 
    플레이어 '{player_name}'의 DNA 데이터를 분석하여, 제공된 템플릿과 모디파이어 풀에서 가장 적합한 3개의 의뢰를 조립해 추천하십시오.

    [플레이어 DNA 데이터]
    {json.dumps(dna_data, indent=2, ensure_ascii=False)}

    [퀘스트 템플릿 풀]
    {json.dumps(available_templates, indent=2, ensure_ascii=False)}

    [모디파이어(특수 조건) 풀]
    {json.dumps(modifier_pool, indent=2, ensure_ascii=False)}

    [큐레이팅 규칙]
    1. 가중치 분석: 골드가 부족하면 골드 보너스 모디파이어를, 실력이 뛰어나면(Slayer DNA) 고난이도 의뢰를 우선하십시오.
    2. 다양성: 3개의 의뢰는 서로 다른 타입(사냥, 수집 등)과 난이도(별점)를 가지도록 구성하십시오.
    3. 논리적 조립: 템플릿에 어울리는 모디파이어를 선택하십시오. (예: 사냥 퀘스트 + 위험 모디파이어)
    4. 텍스트 지양: 오직 JSON 데이터 조립에만 집중하십시오. 새로운 텍스트를 창작하지 마십시오.

    [응답 포맷]
    {{
      "curated_quests": [
        {{
          "template_id": "템플릿 키",
          "star": 별점(1~5),
          "modifiers": ["모디파이어 키1", ...]
        }},
        ... (3개)
      ]
    }}
    """

    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "차분하고 논리적인 게임 데이터 큐레이터 AI입니다."},
                {"role": "user", "content": prompt}
            ],
            response_format={ "type": "json_object" }
        )
        return json.loads(response.choices[0].message.content.strip())
    except Exception as e:
        print(f"Quest AI Error: {e}")
        return None
