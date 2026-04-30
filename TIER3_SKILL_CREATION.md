# Tier3 Skill Creation Guide

**Audience** : agent Claude qui crée les tier3 specs Kanarion. Self-contained, tu n'as besoin de rien d'autre que ce fichier + l'index des specs.

**Status au 2026-04-30** : 18/48 specs complets (Warrior 8/8, Mage 8/8, Healer 2/8 in progress). Restant : Healer (6), Archer (8), Rogue (8), Artisan (8) = 30 specs (150 skills).

---

## 1. Workflow standard (par batch de 2 specs = 1 subclass)

1. **Charger la subclass depuis l'index** :
   ```bash
   grep -n "\"id\": \"<subclass_id>\"" kanarion_database/classes/_classes_index.json
   ```
   Lire les 2 tier3 specs : `id`, `name`, `name_fr`, `identity`, `signature`, `tagline`, `description`, `lore`, `fissure_relation`, `souffle_usage`.

2. **Lore check** :
   - AVOID : démon, diable, infernal, pacte (sauf renommer en "Lien" / "Bond")
   - OK : Abîme, Fissures, Souffle, présence, manifestation, Le Lien (narratif)
   - Si la spec frôle le démonique (Occultist), framing : "présence pas créature/démon", "consume les ténèbres avec violence calculée"

3. **Différenciation** : lister les skills base + subclass existants pour ne pas dupliquer. Le tier3 doit pousser un ASPECT spécifique du subclass (ex: subclass = balance, tier3 = max specialization).

4. **Vérifier conflits noms de skills** :
   ```bash
   grep -n "\"name_fr\": \"<nom>\"" kanarion_database/classes/<class>/skills.json
   grep -n "\"signature\": \"<EN sig>\"" kanarion_database/classes/_classes_index.json
   ```
   Renommer signature si conflit (ex: Sorcerer "Arcane Cataclysm" → "Annihilation").

5. **Proposer 5 FR names + concepts** au user :
   ```
   | # | FR | Tier | Concept | Identité |
   ```

6. **User valide** les noms + identité. Si feedback, ajuster.

7. **EN translations + numbers + descriptions mechanical-only** (no lore intro, per user feedback).

8. **JSON dans `classes/<class>/skills.json`** sous `<subclass>.tier3.<spec_id>.skills`. 5 skills par spec.

9. **Update `classes/_classes_index.json`** : ajouter `signature_fr` après `signature` pour chaque spec. Si renommage, update `signature` aussi.

10. **Régénérer content_hash** (Python snippet ci-dessous).

11. **Validate JSON structure** :
    ```python
    python -c "import json; data = json.load(open(r'classes/<class>/skills.json', encoding='utf-8')); ..."
    ```

12. **Commit** avec message détaillé incluant les 5 skills FR/EN et notes design.

13. **Push si demandé** : `git push origin master`

---

## 2. JSON structure d'un skill tier3

```json
{
  "id": "skill_<class>_<spec_id>_<name_snake>",
  "name_en": "EN Name",
  "name_fr": "FR Nom",
  "tier": "advanced",
  "target": "enemy|ally|enemies|allies|self",
  "pattern": "single|row_3|around_radius_1|rect_2x2|rect_2x3|all|col_2|cone_2x3|...",
  "damage_type": "physical|magical|none",
  "scaling_stat": "atk|mag|def|max_hp|max_mp|...",
  "base_power": 0,
  "scaling_percent": 150,
  "percent_per_level": 7,
  "mana_cost": 10,
  "mana_cost_per_level": 1,
  "cooldown": 5.0,
  "cast_time": 1.5,
  "vfx_type": "magic_bolt|melee_slash|heal|shield|...",
  "is_signature": true,
  "description_fr": "Mécanique seule, pas d'intro lore.",
  "description_en": "Mechanical only.",
  "tags": ["damage", "aoe", "..."],
  "effects": [
    {
      "type": "buff|debuff|utility",
      "stat": "atk_up|bleed|silence|cleanse|...",
      "stacks_to_apply": 5,
      "value": 30,
      "duration": 8.0,
      "duration_per_level": 0.3,
      "scaling": "max_hp|mag|caster_max_hp",
      "target": "self|allies|enemies"
    }
  ],
  "base_class_id": "<class>",
  "subclass_id": "<subclass>",
  "tier3_id": "<spec_id>",
  "source_scope": "TIER3",
  "targeting": {
    "selection_mode": "entity|tile|self",
    "valid_target_team": "enemy|ally|self",
    "requires_line_of_sight": true,
    "bypasses_los": false,
    "requires_entity_on_target_tile": false,
    "aoe_pattern_id": "single|row_3|ring_1_center|rect_2x2|rect_2x3|all|col_2|cone_2x3|..."
  }
}
```

