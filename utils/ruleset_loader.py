import os

from core.rules import Rule, RuleSet


def ruleset_loader(folder):
    print(f'Loading rule sets from {folder}...')
    if not os.path.isdir(folder):
        raise FileNotFoundError
    
    for fn in os.listdir(folder):
        full_fn = os.path.join(folder, fn)
        if not os.path.isfile(full_fn):
            continue

        rule_sets = []

        try:
            rs = RuleSet.load(full_fn)
            rule_sets.append(rs)
        except ValueError as e:
            print(f'{e}, skipping...')

    return rule_sets
