import json
import os
from jsonschema import Draft7Validator
from copy import deepcopy

SCHEMA_PATH = os.path.join(os.path.dirname(__file__), '..', 'schemas', 'output_schema.json')

# Template path (optional): a skeleton with empty defaults that should be used in prompts
TEMPLATE_PATH = os.path.join(os.path.dirname(__file__), '..', 'schemas', 'output_template.json')


def load_schema():
    with open(SCHEMA_PATH, 'r', encoding='utf-8') as f:
        return json.load(f)


def make_empty_template(schema):
    """Create a template object from schema where required properties are present with safe empty defaults.

    Rules used for defaults:
    - string -> ""
    - number -> 0
    - integer -> 0
    - boolean -> False
    - array -> []
    - object -> {} (but for known nested props we recurse)
    """
    def _default_for(prop_schema):
        t = prop_schema.get('type')
        if isinstance(t, list):
            # prefer non-null types
            t = next((x for x in t if x != 'null'), t[0])
        if t == 'string':
            return ""
        if t in ('number', 'integer'):
            return 0
        if t == 'boolean':
            return False
        if t == 'array':
            return []
        if t == 'object':
            # build object with its properties defaulted where possible
            props = prop_schema.get('properties', {})
            obj = {}
            for k, v in props.items():
                obj[k] = _default_for(v)
            return obj
        # fallback
        return None

    template = {}
    props = schema.get('properties', {})
    required = schema.get('required', [])
    for k in required:
        if k in props:
            template[k] = _default_for(props[k])
        else:
            # unknown required -> null fallback
            template[k] = None
    # include diagnostics defaults (optional)
    if 'diagnostics' in props and 'diagnostics' not in template:
        template['diagnostics'] = _default_for(props['diagnostics'])
    return template


def validate_instance(instance, schema):
    validator = Draft7Validator(schema)
    errors = sorted(validator.iter_errors(instance), key=lambda e: e.path)
    return errors


def enforce_and_fill(instance: dict, *, add_metadata=True):
    """Validate instance against schema and fill missing required fields with safe defaults.

    Returns (result_dict, metadata) where metadata contains:
      - valid: bool
      - errors: list of validation error messages (if any)
      - auto_filled: list of field names that were added
    """
    schema = load_schema()
    inst = deepcopy(instance) if instance is not None else {}
    errors = validate_instance(inst, schema)
    auto_filled = []

    if not errors:
        meta = {'valid': True, 'errors': [], 'auto_filled': []}
        return inst, meta

    # Build template of required fields
    template = make_empty_template(schema)

    # Fill missing required fields from template
    for key, default_value in template.items():
        if key not in inst or inst.get(key) is None:
            inst[key] = default_value
            auto_filled.append(key)

    # Re-validate and collect remaining errors
    remaining_errors = validate_instance(inst, schema)
    messages = [format_error(e) for e in remaining_errors]

    meta = {
        'valid': len(remaining_errors) == 0,
        'errors': messages,
        'auto_filled': auto_filled
    }

    # Optionally annotate diagnostics about auto-fill
    if add_metadata:
        diag = inst.setdefault('diagnostics', {})
        diag.setdefault('auto_filled_fields', auto_filled)

    return inst, meta


def load_template():
    if not os.path.exists(TEMPLATE_PATH):
        return None
    with open(TEMPLATE_PATH, 'r', encoding='utf-8') as f:
        return json.load(f)


def enforce_strict_template(instance: dict):
    """Strict mode: do not auto-fill. Instead, ensure that all required keys exist and that no prefilled result fields are present in the input.

    Returns (result_dict, metadata) where metadata has keys:
      - valid: bool
      - errors: list
      - missing_required: list
      - forbidden_present: list
    """
    schema = load_schema()
    required = schema.get('required', [])
    inst = deepcopy(instance) if instance is not None else {}

    missing = [k for k in required if k not in inst or inst.get(k) is None]

    # detect forbidden prefilled result fields (same as schema's required output names)
    forbidden = [k for k in ['score', 'label', 'rationale', 'rationale_user_friendly', 'signals', 'suggestions', 'diagnostics'] if k in inst]

    meta = {
        'valid': len(missing) == 0 and len(forbidden) == 0,
        'errors': [],
        'missing_required': missing,
        'forbidden_present': forbidden
    }

    # if template exists, produce a combined skeleton to return (helpful for prompts)
    template = load_template()
    result = inst.copy()
    if template:
        # ensure keys from template exist but do not overwrite provided values
        for k, v in template.items():
            result.setdefault(k, v)
    return result, meta


def format_error(err):
    path = '.'.join([str(p) for p in err.path])
    return f"{path}: {err.message}"


if __name__ == '__main__':
    import sys
    # simple CLI with optional strict-template mode
    import argparse

    parser = argparse.ArgumentParser(description='Validate and (optionally) fill/emit output template for LLM results.')
    parser.add_argument('input', help='Path to LLM output JSON file')
    parser.add_argument('--strict-template', action='store_true', help='Do not auto-fill; enforce that required keys are missing and no prefilled outputs are present; return template merged (if available)')
    parser.add_argument('--no-add-metadata', dest='add_metadata', action='store_false', help='Do not add diagnostics metadata about auto-fill')
    args = parser.parse_args()

    p = args.input
    with open(p, 'r', encoding='utf-8') as f:
        try:
            doc = json.load(f)
        except Exception as e:
            print('JSON parse error:', e)
            sys.exit(3)

    if args.strict_template:
        out, meta = enforce_strict_template(doc)
        print('Strict template valid:', meta['valid'])
        if meta['missing_required']:
            print('Missing required fields:', meta['missing_required'])
        if meta['forbidden_present']:
            print('Forbidden prefilled fields present in input (remove before prompting):', meta['forbidden_present'])
        # print resulting skeleton (merged with any provided fields)
        print('\n--- Resulting JSON (skeleton/merged) ---')
        print(json.dumps(out, indent=2, ensure_ascii=False))
        # exit code non-zero if invalid
        sys.exit(0 if meta['valid'] else 4)
    else:
        out, meta = enforce_and_fill(doc, add_metadata=args.add_metadata)
        print('Valid after fill:', meta['valid'])
        if meta.get('auto_filled'):
            print('Auto-filled fields:', meta.get('auto_filled'))
        if meta.get('errors'):
            print('Remaining errors:')
            for m in meta.get('errors'):
                print(' -', m)
        # print resulting JSON to stdout
        print('\n--- Resulting JSON ---')
        print(json.dumps(out, indent=2, ensure_ascii=False))
