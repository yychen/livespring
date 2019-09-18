from core.rules import RuleSet
from core.context import TimeTrigger

from datetime import datetime, timedelta
import time


class Demo2TimerRuleSet(RuleSet):
    def __init__(self, name):
        super().__init__(name)
        self.reset()

    def reset(self):
        print('reset...')
        self.bars = {
            '|1': None,
            '|2': None,
            '|3': None,
            '|4': None,
        }
        self.interval = 0.0

    def emit_bars(self):
        if self.ws_emitter:
            event = {}
            event['data'] = {
                'type': 'bars',
                'bars': {b: time.mktime(t.timetuple()) + t.microsecond / 1E6 if t is not None else None for b, t in self.bars.items()},
                'interval': '{0:.3}'.format(self.interval) if self.interval else None,
                'eighth': '{0:.3}'.format(self.interval / 8) if self.interval else None,
            }
            self.ws_emitter.emit(event)


    def attach_ws_emitter(self, emitter):
        self.ws_emitter = emitter

    def examine(self, context):
        triggered = super().examine(context)

        now = datetime.now()
        for trigger in triggered:
            if trigger == '|1':
                if self.interval and self.bars['|4'] and (now - self.bars['|4']).total_seconds() < self.interval * 1.5:
                    # Still within
                    current_bar = int(trigger[-1])
                    previous_bar = '|4'

                    self.bars[trigger] = now
                    if self.bars[previous_bar]:
                        self.interval = (now - self.bars[previous_bar]).total_seconds()
                        eighth = self.interval / 8

                        for i in range(8):
                            context.time_triggers.append(TimeTrigger(now + timedelta(seconds=(i * eighth)), '!%d.%d' % (current_bar, i + 1)))

                        context.time_trigger_next = context.time_triggers.popleft()

                else:
                    self.reset()
                    context.time_triggers.clear()
                    self.bars[trigger] = now

                    context.time_triggers.append(TimeTrigger(now, '!1.1'))
                    context.time_trigger_next = context.time_triggers.popleft()

                self.emit_bars()

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

                    if current_bar == 3:
                        for i in range(8):
                            context.time_triggers.append(TimeTrigger(now + timedelta(seconds=((i + 8) * eighth)), '!%d.%d' % (current_bar + 1, i + 1)))

                        self.bars['|4'] = now + timedelta(seconds=self.interval)

                self.emit_bars()


        return triggered
