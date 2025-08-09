import difflib
import re

def normalize(a: str) -> str:
    cleaned = re.sub(r'\s+', ' ', a.strip())
    return cleaned

def mask_diff(a: str, b: str) -> str:
    matcher = difflib.SequenceMatcher(None, a, b)
    result_a = []
    result_b = []

    for tag, i1, i2, j1, j2 in matcher.get_opcodes():
        if tag == 'equal':
            # Запазваме съвпадението
            result_a.append(a[i1:i2])
            result_b.append(b[j1:j2])
        else:
            # Различията заменяме с '*'
            masked_a = ''.join('*' if not ch.isspace() else ch for ch in a[i1:i2])
            masked_b = ''.join('_' if 1 else ch for ch in b[j1:j2])
            result_a.append(masked_a)
            result_a.append(masked_b)

    return ''.join(result_a)	# , ''.join(result_b)


