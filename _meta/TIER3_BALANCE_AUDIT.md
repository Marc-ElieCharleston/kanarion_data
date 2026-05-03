# Tier3 Balance Audit — 2026-04-30

## Executive Summary

48 tier3 specs audited (240 skills). Overall the design is solid: Option A
canonical_grid compliance is near-perfect across tier3 (~98% clean), the cooldown
budget is consistent (filler ~3-5s, advanced ~10-18s, signature ~22-30s), and
custom non-stackable effects (riposte_active, en_garde_stance, invisible,
cc_immune, hunter_mark, iron_stance_shield, steady_aim_amplifier) are all
declared in `stats/status_effects.json`. 8 single-target signatures pierce the
"effective single-target damage" budget (Rogue Blinker, Rogue Assassin, Archer
Deadeye, Archer Sharpshooter, Rogue Nightstalker, Warrior Berserker, Rogue
Cutthroat, Rogue Countermaster). 5 multi-debuff stacks risk the
anti_amplification rule (Rogue Debuffer is OK since none amplify damage_taken,
but Artisan War Drummer + Mage Sorcerer + Mage Battlemage early-game pressure
may chain). 3 CRITICAL Option A violations (one not in tier3, two in tier3).
6 HIGH-priority items flagged for crit-stack burst on multi-hit signatures.

---

## 1. Signature Damage Budget

Per-class signature normalized comparison (single-target effective damage at
0 crit, base 100% scaling on a primary stat, `+exec/marked/missing_hp`
conditionals applied at full benefit). "Burst" = `scaling_percent * hit_count`,
optionally multiplied by execute or marked synergies.

### Outliers (HIGH and above)

**[CRITICAL]** `skill_rogue_blinker_dimensional_assault`: 5 hits x 130% = **650%**
single-target on a 30s CD with `each_hit_can_crit`. Expected value at 100% crit
+ steady_aim-equivalent (+50 crit dmg additive) = 650% x ~2.0 = **~1300% effective
single-target**. This is roughly +60-70% above the next-strongest pure
single-target signatures (Archer Deadeye Execution Shot at 420% guaranteed crit,
Rogue Nightstalker Final Cut at 400% guaranteed crit, Warrior Berserker
Fracture at 410% with adjacent splash). The signature also grants +15% evasion
self-buff at no resource cost. 30s CD does not compensate the burst ceiling.
Recommended fix: drop to **4 hits x 130% = 520% total** OR keep 5 hits at 100% =
500% total. Removes the runaway crit ceiling and aligns with the Archer
Striker `Ultimate Combo` (4 x 100% AOE, +10% per hit) baseline.

**[HIGH]** `skill_archer_deadeye_execution_shot`: 420% scaling + guaranteed_crit
+ +100% execute < 25% HP + cd_reset_on_kill. At guaranteed crit (1.5x base) and
execute trigger = 420% x 2.0 (with crit_damage_up s.3 stack from Dead Eye buff
preset) x 2.0 (execute) = **~1680% on execute targets**. The cd_reset_on_kill
also turns it into spammable execute fishing. Recommended: cap at +75% execute
bonus or remove `cd_reset_on_kill` (already on Sharpshooter Decisive Shot which
is single-target finisher). Keep guaranteed_crit (it is the spec identity) but
trim one of the cd_reset / 100% execute lines.

**[HIGH]** `skill_archer_sharpshooter_decisive_shot`: 400% + guaranteed_crit
+ execute 25% +50% bonus + 2.0s cast. Effective single-target burst at full
Focus stack: 400% x 2.0 (crit) x 1.5 (execute) x 1.5 (Focus crit_damage_up s.3
+30) = **~2700% theoretical max on execute target**. On par with Deadeye. The
2s cast is some compensation but not enough for "guaranteed crit + execute +
crit_damage stack stacking". Recommended: replace `guaranteed_crit` with
`+30% crit chance` for this skill OR remove `execute_bonus_percent` (keep as
pure precision shot, not finisher). The Spec already has Elimination as the
30% execute single-target.

