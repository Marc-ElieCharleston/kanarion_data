# Level-20 2v2 tournament: locked allocations per matchup (2026-09-10, C++ solver)

Rules: no items, all skills and passives level 1, single game, everyone in range, repeats allowed.
Fight model: base stats, passives, skill damage, status effects, cooldowns, Souffle pool and regen, HP.
300 compositions, 45150 matchups, solved by `cpp/kbal` in under 5 minutes on 16 threads. Table: `balanced_cpp.csv.gz`.

## Result

- With the four allocations locked as in the table, the kill-time margin is within 0.25 s in 99.7% of matchups and the win probability within 0.47..0.53 in 94% (median 0.487).
- When both teams play to win instead, 32% of matchups are more lopsided than 75/25.
- The favoured team gives up a median of 13 points from its best build (p75 28, p90 48); 7% of matchups needed no change.
- A balanced allocation is not unique: the table reports the one nearest (in points moved) to the play-to-win builds, so a different reference can give a different, equally balanced lock. Use `cpp/kbal --matchup` to explore alternatives for a specific pairing.

## Subclasses: play-to-win strength, how often favoured, and the team handicap when favoured

| subclass | base | mean win prob (play to win) | favoured in | team points given up |
|---|---|---|---|---|
| guardian | warrior | 0.712 | 69% | 28.1 |
| weaponmaster | warrior | 0.655 | 76% | 24.1 |
| chef | artisan | 0.631 | 61% | 27.7 |
| berserker | warrior | 0.630 | 56% | 17.5 |
| warlord | warrior | 0.595 | 69% | 21.1 |
| occultist | mage | 0.592 | 66% | 20.3 |
| duelist | rogue | 0.575 | 59% | 18.3 |
| elementalist | mage | 0.567 | 61% | 20.5 |
| corsair | rogue | 0.556 | 60% | 17.1 |
| falconer | archer | 0.535 | 56% | 18.2 |
| shadowblade | rogue | 0.520 | 57% | 16.4 |
| ranger | archer | 0.514 | 55% | 16.6 |
| gunslinger | archer | 0.511 | 53% | 17.5 |
| trickster | rogue | 0.481 | 51% | 15.9 |
| musician | artisan | 0.459 | 57% | 17.7 |
| ballmaster | archer | 0.458 | 30% | 15.3 |
| lifewarden | healer | 0.438 | 49% | 18.5 |
| lightbringer | healer | 0.423 | 46% | 16.9 |
| cantor | healer | 0.421 | 32% | 18.9 |
| martyr | healer | 0.417 | 45% | 17.6 |
| alchemist | artisan | 0.387 | 22% | 17.1 |
| cardmaster | mage | 0.344 | 22% | 14.6 |
| spellblade | mage | 0.305 | 24% | 13.2 |
| blacksmith | artisan | 0.273 | 20% | 14.5 |

## Reading a row of `balanced_cpp.csv`

`lock_class1..4` are the allocations to set, as `hp/mp/atk|mag/def` points (57 per character; `w` is the support weight the rotation was optimized with and can be ignored). `favoured_before` says which team was ahead when both played to win, `points_moved_12/34` how far each team's allocation was moved. `best_class1..4` are the play-to-win builds and `p_team12_wins_free` the play-to-win win probability.

One matchup with rotations and kill times: `cpp/kbal out/tables.bin --matchup <a> <b> <c> <d>` (or `python3 matchup.py <a> <b> vs <c> <d> --balance`).

See `README.md` for the model and its approximations.
