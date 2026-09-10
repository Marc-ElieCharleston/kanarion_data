# Level-20 2v2 tournament allocation model

Answers, for every pair of subclasses (team A) against every other pair (team B):
which stat allocation for the four characters makes the matchup a coin flip
(`balanced.csv`), and, as the reference point, what each team would allocate if it
played to win (`matchups.csv`). The fight model accounts for base stats, passives,
skill damage, status effects, skill cooldowns, Souffle pool and regen, and HP, all
read from the JSON data.

Rules modeled, as decided on 2026-09-10: character level 20, no items, every skill at
level 1 (5 base + 5 subclass, the base-class movement skill excluded), every passive at
level 1, a single 2v2 game, everyone always in range, a team may repeat a subclass.
The only decision per character is the split of its 57 stat points over HP, Souffle,
ATK or MAG (whichever the kit scales with), and DEF.

## Run

```
cd scripts/balance
python3 run_tournament.py                 # ~4 min on 12 cores; outputs in out/
python3 run_tournament.py --from-candidates  # redo stage 2 only, ~2 min
python3 run_tournament.py --no-repeats    # 276 compositions instead of 300
python3 run_tournament.py --rebuild       # recompute the rotation tables (HiGHS MILP, ~1 min)
python3 run_tournament.py --budgets out/budgets.csv   # per-subclass stat-point budgets (CSV: subclass,budget)
python3 calibrate_budgets.py --rounds 6 --target 0.10  # iterate budgets until the subclass spread <= target
python3 run_tournament.py --budgets out/budgets.csv   # per-subclass stat-point budgets (CSV: subclass,budget)
python3 calibrate_budgets.py --rounds 6 --target 0.10  # reduce strong subclasses' budgets until the spread <= target
python3 kdata.py berserker lifewarden     # print how a subclass's skills were priced
python3 plans.py berserker                # print rotations for one subclass
```

Needs only numpy and scipy (HiGHS ships inside scipy: `milp` for the rotations,
`linprog` for the equilibria).

## C++ solver (`cpp/kbal`)

The same pipeline in C++17, multithreaded, for the full table in minutes. HiGHS is
linked for the per-matchup zero-sum LP (`brew install highs`); the rotation MILPs stay
in Python and are exported once.

```
python3 export_tables.py                      # out/tables.bin: level-20 stats + rotation tables (59 MB)
make -C cpp                                   # needs /opt/homebrew/include/highs; make NOHIGHS=1 for a fallback build
cpp/kbal out/tables.bin --threads 16          # full table -> out/balanced_cpp.csv, compositions_cpp.csv, subclasses_cpp.csv
cpp/kbal out/tables.bin --matchup berserker lifewarden elementalist guardian   # one matchup, verbose
cpp/kbal out/tables.bin --eval a b c d hp0/mp12/atk45/def0/w1 ...             # evaluate four given builds
cpp/kbal out/tables.bin --gametest            # HiGHS vs fictitious play on a known game
```

Options: `--tol` (balance tolerance, s), `--tau` (logistic scale, s), `--no-repeats`,
`--limit N`, `--br-iters N` (best-response rounds against the exact opponent, default 2),
`--out DIR`, `--exhaustive`. By default the play-to-win best responses use a step-6
coarse sweep followed by a multi-start pattern search (moves of 4, 2, 1 points between
stats), which is about 3x faster than the exhaustive step-3 grid for the same balance
quality; the handicap step always uses the exhaustive grid because the nearest
in-band allocation is what it must find. `--exhaustive` restores the full grids
everywhere (about 13 min for the table instead of 5). The evaluator is a line-by-line port and reproduces the Python numbers to
six decimals (`--eval` against `evalmodel.evaluate`); the search and balancing follow
the same grids and tie-breaks, so results match the Python tool up to search-order
ties. The tables are shared read-only across threads; each thread owns its HiGHS
instance with `threads=1`.

## Outputs (`out/`)

- `balanced_cpp.csv.gz`: the deliverable, one row per unordered matchup with the locked 50/50 allocations (see above). The uncompressed file and the large reproducible artifacts (`plans.pkl`, `tables.bin`, `matchups.csv`, `candidates.csv`) are gitignored; regenerate them with the commands above.
- `matchups.csv`: one row per unordered matchup, 45,150 rows. `p_team12_wins` is the
  equilibrium win probability of team (class1, class2) against (class3, class4).
  `alloc_*` are the highest-weight equilibrium builds as `hp/mp/atk|mag/def/w`
  where `w` is the support weight the rotation was optimized with. `equilibrium_mix_*`
  lists every build with weight >= 5% when the equilibrium is mixed (it usually is:
  glass-cannon and bulky builds counter each other). `ttfk_*` are the continuous
  times to first kill of the reported build pair; `margin_s` is the volley-snapped
  margin used for the win probability.
- `compositions.csv`: mean equilibrium win probability of each composition over the
  field, with its worst and best matchup.