### Tier convention
- 4 skills `tier: "advanced"` + 1 skill `tier: "signature"` (avec `is_signature: true`)
- Le skill signature a typiquement `cast_time: 1.5-2.5s`, mana 50, CD 24-30s
- Les advanced ont mana 10-30, CD 4-18s

### Targeting team
- Skill enemy : `target: enemy/enemies`, `valid_target_team: enemy`
- Skill ally : `target: ally/allies`, `valid_target_team: ally`
- Skill self : `target: self`, `valid_target_team: self`, `selection_mode: self`

---

## 3. Conventions naming

### Skill IDs
Format : `skill_<class>_<spec_id>_<name_snake_case>`
- class : warrior, mage, healer, archer, rogue, artisan
- spec_id : tier3 spec id (bloodrage, frenzied, frostcaller, etc.)
- name : underscore-separated lowercase

Exemples :
- `skill_warrior_bloodrage_bloody_reckoning`
- `skill_mage_frostcaller_absolute_zero`
- `skill_healer_grove_warden_sylvan_fortress`

### FR-first → EN translation
- FR est source, EN est traduction
- Pas de tirets cadratins (—) dans descriptions, noms, lore
- "Mana" interdit en texte joueur, utiliser "Souffle" (FR) / "Breath" (EN)
- Pour les patterns AOE : "ligne", "zone 2x3", "diagonale" — pas les codes internes (`row_3`, `rect_2x3`)

### Signature renames si conflits
Vérifier que la signature n'existe pas déjà :
- Comme skill name dans la même classe (`grep "name_fr"`)
- Comme signature de tier3 d'une autre classe (`grep "signature"` dans index)

Cases résolus :
- Mage Sorcerer "Arcane Cataclysm" → "Annihilation" (conflit base mage)
- Mage Summoner "Eldritch Eruption" → "Émergence" (lore + brevity)
- Healer Grove Warden "Living Fortress" → "Sylvan Fortress" (conflit Forgemaster Artisan)
- Healer Covenant "Sacred Pact" → "Sacred Bond" (conflit Martyr base + lore "pacte")

---

## 4. Canonical effects (Phase 3 strict)

**Règle absolue** : pour ces effets, utiliser `stacks_to_apply: N` dans le skill effect. Pas de `value` / `value_override` / `value_per_level`. Si `stacks_to_apply > max_stacks`, le surplus est ignoré.

### Offensives (5%/stack max 5 = ±25%, sauf indication)
- `atk_up`, `atk_down`, `mag_up`, `mag_down`, `atk_percent_up` (alias atk_up)
- `damage_percent_up`, `damage_percent_down`
- `accuracy_up`, `accuracy_down`
- `crit_chance_up`, `crit_chance_down` (5%/stack max 3 = ±15%)
- `crit_damage_up`, `crit_damage_down` (10/stack max 3 = ±30 additif sur 150% base)

### Defensives
- `armor_up`, `armor_down` (5%/stack max 5)
- `magic_resist_up`, `magic_resist_down` (5%/stack max 5)
- `damage_reduction_up`, `damage_reduction_down` (5%/stack max 3 = ±15%, multiplicatif post-armor)
- `evasion_up`, `evasion_down` (3%/stack max 5 = ±15%)
- `def_up`, `def_down` (5 flat/stack max 5 = ±25 flat — PAS %)

### Tempo
- `atk_speed_up`, `atk_speed_down` (5%/stack max 5)
- `cast_speed_up`, `cast_speed_down` (5%/stack max 5)

