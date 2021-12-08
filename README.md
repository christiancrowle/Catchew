# Catchew
## A Pokemon breeding tool

Catchew is a pokemon breeding viability calculator with a simple command set. Enter all of the pokemon in your box and party, and quickly access information on breeding viability, egg groups, masuda hunting, and more.

All of the code is in a single file. Just run `catchew.py` with python3 and start entering commands.

Command set: (where <pokemon> is the pokemon being operated on, <gender> is one of M or F, and <region> is either ENG, or something else)
```
"ca <pokemon>!<gender>!<region>": add a pokemon to the box
"re <pokemon>!<gender>!<region>": release a pokemon
"tr <pokemon>!<gender>!<region>!!<pokemon>!<gender>!<region>": trade the first pokemon for the second (shorthand for a ca followed by a re)
"co": view current egg group coverage
"po <pokemon>": check if it's possible to breed a pokemon
"ap": list all possible pokemon to breed
"lg <pokemon>": list information about a pokemon
"vi": view your box
"sa": save the current state
"q!": quit
"h" or "help" or "?": view usage
"clear-all-data-yes-i-mean-to-do-this": delete everything in your box and start fresh
```

This code is under the MIT license