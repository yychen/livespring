from .context import Context
from .rules import Rule, RuleSet

class Live(object):
    def __init__(self):
        self.context = Context()
        self.rule_set = None

    def callback(self, message):
        self.context.incoming_message(message)

        if isinstance(self.rule_set, RuleSet):
            self.rule_set.examine(self.context)