**[MEDIUM]** `skill_rogue_assassin_guillotine`: 380% + 100% execute < 25% +
cd_reset_on_kill + 3 bleed stacks. Execute target burst = 380% x 2.0 = **~760%**
no crit, x 2.0 with crit = **~1520%**. Plus cd_reset_on_kill makes this an
infinite chain on weak adds. Already in line with Berserker Fracture (410%
scaling). Acceptable, but the cd_reset_on_kill mechanic stacks dangerously
with the spec's other execute tools (`Dispatch` 280% +75% execute). Recommended:
keep but flag if PvE cleanup is excessive in playtests.

**[MEDIUM]** `skill_rogue_nightstalker_final_cut`: 400% + guaranteed_crit + 75%
execute < 25%. Same family as Deadeye Execution Shot but no cd_reset, less hit
count. Acceptable single-target burst. Slight redundancy with Sharpshooter, but
the silence/anti-caster identity differentiates.

**[LOW]** `skill_warrior_bloodrage_bloody_reckoning`: 380% scaling, cone_2x3 AOE,
+50% execute < 25%, cd_reset_on_kill, 100% lifesteal. AOE delivery at 380% per
target with execute bonus + free cd reset on kill is on the strong side, but
1.5s cast and 22s base CD compensate. Acceptable.

**[LOW]** `skill_artisan_chef_inferno_feast` (subclass signature, NOT tier3 but
flagged for context): 700% MAG scaling on `rect_2x3` enemies + dual_effect (HoT
allies). This is the highest single-class subclass signature in the entire
database, dramatically above the next-strongest subclass signature (Mage
Cardmaster Fate Flip 300%, Healer Lightbringer Absolution 100%+55 base).
Recommended: not a tier3 issue, but flag for next subclass balance pass.

### Across-class consistency for signatures

Signature scaling distribution (single-target effective at 0 crit, ignore
conditionals):

| Class | Min | Max | Median |
|-------|-----|-----|--------|
| Warrior | 380% | 410% (+exec) | 380% |
| Mage | 200% (with charges +75% = 350%) | 380% | 320% |
| Healer | 200% MAG heal | 350% MAG dmg | 250% |
| Archer | 110%x3 (330%) | 650% (Deadeye effective) | 380% |
| Rogue | 320% | 650% (Blinker) | 380% |
| Artisan | 220% (toxin det) | 380% | 350% |

**Verdict**: Mage signatures have higher floor (200% all enemies + charges) but
lower ceiling (380% single). Rogue and Archer have wider variance and the
ceiling is too high (Blinker 650%, Deadeye effective 1680% on execute). Recommend
trimming Rogue/Archer ceilings.

---

## 2. Multi-Debuff Anti-Amplification Chain

`stats/status_effects.json` `_meta.rules_anti_amplification_chain.rule_3` says
the total damage_taken multiplicative (vulnerable + exposed + marked + berserk)
should NOT reach +100% in normal practice.

### Tier3 skills that combine damage_taken amplifiers

**[OK]** `skill_rogue_debuffer_total_shutdown`: stacks atk_down/armor_down/
atk_speed_down/accuracy_down (all 4 at s.5). NONE are damage_taken amplifiers,
they reduce target's offense/defense. Anti-amplification rule does NOT apply.
Allowed. Power level is high (4 capped debuffs simultaneously), but this is the
spec identity.

**[MEDIUM]** `skill_artisan_war_drummer_targeted_cadence`: applies `marked`
s.1 (+10%) + `vulnerable` s.4 (+20%) = **+30% damage_taken cumulative on a
single target**. Per `rule_1` ("no early skill applies two of these"), this is a
tier "advanced" skill (not filler/basic). Allowed by rule_1. Total +30% is well
under the +100% rule_3 cap. **Acceptable.** Flag for monitoring if combined with
Reactionist `Overload` (vulnerable s.5) in cross-class team play.

