from core.rules import RuleSet
from core.context import TimeTrigger

from datetime import datetime, timedelta


class BrainCrampTimerRuleSet(RuleSet):
    def __init__(self, name):
        super().__init__(name)
        self.reset()

    def reset(self):
        self.bars = {
            '|1': None,
            '|2': None,
            '|3': None,
            '|4': None,
            '|5': None,
        }
        self.interval = 0.0

    def examine(self, context):
        triggered = super().examine(context)

        now = datetime.now()
        for trigger in triggered:
            if trigger == '|1':
                self.reset()
                context.time_triggers.clear()
                self.bars[trigger] = now

                context.time_triggers.append(TimeTrigger(now, '!1.1'))
                context.time_trigger_next = context.time_triggers.popleft()

            elif trigger.startswith('|'):
                current_bar = int(trigger[-1])
                previous_bar = '%s%d' % (trigger[:-1], current_bar - 1)

                self.bars[trigger] = now
                if self.bars[previous_bar]:
                    self.interval = (now - self.bars[previous_bar]).total_seconds()
                    eighth = self.interval / 8

                    for i in range(8):
                        context.time_triggers.append(TimeTrigger(now + timedelta(seconds=(i * eighth)), '!%d.%d' % (current_bar, i + 1)))

                    context.time_trigger_next = context.time_triggers.popleft()

                    if current_bar == 5:
                        for i in range(8):
                            context.time_triggers.append(TimeTrigger(now + timedelta(seconds=((i + 8) * eighth)), '!%d.%d' % (current_bar + 1, i + 1)))


        return triggered
