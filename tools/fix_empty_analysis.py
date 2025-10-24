import os
import glob
import json
from enforce_output_schema import load_schema, make_empty_template

ANALYSIS_DIR = os.path.join(os.path.dirname(__file__), '..', 'reports', 'analysis')


def find_empty_files():
    files = glob.glob(os.path.join(ANALYSIS_DIR, '*.json'))
    empties = []
    for p in files:
        try:
            if os.path.getsize(p) == 0:
                empties.append(p)
        except OSError:
            continue
    return empties


def backup_and_fill(path, template):
    bak = path + '.bak'
    # Backup existing file
    if not os.path.exists(bak):
        with open(bak, 'w', encoding='utf-8') as f:
            f.write('')
    # Write template
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(template, f, indent=2, ensure_ascii=False)


if __name__ == '__main__':
    empties = find_empty_files()
    if not empties:
        print('No empty analysis files found.')
        exit(0)

    schema = load_schema()
    template = make_empty_template(schema)
    # Add marker noting this was auto-filled
    template.setdefault('diagnostics', {})
    template['diagnostics']['auto_filled'] = True

    for p in empties:
        print('Filling empty file:', p)
        backup_and_fill(p, template)

    print('Done. Filled', len(empties), 'files.')