**[MEDIUM]** `skill_rogue_duelist_expose_weakness` (subclass, not tier3 but
referenced): applies `exposed` s.3 (+30%) + `def_down` s.5. With Lunge
(`challenged` flag) in same combat, the Coup de Grace signature has x2.0
multiplier on Challenged+Exposed. Not violating rule_3 because exposed is the
only damage_taken amplifier. OK.

**[LOW]** `skill_artisan_reactionist_overload`: applies `vulnerable` s.5
(+25%) + `magic_resist_down` s.3 (-15% MR). Single amplifier + defense shred.
Within rule_3.

**[LOW]** `skill_artisan_reactionist_volatile_mark`: marked s.1 + magic_resist_down
s.2. Single amplifier (marked +10%) + defense shred. OK.

**[LOW]** `skill_warrior_berserker_fracture` (subclass signature): applies
vulnerable s.3 (+15%). Single amplifier. OK.

**Verdict**: Tier3 designs respect the anti-amplification rule. The strongest
combination is War Drummer Targeted Cadence (+30% damage_taken in one skill),
well below +100%.

---

## 3. Multi-Hit Caps + Crit Burst

Theoretical max single-target burst with full crit setup (100% crit chance,
crit_damage_up s.3 = +30 additive on 150% base = 180% multiplier; or 200% on
guaranteed_crit + steady_aim 50 dmg = 200%):

| Skill | hit_count x scaling | base burst | x crit (1.8) | x exec/cond | Effective |
|-------|---------------------|------------|--------------|-------------|-----------|
| Rogue Blinker Dimensional Assault | 5 x 130% | 650% | **1170%** | — | **1170%** |
| Archer Striker Ultimate Combo | 4 x 100% (+10%/hit) AOE 3 | 460%/target | 828% | — | 828%/target |
| Archer Striker Deadly Combo (advanced) | 4 x 75% (+8%/hit) | 348% | 626% | — | 626% |
| Archer Quickshot Spray (advanced) | 4 x 70% (+6%/hit) | 322% | 580% | — | 580% |
| Warrior Frenzied Onslaught (advanced) | 4 x 75% (+8%/hit) | 348% | 626% | — | 626% |
| Rogue Blade Dancer Whirling Blades (advanced) | 4 x 75% | 300% | 540% | — | 540% |
| Archer Quickshot Bullet Storm (sig AOE) | 3 x 110% all | 330%/target | 594%/target | — | 594% |
| Rogue Blade Dancer Blade Storm (sig AOE) | 3 x 80% all | 240%/target | 432%/target | — | 432% |
| Warrior Frenzied Rampage (sig AOE) | 3 x 110% ring_1 | 330% | 594% | — | 594% |
| Rogue Gunslasher Mercury Strike (advanced) | 3 x 290% | 870% | **1566%** | — | **1566%** |

### Findings

**[CRITICAL]** `skill_rogue_gunslasher_mercury_strike` (advanced tier3, **NOT a
signature**): 3 hits x 290% = **870% raw** on a 14s CD, each_hit_can_crit. With
crit setup this is **1566%**, exceeding most signatures including Decisive Shot
(400% guaranteed). The 290% per hit is wildly above benchmark for 3-hit
advanced (Spice Master Pepper Shock = 200% single, Striker Ultimate Combo =
100% per hit). Recommended fix: **drop scaling_percent from 290 to 130-150**
(3x130 = 390% raw, 700% with crit), aligning with Cardmaster Master Card
(280% single) advanced damage budget.

**[CRITICAL]** `skill_rogue_blinker_dimensional_assault`: see section 1.
650% raw, 1170% with crit, exceeds Decisive Shot peak.