- `subclasses.csv`: mean over every composition containing the subclass, and its best
  partner. This is the per-subclass fairness number.
- `candidates.csv`: the candidate builds of every composition with derived stats.

## How it works

1. **Data** (`kdata.py`): level-20 stats are `base + floor(growth x 19) + points x value`
   with HP/Souffle 5 per point, ATK/MAG 1, DEF +1 armor only, magic resist
   `= base + growth + 0.2 x MAG` (progression.json v4.0). Passives at level 1 are
   applied as flat or percent bonuses. Each skill is turned into per-cast components:
   direct damage `scaling_percent% x stat`, DoT per second, heals, shields, buffs,
   debuffs, control, using the Option A canonical grid for every stackable effect.
2. **Rotations** (`plans.py`): for each subclass, Souffle level (0..57 points), fight
   horizon T (4 to 60 s) and support weight w, a MILP picks integer cast counts that
   maximize HP-equivalent value under three constraints: casts <= 1 + T/cooldown,
   sum of max(2 s, cast time) <= T, sum of Souffle costs <= pool + 1/s x T.
3. **Matchup evaluation** (`evalmodel.py`): each side attacks the enemy member that
   dies fastest (focus fire), using the combat.json pipeline: flat DEF x 0.5 subtracted
   per hit, `100/(100+armor)` and `100/(100+MR)` ratios, damage reduction, expected
   crit `1 + crit% x (crit_dmg-100)%`, 95% hit. Effective HP of a target = HP + shields
   + heals landing on it (heals only after the first GCD) + lifesteal. Control lands on
   the enemy's main damage dealer; taunt, confusion and damage transfer from the
   partner shield the focus target. The horizon T is chosen by fixed point so that the
   rotation matches the fight length it implies. Kill times snap to the 2-second
   volleys. `ttfk` shows `none` when a side cannot kill within a minute.
4. **Best response** (`search.py`): exhaustive vectorized sweep of the allocation grid
   for one member while the partner is fixed, coordinate descent between the two. The
   play-to-win score is the kill-time margin divided by the fight length, so a 4 s edge
   in an 8 s fight beats a 12 s edge in a 32 s slugfest.
5. **Game** (`run_tournament.py`, `game.py`): each composition gets ~11 candidate builds
   (best responses against six reference opponents plus generic builds). For each
   matchup all candidate pairs are evaluated, the margin is mapped to a win probability
   with a 2-second logistic scale, and the zero-sum game is solved by LP. With
   `--refine N`, each matchup additionally runs N rounds of best responses between the
   two exact teams, starting from the pool equilibrium, and adds the visited builds to
   the pool before the final solve (`build_tag` = `br:opponent`).

## Per-subclass budgets

`calibrate_budgets.py` runs the full pipeline repeatedly. After each round every
subclass's budget moves against its deviation from a 0.5 mean win probability
(`gain` points per 1.0 of deviation, damped each round), keeping the field's total
budget constant and each budget within 20..100. Rounds are written to
`out/calib/round_<k>/`, the latest budgets to `out/budgets.csv`, and the trajectory to
`out/calibration_history.csv`. The rotation tables cover Souffle allocations up to 100
points so any budget in that range works.

## Optional: per-subclass point budgets

`calibrate_budgets.py` is a separate experiment that reduces the stat budget of the
strongest subclasses round after round (level 20 gives 57 points, so budgets only go
down, floor 10). It is not part of the allocation answer. Its runs live in
`out/calib/`; the 2026-09-10 run showed the lever saturating around a 0.25 spread.

## Approximations to keep in mind

- Fights are 2 to 5 volleys long at this level without gear, so the result is a burst
  race. Average-rate pricing of buffs, DoTs and heals is coarse at that scale; a
  tick-by-tick simulator would sharpen the numbers but not change the picture.
- The free innate procs (warrior +15% ATK, mage +8% MAG, archer +10% damage taken on
  target, rogue +12% damage +8 armor pen, healer +5% healing, artisan +6% heal/shield)
  are steady-state constants, see `INNATE` in `kdata.py`.
- Unpriced engine verbs: cleanse, purge, steal_buff, interrupt, invisible, cover,
  cc_immune, riposte, en garde, enchanted blade, mana steal/lock/drain, heal_block,
  double attack, hp_dot, sacrifice. `python3 kdata.py` lists them per skill. Support
  subclasses that lean on these are undervalued.
- `shield_crush` scales on `current_shield`, approximated as 15% of max HP.
- DoT ticks are reduced by armor/MR ratio only, not by flat DEF (status_effects.json
  says "reduit par armure"). No flat magic defense exists in the data.
- AoE skills hit only the focus target (teams are assumed to spread).
- Hard control (stun, freeze, fear, silence) from the enemy team lands on the main
  damage dealer with full effect and no diminishing returns; two chained 3-second
  stuns really do blank a 6-second fight. The data defines no CC diminishing rule.
- The 2-of-5 class passive rule is not enforced by the server, so all five are at
  level 1; the three subclass passive files are included at level 1 too.
