# livespring
Livespring is a simple system that handles MIDI note/chord detection and signal triggering for live performance, based on Tornado web framework and python-rtmidi. It reads MIDI signals from the MIDI input, and see if it matches any rules for it the trigger to some outputs. The output might be a websocket data to a web page, some bytes to serial port, or to a route to a OSC destination.

This is just a demo code of the whole idea. You can tailor it for your own needs, but hacking it is definitely required at this point of time. It is not a comprehensive system.

This is tested only on a Macbook. There are still bugs and a lot to improve. Use at your own risk.

## Installing
### Dependencies
It depends on `python-rtmidi` to work. Please take a look at the [requirements](https://spotlightkid.github.io/python-rtmidi/installation.html#requirements) section of python-rtmidi's [documentation](https://spotlightkid.github.io/python-rtmidi/index.html).

### Get the code first
Clone it from the repository:

```
$ git clone https://github.com/yychen/livespring.git
```

### Virtual Environment
Create a virtual environment. You can choose whatever way that suits you, we're using `virtualenvwrapper` here. 

```
$ mkvirtualenv livespring
(livespring)$ 
```

### Install required packages
```
(livespring)$ cd livespring
(livespring)$ pip install -r requirements.txt
```

### Run it
Now, we're good to go!

```
(livespring)$ python server.py
```

You should be able to visit the console at [http://localhost:8001](http://localhost:8001).


## Commands & Parameters
### `-l`, List MIDI devices
If you have multiple MIDI devices, the following command list the names.

```
(livespring)$ python server.py -l
Available MIDI devices:
IAC Driver Bus 1
Oxygen 61
```

### `-m`, Specify MIDI Input
You can specify the desired MIDI Input so the server will listen to it, by putting the name through the `-m` parameter, don't forget to quote it if there are spaces in it.

```
(livespring)$ python server.py -m "Oxygen 61"
```

Or, you can use a 0-indexed number to indicate the device. The server will choose Oxygen 61 as it is the second device returned from the list in the following command.

```
(livespring)$ python server.py -m 1
```

If you don't specify the device explicitly, it will just choose whatever comes first from the list.
### `-p`, Specify Port
The default port that the server listens to is `8001`. You can specify another one by using the `-p` parameter:

```
(livespring)$ python server.py -p 8080
```

## Rules
You can find some sample rules in the [rules-available](rules-available/) folder. These rules are enabled by making a symbolic link to the [rules-enabled](rules-enabled/) folder. Of course you can create rules directly in `rules-enabled/` if you want.

Each file in the folder is considered a **rule set**, and the filename represents the name of that rule set. The rule set file is a yaml format file. The following is a portion from [rules-available/cakewalk](rules-available/cakewalk)

```yaml
-
  name: Cakewalk 1
  notes: A#2 A#3 D4 G4
  trigger: led-pattern-4!
  type: everytime
  enabled: true

-
  name: LED Text
  notes: B6
  trigger: led-text
  type: everytime
  enabled: true

-
  name: Reset
  notes: C7
  trigger: reset
  type: everytime
  enabled: true
```

The outermost level is a list, which consists of all rules. Each rule consists of the following elements:

 - name
 - notes
 - trigger
 - type
 - enabled

At this point of time, only `notes` and `trigger` is taken into consideration. The other elements are not yet implemented. The idea is easy: if the current keys on the keyboard contains the `notes` defined by the rule, it will trigger a signal.

## Emitters
Emitters are the output of the triggered signals. As you can see in the [emitters](emitters/) folder, there are currently three different emitters: [WebSocketEmitter](emitters/WebSocketEmitter.py), [SerialPortEmitter](emitters/SerialPortEmitter.py) and [OSCEmitter](emitters/OSCEmitter.py).

You can modify these or write your own. Basically what WebSocketEmitter does is to send whatever triggered to the client. While SerialPortEmitter and OSCEmitter only send selected triggers.

## Live
live is the core object that handles the main procedure. It has a polling function `midi_poll` registered to tornado's [PeriodicCallback](https://www.tornadoweb.org/en/stable/ioloop.html#tornado.ioloop.PeriodicCallback) to poll the MIDI events, and it examines through the rule sets when there are MIDI signals. You can add emitter, rule sets and change the current rule set by calling live's corresponding functions.

Take a look at [server.py](server.py) and [core/live.py](core/live.py) to see how live object can be used.

## Styles
We're using [scss](https://sass-lang.com/) here. So if you want to change the style, go to the static folder and use the scss watch command.

```
$ cd static
$ scss --watch scss:css
```

## Advanced Usage
### Time based signals
You can create rules for the notes of the first beat in a bar, so after the second bar, you can calculate how many seconds a bar takes (the current speed). And then, you can trigger time based signals on every eighth note.

In order to achieve this, you need to write a custom class derived from `RuleSet` ([core/rules.py](core/rules.py)). Take a look at [rules/BrainCrampTimerRuleSet.py](rules/BrainCrampTimerRuleSet.py) and [rules-available/braincramp](rules-available/braincramp) to see how it is done.

### Control the server
You can change the rule sets from the web page. See how it is done by searching `changeRuleSet` in [static/screen.html](static/screen.html) and how the `ScreenSocketHandler` handles it in [server.py](server.py).
