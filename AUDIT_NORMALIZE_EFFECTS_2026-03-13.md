# Audit Normalisation effects[] — 2026-03-13

## Contexte

Les skills joueurs utilisent un mélange de champs custom (`applies_bleed_stacks`, `mana_steal_percent`, `shield_scaling_percent`, etc.) et d'entrées `effects[]` standardisées. Le backend C++ parse certains de ces champs, en ignore d'autres. L'objectif est un pipeline unique : **tout passe par `effects[]`**.

---

## État du parser backend (content_loader.cpp)

### Ce que le serveur parse AUJOURD'HUI

| Champ JSON | Stockage C++ | Exécution | Status |
|------------|-------------|-----------|--------|
| `effects[]` (array complet) | `applied_effects[]` + `effect_values{}` + `effect_durations_sec{}` + `effect_scalings{}` | `StatusManager::apply_effect()` | **OK — pipeline principal** |
| `heal_scaling_percent` | `skill.heal_scaling` (float) | `DamageCalculator::calculate_healing()` | **OK** |
| `hot_percent` + `hot_duration` | `effect_values["_hot_percent"]` + `effect_durations_sec["_hot"]` | Appliqué comme `"heal_over_time"` status | **OK** |
| `shield_scaling_percent` + `shield_duration` | `effect_values["_shield_scaling_percent"]` + `effect_durations_sec["_shield"]` | Appliqué comme `"shield"` status | **OK** |
| `self_shield_scaling_percent` | `effect_values["_self_shield_scaling_percent"]` | Shield sur le caster | **OK** |
| `applies_bleed_stacks` | Ajoute `"bleed"` à `applied_effects` | `StatusManager::apply_effect("bleed")` | **OK — legacy shorthand** |
| `effect` (string) | Ajoute l'ID à `applied_effects` | `StatusManager::apply_effect(id)` | **OK — legacy shorthand** |
| `buff` (string, sauf "heal") | Ajoute l'ID à `applied_effects` | `StatusManager::apply_effect(id)` | **OK — legacy shorthand** |
| `debuff` (string) | Ajoute l'ID à `applied_effects` | `StatusManager::apply_effect(id)` | **OK — legacy shorthand** |

### Ce que le serveur NE PARSE PAS (ignoré silencieusement)

| Champ JSON | Skills concernés | Impact |
|------------|-----------------|--------|
| `applies_burn_stacks` | 10+ skills (elem, artisan) | **Burn jamais appliqué** |
| `applies_toxin_stacks` | 5 skills (alchemist) | **Toxin jamais appliqué** |
| `applies_corruption_stacks` | 1 skill (occultist) | **Corruption jamais appliquée** |
| `applies_chill_stacks` | 2 skills (elementalist) | **Chill jamais appliqué** |
| `generates_charges` / `consumes_charges` | 15+ skills (mage) | **Système de charges mort** |
| `generates_momentum` | 1 skill (spellblade) | **Momentum mort** |
| `mana_steal_percent` / `mana_steal_flat` | 3 skills | **Vol de mana mort** |
| `lifesteal_percent` (per-skill) | 3 skills | **Lifesteal per-skill mort** |
| `execute_threshold` / `execute_bonus_percent` | 3 skills | **Execute mort** |
| `hit_count` | 2 skills | **Multi-hit mort** |
| `chain_bounces` / `damage_per_bounce` | 5 skills (ballmaster) | **Bounce mort** |
| `ignore_los` | 15 skills | **LoS bypass mort** |
| `purge_count` | 4 skills | **Purge mort** |
| `cleanse_count` | 6 skills | **Cleanse mort** |
| `interrupts_cast` | 2 skills | **Interrupt mort** |
| `stealth_bonus_damage` | 1 skill | **Stealth bonus mort** |
| `armor_pen` / `shield_break` | 3 skills | **Pen/break mort** |
| `guaranteed_crit` / `cd_reset_on_kill` | 1 skill | **Crit garanti mort** |
| `double_hit_chance` | 2 skills | **Double hit mort** |
| `counter_chance` / `reflects_damage` | 2 skills | **Counter/reflect mort** |
| `resurrect` | 1 skill | **Résurrection morte** |
| `conditional_bonus` (object) | 5 skills | **Bonus conditionnels morts** |
| `random_buffs_*` / `random_debuffs_*` | 3 skills (cardmaster) | **Random pools morts** |
| `damage_per_adjacent_ally` | 1 skill (artisan) | **Synergie adjacence morte** |
| `bonus_damage_per_debuff` | 2 skills | **Scaling par debuff mort** |
| `dot_heals_lowest_ally` | 1 skill (martyr) | **DoT→heal mort** |
| `drain_to_all_allies` | 1 skill (martyr) | **Drain→heal mort** |
| `redirect_to` | 1 skill (trickster) | **Redirect mort** |
| `sacrifice_hp_percent` | 1 skill (martyr) | **Self-damage mort** |

