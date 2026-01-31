def get_dialog(type, **kwargs):
    """
    대사 타입과 필요한 인자(kwargs)를 받아 대사 리스트를 반환합니다.
    type: "CHEIF_DEFAULT", "MAIN_COMPLETE", "MAIN_PROGRESS", 
          "SUB_COMPLETE", "SUB_NEW", "NPC_DEFAULT"
    kwargs: player_name, quest_name, reward_gold, reward_exp, quest_desc, npc_name
    """
    player_name = kwargs.get("player_name", "모험가")
    quest_id = kwargs.get("quest_id", 0)
    quest_name = kwargs.get("quest_name", "")
    reward_gold = kwargs.get("reward_gold", 0)
    reward_exp = kwargs.get("reward_exp", 0)
    quest_desc = kwargs.get("quest_desc", "")
    npc_name = kwargs.get("npc_name", "")

    # ------------------------------------------------
    # 1. 촌장 (메인 퀘스트)
    # ------------------------------------------------
    if type == "CHIEF_DEFAULT":
        # 3(퀘스트 클리어 후 첫 대화 후 대화) - 더 이상 메인 퀘스트가 없을 때
        return [
            "마을 밖은 위험하니 조심하게.",
            "더 강한 몬스터들이 기다리고 있을걸세."
        ]
    
    elif type == "MAIN_COMPLETE":
        # 2(퀘스트 클리어 후 첫 대화) - 해당 퀘스트 완료 시
        if quest_id == 1:
            return [
                "오오, 무사히 돌아왔군!",
                "슬라임을 처치하다니 대단해.",
                "이제 자네도 어엿한 모험가야.",
                "레벨업을 했다면 C키를 눌러 스탯을 올려보게.",
                "이제 더 넓은 세상으로 나갈 준비가 된 것 같구만.",
                f"보상: {reward_gold}G, {reward_exp}EXP"
            ]
        else:
            return [
                f"훌륭하네! 자네가 해낼 줄 알았어.",
                f"[{quest_name}] 완료!",
                f"보상: {reward_gold}G, {reward_exp}EXP"
            ]
    
    elif type == "MAIN_PROGRESS":
        # 0(처음 대화) & 1(첫 대화 후 진행 중)
        # 진행도(count)를 알면 구분 가능하지만, 여기서는 quest_desc가 넘어옴.
        # 1번 퀘스트의 경우
        if quest_id == 1:
             # 진행 상황에 따라 구분해야 하는데, game.py나 quest.py에서 구분 로직이 없으면
             # 범용적으로 두 대사를 섞거나, 랜덤? 
             # 여기서는 '진행 중'이므로 1번 대사가 적절함.
             # 0번 대사는 '퀘스트 시작'인데 자동 시작이므로 플레이어가 처음 촌장을 볼 땐 이미 진행 중임.
             # 하지만 플레이어 입장에선 처음 보는 거라면 0번이 맞음.
             # 이를 구분하려면 quest_manager가 '이 퀘스트에 대해 대화를 한 적이 있는지'를 알아야 함.
             # 하지만 복잡해지므로, 그냥 '진행 중' 대사를 1번으로 고정하고,
             # 0번은 게임 시작 시 프롤로그 등으로 처리하는게 맞음.
             # 사용자 요청은 'dialog_map 스타일'이므로, 그 뉘앙스를 살려 1번을 출력.
             return [
                "아직 슬라임을 처치하지 못했나?",
                "숲은 마을 북쪽에 있다네."
             ]
        else:
             return [
                f"{player_name}, 자네만 믿고 있네."
             ]
    
    # 0번 대사(처음 대화)를 위한 별도 타입 추가
    elif type == "CHIEF_START":
        if quest_id == 1:
            return [
                f"반갑네, {player_name}.",
                "숲 속에 슬라임이 나타났다네.",
                "가서 슬라임과 싸워주게!"
            ]
        elif quest_id == 2:
            return [
                "장비가 부실해 보이는군.",
                "마을 아래쪽에 있는 상점으로 가서 무기와 방어구를 하나씩 구매해서 착용하게.",
                "장비는 C키를 눌러서 착용할 수 있다네!"
            ]
        elif quest_id == 5:
            return [
                "장비를 갖추었으니 이제 본격적인 훈련일세.",
                "숲속의 버섯들이 너무 늘어나고 있어.",
                "마을 주변 숲에서 버섯 3마리만 처치해 주게!"
            ]
        else:
            return [f"{player_name}, 새로운 임무일세."]

    # ------------------------------------------------
    # 2. 서브 퀘스트 (공통)
    # ------------------------------------------------
    elif type == "SUB_COMPLETE":
        return [
            "수고했네. 여기 보상일세.",
            f"[{quest_name}] 의뢰 완료!",
            f"보상: {reward_gold}G, {reward_exp}EXP"
        ]
    
    elif type == "SUB_NEW":
        return [
            "새로운 의뢰가 들어왔네.",
            f"[{quest_name}] 의뢰 수락."
        ]

    # ------------------------------------------------
    # 3. NPC 기본 대사 (퀘스트 없을 때)
    # ------------------------------------------------
    elif type == "NPC_DEFAULT":
        if npc_name == "게시판":
            return ["게시판에 새로운 의뢰가 가득합니다.", "마을의 소식들을 확인해 보세요."]
        elif npc_name == "대장장이":
            return ["어이, 장비 강화하러 왔나?", "내 실력은 확실하지."]
        elif npc_name == "상점":
            return ["어서오세요! 좋은 물건 많아요.", "필요한 게 있으신가요?"]
        elif npc_name == "전직관":
            return ["자신의 한계를 시험하게.", "더 높은 곳을 향해 정진하게."]
        elif npc_name == "용병단장":
            return ["동료가 필요하면 언제든 말하게.", "강한 녀석들로 준비해뒀지."]
        else:
            return [f"반갑네, {player_name}."]  
    
    return []
