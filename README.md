# Mr. Stopwatch mark II

![0012087](https://github.com/TheOpponent/mr-stopwatch-2/assets/8432212/ba2fda79-473a-43c9-bf03-bf186a0bd6a2)

A simple Python program written in wxPython that keeps time and writes it to time.txt. Two times are kept:
- Session time, kept until the program is closed or the active timer is switched.
- Total time, kept until the Reset button is pressed.

Multiple timers can be saved and edited while the program is running. Times are saved in a JSON file.

time.txt is intended to be read by another program, e.g. OBS, to show time elapsed for a single stream and for a whole playthrough across multiple streams.

The timer is not precise and keeps seconds, not milliseconds. Days are not tracked either; the hour counter can go into triple digits.
