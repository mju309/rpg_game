import os

def refactor():
    file_path = "y:/민지우_중1_2024/asdf/game.py"
    with open(file_path, "r", encoding="utf-8") as f:
        lines = f.readlines()

    new_lines = []
    
    for line in lines:
        stripped = line.strip()
        
        # 1. Update NPC Rects
        if "npc_guard =" in line:
            # Comment out or remove guard
            continue
        if "npc_board =" in line:
            # Move board to where guard was
            new_lines.append("npc_board = pygame.Rect(280, 80, 40, 40)\n")
            continue
            
        # 2. Update Sprite Loads
        if "load_sprite(\"guard\"" in line:
            continue
            
        # 3. Update draw_town_objects
        if "draw_sprite(screen, \"guard\", npc_guard)" in line:
            continue
        
        # 4. Update Interaction in STATE_TOWN
        # Remove Guard Interaction
        if "if (abs(player.x - npc_guard.x)" in line:
             # We need to skip this block. 
             # Usually it looks like:
             # if (abs(player.x - npc_guard.x) <= 40 and abs(player.y - npc_guard.y) <= 40):
             #     for event in events:
             #         ...
             # We skip until the next top level if/elif in TOWN.
             pass 
             
        new_lines.append(line)

    # Indentation-aware removal is better with a script that knows blocks.
    # Let's try a better approach.
    
    final_lines = []
    skip_until_blank = False
    
    for i, line in enumerate(new_lines):
        stripped = line.strip()
        
        # Detect Guard Interaction block
        if "if (abs(player.x - npc_guard.x)" in line:
            skip_until_blank = True
            continue
            
        if skip_until_blank:
            # Check for block end. In game.py, these blocks usually end before a new comment or a new if/elif
            if "#" in line and not line.startswith(" "):
                 skip_until_blank = False
            elif "if " in line and not line.startswith(" ") and "(" not in line: # Main level if
                 skip_until_blank = False
            elif stripped.startswith("# ") and i+1 < len(new_lines) and ("대화" in new_lines[i+1] or "상호작용" in new_lines[i+1]):
                 skip_until_blank = False
            else:
                 continue
        
        final_lines.append(line)

    with open(file_path, "w", encoding="utf-8") as f:
        f.writelines(final_lines)

if __name__ == "__main__":
    refactor()
