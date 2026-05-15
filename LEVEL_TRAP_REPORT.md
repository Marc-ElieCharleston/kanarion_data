# Skills "level-trap" — review & fix log

**Statut au 2026-05-15** : 99 skills traités. Reste 1 cas spécial (DoT) qui dépend de l'extension du schéma Skill (Task #4).

## Historique

| Date | Étape | Hits restants |
|------|-------|---------------|
| ~2026-05-14 | Premier rapport `lint_useless_level.py` | 129 (avec faux positifs) |
| 2026-05-15 | Lint patché : nested `effects[].duration_per_level` + champs additionnels reconnus | 99 |
| 2026-05-15 | Apply des défauts par bucket (`apply_level_trap_fixes.py`) | 1 (DoT-static, déféré task #4) |

## Décisions de design (CTO 2026-05-15)

| Bucket | Skills | Action appliquée |
|--------|--------|------------------|
| 1 — Buffs offensifs canonical (atk_up/crit_up/atk_speed_up via stacks) | 21 + 7 mixed | `duration_per_level: 0.2` (+1.8s à lvl 10) |
| 2 — Buffs défensifs canonical (DR/armor/MR via stacks) | 8 | `duration_per_level: 0.2` |
| 2b — Resource buff non-canonical (mana_regen, heal_over_time avec stacks_to_apply) | 2 | `duration_per_level: 0.2` |
| 3 — Shields (shield_max_hp/def/mag avec `value`/`pct`) | 15 + 9 mixed | `effects[i].value_per_level: 1` |
| 4 — HoT-only (heal_over_time_max_hp avec `pct`) | 5 + 4 mixed | `effects[i].pct_per_level: 0.2` |
| 5 — Debuffs/CC (atk_down/fear/stun/etc.) | 11 | `duration_per_level: 0.2` (stat) ou `0.1` (CC dur) |
| 6 — Binary utility (invisible/cc_immune/stance) | 5 | `duration_per_level: 0.2` |
| 6b — Cleanse/purge/steal_buff | 2 | `mana_cost_per_level: 0` (effet binaire fixe) |
| 7 — DEAD `heal_scaling_per_level` (loader ne lisait jamais) | 5 + 2 cachés | Migration → `percent_per_level: N` (même valeur) |
| 8 — Mystery skills (card_lucky_draw, fate_gambler, cantor_requiem) | 3 | `mana_cost_per_level: 0` (effets intentionnellement fixes / threshold-based) |

## Audit de cohérence loader / data (effectué 2026-05-15)

Découvert pendant le review :

| Field | Backend C++ | Client Godot | Verdict |
|-------|-------------|--------------|---------|
| `effects[i].value_per_level` | OK Lu (`content_loader.cpp:590`, `room.cpp:3320`) | KO Pas lu | **Combat OK, tooltip cassé** → Task #6 |
| `effects[i].pct_per_level` | OK Lu (`content_loader.cpp:594`, `room.cpp:3324`) | KO Pas lu | **Combat OK, tooltip cassé** → Task #6 |
| `effects[i].pct` | OK Lu (`content_loader.cpp:585`) | KO Pas lu | **Combat OK, tooltip cassé** → Task #6 |
| `heal_scaling_per_level` | KO Pas lu | KO Pas lu | **Truly dead** → migré vers `percent_per_level` (task #5 closed) |
| `dot_percent_per_level` / `dot_duration_per_level` | KO Pas dans schéma | KO Pas dans schéma | **À implémenter** → Task #4 |

Conséquence : les choix Buckets 3 et 4 (`value_per_level` / `pct_per_level` nested) sont **valides** car le combat les applique correctement. Seuls les tooltips client doivent être patchés en parallèle (Task #6).

## Cas spécial restant : `dot-static` (1 skill)

| Skill ID | Détail | Statut |
|----------|--------|--------|
| `skill_healer_martyr_intercession` | dot_percent=3, dot_duration=6, dot_heals_lowest_ally=true | **Bloqué par Task #4** : extension du schéma Skill avec `dot_percent_per_level: 0.5` et `dot_duration_per_level`. Une fois implémenté côté backend C++ + Godot loader, appliquer `dot_percent_per_level: 0.5` à ce skill (lvl 1 = 3% → lvl 10 = 7.5%). |

## Scripts associés

- `scripts/lint_useless_level.py` — détection (peut tourner à tout moment, devrait toujours retourner 1 hit jusqu'à la résolution du DoT-static).
- `scripts/apply_level_trap_fixes.py` — application des défauts par bucket. Idempotent. Mode `--dry-run` pour preview.

## Tâches de suivi (cross-repo)

1. **Task #4** — Extension du schéma Skill avec `dot_percent_per_level` et `dot_duration_per_level` (backend C++ + Godot loader). Bloquant pour Intercession.
2. **Task #6** — Patch `kanarion_front/scripts/skills/skill.gd` pour lire les fields nested per-level (visualisation/tooltip uniquement, le combat est déjà correct).
