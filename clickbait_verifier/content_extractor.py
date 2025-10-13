# simple content extractor that loads YAML configs
import yaml
import os


def load_extractor(name):
    path = f"clickbait_verifier/extractors/{name}.yaml"
    try:
        return yaml.safe_load(open(path))
    except FileNotFoundError:
        return None


def load_extractor_for_source(source_name):
    # map simple name to yaml under extractors/
    fname = source_name.lower().replace(' ', '').replace('.', '')
    path = os.path.join('clickbait_verifier', 'extractors', f"{fname}.yaml")
    try:
        return yaml.safe_load(open(path))
    except FileNotFoundError:
        return None