### Support
- `heal_power_up`, `heal_power_down` (5%/stack max 5)
- `heal_received_down` (15%/stack max 3 = -45%)
- `heal_reduction` (15%/stack max 3, cap 95%)
- `crit_resistance_down` (5%/stack max 3 = -15%)
- `heal_over_time` (1% maxHP/s/stack max 3 = +3%/s, scaling=max_hp)

### Special
- `vulnerable` (5%/stack max 5 = +25% dmg taken)
- `exposed` (10%/stack max 3 = +30% dmg taken)
- `marked` (10%/stack max 1 = +10% dmg taken, refresh)
- `berserk` (5%/stack max 5, +25% dmg dealt ET dmg taken — runtime à confirmer)
- `lifesteal` (5%/stack max 5 = +25%)
- `thorns` (1 stack = DEF*0.1, max 10 — runtime à confirmer)
- `regen` (1% maxHP/s/stack max 5)

### DoTs (formules canoniques)
- `bleed` (max 3, ATK*0.3/stack/tick, physical)
- `burn` (max 3, MAG*0.25/stack/tick, magical)
- `chill` (max 3, MAG*0.1+10% slow/stack/tick)
- `poison` (max 5, 2% maxHP/stack/tick)
- `corruption` (max 5, MAG*0.15/stack/tick)
- `toxin` (max 5, MAG*0.1/stack/tick — Alchemist exclusive)

### CC (non-stackables, refresh)
- Hard : `stun`, `freeze`, `sleep`, `petrify`, `knockdown` (skip turn)
- Soft : `slow`, `silence`, `blind`, `taunt`, `root`, `fear`, `confusion`, `disarm`

Format CC effect :
```json
{ "type": "debuff", "stat": "stun", "duration": 2.0 }
```
Pas de `stacks_to_apply` sur les CC.

---

## 5. Custom non-stackable effects (named, runtime-supported)

### Drapeaux trigger (lit metadata du skill)
- `riposte_active` (Rogue Duelist) — lit `reflects_damage`, `reflects_debuffs`, `reflect_bonus_vs_challenged`
- `replique_active` (Warrior Bulwark) — parallel à riposte_active
- `en_garde_stance` (Rogue Duelist) — lit `counter_chance`, `counter_chance_vs_challenged`
- `arcane_armor_active` (Mage Battlemage — DEFERRED, à activer si backend prêt) — lit `shield_per_hit_percent_max_mp`

### Effets nommés à valeur fixe
- `iron_stance_shield` (Warrior Guardian) — -50% damage taken pendant durée
- `hunter_mark` (Archer base) — +15% dmg taken, refresh on hit, spread on kill, bypass LoS
- `steady_aim_amplifier` (Archer Ranger) — +50 crit damage
- `enchanted_blade` (Mage Spellblade) — +25% MAG sur autos, +15% magic pen, génère momentum sur autos

### Buffs custom team
- `cover` (Guardian) — porteur intercepte attaques pour ally
- `damage_transfer` (Guardian, Sentinel) — porte un % d'absorption (avec value)

### Immunités
- `cc_immune` (Lightbringer Absolution, Sacred Ward, Bulwark Last Bastion, Runeknight Runic Wall, Phalanx)
- `untargetable`, `invulnerable` (custom, peu utilisés)
- `invisible` (Shadowblade Vanish)

### Utility (one-shot)
- `cleanse` (value: N debuffs retirés)
- `purge` (value: N buffs retirés ennemi)
- `interrupt` (value: 1, interrompt cast en cours)
- `mana_steal`, `mana_drain`, `mana_lock` (custom mp manipulation)

---

## 6. Top-level scalar fields (pas des effects, à mettre direct sur le skill)

