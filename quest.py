from quest_data import QUEST_DB
from quest_dialog import get_dialog

class QuestManager:
    def __init__(self):
        self.main_quest_id = 1  # 1번부터 시작
        self.completed_quests = set()
        self.active_quests = {} # {quest_id: {"current_count": 0}} 서브 전용이 아닌, 진행 중인 모든 퀘스트(주로 서브)
        self.quest_display_text = "" # 화면에 표시될 텍스트
        self.allow_sub_quests = False # 서브 퀘스트 활성화 여부

    def get_quest_info(self, quest_id):
        return QUEST_DB.get(quest_id)

    def is_quest_completed(self, quest_id):
        return quest_id in self.completed_quests

    def is_quest_active(self, quest_id):
        return quest_id in self.active_quests or (quest_id == self.main_quest_id and QUEST_DB[quest_id]["type"] == "MAIN")

    def start_quest(self, quest_id):
        if quest_id not in QUEST_DB:
            return False
            
        q_data = QUEST_DB[quest_id]
        if q_data["type"] == "MAIN":
            self.main_quest_id = quest_id
            if quest_id not in self.active_quests:
                self.active_quests[quest_id] = {"current_count": 0}
        else:
            if quest_id not in self.active_quests:
                self.active_quests[quest_id] = {"current_count": 0}
            
        self.update_display_text()
        return True

    def complete_quest(self, quest_id, player_inventory=None, player_gold=None, player_exp=None):
        if not self.is_quest_active(quest_id):
            return None, None, None # gold, exp, items

        q_data = QUEST_DB[quest_id]
        
        # 보상 지급을 위한 데이터 반환
        rewards = q_data.get("rewards", {})
        r_gold = rewards.get("gold", 0)
        r_exp = rewards.get("exp", 0)
        r_items = []
        r_items = []
        if "item" in rewards:
            r_items.append({"name": rewards["item"], "count": rewards.get("item_count", 1)})

        self.completed_quests.add(quest_id)
        
        # 목록에서 제거
        if quest_id in self.active_quests:
            del self.active_quests[quest_id]

        if q_data["type"] == "MAIN":
            # 현재 퀘스트를 선행으로 하는 다음 'MAIN' 퀘스트를 찾음
            next_main = None
            for q_id, q_info in QUEST_DB.items():
                if q_info["type"] == "MAIN" and q_info.get("req_quest") == quest_id:
                    next_main = q_id
                    break
            
            if next_main:
                self.main_quest_id = next_main
                q_next = QUEST_DB[next_main]
                # 처치/수집 목표인 경우 수락 전이라도 active_quests에 등록 (진행도 추적을 위함)
                # 다만 UI상으로는 촌장과 대화해야 공식 시작됨
                if "objective" in q_next and q_next["objective"]["type"] in ["kill", "collect"]:
                    self.active_quests[next_main] = {"current_count": 0}

        self.update_display_text()
        return r_gold, r_exp, r_items

    def on_kill_monster(self, monster_name):
        updated = False
        # 활성 퀘스트 중 처치 목표인 것 확인
        # 메인 퀘스트 체크
        main_q = QUEST_DB.get(self.main_quest_id)
        if main_q and main_q["type"] == "MAIN" and main_q["objective"]["type"] == "kill_boss":
             if main_q["objective"]["target"] == monster_name:
                 # 보스 처치는 카운트 1
                 # 바로 완료 처리는 아니고, 조건 달성 상태로 만듦
                 # 여기서는 active_quests에 등록해서 카운트를 올림
                 if self.main_quest_id not in self.active_quests:
                     self.active_quests[self.main_quest_id] = {"current_count": 0}
                 self.active_quests[self.main_quest_id]["current_count"] = 1
                 updated = True

        # 일괄 체크
        for qid, progress in self.active_quests.items():
            q_data = QUEST_DB[qid]
            obj = q_data["objective"]
            if obj["type"] == "kill" and obj["target"].strip() == monster_name.strip():
                if progress["current_count"] < obj["count"]:
                    progress["current_count"] += 1
                    updated = True
        
        if updated:
            self.update_display_text()

    def check_collect_condition(self, inventory):
        # 수집 퀘스트 조건 만족 여부 확인 (실시간 갱신용은 아니고 완료 대화 시 체크)
        pass

    def update_display_text(self):
        # 화면에 표시할 텍스트 갱신 (메인 퀘스트 우선)
        q_data = QUEST_DB.get(self.main_quest_id)
        if q_data:
            obj = q_data["objective"]
            status = ""
            
            # 진행도 표시
            if self.main_quest_id in self.active_quests:
                curr = self.active_quests[self.main_quest_id]["current_count"]
                req = obj["count"]
                if curr >= req:
                    status = "(완료 가능)"
                else:
                    status = f"({curr}/{req})"
            elif obj["type"] == "equip":
                status = "(장비 필요)"
            elif obj["type"] == "level_job":
                status = "(레벨/전직 필요)"
            
            # 대사 형태로 변경
            # 예: "촌장: {desc} (1/3)" 느낌으로
            # desc 자체가 "~~를 처치하세요" 같은 명령조라면 그대로 쓰고 뒤에 카운트 붙임
            
            speaker = q_data.get("start_npc", "시스템")
            desc = q_data["desc"]
            
            # 진행도 파악을 위해 status 재생성
            status_suffix = ""
            if self.main_quest_id in self.active_quests:
                curr = self.active_quests[self.main_quest_id]["current_count"]
                req = obj["count"]
                if curr >= req:
                    status_suffix = " (완료 가능)"
                else:
                    status_suffix = f" ({curr}/{req})"
            elif obj["type"] == "equip" or obj["type"] == "level_job":
                 # 특정 조건은 자동 체크되므로 별도 표기 안하거나 필요시 추가
                 pass
            
            self.quest_display_text = f"{speaker}: {desc}{status_suffix}"
        else:
            self.quest_display_text = "Main: 모든 퀘스트 완료"

        # 서브 퀘스트 표시 (최대 1~2개?)
        pass

    def get_npc_dialog(self, npc_name, player_name, player_level, player_job, player_inventory, player_equipment, item_db_ref):
        """
        NPC와의 상호작용 결과를 처리하고 대사를 반환합니다.
        Returns: (dialog_list, reward_info_dict)
        reward_info_dict: {"gold": 0, "exp": 0, "items_added": []}
        """
        dialog = []
        rewards = {"gold": 0, "exp": 0, "items_added": []}
        
        # -----------------------------------------------
        # 1. 촌장 (Chief): 메인 퀘스트 담당
        # -----------------------------------------------
        if npc_name == "촌장":
            mq_id = self.main_quest_id
            mq_data = QUEST_DB.get(mq_id)
            
            if not mq_data:
                return get_dialog("CHIEF_DEFAULT"), rewards

            # 완료 대기 체크
            is_ready = False
            if mq_data["end_npc"] == "촌장" and self.is_quest_active(mq_id):
                # 조건 방어적 체크
                if mq_id not in self.active_quests:
                     # 진행도 데이터가 없는 경우 (수집/처치가 아닌 경우)
                     pass
                else:
                     pass
                
                # 타입별 체크
                obj = mq_data["objective"]
                if obj["type"] in ["kill", "kill_boss", "collect"]:
                    curr = self.active_quests.get(mq_id, {"current_count": 0})["current_count"]
                    if curr >= obj["count"]: is_ready = True
                elif obj["type"] == "equip":
                    if player_equipment["weapon"] and player_equipment["armor"]: is_ready = True
                elif obj["type"] == "level_job":
                    if player_level >= obj["target"] and player_job != "초보자": is_ready = True
                elif obj["type"] == "talk":
                    is_ready = True # 대화만 하면 완료

            if is_ready:
                # 완료 처리
                rg, re, r_items = self.complete_quest(mq_id)
                rewards["gold"] += rg
                rewards["exp"] += re
                
                # 아이템 지급 처리
                for ri in r_items:
                    # item_code -> item_data (from item_db_ref)
                    if ri["name"] in item_db_ref:
                        new_it = item_db_ref[ri["name"]].copy()
                        new_it["count"] = ri["count"]
                        player_inventory.append(new_it)
                        # 보상 목록에 한글 이름 추가
                        rewards["items_added"].append(f"{new_it['name']} x{ri['count']}")
                    else:
                        rewards["items_added"].append(f"{ri['name']} x{ri['count']}")

                dialog = get_dialog("MAIN_COMPLETE", quest_name=mq_data['name'], reward_gold=rg, reward_exp=re, quest_id=mq_id)
                
                if rewards["items_added"]:
                    for msg in rewards["items_added"]:
                        dialog.append(f"획득: {msg}")
            else:
                # 진행도 체크 또는 활성화 여부 체크
                is_started = mq_id in self.active_quests
                obj_type = mq_data["objective"]["type"]
                
                # 1. 진행형 퀘스트인데 진행도가 0이거나, 2. 카운트가 없는 퀘스트인데 아직 수락 전이면 시작 대사
                dialog_type = "MAIN_PROGRESS"
                if (obj_type in ["kill", "kill_boss", "collect"] and not is_started) or \
                   (obj_type in ["equip", "level_job", "talk"] and not is_started):
                     dialog_type = "CHIEF_START"
                     self.start_quest(mq_id)
                
                dialog = get_dialog(dialog_type, player_name=player_name, quest_desc=mq_data['desc'], quest_id=mq_id)

        # -----------------------------------------------
        # 2. 서브 퀘스트 담당 NPC들 (경비병, 대장장이 등)
        # -----------------------------------------------
        else:
            # A. 완료 가능한 퀘스트가 있는지 확인 (우선순위 1)
            complete_hit = None
            for qid, progress in list(self.active_quests.items()):
                q_data = QUEST_DB[qid]
                if q_data["end_npc"] == npc_name:
                    # 목표 달성 여부 체크
                    obj = q_data["objective"]
                    is_ok = False
                    
                    if obj["type"] == "kill":
                        if progress["current_count"] >= obj["count"]: is_ok = True
                    elif obj["type"] == "collect":
                        # 수집 아이템 체크
                        t_name = obj["target"] # 한글 이름
                        needed = obj["count"]
                        has_cnt = sum(it.get("count", 1) for it in player_inventory if it["name"] == t_name)
                        if has_cnt >= needed:
                            is_ok = True
                            # 소모 처리
                            rem_needed = needed
                            for it in player_inventory[:]:
                                if it["name"] == t_name:
                                    c = it.get("count", 1)
                                    if c >= rem_needed:
                                        it["count"] = c - rem_needed
                                        rem_needed = 0
                                        if it["count"] <= 0: player_inventory.remove(it)
                                    else:
                                        rem_needed -= c
                                        player_inventory.remove(it)
                                    if rem_needed <= 0: break
                    
                    if is_ok:
                        complete_hit = qid
                        break
            
            if complete_hit:
                # 완료 처리
                q_data = QUEST_DB[complete_hit]
                rg, re, r_items = self.complete_quest(complete_hit)
                rewards["gold"] += rg
                rewards["exp"] += re
                
                for ri in r_items:
                    if ri["name"] in item_db_ref:
                        new_it = item_db_ref[ri["name"]].copy()
                        new_it["count"] = ri["count"]
                        player_inventory.append(new_it)
                        rewards["items_added"].append(f"{new_it['name']} x{ri['count']}")
                    else:
                         rewards["items_added"].append(f"{ri['name']} x{ri['count']}")
                
                dialog = get_dialog("SUB_COMPLETE", quest_name=q_data['name'], reward_gold=rg, reward_exp=re)
                
                if rewards["items_added"]:
                    for msg in rewards["items_added"]:
                        dialog.append(f"획득: {msg}")
            
            # B. 새로운 퀘스트 수주 (우선순위 2, 경비병만 해당하거나 시작 NPC인 경우)
            else:
                new_quest_found = None
                # 해당 NPC가 시작해주는 퀘스트 찾기
                if self.allow_sub_quests:
                    for qid, q_data in QUEST_DB.items():
                        if q_data["start_npc"] == npc_name and q_data["type"] == "SUB":
                             if not self.is_quest_completed(qid) and not self.is_quest_active(qid):
                                  # 조건 체크
                                  if player_level >= q_data["req_level"]:
                                       if q_data["req_quest"] is None or self.is_quest_completed(q_data["req_quest"]):
                                            new_quest_found = qid
                                            break
                
                if new_quest_found:
                    self.start_quest(new_quest_found)
                    q_data = QUEST_DB[new_quest_found]
                    dialog = get_dialog("SUB_NEW", quest_name=q_data['name'], quest_desc=q_data['desc'])
                else:
                    # 기본 대사
                    dialog = get_dialog("NPC_DEFAULT", npc_name=npc_name, player_name=player_name)

        return dialog, rewards

    def get_state(self):
        """저장을 위해 현재 상태를 딕셔너리로 반환합니다."""
        return {
            "main_quest_id": self.main_quest_id,
            "completed_quests": list(self.completed_quests), # JSON 저장을 위해 리스트로 변환
            "active_quests": self.active_quests,
            "allow_sub_quests": self.allow_sub_quests
        }

    def load_state(self, state_data):
        """저장된 데이터를 바탕으로 상태를 복구합니다."""
        if not state_data: return
        self.main_quest_id = state_data.get("main_quest_id", 1)
        self.completed_quests = set(state_data.get("completed_quests", []))
        self.active_quests = state_data.get("active_quests", {})
        self.allow_sub_quests = state_data.get("allow_sub_quests", False)
        self.update_display_text()