**Conclusion : la majorité des mécaniques de sous-classes ne fonctionnent PAS côté serveur.**

---

## Plan de migration

### Principe

Trois catégories de champs custom :

1. **Migrables vers `effects[]` existant** — Le champ custom est un raccourci pour un effet que `StatusManager` sait déjà appliquer. Migration = ajouter l'entrée dans `effects[]` + supprimer le champ custom.

2. **Nécessitent un nouveau type d'effet** — La mécanique existe conceptuellement mais `StatusManager` ne la gère pas. Migration = définir le nouveau type dans `status_effects.json` + ajouter le parsing + ajouter l'exécution C++.

3. **Métadonnées de skill (pas des effets)** — Le champ modifie le comportement du skill lui-même (pas un status effect sur une entité). Ces champs restent top-level dans le JSON mais doivent être parsés par `content_loader.cpp` et stockés dans `SkillData`.

---

### Catégorie 1 — Migration simple vers effects[] (pas de changement C++)

Ces champs ont un équivalent direct dans le système `effects[]` actuel. Le backend les parsera automatiquement.

#### 1A. DoT stacks → effects[] debuff

Le serveur sait déjà appliquer `"bleed"` via `applies_bleed_stacks`. Il suffit d'étendre le même pattern à burn, poison, toxin, corruption, chill.

| Champ custom | Migration effects[] | Skills |
|-------------|-------------------|--------|
| `applies_bleed_stacks: N` | `{"type":"debuff","stat":"bleed","value":N,"duration":X}` | 9 skills |
| `applies_burn_stacks: N` | `{"type":"debuff","stat":"burn","value":N,"duration":X}` | 10 skills |
| `applies_toxin_stacks: N` | `{"type":"debuff","stat":"toxin","value":N,"duration":X}` | 5 skills |
| `applies_corruption_stacks: N` | `{"type":"debuff","stat":"corruption","value":N,"duration":X}` | 1 skill |
| `applies_chill_stacks: N` | `{"type":"debuff","stat":"chill","value":N,"duration":X}` | 2 skills |

**Prérequis :** vérifier que `burn`, `toxin`, `corruption`, `chill` existent dans `stats/status_effects.json` comme DoT. Si non, les ajouter.

**27 skills total.**

#### 1B. Buff/debuff stat → effects[] buff/debuff

Champs qui sont déjà des buff/debuff simples mais écrits en custom.

| Champ custom | Migration effects[] | Skills |
|-------------|-------------------|--------|
| `buff_value_atk: 30` | `{"type":"buff","stat":"atk","value":30,"duration":X}` | berserker_frenzy |
| `buff_value_speed: 20` | `{"type":"buff","stat":"speed","value":20,"duration":X}` | berserker_frenzy |
| `buff_scaling_percent: 15` | `{"type":"buff","stat":"atk","value":15,"duration":X}` | berserker_bloodlust |
| `defense_reduction: 25` | `{"type":"debuff","stat":"def","value":-25,"duration":X}` | duelist_expose_weakness |

**4 skills.**

#### 1C. HoT → effects[] (déjà parsé par le backend via `_hot_percent`)

Le backend parse déjà `hot_percent` + `hot_duration` et les stocke dans `effect_values`. La migration consiste à les écrire sous forme `effects[]` pour cohérence, ET adapter le parser pour lire les deux formats.

| Champ custom | Migration effects[] | Skills |
|-------------|-------------------|--------|
| `hot_percent: X, hot_duration: Y` | `{"type":"buff","stat":"heal_over_time","value":X,"duration":Y,"scaling":"max_hp"}` | ~10 skills |

**~10 skills (healer, artisan).**

#### 1D. Shield → effects[] (déjà parsé par le backend via `_shield_*`)