### Damage modifiers
- `armor_pen: N` — % d'armure ignorée (ex: piercing_strike 30, brise-acier 40)
- `shield_break: true` — ignore tous les boucliers
- `execute_threshold: 30` + `execute_bonus_percent: 100` — bonus si cible <X% HP
- `bonus_condition: "hp_below_50"` + `bonus_damage_percent: 40` — bonus conditionnel cast (rage_slash)
- `damage_per_missing_hp_percent: 2` + `max_missing_hp_bonus: 100` — scaling avec HP manquant du caster (zealous_strike, acharnement)
- `damage_per_bleed_stack: 15` — bonus damage par stack bleed sur cible (talon_rend, hemorrhage)
- `damage_per_bounce: 8` — escalation chain skills (endless_volley)
- `damage_per_hit_bonus: 8` — escalation multi-hit (déferlement)
- `marked_bonus_percent: 50` — bonus si target marqué (precise_shot, master_card, royal_flush)

### Consume mechanics
- `consumes_charges: true` + `max_charges_consumed: 3` + `bonus_per_charge: 25` (mage signatures)
- `consumes_bleed_stacks: true` (reaver execution) — consomme bleed après damage
- `detonates_toxin: true` + `detonate_damage_per_stack: 30` (alchemist catalyze)
- `detonates_burn: true` + `detonate_damage_per_stack: 30` (spice_master, magma_sage volcanic eruption)
- `detonates_marks: true` (reactionist detonate)
- `cd_reset_on_kill: true` (headshot) — reset CD si kill

### Multi-hit
- `hit_count: N` (weapon_combo, double_tap, frenzied skills, reaver) — N hits par cast
- `each_hit_can_crit: true` — chaque hit roll crit séparément

### Reflect
- `reflects_damage: 75` — % dmg renvoyé à l'attaquant (avec riposte_active/replique_active)
- `reflects_debuffs: true` — renvoie aussi les debuffs
- `thorn_reflect_percent: 20` — sur shields (vine_shield, grove warden)

### Marks
- `mark_refresh_on_hit: true` (hunter_mark)
- `mark_spread_on_kill: true` (hunter_mark spread sur kill)
- `mark_ignore_los: true` (mark_target rogue)

### Resources
- `generates_charges: 1` (mage filler/basic/standard)
- `generates_momentum: 1` (spellblade arcane_slash)
- `bonus_damage_per_momentum: 5` (arcane_cleave, saturated_strike)

### Pets / Summons
- `summons: ["mob_id"]` (rare, summon mechanic)
- (Si tu vois besoin d'un pet, vérifier subclass identity avant d'introduire)

### RNG (random buffs/debuffs from pool)
- `random_buffs_min: 1`, `random_buffs_max: 4`, `random_buffs_min_at_level_5: 2`
- `buff_pool: [{ "buff": "atk_up", "value": 25 }, ...]` — pool entries
- `random_debuffs_min/max`, `debuff_pool` (idem côté debuff)
- Les `value` dans pool entries sont EXEMPTÉS du Phase 3 strict (special case validate_skills.py)

### Conditional bonus (object form)
- `conditional_bonus: { "condition": "caster_below_hp", "hp_threshold": 50, "lifesteal_bonus_percent": 30 }` (restorative_strike)
- `conditional_bonus: { "condition": "caster_below_hp_after", "hp_threshold": 30, "shield_bonus_percent": 50 }` (sacred_pact)

---

## 7. Class-specific resources

### Mage : Arcane Charges
- Filler/basic/standard : `generates_charges: 1`
- Strong/signature : `consumes_charges: true` + `max_charges_consumed: 3` + `bonus_per_charge: 25` (% damage)
- Bonus alternative : `bonus_stacks_per_charge: 1` (elemental_storm) — +1 stack DoT par charge

Tous les tier3 Mage suivent ce pattern, sauf 1 skill par spec qui peut être hors-ressource (le strong typiquement).

### Mage Spellblade : Arcane Momentum (en plus des Charges)
- Filler/basic : `generates_momentum: 1`
- Auto-attaques pendant `enchanted_blade` actif : génèrent momentum
- Strong/signature : `bonus_damage_per_momentum: 5` (sans consume explicite, max 10 stacks)

### Berserker Warrior : pas de resource
Mais on stack canonical (atk_up, lifesteal, berserk).

### Healer : pas de resource
Skills sur cooldown pur. Différenciation via tier (advanced vs signature) et durée.

### Archer Cardmaster (Mage subclass) : RNG pools
- `random_buffs_min/max` + `buff_pool` (lucky_draw pattern)
- `random_debuffs_min/max` + `debuff_pool` (bad_luck pattern)

