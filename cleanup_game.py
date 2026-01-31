import os

def cleanup():
    file_path = "y:/민지우_중1_2024/asdf/game.py"
    with open(file_path, "r", encoding="utf-8") as f:
        lines = f.readlines()

    seen_states = set()
    new_lines = []
    
    current_state_block = None
    buffer = []
    
    for line in lines:
        stripped = line.strip()
        
        # Detect state start
        if stripped.startswith("elif state == STATE_") or stripped.startswith("if state == STATE_"):
            # If we were in a block, decide to keep or discard
            if current_state_block:
                if current_state_block not in seen_states:
                    new_lines.extend(buffer)
                    seen_states.add(current_state_block)
                buffer = []
            
            # Determine which state this is
            state_name = stripped.split("==")[1].split(":")[0].strip()
            current_state_block = state_name
            buffer.append(line)
        elif current_state_block:
            # Check for end of block (main loop level indentation)
            # In game.py, the state blocks are inside the main while loop.
            # Indentation is usually 4/8 spaces.
            # If line is less indented than it should be, it's end of loop.
            # But here they are all at the same level (elif).
            buffer.append(line)
        else:
            new_lines.append(line)

    # Add last block
    if current_state_block and current_state_block not in seen_states:
        new_lines.extend(buffer)

    with open(file_path, "w", encoding="utf-8") as f:
        f.writelines(new_lines)

if __name__ == "__main__":
    # Actually, the logic above is a bit risky if I don't know the exact indentation.
    # Let's just fix the specific duplicates.
    pass
