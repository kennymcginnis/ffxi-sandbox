# Steps

Modified version of Debuffed to track DNC step durations and levels on your current target.

Original addon: Debuffed by Xathe (Asura). Modified by Cypan (Bahamut).

## Commands

All commands use `//steps`:

| Command                                | Description                                                        |
| -------------------------------------- | ------------------------------------------------------------------ |
| `//steps mode` (or `m`)                | Switches between blacklist and whitelist mode (default: blacklist) |
| `//steps timers` (or `t`)              | Toggles display of debuff timers (default: on)                     |
| `//steps interval <value>` (or `i`)    | Changes the refresh interval in seconds (default: 0.1)             |
| `//steps hide` (or `h`)                | Toggles hiding timers that reach 0 (default: off)                  |
| `//steps blacklist add\|remove <name>` | Adds/removes an ability from the blacklist                         |
| `//steps whitelist add\|remove <name>` | Adds/removes an ability from the whitelist                         |

Any unrecognized command prints the in-game help.

## Known Issue

Timer duration isn't 100% accurate due to how step duration is handled, but it's accurate enough to show which step needs refreshing and which steps have worn off.

## Support

First and foremost: Please support the original author if this is an addon modification.
If you enjoy the addon and you'd like to buy me a coffee, it's appreciated but never expected:

[![Buy Me a Coffee](https://img.shields.io/badge/Buy%20Me%20a%20Coffee-cypan-FFDD00?logo=buymeacoffee&logoColor=black)](https://buymeacoffee.com/cypan)

Bug reports and pull requests are worth more than donations, so open an issue if something's broken please.
