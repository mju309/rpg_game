
import os

def refactor():
    file_path = "y:/민지우_중1_2024/asdf/game.py"
    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()

    # Find the job instructor block
    old_block = """                        if player_level < 10:
                             state = STATE_DIALOG
                             current_dialog = ["아직 전직할 준비가 되지 않았네.", "10레벨을 달성하고 오게."]
                             dialog_page = 0
                        elif player_job == "초보자":
                             # AI 히든 직업 결정 로직 트리거
                             state = STATE_HIDDEN_JOB
                             globals()['hidden_job_requested'] = False
                             globals()['hidden_job_result'] = None
                             menu_nav_timer = now
                        else:
                             state = STATE_DIALOG
                             current_dialog = [f"이미 {player_job}의 길을 걷고 있군."]
                             dialog_page = 0"""
    
    # Let's try to find it by a substring instead of full block to avoid whitespace issues
    target_part = 'if player_level < 10:'
    
    new_block = """                        if player_level < 20:
                             state = STATE_DIALOG
                             current_dialog = ["아직 전직할 준비가 되지 않았네.", "20레벨을 달성하고 오게."]
                             dialog_page = 0
                        elif player_job == "초보자":
                             # 첫 번째 전직 (20레벨)
                             state = STATE_JOB_SELECT
                             menu_nav_timer = now
                        elif player_level >= 50 and player_job in ["전사", "마법사", "사수", "도적"]:
                             # 두 번째 히든 전직 (50레벨)
                             state = STATE_HIDDEN_JOB
                             globals()['hidden_job_requested'] = False
                             globals()['hidden_job_result'] = None
                             menu_nav_timer = now
                        else:
                             msg = f"이미 {player_job}의 길을 걷고 있군."
                             if player_level < 50:
                                 msg += " 50레벨이 되면 히든 전직에 도전할 수 있네."
                             state = STATE_DIALOG
                             current_dialog = [msg]
                             dialog_page = 0"""

    # We need to find the specific block.
    # Lines around 1402
    lines = content.split('\n')
    start_idx = -1
    end_idx = -1
    for i, line in enumerate(lines):
        if 'if player_level < 10:' in line and i > 1390 and i < 1420:
            start_idx = i
            # Look for the end of the else block
            for j in range(i, i + 20):
                if 'break' in lines[j] and len(lines[j].strip()) == 5:
                    end_idx = j
                    break
            break
    
    if start_idx != -1 and end_idx != -1:
        # Replace the lines from start_idx to end_idx-1
        # Preserving original indentation as much as possible
        indent = lines[start_idx][:lines[start_idx].find('if')]
        
        replacement = [
            f"{indent}if player_level < 20:",
            f"{indent}     state = STATE_DIALOG",
            f"{indent}     current_dialog = [\"아직 전직할 준비가 되지 않았네.\", \"20레벨을 달성하고 오게.\"]",
            f"{indent}     dialog_page = 0",
            f"{indent}elif player_job == \"초보자\":",
            f"{indent}     # 첫 번째 전직 (20레벨)",
            f"{indent}     state = STATE_JOB_SELECT",
            f"{indent}     menu_nav_timer = now",
            f"{indent}elif player_level >= 50 and player_job in [\"전사\", \"마법사\", \"사수\", \"도적\"]:",
            f"{indent}     # 두 번째 히든 전직 (50레벨)",
            f"{indent}     state = STATE_HIDDEN_JOB",
            f"{indent}     globals()['hidden_job_requested'] = False",
            f"{indent}     globals()['hidden_job_result'] = None",
            f"{indent}     menu_nav_timer = now",
            f"{indent}else:",
            f"{indent}     msg = f\"이미 {{player_job}}의 길을 걷고 있군.\"",
            f"{indent}     if player_level < 50:",
            f"{indent}         msg += \" 50레벨이 되면 히든 전직에 도전할 수 있네.\"",
            f"{indent}     state = STATE_DIALOG",
            f"{indent}     current_dialog = [msg]",
            f"{indent}     dialog_page = 0"
        ]
        
        lines[start_idx:end_idx] = replacement
        new_content = '\n'.join(lines)
        
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(new_content)
        print("Successfully updated job logic")
    else:
        print(f"Failed to find job block. start_idx: {start_idx}, end_idx: {end_idx}")

if __name__ == "__main__":
    refactor()
