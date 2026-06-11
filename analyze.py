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


def extract_action_items_with_owners(raw_text):
    keywords = ['action item:', 'todo:', 'task:', 'action:']
    owner_keywords = ['owner:', 'assigned to:']
    speaker_pattern = r'^([A-Za-z][A-Za-z0-9 _-]*):\s*$'
    lines = raw_text.split('\n')
    items = []
    i = 0
    while i < len(lines):
        line = lines[i].lstrip()
        lower = line.lower()
        found = None
        for kw in keywords:
            if lower.startswith(kw):
                found = kw
                break
        if found:
            content = line[len(found):].strip()
            action_line = i
            if not content:
                j = i + 1
                while j < len(lines) and not lines[j].strip():
                    j += 1
                if j < len(lines):
                    content = lines[j].strip()
                    i = j
            if content:
                owner = None
                for k in range(action_line - 1, -1, -1):
                    cl = lines[k].lstrip()
                    cll = cl.lower()
                    for okw in owner_keywords:
                        if cll.startswith(okw):
                            owner = cl[len(okw):].strip()
                            break
                    if owner:
                        break
                if not owner:
                    for k in range(action_line - 1, -1, -1):
                        m = re.match(speaker_pattern, lines[k].strip())
                        if m:
                            owner = m.group(1)
                            break
                if not owner:
                    owner = "Unassigned"
                items.append({'text': content, 'owner': owner})
        i += 1
    return items
