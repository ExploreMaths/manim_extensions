"""Script to fix manim docstring directives across all source files.

Rules:
1. Static scenes (only self.add(), no animations) -> remove self.wait(), keep/add :save_last_frame:
2. Video scenes (have self.play(), self.animate(), or custom animations) -> remove :save_last_frame:
"""

import re
import os

SOURCE_DIR = os.path.join(os.path.dirname(__file__), "manim_extensions")

ANIMATION_KEYWORDS = [
    "self.play(",
    "self.animate(",
    "Write(",
    "FadeIn(",
    "FadeOut(",
    "GrowFromCenter(",
    "GrowFromEdge(",
    "ShrinkToCenter(",
    "ScaleInPlace(",
    "Rotate(",
    "ApplyMethod(",
    "ApplyWave(",
    "ShowCreation(",
    "Uncreate(",
    "DrawBorderThenFill(",
    "Create(",
    "Transform(",
    "ReplacementTransform(",
    "AnimationGroup(",
    "Succession(",
    "FadeTransform(",
    "TypeWriter(",
    "VisDrawArc(",
    "Shift(",
    "MoveTo(",
    "DrawArrow(",
    "GrowArrow(",
    "Indicate(",
    "Circumscribe(",
    "FocusOn(",
    "Wiggle(",
    "Bounce(",
    "Restart(",
    "Restore(",
    "FadeInFrom(",
    "FadeOutTo(",
    "TransformMatchingStrings(",
    "TransformMatchingTex(",
    "Flash(",
    "ShowPassingFlash(",
    "SpinInFromNothing(",
    "ClockwiseTransform(",
    "CounterclockwiseTransform(",
    "RunTime(",
    "LaggedCreation(",
    "HighLightWithLines(",
    "UnHighLightWithLines(",
    "PassingRectangle(",
    "EaseOutBounce(",
    "EaseInBounce(",
    "EaseInOutBounce(",
    "EaseOutElastic(",
]


def is_video(construct_body: str) -> bool:
    for kw in ANIMATION_KEYWORDS:
        if kw in construct_body:
            return True
    return False


def get_indent(line: str) -> int:
    return len(line) - len(line.lstrip())


def parse_manim_blocks(content: str):
    """Parse all manim blocks from file content using line-by-line parsing.
    
    Returns list of dicts with keys:
      start_line, end_line, text, construct_body, has_save, block_name
    """
    lines = content.split('\n')
    blocks = []
    i = 0
    
    while i < len(lines):
        stripped = lines[i].strip()
        
        if stripped.startswith('.. manim::'):
            block_indent = get_indent(lines[i])
            block_start = i
            block_lines = [lines[i]]
            
            # Extract block name
            m = re.match(r'\.\. manim::\s*(\w+)', stripped)
            block_name = m.group(1) if m else "Unknown"
            
            has_save = False
            
            i += 1
            
            # Parse prelude: :save_last_frame: and blank lines
            while i < len(lines):
                s = lines[i].strip()
                if s.startswith(':save_last_frame:'):
                    has_save = True
                    block_lines.append(lines[i])
                    i += 1
                elif s == '':
                    block_lines.append(lines[i])
                    i += 1
                else:
                    break
            
            # Parse code lines (indented more than block_indent)
            code_lines = []
            while i < len(lines):
                line = lines[i]
                s = line.strip()
                indent = get_indent(line)
                
                if s == '':
                    # Blank line - could be in code or end of block
                    block_lines.append(line)
                    code_lines.append(line)
                    i += 1
                    # Peek ahead
                    if i < len(lines):
                        peek_indent = get_indent(lines[i])
                        peek_stripped = lines[i].strip()
                        if peek_stripped == '':
                            # Two blank lines - check one more
                            if i + 1 < len(lines):
                                peek2_indent = get_indent(lines[i + 1])
                                peek2_stripped = lines[i + 1].strip()
                                if peek2_stripped == '' or peek2_indent <= block_indent:
                                    break
                                else:
                                    continue
                            else:
                                break
                        elif peek_indent > block_indent:
                            continue
                        else:
                            break
                    else:
                        break
                elif indent > block_indent:
                    block_lines.append(line)
                    code_lines.append(line)
                    i += 1
                else:
                    break
            
            # Extract construct body from code
            code_text = '\n'.join(code_lines)
            construct_body = ""
            
            # Find def construct(self): and its indentation
            construct_match = re.search(r'^(\s*)def construct\(self\):', code_text, re.MULTILINE)
            if construct_match:
                construct_indent = construct_match.group(1)
                construct_start = construct_match.end()
                raw = code_text[construct_start:]
                
                # Find the first line that has same or less indentation than def construct
                # This marks the end of the construct body
                min_spaces = len(construct_indent)
                body_lines = raw.split('\n')
                collected = []
                for bline in body_lines:
                    if bline.strip() == '':
                        collected.append(bline)
                        continue
                    line_indent = len(bline) - len(bline.lstrip())
                    if line_indent <= min_spaces and bline.strip():
                        break
                    collected.append(bline)
                
                construct_body = '\n'.join(collected)
            
            blocks.append({
                'start_line': block_start,
                'end_line': block_start + len(block_lines),
                'text': '\n'.join(block_lines),
                'construct_body': construct_body,
                'has_save': has_save,
                'block_name': block_name,
            })
        
        i += 1
    
    return blocks