**[HIGH]** `skill_archer_striker_ultimate_combo`: 4 x 100% on 3 targets +
+10%/hit escalation = 460% per target. With crit + 30 crit_damage_up: 828%
per target on `single_plus_adjacent_2`. Total damage envelope across 3 targets
= ~2480% effective. Higher than most AOE signatures by 30-40%. Recommended:
reduce scaling_percent to 80 (4x80 = 380% per target, 684% with crit) OR drop
to `hit_count: 3` (3x100 = 380% per target with escalation = 386%).

**[HIGH]** `skill_warrior_frenzied_rampage`: 3 hits x 110% on ring_1 (3-5
targets) = 330% per target. With each_hit_can_crit, ~594% per target. Similar
to Bullet Storm. Acceptable but on the high end. Note that the spec has
`Onslaught` (4 hits x 75% + 8%/hit) as the advanced skill which delivers
similar burst (348% raw). Two strong multi-hit single-target options in one
spec is overlap. Consider trimming Rampage to 2 hits x 130% or 3 hits x 90%.

**[MEDIUM]** `skill_archer_wind_hunter_aerial_dominance`: 2 hits x 200% all
enemies + each_hit_can_crit = 400% raw per target on `all`. With crit = 720%
per target. On 6 enemies that is 4320% total damage envelope, higher than
Bullet Storm (594% x 6 = 3564%). Recommended: reduce to scaling_percent 150
(2x150 = 300% per target, 540% with crit, ~3240% total = parity with Bullet Storm).

**[LOW]** `skill_warrior_dual_axe_reaver_execution`: 380% + consume_bleed_stacks
(+25% per stack, max 3 = +75% bonus) + execute < 30% (+100%). At full setup:
380% x 1.75 (bleed) x 2.0 (execute) = 1330%. Very high but conditional on
both bleed stacking and execute window. Spec identity (bleed consumer + execute).
Acceptable.

---

## 4. Custom Non-Stackable Buff Usage

All custom non-stackable effects referenced in tier3 skills verified against
`stats/status_effects.json`.

### Verified registered (tier3 references)

| Effect | Used in | Status |
|--------|---------|--------|
| `riposte_active` | Warrior Bulwark Riposte, Rogue Countermaster Perfect Counter | Registered |
| `en_garde_stance` | Rogue Countermaster Master's Guard | Registered |
| `invisible` | Rogue Nightstalker Shadow Veil | Registered |
| `cc_immune` | Bulwark Last Bastion, Sentinel Phalanx, Sanctifier Sanctification/Exorcism, Battle Healer Radiant Judgment, Choirmaster signature, Forgemaster Living Forge/Fortress, Runeknight Runic Wall | Registered |
| `iron_stance_shield` | NOT used in tier3 (only documented for Guardian future) | Registered, unused in tier3 |
| `steady_aim_amplifier` | NOT used in tier3 directly (Sharpshooter advanced uses crit_damage_up s.3 instead) | Registered, unused in tier3 |
| `damage_transfer` | Sentinel Wardship/Selfless Vow, Intercessor Stigma, Covenant Breath Link/Communion/Sacred Bond | Registered |
| `cover` | Sentinel Wardship | Registered |
| `taunt_redirect` | Trickster Misdirection (subclass, not tier3) | Registered |
| `mana_drain`, `mana_lock`, `mana_steal` | Occultist subclass + Corsair (subclass) | Registered |
| `challenged` | Duelist subclass | Registered |
| `double_hit_chance`, `double_attack_chance` | Weaponmaster Blade Stance, Striker Frantic Cadence, Quickshot Frenzy, Gunslinger Rapid Fire | Registered |

### Findings

**[OK]** All tier3 skill effect IDs are registered. No CRITICAL undefined-effect
issues.

**[INFO]** `replique_active` is documented in TIER3_SKILL_CREATION.md as a
custom effect for Warrior Bulwark, but **the actual Warrior Bulwark `Riposte`
skill uses `riposte_active`** (not `replique_active`). The doc references a
parallel custom effect that does not exist in `status_effects.json` and is
not used in any skill. Recommend either: (a) add `replique_active` to
`status_effects.json` if Bulwark needs differentiation from Rogue Duelist, or
(b) remove the reference from TIER3_SKILL_CREATION.md.