Même logique que HoT.

| Champ custom | Migration effects[] | Skills |
|-------------|-------------------|--------|
| `shield_scaling_percent: X, shield_duration: Y` | `{"type":"buff","stat":"shield","value":X,"duration":Y,"scaling":"mag"}` | ~10 skills |
| `self_shield_scaling_percent: X` | `{"type":"buff","stat":"shield","value":X,"duration":Y,"scaling":"mag","target":"self"}` | 2 skills |

**~12 skills.**

**Total Catégorie 1 : ~53 skills — migration JSON uniquement, pas de nouveau code C++ requis (sauf éventuellement adapter le parser pour lire `effects[]` au lieu des champs custom).**

---

### Catégorie 2 — Nouveaux types d'effets (changement C++ requis)

Ces mécaniques n'existent pas encore dans `StatusManager`. Il faut :
1. Définir le type dans `stats/status_effects.json`
2. Ajouter le parsing dans `content_loader.cpp`
3. Ajouter l'exécution dans `room.cpp` / `skill_executor.cpp` / `status_manager.cpp`

#### 2A. Cleanse (retirer debuffs alliés)

**Mécanique :** retire N debuffs d'un allié.
**Format effects[] proposé :**
```json
{"type": "utility", "stat": "cleanse", "value": 2}
```
**C++ requis :** `StatusManager::cleanse(entity, count)` — itère les status debuff, retire les N plus anciens.
**Skills :** skill_healer_purify (2), skill_healer_lifewarden_regrowth (1), skill_healer_lightbringer_cleanse_wave (2), skill_healer_cantor_sacred_ward (2), skill_warrior_guardian_protect_ally (1). **6 skills.**

#### 2B. Purge (retirer buffs ennemis)

**Mécanique :** retire N buffs d'un ennemi.
**Format effects[] proposé :**
```json
{"type": "utility", "stat": "purge", "value": 2}
```
**C++ requis :** `StatusManager::purge(entity, count)` — itère les status buff, retire les N plus anciens.
**Skills :** skill_warrior_warlord_weakening_roar (2), skill_mage_occ_soul_rend (1), skill_archer_gunslinger_suppressing_fire (1). **3 skills.**

#### 2C. Buff Steal (voler buffs ennemis)

**Mécanique :** vole N buffs d'un ennemi et les applique sur soi.
**Format effects[] proposé :**
```json
{"type": "utility", "stat": "steal_buff", "value": 2}
```
**C++ requis :** `StatusManager::steal_buff(source, target, count)`.
**Skills :** skill_rogue_trickster_grand_swindle (2), skill_rogue_corsair_raid (99=all). **2 skills.**

#### 2D. Mana Steal

**Mécanique :** vole du mana à la cible (flat ou %).
**Format effects[] proposé :**
```json
{"type": "utility", "stat": "mana_steal", "value": 15, "scaling": "flat"}
{"type": "utility", "stat": "mana_steal", "value": 30, "scaling": "percent"}
```
**C++ requis :** Réduire MP cible, augmenter MP caster.
**Skills :** skill_mage_arcane_siphon (30%), skill_rogue_corsair_plunder (15 flat), skill_rogue_corsair_raid (10%). **3 skills.**

#### 2E. Mana Regen (buff)

**Mécanique :** restore du mana sur la durée.
**Format effects[] proposé :**
```json
{"type": "buff", "stat": "mana_regen", "value": 2, "duration": 8.0, "scaling": "max_mp"}
```
**C++ requis :** Tick de mana regen dans `StatusManager::tick()`.
**Skills :** skill_healer_cantor_hymn_of_vigor, skill_artisan_tool_support. **2 skills.**

#### 2F. Mana Restore (instant)

**Mécanique :** restore du mana instantanément sur un allié.
**Format effects[] proposé :**
```json
{"type": "utility", "stat": "mana_restore", "value": 60, "scaling": "mag"}
```
**C++ requis :** Augmenter MP cible de `caster.mag * value%`.
**Skills :** skill_artisan_tool_support. **1 skill.**

#### 2G. Lifesteal (per-skill)