### Archer / Rogue (TBD) : marked / hunter_mark / assassin_mark / unstable_mark
- Existing : `hunter_mark` (Archer base), `marked` canonical, `unstable` (Reactionist), `reactive` (Reactionist)
- TODO design : Sharpshooter, Falconer Master, etc.

### Artisan : tier3 existants en LEGACY format
- Forgemaster + Breaker (Blacksmith), Plague Brewer + Reactionist (Alchemist), Battle Cook + Spice Master (Chef), Guitarist + War Drummer (Musician)
- TOUS utilisent le format `buff: "X", buff_value: 25, buff_duration: 12.0` (pré-Option A)
- À MIGRER vers Option A `effects[]` avec `stacks_to_apply` quand on touche à Artisan tier3

---

## 8. Lore guards (par classe)

### Warrior
- Berserker : "marqué par les Abysses" OK, mais "fureur calculée par la douleur", pas démoniaque
- Guardian : "rempart", "mur", pure martial
- Weaponmaster : pure technique, "discipline", aucune interaction lore avec Fissures
- Warlord : leader, stratège, "Le Lien" via "ensemble invincibles"

### Mage
- Elementalist : refuse les Fissures, élements naturels
- Occultist : étudie l'Abîme — **lore prudent** : "consume les ténèbres avec violence calculée", "pas une créature, pas un démon, une présence"
- Cardmaster : RNG, probabilités, neutre lore
- Spellblade : fusion martial-arcane, neutre

### Healer
- Lifewarden : nature, vie, "racines", "forces vitales"
- Lightbringer : lumière, lumière purificatrice, sacré
- Cantor : voix, hymnes, paroles anciennes, résurrection
- Martyr : sacrifice de soi, "donner sa vie pour ceux qu'on protège", Le Lien

### Archer
- Ranger : pure technique, patience, précision
- Falconer : lien avec rapace
- Ballmaster : trajectoires, rythme
- Gunslinger : vitesse, instinct

### Rogue
- Shadowblade : ombres, stealth
- Trickster : tromperie, illusions
- Corsair : pirate, butin, "sale"
- Duelist : honneur, riposte, 1v1

### Artisan
- Blacksmith : forge, métal, marteau
- Alchemist : poisons, distillation, toxines
- Chef : cuisine, feu de cuisine, épices
- Musician : son, harmonie, dissonance

---

## 9. Anti-patterns à éviter