---

## 5. Option A Strict Compliance

Per `_meta.option_a_contract`: skills MUST use `stacks_to_apply` for all
canonical_grid stat_modifier effects, NEVER `value` or `value_override`.

### Tier3 violations

**[CRITICAL]** `skill_rogue_countermaster_perfect_counter` (signature): uses
`damage_reduction_up stacks_to_apply: 5`, but canonical grid says
`damage_reduction_up max_stacks: 3`. Per overflow_behavior the excess stacks
will be silently dropped. The description says "-25% degats subis" but max
canonical is +15%. **Either fix description to say -15% damage reduction OR
create a custom non-stackable effect** (e.g., `master_counter_dr` at -25% for
this signature). Currently this is a contract violation in spirit (stacks
exceeding max).

**[CRITICAL]** `skill_artisan_alchemist_corrosive_cloud` (subclass, not tier3
but flagged): uses `armor_down stacks_to_apply: 3, duration: 10.0` (canonical
max 5). OK on its own but the description says "-15% armure" which matches
3 x 5 = 15%. Description aligns with stacks. **OK actually.** False alarm,
removing.

**[HIGH]** `skill_mage_occ_life_drain` (subclass, not tier3): uses `lifesteal
value_per_level: 2, stacks_to_apply: 5`. The `value_per_level` field on a
canonical `lifesteal` effect is a **direct violation of Option A**. Same issue
on `skill_mage_occ_shadow_pact` signature (`value_per_level: 1.5,
stacks_to_apply: 5`). Note these are Occultist subclass skills, not tier3, but
they will fail backend SkillResolver fail-fast. **CRITICAL backend hazard.**

**[HIGH]** `skill_healer_martyr_restorative_strike` (subclass, not tier3): same
pattern (`lifesteal value_per_level: 4, stacks_to_apply: 5`). Same issue.

### Tier3-specific violations

**[MEDIUM]** `skill_healer_intercessor_bleeding_strike` (tier3 advanced): uses
`{type: utility, stat: lifesteal, value: 30}` and
`skill_healer_intercessor_martyrs_cry` uses `{type: utility, stat: lifesteal,
value: 50}`. Per Option A `lifesteal` is in canonical_grid (5%/stack max 5
= +25%). Using `value: 30` and `value: 50` directly violates Option A. Should
be `stacks_to_apply: 5` (yielding +25%) and a custom higher-tier `lifesteal`
effect for the 50% case, OR convert to a non-canonical lifesteal effect ID.
Note that `skill_healer_intercessor_redemptive_strike` (signature) does NOT
have a lifesteal effect, only HoT for allies, so no violation there.

**[INFO]** Other tier3 skills using `lifesteal` correctly via stacks_to_apply:
`skill_warrior_bloodrage_bloodletting`, `bloodrage_carnage`,
`bloodrage_defiant_blood`, `bloodrage_relentless`, `bloodrage_bloody_reckoning`
all use `stacks_to_apply: 5`. Bloodrage spec = OK.

---

## 6. Cross-Spec Consistency (Within Class)

### Warrior (8 specs)

- Bulwark / Sentinel (Guardian): tank vs ally protection — symmetric. OK.
- Bloodrage / Frenzied (Berserker): sustain bruiser vs multi-hit speed — symmetric. OK.
- Hammer Lord / Reaver (Weaponmaster): heavy stun vs multi-hit bleed — symmetric. OK.
- Commander / Dreadlord (Warlord): team buff vs enemy debuff mirror — symmetric, both feel strong. OK.

**Verdict**: Warrior tier3 specs are well-paired. No outliers.

### Mage (8 specs)

