# House of Gains: Unity Casino Mini-Games

Gameplay scripts for *House of Gains*, a casino-themed Unity game. The player climbs floors by earning chips in mini-games. These scripts implement the mini-game framework, the in-game economy and two of the games.

**Context:** Game Design module, UCT Honours (2026).

## Contents
| Folder | Contents |
|---|---|
| `EconomyAndHigherLower/` | `EconomyManager` singleton (chips, round tokens, floor thresholds, buy-ins), the `BaseMiniGame` abstract class, `Card` model, and the Higher/Lower game logic and UI |
| `Presents/` | Final versions of Higher/Lower and Roulette (red/black, odd/even and number bets), table-interaction triggers, and UI prefabs |

**Tech:** C#, Unity (MonoBehaviour, prefabs, UI), with object-oriented design built around a shared mini-game base class.
