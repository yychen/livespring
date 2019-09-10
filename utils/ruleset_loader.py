#!/usr/bin/env python
import os

from core.rules import Rule, RuleSet

from yaml import load, dump
try:
    from yaml import CLoader as Loader, CDumper as Dumper
except ImportError:
    from yaml import Loader, Dumper


def ruleset_loader(folder):
    if not os.path.isdir(folder):
        raise FileNotFoundError
    
    for fn in os.listdir(folder):
        full_fn = os.path.join(folder, fn)
        if not os.path.isfile(full_fn):
            continue

        rule_sets = []

        with open(full_fn, 'r') as f:
            rs = RuleSet(fn)
            document = load(f, Loader=Loader)
            
            for entry in document:
                rule = Rule(entry.get('notes'), entry.get('trigger'), entry.get('type'))
                rs.add(rule)

            rule_sets.append(rs)

    return rule_sets