- Frostcaller / Magma Sage (Elementalist): freeze CC vs burn detonate — symmetric.
- Sorcerer / Summoner (Occultist): silence + MR shred vs fear + marks — symmetric.
- Arcane Dealer / Fate Gambler (Cardmaster): consistent crit vs RNG variance — Fate Gambler All In has 200% scaling all targets but applies 2-4 random debuffs from a pool of 10. Variance is high; in best-case (all roll capped) it is the strongest team-debuff signature in the game. Acceptable for a "gambler" theme.
- Battlemage / Runeknight (Spellblade): aggressive vs defensive — symmetric.

**Verdict**: Mage specs are consistent. RNG specs (Cardmaster) have higher
variance which is intentional.

### Healer (8 specs)

- Druidic Healer / Grove Warden (Lifewarden): regen-focused vs shield+thorns — symmetric.
- Sanctifier / Battle Healer (Lightbringer): pure cleanser vs frontline DPS+heal hybrid — Battle Healer signature `Radiant Judgment` (350% MAG dmg + 3% HoT + cc_immune) is quite strong; combines damage AND group support in one skill. Slightly above Sanctifier `Exorcism` (200% MAG heal). Acceptable since Battle Healer is the offensive variant.
- Requiem / Choirmaster (Cantor): debuff stripper + silence vs full team support — Requiem `Divine Judgment` (320% MAG dmg + silence + 5 buffs purge + MR shred all enemies) is the most punishing utility signature in the game. Very strong vs buff-heavy teams.
- Intercessor / Covenant (Martyr): self-sacrifice DPS vs life-link tank healer — symmetric.

**Verdict**: Healer specs are diverse. `Divine Judgment` and `Radiant Judgment`
are slightly above the rest but the trade-off is appropriate (Sanctifier has
better single-target cleanse; Battle Healer has lower healing throughput).

### Archer (8 specs)

- Sharpshooter / Skirmisher (Ranger): crit burst vs evasion harass — Sharpshooter Decisive Shot is on the Top 10 list (see Section 1).
- Falcon Striker / Wind Hunter (Falconer): coordinated burst vs aerial mobility — Falcon Striker Synchronized Kill (380% +50% exec + 20%/bleed) high but conditional. Wind Hunter Aerial Dominance flagged in Section 3.
- Bouncer / Striker (Ballmaster): chain bounces vs rapid combo — Striker Ultimate Combo flagged in Section 3.
- Quickshot / Deadeye (Gunslinger): rapid fire vs precision execute — Deadeye Execution Shot flagged in Section 1.

**Verdict**: Archer has the most outliers (Deadeye, Sharpshooter, Striker, Wind
Hunter). Recommend a class-wide pass to trim crit-stacking ceilings on
hit_count signatures.

### Rogue (8 specs)

- Nightstalker / Assassin (Shadowblade): anti-caster stealth vs bleed-execute — both single-target executors with slightly different identity. Both flagged.
- Debuffer / Blinker (Trickster): crippling debuffs vs hit-and-run — Blinker Dimensional Assault is the worst offender in the audit. Debuffer Total Shutdown is intentionally extreme but does not violate amplification rule.
- Cutthroat / Gunslasher (Corsair): bleed bruiser vs hybrid melee/ranged — Gunslasher Mercury Strike flagged (advanced 870% raw before crit).
- Blade Dancer / Countermaster (Duelist): multi-hit combos vs reflective tank — Countermaster Perfect Counter has Option A violation (s.5 on damage_reduction_up cap 3).

**Verdict**: Rogue has 4 of the top 10 fixes. Class-wide rebalance recommended
toward damage ceilings.

### Artisan (8 specs)

- Forgemaster / Breaker (Blacksmith): protective shields vs anti-boss — symmetric. OK.
- Plague Brewer / Reactionist (Alchemist): toxin DoT stacker vs detonation specialist — symmetric. OK.
- Battle Cook / Spice Master (Chef): premium support vs aggressive burn DPS — symmetric. Spice Master Inferno Seasoning (350% AOE + burn detonate) is on par with Magma Sage Volcanic Eruption. OK.
- Guitarist / War Drummer (Musician): support anchor vs DPS pressure — symmetric. War Drummer Targeted Cadence (marked + vulnerable) flagged for amplification monitoring (Section 2).

