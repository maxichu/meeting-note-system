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
                cleaned, deadline = _detect_deadline(content)
                items.append({'text': cleaned, 'owner': owner, 'deadline': deadline})
        i += 1
    return items


def _detect_deadline(text):
    if not text:
        return text, None
    m = re.search(r'\b(\d{4}[-/]\d{2}[-/]\d{2})\b', text)
    if m:
        dl = m.group(1)
        c = re.sub(r'\s*(?:by|before|until)?\s*' + re.escape(dl), '', text, flags=re.IGNORECASE).strip()
        c = re.sub(r'\s{2,}', ' ', c)
        return c or dl, dl
    kws = ['next week', 'next month', 'tomorrow',
           'next monday', 'next tuesday', 'next wednesday', 'next thursday',
           'next friday', 'next saturday', 'next sunday',
           'monday', 'tuesday', 'wednesday', 'thursday',
           'friday', 'saturday', 'sunday']
    kws.sort(key=len, reverse=True)
    tl = text.lower()
    for kw in kws:
        m = re.search(r'\b' + re.escape(kw) + r'\b', tl)
        if m:
            matched = text[m.start():m.end()]
            c = re.sub(r'\s*(?:by|before|until)?\s*' + re.escape(matched), '', text, flags=re.IGNORECASE).strip()
            c = re.sub(r'\s{2,}', ' ', c)
            return c or matched, matched
    return text, None


def build_knowledge_graph(action_items_data):
    import networkx as nx
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    from io import BytesIO

    G = nx.DiGraph()
    for item in action_items_data:
        owner = item.get('owner') or 'Unassigned'
        text = item.get('text', '')
        if owner != 'Unassigned' and text:
            G.add_edge(owner, text)

    if G.number_of_nodes() == 0:
        return None, 0, 0

    fig, ax = plt.subplots(figsize=(10, 6))
    pos = nx.spring_layout(G, k=1.5, iterations=50)
    nx.draw(G, pos, with_labels=True, node_color='lightblue',
            node_size=2000, font_size=10, font_weight='bold',
            arrows=True, arrowstyle='->', arrowsize=20,
            edge_color='gray', ax=ax)
    buf = BytesIO()
    fig.savefig(buf, format='png', bbox_inches='tight', dpi=100)
    plt.close(fig)
    buf.seek(0)
    return buf.read(), G.number_of_nodes(), G.number_of_edges()


def generate_summary(meeting_text, speakers, action_items):
    try:
        import llm as llm_module
        prompt = _build_summary_prompt(meeting_text, speakers, action_items)
        result = llm_module.generate_response(prompt)
        if result:
            return result
    except Exception:
        pass
    return _rule_based_summary(meeting_text, speakers, action_items)


def _build_summary_prompt(meeting_text, speakers, action_items):
    return f"""You are a meeting analysis assistant. Analyze the following meeting notes and provide a structured summary.

Meeting Notes:
{meeting_text}

Extracted Speakers: {speakers}
Extracted Action Items: {action_items}

Please provide:
1. Key Discussion
2. Decisions
3. Risks
4. Action Items"""


def _rule_based_summary(meeting_text, speakers, action_items):
    lines = []
    lines.append("Key Discussion:")
    if speakers:
        names = ', '.join(speakers.keys())
        lines.append(f"Speakers: {names}. Topics were discussed as reflected in the meeting notes.")
    else:
        lines.append("No specific speakers identified.")

    lines.append("")
    lines.append("Decisions:")
    lines.append("None detected.")

    lines.append("")
    lines.append("Risks:")
    lines.append("None detected.")

    lines.append("")
    lines.append("Action Items:")
    if action_items:
        for item in action_items:
            owner = item.get('owner', 'Unassigned')
            deadline = item.get('deadline', 'No deadline')
            lines.append(f"- {item['text']} (Owner: {owner}, Deadline: {deadline})")
    else:
        lines.append("None detected.")

    return '\n'.join(lines)