def fix_file(filepath: str) -> tuple:
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    original = content
    changes = []
    
    blocks = parse_manim_blocks(content)
    
    for block in reversed(blocks):
        block_text = block['text']
        has_save = block['has_save']
        construct_body = block['construct_body']
        
        if not construct_body:
            continue
        
        if is_video(construct_body):
            if has_save:
                new_block = re.sub(
                    r'\n\s*:save_last_frame:\s*\n',
                    '\n',
                    block_text,
                    count=1
                )
                if new_block != block_text:
                    start_char = sum(len(l) + 1 for l in content.split('\n')[:block['start_line']])
                    end_char = sum(len(l) + 1 for l in content.split('\n')[:block['end_line']])
                    content = content[:start_char] + new_block + content[end_char:]
                    changes.append(f"Removed :save_last_frame: from video scene '{block['block_name']}' at {filepath}")
        else:
            new_block = block_text
            
            wait_pattern = re.compile(r'^\s*self\.wait\([^)]*\)\s*(""")?\s*$', re.MULTILINE)
            new_block = wait_pattern.sub(r'\1', new_block)
            new_block = re.sub(r'\n{3,}', '\n\n', new_block)
            
            if not has_save:
                new_block = re.sub(
                    r'(\.\. manim::\s*\w+\s*\n)',
                    r'\1   :save_last_frame:\n',
                    new_block,
                    count=1
                )
            
            if new_block != block_text:
                start_char = sum(len(l) + 1 for l in content.split('\n')[:block['start_line']])
                end_char = sum(len(l) + 1 for l in content.split('\n')[:block['end_line']])
                content = content[:start_char] + new_block + content[end_char:]
                if ':save_last_frame:' not in block_text and ':save_last_frame:' in new_block:
                    changes.append(f"Added :save_last_frame: to static scene '{block['block_name']}' at {filepath}")
                elif 'self.wait' in block_text:
                    changes.append(f"Removed self.wait() from static scene '{block['block_name']}' at {filepath}")
                else:
                    changes.append(f"Fixed static scene '{block['block_name']}' at {filepath}")
    
    if content != original:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        return True, changes
    return False, []


def verify_file(filepath: str) -> list:
    """Verify manim directives in a single file. Returns list of issues."""
    issues = []
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    blocks = parse_manim_blocks(content)
    
    for block in blocks:
        construct_body = block['construct_body']
        has_save = block['has_save']
        name = block['block_name']
        
        if not construct_body:
            if not has_save:
                issues.append(f"  {filepath}: {name} - EMPTY construct without :save_last_frame:")
            continue
        
        video = is_video(construct_body)
        
        if 'self.wait(' in construct_body and not video:
            issues.append(f"  {filepath}: {name} - STATIC scene has self.wait() (should be removed)")
        
        if video and has_save:
            issues.append(f"  {filepath}: {name} - VIDEO scene has :save_last_frame: (should be removed)")
        
        if not video and not has_save:
            issues.append(f"  {filepath}: {name} - STATIC scene missing :save_last_frame:")
    
    return issues


def main():
    total_files_changed = 0
    total_changes = []
    total_issues = []
    stats = {"static": 0, "video": 0, "total": 0}
    
    for root, dirs, files in os.walk(SOURCE_DIR):
        dirs[:] = [d for d in dirs if d != '__pycache__']
        
        for file in files:
            if file.endswith('.py'):
                filepath = os.path.join(root, file)
                
                # Count scenes for stats
                blocks = parse_manim_blocks(open(filepath, 'r', encoding='utf-8').read())
                for b in blocks:
                    if b['construct_body']:
                        stats['total'] += 1
                        if is_video(b['construct_body']):
                            stats['video'] += 1
                        else:
                            stats['static'] += 1
                
                changed, changes = fix_file(filepath)
                if changed:
                    total_files_changed += 1
                    total_changes.extend(changes)
                    print(f"Fixed: {filepath}")
                    for c in changes:
                        print(f"  - {c}")
                
                file_issues = verify_file(filepath)
                total_issues.extend(file_issues)
    
    print(f"\n{'='*60}")
    print(f"Total manim blocks: {stats['total']}")
    print(f"  Static scenes: {stats['static']}")
    print(f"  Video scenes:  {stats['video']}")
    print(f"\nTotal files changed: {total_files_changed}")
    print(f"Total changes: {len(total_changes)}")
    
    if total_issues:
        print(f"\nVERIFICATION - FOUND {len(total_issues)} ISSUES:")
        for i in total_issues:
            print(i)
    else:
        print("\nVERIFICATION - ALL CLEAN!")


if __name__ == '__main__':
    main()