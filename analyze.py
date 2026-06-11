import re
from collections import Counter


def extract_speakers(raw_text):
    pattern = r'^([A-Za-z][A-Za-z0-9 _-]*):\s*$'
    matches = re.findall(pattern, raw_text, re.MULTILINE)
    return Counter(matches)


def extract_action_items(raw_text):
    keywords = ['action item:', 'todo:', 'task:', 'action:']
    items = []
    lines = raw_text.split('\n')
    i = 0
    while i < len(lines):
        line = lines[i].lstrip()
        lower = line.lower()
        for kw in keywords:
            if lower.startswith(kw):
                content = line[len(kw):].strip()
                if not content:
                    j = i + 1
                    while j < len(lines) and not lines[j].strip():
                        j += 1
                    if j < len(lines):
                        content = lines[j].strip()
                        i = j
                if content:
                    items.append(content)
                break
        i += 1
    return items