**Mécanique :** le caster se soigne d'un % des dégâts infligés par CE skill.
**Format effects[] proposé :**
```json
{"type": "utility", "stat": "lifesteal", "value": 30}
```
**C++ requis :** Après `DamageCalculator::calculate()`, heal caster de `damage * value%`. Différent du lifesteal stat (qui s'applique à toutes les attaques).
**Skills :** skill_mage_occ_life_drain (30%), skill_mage_occ_shadow_pact (25%), skill_healer_martyr_restorative_strike (60%). **3 skills.**

#### 2H. Resurrection

**Mécanique :** ramène un allié mort avec X% HP.
**Format effects[] proposé :**
```json
{"type": "utility", "stat": "resurrect", "value": 40}
```
**C++ requis :** Vérifie que la cible est morte, remet HP à `max_hp * value%`, retire l'état mort.
**Skills :** skill_healer_cantor_requiem (40%). **1 skill.**

#### 2I. Interrupt

**Mécanique :** interrompt le cast en cours de la cible.
**Format effects[] proposé :**
```json
{"type": "utility", "stat": "interrupt"}
```
**C++ requis :** Annule le cast en cours de la cible (`Room::cancel_cast(target)`).
**Skills :** skill_archer_gunslinger_quickshot. **1 skill.**

**Total Catégorie 2 : ~22 skills, 9 nouveaux types d'effets à implémenter en C++.**

---

### Catégorie 3 — Métadonnées de skill (restent top-level, parsing C++ requis)

Ces champs modifient le COMPORTEMENT du skill, pas un status effect sur une entité. Ils restent dans le JSON comme champs top-level mais doivent être parsés par `content_loader.cpp` et stockés dans `SkillData`.

#### 3A. ignore_los (boolean)

**Mécanique :** le skill bypass la Line of Sight.
**JSON :** `"ignore_los": true` (reste tel quel)
**C++ requis :** Ajouter `bool ignore_los = false` dans `SkillData`. Parser dans `content_loader.cpp`. Check dans `Room::validate_action()`.
**Skills :** 15 skills (archer, rogue, artisan).

#### 3B. hit_count (multi-hit)

**Mécanique :** le skill frappe N fois.
**JSON :** `"hit_count": 3` (reste tel quel)
**C++ requis :** Ajouter `int hit_count = 1` dans `SkillData`. Loop dans `apply_skill_effects()`.
**Skills :** skill_warrior_weaponmaster_weapon_combo (3), skill_archer_gunslinger_double_tap (2). **2 skills.**

#### 3C. execute_threshold / execute_bonus_percent

**Mécanique :** bonus de dégâts si la cible est sous X% HP.
**JSON :** `"execute_threshold": 30, "execute_bonus_percent": 100` (reste tel quel)
**C++ requis :** Ajouter dans `SkillData`. Check dans `DamageCalculator`.
**Skills :** 3 skills (berserker, ranger, shadowblade).

#### 3D. conditional_bonus (object)

**Mécanique :** bonus conditionnel (HP seuil, status sur cible, etc.).
**JSON :** `"conditional_bonus": {"condition": "target_has_hot", "heal_bonus_percent": 40}` (reste tel quel)
**C++ requis :** Parser l'objet, évaluer la condition pendant l'exécution.
**Skills :** 5 skills (healer martyr, lifewarden, spellblade, corsair).

#### 3E. chain_bounces / damage_per_bounce / can_bounce_same_target

**Mécanique :** projectile qui rebondit entre cibles.
**JSON :** `"chain_bounces": 4, "damage_per_bounce": 5, "can_bounce_same_target": true` (reste tel quel)
**C++ requis :** Loop de bounce dans `apply_skill_effects()` avec Manhattan distance. **Partiellement implémenté** dans `Room::validate_action()` pour le targeting chain/bounce.
**Skills :** 5 skills (ballmaster).

#### 3F. generates_charges / consumes_charges / generates_momentum

**Mécanique :** système de resource secondaire (charges arcanes, momentum).
**JSON :** `"generates_charges": 1, "consumes_charges": true, "max_charges_consumed": 3` (reste tel quel)
**C++ requis :** Nouveau composant ECS `ChargesComponent`. Parsing + exécution.
**Skills :** 15+ skills (toutes les sous-classes mage).

#### 3G. double_hit_chance

**Mécanique :** chance de frapper deux fois.
**JSON :** `"double_hit_chance": 0.5` (reste tel quel)
**C++ requis :** RNG roll dans `apply_skill_effects()`.
**Skills :** 2 skills (cardmaster).

#### 3H. random_buffs / random_debuffs pools

**Mécanique :** applique N buffs/debuffs aléatoires depuis un pool.
**JSON :** `"random_buffs_min": 1, "random_buffs_max": 4, "buff_pool": [...]` (reste tel quel)
**C++ requis :** RNG selection dans `apply_skill_effects()`.
**Skills :** 3 skills (cardmaster).

#### 3I. armor_pen / shield_break / ignore_shields

**Mécanique :** modificateurs de la pipeline de dégâts.
**JSON :** `"armor_pen": 30, "shield_break": 50` (reste tel quel)
**C++ requis :** Override dans `DamageCalculator`.
**Skills :** 3 skills (warlord, ranger, shadowblade).

#### 3J. guaranteed_crit / cd_reset_on_kill / stealth_bonus_damage

**Mécanique :** modificateurs spéciaux de skill.
**JSON :** reste tel quel.
**C++ requis :** Parsing + logique dans `DamageCalculator` / `Room`.
**Skills :** 2 skills (ranger headshot, shadowblade backstab).

#### 3K. counter_chance / reflects_damage / reflects_debuffs

**Mécanique :** contre-attaque / réflexion.
**JSON :** reste tel quel.
**C++ requis :** Event listener dans le tick loop (quand l'entité subit des dégâts).
**Skills :** 2 skills (duelist).

#### 3L. sacrifice_hp_percent / drain_to_all_allies / dot_heals_lowest_ally

**Mécanique :** skills de Martyr (self-damage → heal allies).
**JSON :** reste tel quel.
**C++ requis :** Logique dans `apply_skill_effects()`.
**Skills :** 3 skills (martyr).

#### 3M. damage_per_bleed_stack / bonus_damage_per_debuff / damage_per_missing_hp_percent

**Mécanique :** scaling de dégâts conditionnel.
**JSON :** reste tel quel.
**C++ requis :** Calcul dans `DamageCalculator`.
**Skills :** 5 skills.

#### 3N. is_signature / cast_interruptible

**Mécanique :** métadonnées de skill.
**JSON :** reste tel quel.
**C++ requis :** `is_signature` déjà dans tags. `cast_interruptible` = default pour tout cast_time > 0.
**Skills :** ~10 skills. **Pas de changement nécessaire** — déjà géré par les tags et le système de cast.

**Total Catégorie 3 : ~55 skills, 13 features C++ à implémenter (3A-3M).**

---

## Ordre de migration

### Phase 1 — Migration JSON pure (0 changement C++)
**Objectif :** Aligner le JSON sur le format `effects[]` pour tout ce que le backend parse déjà.

| Étape | Quoi | Skills | Effort |
|-------|------|--------|--------|
| 1.1 | DoT stacks → `effects[]` debuff | 27 | Faible — format identique à `bleed` existant |
| 1.2 | Buff/debuff simples → `effects[]` | 4 | Faible |
| 1.3 | HoT → `effects[]` | 10 | Moyen — adapter le parser pour lire `effects[]` OU `hot_percent` |
| 1.4 | Shield → `effects[]` | 12 | Moyen — même adaptation que HoT |

**~53 skills. Résultat : le JSON est propre, le backend continue de fonctionner.**

### Phase 2 — Nouveaux types d'effets (C++ requis)
**Objectif :** Implémenter les mécaniques utilitaires manquantes.

| Étape | Quoi | Skills | Effort C++ |
|-------|------|--------|------------|
| 2.1 | Cleanse | 6 | Faible — itérer + retirer debuffs |
| 2.2 | Purge | 3 | Faible — itérer + retirer buffs |
| 2.3 | Buff Steal | 2 | Moyen — purge + apply sur caster |
| 2.4 | Mana Steal | 3 | Moyen — modifier MP des deux entités |
| 2.5 | Mana Regen/Restore | 2 | Faible — tick ou instant MP |
| 2.6 | Lifesteal per-skill | 3 | Faible — déjà un lifesteal stat, juste override |
| 2.7 | Resurrect | 1 | Moyen — gérer l'état mort |
| 2.8 | Interrupt | 1 | Faible — cancel_cast existe déjà |

**~22 skills. 9 features C++, la plupart faibles.**

### Phase 3 — Métadonnées de skill (C++ requis, plus complexe)
**Objectif :** Implémenter les mécaniques de skill qui modifient le comportement du skill lui-même.

| Priorité | Quoi | Skills | Effort C++ |
|----------|------|--------|------------|
| **HAUTE** | ignore_los (3A) | 15 | Faible — 1 bool dans SkillData |
| **HAUTE** | execute_threshold (3C) | 3 | Faible — 1 check dans DamageCalc |
| **HAUTE** | armor_pen/shield_break (3I) | 3 | Faible — override dans DamageCalc |
| **MOYENNE** | hit_count (3B) | 2 | Moyen — loop dans apply_effects |
| **MOYENNE** | conditional_bonus (3D) | 5 | Moyen — évaluation de conditions |
| **MOYENNE** | chain_bounces (3E) | 5 | Moyen — partiellement fait |
| **MOYENNE** | charges/momentum (3F) | 15+ | **Élevé** — nouveau composant ECS |
| **MOYENNE** | sacrifice/drain (3L) | 3 | Moyen |
| **MOYENNE** | damage scaling (3M) | 5 | Moyen — DamageCalc |
| **BASSE** | double_hit (3G) | 2 | Faible |
| **BASSE** | random pools (3H) | 3 | Moyen — RNG pool |
| **BASSE** | guaranteed_crit (3J) | 2 | Faible |
| **BASSE** | counter/reflect (3K) | 2 | **Élevé** — event listener |

**~55 skills. 13 features C++, effort variable.**

---

## Résumé global

| Phase | Skills | Changement C++ | Priorité |
|-------|--------|---------------|----------|
| Phase 1 — JSON pur | 53 | Aucun (ou adaptation parser minor) | **IMMÉDIAT** |
| Phase 2 — Utility effects | 22 | 9 features (faible-moyen) | **HAUTE** |
| Phase 3 — Skill metadata | 55 | 13 features (faible-élevé) | **MOYENNE** |
| **Total** | **~130 skills** | **22 features C++** | — |

### Dépendances

```
Phase 1 (JSON)  ←  pas de dépendance, faisable maintenant
     ↓
Phase 2 (Utility effects)  ←  requiert que le parser lise effects[] "utility" type
     ↓
Phase 3 (Skill metadata)  ←  requiert refactor SkillData + DamageCalculator
     ↓
Système de charges mage (3F)  ←  le plus gros chantier, nouveau composant ECS
```

### Risque zéro

Les champs custom restent dans le JSON pendant la migration. Le backend continue de parser ceux qu'il connaît (`applies_bleed_stacks`, `hot_percent`, etc.). On ajoute les `effects[]` en PARALLÈLE, puis on nettoie les champs custom une fois le nouveau parsing confirmé.

---

## Vérifications à faire dans status_effects.json

Avant la Phase 1, vérifier que ces IDs existent dans `stats/status_effects.json` :

| ID | Catégorie | Existe ? |
|----|-----------|----------|
| `bleed` | dot | ✅ Oui |
| `burn` | dot | ✅ Oui |
| `poison` | dot | ✅ Oui |
| `toxin` | special | ✅ Oui (⚠️ dans "special", pas "dot" — vérifier si le tick DoT s'applique) |
| `corruption` | special | ✅ Oui (⚠️ même remarque que toxin) |
| `chill` | special | ✅ Oui (⚠️ même remarque) |
| `heal_over_time` | hot | ✅ Oui |
| `shield` | defensive | ✅ Oui |

**⚠️ Attention :** `toxin`, `corruption` et `chill` sont dans la catégorie `"special"`, pas `"dot"`. Le `StatusManager` C++ traite les DoT via `StatusType::DOT` — vérifier que les effets `"special"` tickent correctement comme des DoT. Sinon, les déplacer vers `"dot"` dans `status_effects.json`.

---

## Impact attendu

- **Phase 1 :** Le JSON est propre et cohérent. Le pipeline `effects[]` est le standard unique. Plus de confusion entre champs custom et effects[].
- **Phase 2 :** Les mécaniques utilitaires (cleanse, purge, steal, mana, resurrect) fonctionnent. ~20% des sous-classes deviennent jouables.
- **Phase 3 :** Les mécaniques avancées (execute, bounces, charges) fonctionnent. 100% des sous-classes sont jouables.
- **Système de charges (3F) :** Le mage est la classe la plus impactée. Sans les charges, 4/4 sous-classes mage ont des skills cassés.