**Verdict**: Artisan tier3 is the cleanest class-wide. Solid balance.

---

## Top 10 Highest-Priority Changes

1. **[CRITICAL]** `skill_rogue_blinker_dimensional_assault`: Reduce 5x130% to 4x130% (520%) OR 5x100% (500%). Drop ceiling from 1170% (with crit) to ~720-900%. (Section 1)

2. **[CRITICAL]** `skill_rogue_gunslasher_mercury_strike` (advanced): Reduce scaling 290% -> 130-150%. Currently delivers signature-tier burst at advanced cooldown. (Section 3)

3. **[CRITICAL]** `skill_rogue_countermaster_perfect_counter`: Fix `damage_reduction_up stacks_to_apply: 5` to `: 3` (canonical max), OR create custom `master_counter_dr` non-stackable -25%. Description says -25% which exceeds canonical +15% cap. (Section 5)

4. **[CRITICAL]** `skill_healer_intercessor_bleeding_strike` & `martyrs_cry`: Replace `lifesteal value: 30` / `value: 50` with `stacks_to_apply: 5` (= +25% canonical) OR move to a custom non-canonical effect ID. Currently violates Option A strict. (Section 5)

5. **[HIGH]** `skill_archer_deadeye_execution_shot`: Remove `cd_reset_on_kill` OR drop `execute_bonus_percent` from 100 to 50 to reduce ~1680% effective ceiling on execute targets. (Section 1)

6. **[HIGH]** `skill_archer_sharpshooter_decisive_shot`: Replace `guaranteed_crit` with `+30% crit_chance` OR remove `execute_threshold/bonus`. Currently theoretical max ~2700% on execute, far above peer signatures. (Section 1)

7. **[HIGH]** `skill_archer_striker_ultimate_combo`: Reduce scaling_percent 100% -> 80% OR hit_count 4 -> 3. 4x100% AOE on 3 targets with crit = 828%/target = 2480% total. (Section 3)

8. **[HIGH]** `skill_archer_wind_hunter_aerial_dominance`: Reduce scaling_percent 200% -> 150% to bring total damage envelope on `all` enemies in line with Bullet Storm baseline. (Section 3)

9. **[HIGH]** `skill_mage_occ_life_drain` & `skill_mage_occ_shadow_pact` (subclass, not tier3 but backend hazard): Remove `value_per_level` on canonical `lifesteal`. Same fix needed on `skill_healer_martyr_restorative_strike`. Backend SkillResolver will fail-fast on these. (Section 5)

10. **[MEDIUM]** Documentation cleanup: Either add `replique_active` effect to `stats/status_effects.json` (currently referenced in TIER3_SKILL_CREATION.md but missing) OR remove the reference. No tier3 skill currently uses it. (Section 4)

---

## Closing Notes

- The Option A migration is **mostly successful** at the tier3 layer. Subclass-tier
skills (especially Occultist `lifesteal value_per_level`, Healer Martyr
`lifesteal value_per_level`) carry residual violations from the pre-Phase-3
era that will fail backend fail-fast.
- The amplification chain rule is **respected** across tier3. War Drummer Targeted
Cadence (+30%) is the high-water mark, well within the +100% cap.
- The custom non-stackable effect registry is **complete** for all referenced
tier3 effects. No undefined-effect runtime crashes expected.
- The principal balance risk is in **single-target multi-hit signatures with
crit stacking** (Rogue Blinker, Archer Deadeye/Sharpshooter, Rogue Gunslasher
Mercury Strike). These exceed the de-facto effective burst budget by 30-100%.
- **Class symmetry within tier3 spec pairs is excellent** for Warrior, Healer,
Artisan; less so for Archer and Rogue where multiple specs lean into the same
"crit + multi-hit + execute" archetype.
