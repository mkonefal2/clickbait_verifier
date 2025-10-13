import re

def normalize_text(s):
    if not s:
        return ''
    s = re.sub('\s+', ' ', s)
    return s.strip()
