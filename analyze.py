import re
from collections import Counter


def extract_speakers(raw_text):
    pattern = r'^([A-Za-z][A-Za-z0-9 _-]*):\s*$'
    matches = re.findall(pattern, raw_text, re.MULTILINE)
    return Counter(matches)