### Skill design
- ❌ Cloner un skill existant avec valeurs +10% (paresseux)
- ❌ Filler ultra-chargé en effets multiples (filler doit être SIMPLE)
- ❌ Signature qui répète exactement la mécanique du subclass signature (doit POUSSER l'identité, pas dupliquer)
- ❌ Mélanger damage on enemy + buff on allies dans le même filler (utiliser `dual_effect` seulement pour skills lourds, pas filler)
- ❌ Tier3 standard plus puissant que subclass strong (cohérence power level)

### Mécanique
- ❌ Réintroduire `value` ou `value_per_level` sur un effet canonical_grid (Phase 3 strict, CI fail)
- ❌ Hardcoder un effect_id sans vérifier dans `stats/status_effects.json` (combat service refuse de démarrer)
- ❌ `stacks_to_apply` hors range [1, max_stacks] (CI fail)
- ❌ Créer un nouvel effect_id quand un canonical fait l'affaire (préférer `damage_percent_up` plutôt qu'un custom "damage_amp")
- ❌ Skip `target: "self"` sur effects qui ciblent le caster dans un skill ciblant un ennemi (par défaut, l'effet va sur la cible enemy)

### Lore
- ❌ Démon, diable, infernal, pacte (sauf renommer en Lien)
- ❌ Em dashes (—) dans descriptions ou réponses

### Process
- ❌ Oublier de regen content_hash après modif JSON (CI fail)
- ❌ Commit le hash avant un changement final (toujours regen DERNIER avant commit)
- ❌ Commit auto-fix artisan sans valider (changes mécaniques cachés)

---

## 10. Validation & commit workflow

### Régen content_hash (Python, pas le shell script qui crash sur Windows CRLF)
```python
python -c "
import hashlib, json, os, datetime
os.chdir(r'C:\Users\Charl\Documents\Kanarion Online\kanarion_database')
exclude_files = {'./_meta/version.json', './_meta/statistics.json', './_meta/index.json', './_meta/changelog.json', './_meta/ideas_to_integrate.json'}
exclude_dirs = {'.git', 'kanarion-editor', 'scripts'}
json_files = []
for root, dirs, files in os.walk('.'):
    dirs[:] = [d for d in dirs if d not in exclude_dirs]
    for f in files:
        if f.endswith('.json'):
            path = os.path.join(root, f).replace(os.sep, '/')
            if path not in exclude_files:
                json_files.append(path)
json_files.sort()
content = b''
for fp in json_files:
    content += (fp + '\n').encode()
    with open(fp, 'rb') as fh:
        content += fh.read()
h = hashlib.sha256(content).hexdigest()
with open('_meta/version.json', 'r', encoding='utf-8') as f:
    v = json.load(f)
v['content_hash'] = f'sha256:{h}'
v['last_updated'] = datetime.date.today().isoformat()
with open('_meta/version.json', 'w', encoding='utf-8') as f:
    json.dump(v, f, indent=2, ensure_ascii=False)
    f.write('\n')
print(f'Updated content_hash: sha256:{h}')
"
```

### Validate JSON structure
```python
python -c "
import json
with open(r'classes/<class>/skills.json', 'r', encoding='utf-8') as f:
    data = json.load(f)
sub = data['subclass_skills']['<subclass>']
tier3 = sub.get('tier3', {})
print(f'<subclass> tier3 specs: {list(tier3.keys())}')
for spec_id, spec in tier3.items():
    print(f'\n  {spec_id}:')
    for s in spec.get('skills', []):
        print(f'    - {s[\"id\"]} ({s[\"name_fr\"]} / {s[\"name_en\"]}, tier={s[\"tier\"]})')
"
```

### Commit
```bash
git add _meta/version.json classes/_classes_index.json classes/<class>/skills.json
git commit -m "data(<class>): add <Spec1> + <Spec2> tier3 specs (10 skills)

Implements both <Subclass> tier3 specializations using <patterns>. Zero/N new mechanics introduced.

<Spec1> (<Nom FR>) — <identity>:
- <Skill1 / Skill1 EN> (advanced, <role>): <stats summary>
...
- <Sig FR / Sig EN> (signature): <stats summary>, Xs cast

<Spec2> (<Nom FR>) — <identity>:
- ...

<Notes design éventuelles, conflits résolus, mécaniques deferred>

Updates _classes_index.json with signature_fr '<...>' and '<...>'."
git push origin master
```

---

## 11. Tier3 specs catalog (status au 2026-04-30)

### ✅ COMPLET
- **Warrior** : Berserker (Bloodrage, Frenzied) + Guardian (Bulwark, Sentinel) + Weaponmaster (Hammer Lord, Dual Axe Reaver) + Warlord (Commander, Dreadlord)
- **Mage** : Elementalist (Frostcaller, Magma Sage) + Occultist (Sorcerer, Summoner) + Cardmaster (Arcane Dealer, Fate Gambler) + Spellblade (Battlemage, Runeknight)

### ⏳ EN COURS
- **Healer** : Lifewarden (Druidic Healer ✅, Grove Warden ✅) + Lightbringer (Sanctifier, Battle Healer) + Cantor (Requiem, Choirmaster) + Martyr (Intercessor, Covenant)

### ❌ TODO
- **Archer** : Ranger (Sharpshooter, ?) + Falconer (?, ?) + Ballmaster (?, ?) + Gunslinger (?, ?)
- **Rogue** : Shadowblade + Trickster + Corsair + Duelist (4 × 2 = 8 specs)
- **Artisan** : Blacksmith + Alchemist + Chef + Musician — **les tier3 existent déjà en JSON LEGACY** (`buff_value` format), à migrer Option A puis enrichir si nécessaire

---

## 12. Tier3 specs design synthesis (cas existants pour inspiration)

### Patterns Spec design

| Pattern Spec | Exemple | Skills typiques |
|---|---|---|
| Sustain bruiser | Bloodrage | filler lifesteal, AOE bleed, self-buff atk+lifesteal+DR, big dmg scaling missing HP, signature execute |
| Multi-hit speed | Frenzied | filler 2-hit, AOE 2-hit ring, self atk_speed buff, multi-hit escalation, signature 3-hit AOE |
| Self-fortress | Bulwark | filler dmg + armor self, AOE taunt + dmg_red, max armor stance, riposte counter, signature shield + cc_immune |
| Team protection | Sentinel | filler ally shield, AOE shield + DR row, single damage_transfer + cleanse, multi-ally damage_transfer, signature team shield + cc_immune |
| Heavy single hit | Hammer Lord | filler heavy hit + armor_down, AOE stun + armor_down, atk + dmg buff stance, big single + armor_pen + stun, signature AOE stun + armor crush |
| Multi-hit bleed | Reaver | filler 2-hit + bleed, AOE 2-hit + bleed, atk + dmg + def_down stance, single + bleed scaling, signature + consume_bleed_stacks + execute |
| Team buffer | Commander | filler row buff, AOE row 2 stats buff, single max 4-stat buff, all team 2-stat, signature all team 5-stat max |
| Fear debuffer | Dreadlord | filler atk_down, AOE row fear + atk_down, AOE max debuff, single big + dual debuff, signature all fear + max debuffs |

### Numbers benchmark

| Tier | Damage range | Mana | CD | Cast |
|------|-------------|------|----|----|
| Filler advanced | 90-150% (single) ; 130-180% (AOE) | 8-12 | 4-5s | — |
| Basic advanced | 180-240% (AOE) ; 200% (single) | 16-24 | 8-12s | 1.0s |
| Standard advanced | 200-280% (single) | 18-26 | 12-16s | — / 1.0s |
| Strong advanced | 280-340% (single) ; 280% (AOE) | 26-30 | 12-18s | — / 1.5s |
| Signature | 350-420% (AOE) ; 380% (single+adj) | 45-50 | 22-30s | 1.5-2.5s |

### Heal range (Healer tier3)
- Filler : 80% MAG single
- Basic : 150% MAG row_3 ou HoT s.3
- Standard : 200% MAG col_2 + cleanse
- Strong : 250% MAG single + buffs
- Signature : 250% MAG all + HoT s.3 + cleanse + DR (~10s duration)

### Shield range (Healer / Defensive tier3)
- Filler : 8% maxHP single ally
- Basic : 12-18% maxHP row_3
- Standard : 15-25% maxHP single
- Strong : 25% maxHP row + cc_immune
- Signature : 30% maxHP all + DR + cc_immune

---

## 13. Examples concrets

### Skill canonical buff (Stone Form, Bulwark standard)
```json
{
  "id": "skill_warrior_bulwark_stone_form",
  "name_en": "Stone Form",
  "name_fr": "Forme de Pierre",
  "tier": "advanced",
  "target": "self",
  "pattern": "single",
  "damage_type": "none",
  "base_power": 0,
  "mana_cost": 22,
  "mana_cost_per_level": 2,
  "cooldown": 18.0,
  "vfx_type": "shield",
  "description_fr": "+25% armure, +25% résistance magique et +15% réduction de dégâts sur le lanceur pendant 10s. -25% vitesse d'attaque (coût).",
  "description_en": "+25% armor, +25% magic resist and +15% damage reduction on the caster for 10s. -25% attack speed (cost).",
  "tags": ["buff", "self", "armor_up", "magic_resist", "damage_reduction", "tank"],
  "effects": [
    { "type": "buff", "stat": "armor_up", "stacks_to_apply": 5, "duration": 10.0 },
    { "type": "buff", "stat": "magic_resist_up", "stacks_to_apply": 5, "duration": 10.0 },
    { "type": "buff", "stat": "damage_reduction_up", "stacks_to_apply": 3, "duration": 10.0 },
    { "type": "debuff", "stat": "atk_speed_down", "stacks_to_apply": 5, "duration": 10.0, "target": "self" }
  ],
  "base_class_id": "warrior",
  "subclass_id": "guardian",
  "tier3_id": "bulwark",
  "source_scope": "TIER3",
  "targeting": {
    "selection_mode": "self",
    "valid_target_team": "self",
    "requires_line_of_sight": true,
    "bypasses_los": false,
    "requires_entity_on_target_tile": false,
    "aoe_pattern_id": "single"
  }
}
```

### Skill multi-hit (Onslaught, Frenzied strong)
```json
{
  "id": "skill_warrior_frenzied_onslaught",
  "name_en": "Onslaught",
  "name_fr": "Déferlement",
  "tier": "advanced",
  "target": "enemy",
  "pattern": "single",
  "damage_type": "physical",
  "scaling_stat": "atk",
  "base_power": 0,
  "scaling_percent": 75,
  "percent_per_level": 4,
  "hit_count": 4,
  "damage_per_hit_bonus": 8,
  "each_hit_can_crit": true,
  "mana_cost": 26,
  "mana_cost_per_level": 3,
  "cooldown": 12.0,
  "vfx_type": "melee_slash",
  "description_fr": "Inflige 75% ATK dégâts physiques en 4 frappes. +8% dégâts par frappe successive. Chaque frappe peut critiquer.",
  "description_en": "Deals 75% ATK physical damage in 4 hits. +8% damage per successive hit. Each hit can crit.",
  "tags": ["damage", "melee", "multi_hit", "escalating"],
  ...
}
```

### Skill consume + execute (Bloody Reckoning, Bloodrage signature)
```json
{
  "id": "skill_warrior_bloodrage_bloody_reckoning",
  "tier": "signature",
  "target": "enemies",
  "pattern": "cone_2x3",
  "damage_type": "physical",
  "scaling_stat": "atk",
  "scaling_percent": 380,
  "percent_per_level": 11,
  "execute_threshold": 25,
  "execute_bonus_percent": 50,
  "cd_reset_on_kill": true,
  "mana_cost": 45,
  "mana_cost_per_level": 4,
  "cooldown": 22.0,
  "cast_time": 1.5,
  "is_signature": true,
  "effects": [
    { "type": "debuff", "stat": "bleed", "stacks_to_apply": 2, "duration": 6.0 },
    { "type": "utility", "stat": "lifesteal", "value": 100 }
  ],
  ...
}
```

### Skill mage charge consume (Absolute Zero)
```json
{
  "id": "skill_mage_frostcaller_absolute_zero",
  "tier": "signature",
  "scaling_percent": 200,
  "percent_per_level": 13,
  "consumes_charges": true,
  "max_charges_consumed": 3,
  "bonus_per_charge": 25,
  "cast_time": 2.5,
  "effects": [
    { "type": "debuff", "stat": "freeze", "duration": 2.0 },
    { "type": "debuff", "stat": "chill", "stacks_to_apply": 3, "duration": 6.0 }
  ],
  ...
}
```

### Skill RNG pool (Big Bet, Fate Gambler strong)
```json
{
  "id": "skill_mage_fate_gambler_big_bet",
  "tier": "advanced",
  "scaling_percent": 320,
  "random_debuffs_min": 2,
  "random_debuffs_max": 3,
  "debuff_pool": [
    { "debuff": "atk_down", "value": 25 },
    { "debuff": "mag_down", "value": 25 },
    { "debuff": "atk_speed_down", "value": 25 },
    { "debuff": "blind", "value": 25 },
    { "debuff": "slow", "value": 25 },
    { "debuff": "damage_reduction_down", "value": 15 }
  ],
  ...
}
```

---

## 14. Si tu hésites

- **Skill paraît déjà puissant** → vérifier vs subclass standard/strong existants. Tier3 advanced ≈ subclass strong en power
- **Mécanique pas listée ici** → vérifier `EFFECTS_INTEGRATION_GUIDE.md` (root) pour les détails backend
- **Lore borderline** → demander au user, vaut mieux clarifier que livrer un skill qui doit être renommé
- **Naming conflict** → grep + propose 2-3 alternatives au user

---

**Document maintenu collaboratively. Mettre à jour quand de nouveaux patterns émergent ou que des effets sont ajoutés au runtime.**
