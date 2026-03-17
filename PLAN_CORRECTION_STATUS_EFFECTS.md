# Plan de Correction — Status Effects System

**Date:** 2026-03-17
**Auteur:** Equipe dev — valide par CTO
**Scope:** `kanarion_database/stats/status_effects.json` (source canonique unique), `kanarion_back/server-combat/`, `kanarion_front/`
**Statut:** VALIDE CTO — 2026-03-17

---

## Contexte

L'audit complet du systeme de status effects a revele que le DoT de Smite (`holy_dot`) ne fonctionne pas, et que le probleme est systemique : ecarts entre les donnees JSON, le code C++ backend, et le frontend Godot.

**Decision d'architecture validee (CTO) :**
- **Source canonique unique** : `stats/status_effects.json`
- **Suppression totale** de `config/status_effects.json` (deja fait)
- **Interdiction** d'ajouter un nouvel effet ailleurs que dans `stats/status_effects.json`
- **Regle de contenu** : Un effet `impl: "todo"` peut exister dans le registre, mais ne doit etre reference par **aucun skill actif**. Toute reference skill → effect absent ou `impl: todo` = **echec de chargement**, y compris en prod
- **Aucun fallback, aucun merge, aucune tolerance** : skill invalide = contenu refuse au chargement

---

## Etat des lieux — Chiffres cles

| Metrique | Valeur |
|----------|--------|
| Effects definis dans `stats/status_effects.json` | 99 |
| Effects references par au moins 1 skill | 36 |
| Effects `impl: done` et utilises | 32 |
| Effects `impl: todo` mais utilises par des skills actifs | **4 (BLOQUANT)** |
| Effects references par des skills mais **non definis** | **4 (CRITIQUE)** |
| Effects definis mais jamais references | 63 |
| Cas speciaux hardcodes dans le C++ | 16 IDs |
| Champs legacy dans le skill loader non convertis | 5+ formats |

---

## Etape 1 — Remplacer le loader backend par `stats/status_effects.json`

### 1.1 — Audit des points de chargement (recherche globale)

Recherche exhaustive dans tous les repos sur :
- `config/status_effects.json`
- `status_effects.json`
- `dot_balance`
- `burn`, `bleed`, `poison`, `holy_dot`

**Points trouves :**

| Fichier | Reference | Statut |
|---------|-----------|--------|
| `kanarion_back/server-combat/src/status/status_manager.cpp:15` | `stats/status_effects.json` | ✅ Deja correct |
| `kanarion_back/server-combat/src/status/status_manager.cpp:17` | Fallback `status_effects.json` (racine) | A SUPPRIMER |
| `kanarion_front/scripts/data/db/data_db.gd:140` | `config/status_effects.json` | ✅ Corrige → `stats/status_effects.json` |
| `kanarion_front/scripts/data/db/data_db.gd:147` | `stats/status_effects.json` | ✅ Deja correct |
| `kanarion_database/config/game.json:488` | `config/status_effects_config.json` | ✅ Corrige → `stats/status_effects.json` |
| `kanarion_database/CLAUDE.md` | Reference a `config/status_effects.json` | ✅ Corrige |
| Docs : `06_global_recap.txt`, `REFACTO_PLAN_DB_SERVER_2026-03.md` | References historiques | A mettre a jour |

### 1.2 — Corriger le loader backend

```
Fichier : server-combat/src/status/status_manager.cpp
Fonction : load_from_directory() — lignes 13-18

Actuel :
  fs::path status_file = fs::path(path) / "stats" / "status_effects.json";
  if (!fs::exists(status_file)) {
      status_file = fs::path(path) / "status_effects.json";  // Fallback
  }

Correction :
  fs::path status_file = fs::path(path) / "stats" / "status_effects.json";
  if (!fs::exists(status_file)) {
      spdlog::critical("[STATUS] FATAL: {} not found — server cannot start without status effects", status_file.string());
      return false;  // Boot failure, pas de fallback silencieux
  }
```

**Regle :** Au boot, le serveur charge UN SEUL fichier. Si ce fichier manque ou est invalide → **boot failure**. Plus de fallback silencieux.

### 1.3 — Supprimer toute logique de merge config + stats

Verifier qu'aucun code ne tente de fusionner deux sources. Le registre est construit a partir d'un seul fichier.

---

## Etape 2 — Migrer les donnees utiles de `config/` vers `stats/`

### 2.1 — Supprimer la dependance a `dot_balance`

L'ancien `config/status_effects.json` contenait une section `dot_balance` avec poison, bleed et burn — mais pas holy_dot. Cette information doit vivre dans `stats/status_effects.json`.

**Etat actuel dans `stats/status_effects.json` :**

| DOT | Defini ? | `runtime` bloc ? | `impl` | Formule exploitable ? |
|-----|----------|-------------------|--------|-----------------------|
| `burn` | ✅ | ✅ (tick_damage, tick_rate, vfx_type) | done | ✅ |
| `poison` | ✅ | ✅ | done | ✅ |
| `bleed` | ✅ | ✅ | done | ✅ |
| `holy_dot` | ✅ | ❌ MANQUANT | **todo** | ❌ Formule textuelle seulement |
| `curse_dot` | ✅ | ❌ MANQUANT | **todo** | ❌ Formule textuelle seulement |
| `corruption` | ✅ | ❌ MANQUANT | **todo** | ❌ |
| `toxin` | ✅ | ❌ MANQUANT | **todo** | ❌ |

**Action :** Ajouter un bloc `runtime` exploitable a chaque DOT/HOT. Schema cible :

```json
"holy_dot": {
  "impl": "done",
  "runtime": {
    "tick_damage": "value",
    "tick_rate": 1.0,
    "vfx_type": "holy_glow",
    "scaling_stat": "mag",
    "scaling_percent": 0.10,
    "scaling_behavior": "ramp",
    "ramp_per_tick": 0.05,
    "damage_ignores_defense": false
  }
}
```

### 2.2 — Table complete des blocs `runtime` a ajouter

| Effect ID | `scaling_stat` | `scaling_percent` | `scaling_behavior` | Notes |
|-----------|---------------|-------------------|-------------------|-------|
| `holy_dot` | `mag` | 0.10 | `ramp` (+0.05/tick) | Degats croissants, duree fixe, non refreshable |
| `curse_dot` | `mag` | 0.20 | `flat` | + explosion 50% MAG a expiration |
| `corruption` | `target_max_hp` | 0.03 | `flat` | % HP, stackable |
| `toxin` | `mag` | 0.20 | `flat` | Variante poison alchimiste |
| `heal_over_time` | `target_max_hp` | 0.02 | `flat` | Standard HOT |
| `mana_regen` | `target_max_mp` | 0.02 | `flat` | Regen mana |
| `mana_drain` | `target_max_mp` | 0.03 | `flat` | Drain mana |

### 2.3 — Geler le schema canonique

Chaque effet dans `stats/status_effects.json` DOIT avoir au minimum :

| Champ | Obligatoire | Description |
|-------|-------------|-------------|
| `id` (= cle JSON) | ✅ | Identifiant unique |
| `category` (= section parente) | ✅ | dot, hot, stat_modifiers, tempo, control, defensive, immunity, aggro, special |
| `impl` | ✅ | `"done"` ou `"todo"` |
| `stacking` | ✅ | `"stackable"`, `"refresh"`, `"unique"`, `"independent"` |
| `max_stacks` | ✅ | Nombre max de stacks |
| `name_fr` / `name_en` | ✅ | Noms localises |
| `polarity` | ✅ | `"buff"` ou `"debuff"` |
| `runtime` | ✅ si periodique | Bloc avec tick_rate, scaling, vfx |
| `tick_interval` | ✅ si DOT/HOT | Intervalle en secondes |
| `damage_type` | ✅ si DOT | `"physical"`, `"magical"`, `"none"` |
| `duration_modifiable` | Optionnel | Indique si extendable/reducible |

**Regle :** Plus de logique dupliquee entre sections concurrentes. Plus de "cet effet existe seulement dans config".

---

## Etape 3 — Validation croisee skills ↔ status

### 3.1 — Script de validation CI (`scripts/validate_status_effects.py`)

```python
# Pour chaque skill dans classes/*/skills.json et skills/monster_skills.json :
#   Pour chaque effect dans skill.effects[] :
#     - effect.stat DOIT exister dans stats/status_effects.json
#     - effect.stat DOIT avoir impl == "done"
#     - Verifier coherence type/categorie
#
# Sortie : ERREUR si un ID manque ou est "todo"
# Exit code 1 = echec bloquant
```

### 3.2 — Fail-fast au boot du serveur combat

```cpp
// Fichier : server-combat/src/content/content_loader.cpp ou combat_host.cpp
// Apres chargement des skills et du registre status :

bool content_valid = true;
for (const auto& [skill_id, skill] : skill_registry.all_skills()) {
    for (const auto& effect_id : skill.applied_effects) {
        if (!status_manager.has_effect(effect_id)) {
            spdlog::critical("[CONTENT] Skill '{}' references unknown status effect '{}' — FATAL",
                              skill_id, effect_id);
            content_valid = false;
        }
    }
}
if (!content_valid) {
    spdlog::critical("[CONTENT] Invalid game content — server refuses to start");
    return false;  // Meme en prod : contenu refuse = serveur ne demarre pas
}
```

**Regle stricte (dev ET prod) :**
- `effect_id` absent du registre = **contenu refuse, serveur ne demarre pas**
- Doublon d'ID dans le JSON = **contenu refuse**
- `impl: "todo"` reference par un skill actif = **contenu refuse**
- Champ obligatoire manquant = **contenu refuse**
- Aucune tolerance : un serveur avec un gameplay partiellement casse est pire qu'un serveur arrete

### 3.3 — Etat actuel du croisement

**4 effects `impl: todo` utilises par des skills actifs (BLOQUANT) :**

| Effect ID | Categorie | Utilise par | Action |
|-----------|-----------|-------------|--------|
| `holy_dot` | dot | `skill_healer_divine_wrath` (Smite) | → `impl: "done"` + `runtime` |
| `heal_over_time` | hot | `skill_healer_regeneration` | → `impl: "done"` + `runtime` |
| `fear` | control | `skill_mage_terrify` | → `impl: "done"` — comportement fige : **stun avec tag `fear`** (voir 4.2) |
| `revealed` | special | `skill_archer_track_prey` | → `impl: "done"` + `runtime` |

**4 effect IDs references mais non definis (CRITIQUE) :**

| Effect ID | Nature | Utilise par | Action |
|-----------|--------|-------------|--------|
| `cleanse` | Action (retire debuffs) | Healer, Artisan | Ajouter categorie `special`, `is_instant: true` |
| `purge` | Action (retire buffs) | Archer, Mage, Monsters | Idem |
| `mana_steal` | Action (vole mana) | Mage, Rogue | Idem |
| `mana_restore` | Action (regen mana) | Artisan | Idem |

**Decision CTO (tranchee) :** Ces 4 mecaniques sont des actions instantanees, **pas des status persistants**. Elles ne passent PAS par le StatusManager :

| Mecanique | Traitement | Lieu |
|-----------|-----------|------|
| `cleanse` | Utility instantanee (retire N debuffs) | `SkillExecutor` via `utility_effects` |
| `purge` | Utility instantanee (retire N buffs) | `SkillExecutor` via `utility_effects` |
| `mana_steal` | Skill effect instantane (vole X mana) | `SkillExecutor` via `utility_effects` |
| `mana_restore` | Skill effect instantane (rend X mana) | `SkillExecutor` via `utility_effects` |

**Consequence :** Ces IDs ne doivent PAS etre dans `stats/status_effects.json`. Les skills qui les utilisent doivent declarer `type: "utility"` dans leurs `effects[]`, et le `SkillExecutor` les traite directement (deja partiellement fait pour `cleanse_count`/`purge_count`). La validation croisee CI doit exclure les effects de type `utility` du check contre le registre status.

---

## Etape 4 — Finaliser les effects `todo` et corriger le runtime

### 4.1 — Implementer `holy_dot` proprement

**Checklist specifique :**
- [ ] Passer `impl: "todo"` → `impl: "done"` dans `stats/status_effects.json`
- [ ] Formule canonique : `tick_n = MAG * (0.10 + 0.05 * tick_index)`
- [ ] Categorie : `dot`
- [ ] Tick a 1 seconde (`tick_interval: 1.0`)
- [ ] Degats croissants par tick
- [ ] Non refreshable (`duration_modifiable: false`)
- [ ] Non extensible
- [ ] `damage_type: "magical"`
- [ ] `stacking: "unique"`, `max_stacks: 1`
- [ ] Bloc `runtime` complet
- [ ] Test dedie obligatoire

### 4.2 — Finaliser les 4 autres effects prioritaires

| Effect | Checklist |
|--------|-----------|
| `heal_over_time` | `impl: done`, `runtime` avec `scaling_stat: "target_max_hp"`, `scaling_percent: 0.02`, tick 1s |
| `fear` | `impl: done` — **Decision design figee : stun avec tag `fear`**. Meme comportement mecanique que stun (empeche d'agir), mais tag distinct pour : (1) immunites specifiques futures, (2) VFX/animation differente, (3) passifs qui reagissent au fear. Le C++ mappe `fear → StatusType::STUN` avec `tags: ["fear"]`. Pas de mouvement aleatoire — trop complexe pour le grid combat et sans gain gameplay clair. |
| `revealed` | `impl: done`, `runtime` avec `flags: ["reveals_invisible", "prevents_invisible"]` |
| `curse_dot` | `impl: done` (si skill l'utilise), `runtime` avec MAG * 0.20 + explosion |

### 4.3 — Corriger le fallback DOT dans le C++

**Bug :** Quand `tick_value == 0`, le code derive 30% ATK du caster. Faux pour les DOTs magiques.

```
Fichier : server-combat/src/status/status_manager.cpp
Fonction : apply_effect() — lignes ~1190-1208

Correction :
  if (effect_data.type == StatusType::DOT && instance.value == 0) {
      if (effect_data.damage_type == "magical" || effect_data.damage_type == "holy") {
          instance.value = max(1, static_cast<int32_t>(caster_stats.magic_power * 0.25f));
      } else {
          instance.value = max(1, static_cast<int32_t>(caster_stats.attack_power * 0.3f));
      }
  }
```

### 4.4 — Corriger le `value_override` pour DOT/HOT

**Bug :** Le `value_override` transmis par le skill est ignore pour les DOT/HOT.

```
Fichier : server-combat/src/status/status_manager.cpp
Fonction : apply_effect() — apres ligne ~1188

Ajouter :
  if ((effect_data.type == StatusType::DOT || effect_data.type == StatusType::HOT)
      && value_override > 0 && effect_data.stat_mod_type == StatModType::NONE) {
      instance.value = value_override;
  }
```

### 4.5 — Corriger les formules DOT dans `process_periodic_effects()`

| DOT | Formule design | Code C++ actuel | Correction |
|-----|---------------|-----------------|------------|
| `burn` | MAG * 0.25/tick/stack | Fallback ATK * 0.3 | Ajouter : `value = caster.magic_power * 0.25 * stacks` |
| `poison` | 2% max HP/tick/stack | Fallback ATK * 0.3 | Ajouter : `value = target.max_hp * 0.02 * stacks` |
| `bleed` | ATK * 0.3/tick/stack | Fallback ATK * 0.3 | Expliciter le cas (OK par hasard) |
| `holy_dot` | MAG * escalating | Escalation OK, base fausse | Fix via 4.3 (fallback MAG) |
| `corruption` | 3% max HP | Code special OK | ✅ Deja correct |
| `curse_dot` | MAG * 0.2 + explosion | Explosion OK, base fausse | Fix via 4.3 |

---

## Etape 5 — Nettoyer runtime + parsing legacy

### 5.1 — Supprimer les hypotheses "seuls burn/bleed/poison existent"

Rechercher et corriger tout code qui suppose :
- "Les DoT viennent de `dot_balance`"
- "holy_dot est special mais pas encore branche"
- "Si un effet inconnu arrive, on ignore"

**Regle saine :**
- Effet inconnu = **erreur**
- Effet connu = traite via le registre
- Plus de fallback silencieux

### 5.2 — Migrer les skills vers un format d'effets unique

**Formats legacy a deprecier progressivement dans le skill loader :**

| Champ legacy | Conversion cible |
|-------------|-----------------|
| `applies_burn: true` | `applied_effects: [{ effect_id: "burn", ... }]` |
| `burn_stacks: 2` | → `stacks: 2` dans applied_effects |
| `burn_duration: 4.0` | → `duration_ms: 4000` dans applied_effects |
| `mana_regen_percent: X` | `applied_effects: [{ effect_id: "mana_regen", ... }]` |
| `mana_regen_duration: X` | → `duration_ms` dans applied_effects |
| `hot_percent: X` | `applied_effects: [{ effect_id: "heal_over_time", ... }]` |
| `buff: "xxx"` | `applied_effects: [{ effect_id: "xxx", type: "buff" }]` |
| `debuff: "xxx"` | `applied_effects: [{ effect_id: "xxx", type: "debuff" }]` |
| `effect: "xxx"` | `applied_effects: [{ effect_id: "xxx" }]` |

**Pendant migration :**
- Compat legacy acceptee
- Log de depreciation obligatoire a chaque conversion

**Apres migration :**
- Suppression des anciens champs dans le loader
- Un seul format autorise : `effects[]` avec `{ type, stat, value, duration, ... }`

### 5.3 — Eliminer les `if (effect_id == "xxx")` dans le C++

**Phase 1 (hotfix) :** Ajouter les cas speciaux burn/poison (necessaire immediatement)

**Phase 2 (refacto propre) :** Remplacer par lecture du champ `runtime.scaling_behavior` :

```cpp
// Cible — plus de if-chain par effect_id
switch (effect_data.scaling_behavior) {
    case ScalingBehavior::FLAT:
        value = derive_from_scaling_stat(effect_data, instance, entities);
        break;
    case ScalingBehavior::RAMP:
        value = derive_from_scaling_stat(effect_data, instance, entities);
        value *= (1.0f + effect_data.ramp_per_tick * tick_count);
        break;
    case ScalingBehavior::PERCENT_TARGET_MAX:
        value = target_max * effect_data.scaling_percent * instance.stacks;
        break;
}
```

**Champs a ajouter dans `StatusEffectData` (status_effect.hpp) :**

```cpp
struct StatusEffectData {
    // ... existant ...
    std::string scaling_stat;           // "atk", "mag", "target_max_hp", "target_max_mp"
    float scaling_percent = 0.0f;
    ScalingBehavior scaling_behavior = ScalingBehavior::FLAT;
    float ramp_per_tick = 0.0f;
    bool damage_ignores_defense = false;
    std::string damage_type;            // "physical", "magical", "none"
    std::vector<std::string> flags;     // ["blocks_healing", "reveals_invisible", etc.]
    std::vector<StatModEntry> stat_mods; // Multi-stat effects (remplace les 5 hardcodes)
};
```

### 5.4 — Extraire les 5 multi-stat effects hardcodes

Remplacer les `if (effect_id == "all_stats")` / `"berserk"` / `"predation"` etc. par un array `stat_mods[]` dans le JSON :

```json
"berserk": {
  "stat_mods": [
    { "stat": "atk", "op": "add_percent", "value_per_stack": 10 },
    { "stat": "damage_taken", "op": "add_percent", "value_per_stack": 10 }
  ]
}
```

### 5.5 — Remplacer les string-contains checks par `flags[]`

```json
"heal_block": { "flags": ["blocks_healing"] },
"heal_reduction": { "flags": ["reduces_healing"], "heal_reduction_percent": 50 },
"mana_lock": { "flags": ["blocks_mana_regen"] },
"shield_block": { "flags": ["blocks_shields"] },
"revealed": { "flags": ["reveals_invisible", "prevents_invisible"] },
"cc_immune_zone": { "flags": ["aoe_cc_immunity"] },
"invisible": { "flags": ["untargetable_auto"] }
```

---

## Etape 6 — Supprimer physiquement `config/status_effects.json`

### 6.1 — Suppression (DEJA FAIT)

- [x] `git rm config/status_effects.json` dans `kanarion_database/`
- [x] Mise a jour `data_db.gd` → charge `stats/status_effects.json`
- [x] Mise a jour `config/game.json` → reference `stats/status_effects.json`
- [x] Mise a jour `CLAUDE.md`
- [x] Regeneration content hash

### 6.2 — Verifications restantes

- [x] Supprimer les references dans `_meta/suggestions/06_global_recap.txt`
- [ ] Supprimer les references dans `REFACTO_PLAN_DB_SERVER_2026-03.md`
- [ ] Verifier que le submodule `kanarion-meta/` est a jour dans `kanarion_back/` et `kanarion_front/`
- [ ] Verifier que `kanarion_back/content/` n'a PAS ete mis a jour (copie obsolete a supprimer — voir 6.3)

### 6.3 — Supprimer `kanarion_back/content/` (copie obsolete)

Le serveur charge depuis `kanarion-meta/` (submodule). Le repertoire `content/` est une copie ancienne divergente qui cree de la confusion.

**Action :** `git rm -r content/` dans `kanarion_back/`

### 6.4 — Front sur la meme verite

- [x] `data_db.gd` : `status_effects_config` charge `stats/status_effects.json`
- [ ] Verifier que `_build_server_status_effect()` dans `CombatEventRouter` resout correctement depuis `stats/status_effects.json` :
  - Nom localise (name_fr/name_en)
  - Icone (resolution auto via effect_id)
  - Categorie (dot/hot/buff/debuff/control)
  - Tooltip
- [ ] Verifier qu'aucun code client n'a de mini-definition parallele d'effects
- [ ] Verifier qu'aucun nom diverge entre front et back

### 6.5 — Icones manquantes

Verifier que chaque effect utilise par un skill actif a une icone dans `res://assets/icons/status/` :

| Icone | Statut |
|-------|--------|
| `holy_dot.png` | A verifier |
| `heal_over_time.png` | A verifier |
| `fear.png` | A verifier |
| `revealed.png` | A verifier |
| `cleanse.png` | A verifier (si affiche) |
| `mana_steal.png` | A verifier |
| `purge.png` | A verifier |
| `mana_restore.png` | A verifier |

---

## Etape 7 — Garde-fous CI

### 7.1 — Test : `config/status_effects.json` ne doit pas reapparaitre

```yaml
# Dans .github/workflows/validate.yml
- name: Guard against config/status_effects.json resurrection
  run: |
    if [ -f config/status_effects.json ]; then
      echo "ERROR: config/status_effects.json must not exist — canonical source is stats/status_effects.json"
      exit 1
    fi
```

### 7.2 — Test : aucun code ne reference l'ancien chemin

```bash
# Grep dans tous les repos — doit retourner 0 match (hors docs historiques)
grep -r "config/status_effects" --include="*.cpp" --include="*.hpp" --include="*.gd" --include="*.py"
# Resultat attendu : 0 match
```

### 7.3 — Test : tous les effect_id de skills existent dans `stats/`

Script `validate_status_effects.py` (voir Etape 3.1) integre dans la CI.

### 7.4 — Test de non-regression : le boot serveur charge correctement

Test d'integration qui :
1. Demarre le serveur combat
2. Verifie que le log contient `[STATUS] Loaded XX status effects from stats/status_effects.json`
3. Verifie que le log ne contient PAS `Effect 'xxx' not found in registry`
4. Verifie que le log ne contient PAS `Zero status effects loaded`

---

## Tests indispensables

### Tests de chargement

| Test | Assertion |
|------|-----------|
| Registre charge `stats/status_effects.json` | Nombre d'effects > 0 |
| Doublon d'ID | = erreur fatale |
| Champ obligatoire manquant | = erreur fatale |
| `impl: "todo"` utilise par skill | = erreur fatale |

### Tests de validation croisee

| Test | Assertion |
|------|-----------|
| Skill avec effect absent | = erreur fatale |
| Skill avec effect `impl: todo` | = erreur fatale |
| Legacy field sans conversion | = warning (puis erreur apres migration) |

### Tests runtime — matrice des effects periodiques

| # | Effect | Test | Resultat attendu |
|---|--------|------|------------------|
| 1 | `holy_dot` | Healer cast Smite | DOT applique, degats croissants tick 1 < tick 2 < tick 3, base = MAG |
| 2 | `burn` | Mage cast Inferno | DOT = MAG * 0.25 * stacks par tick |
| 3 | `poison` | Rogue applique | DOT = 2% max HP * stacks par tick |
| 4 | `bleed` | Warrior Heavy Strike | DOT = ATK * 0.3 * stacks par tick |
| 5 | `corruption` | Mage Occultist | DOT = 3% max HP * stacks par tick |
| 6 | `curse_dot` | Mage Occultist | DOT + explosion 50% MAG a expiration |
| 7 | `heal_over_time` | Healer Regeneration | HOT applique, soin par tick |
| 8 | `mana_regen` | Healer Cantor | Mana regen par tick |

### Tests runtime — CC et buffs/debuffs

| # | Effect | Test | Resultat attendu |
|---|--------|------|------------------|
| 9 | `stun` | Warrior Shield Bash | CC, cible ne peut pas agir |
| 10 | `silence` | Mage Mana Lock | CC, cible ne peut pas cast |
| 11 | `fear` | Mage Terrify | CC applique |
| 12 | `taunt` | Warrior Taunting Shout | Cible forcee d'attaquer le caster |
| 13 | `magic_resist_down` | Smite debuff | MR reduite |
| 14 | `shield` | Healer Holy Shield | Shield absorb correct |
| 15 | `cc_immune` | Healer Absolution | Immunite CC active |
| 16 | `revealed` | Archer Track Prey | Cible ne peut pas devenir invisible |
| 17 | `cleanse` | Healer Purify | Retire N debuffs |
| 18 | `purge` | Monster Dispel Magic | Retire N buffs |
| 19 | `damage_reduction_up` | Healer Sanctuary | DR applique |
| 20 | `marked` | Archer Hunter Mark | Cible marquee |

### Tests de non-regression

| Test | Assertion |
|------|-----------|
| Suppression `config/status_effects.json` ne casse pas le boot | ✅ |
| Aucun code ne tente de charger l'ancien fichier | ✅ |
| Chaque DOT produit `value > 0` au premier tick | ✅ |
| Expiration fonctionne pour tous les effects periodiques | ✅ |
| Stacks respectent `max_stacks` | ✅ |

---

## Ordre d'execution recommande (valide CTO)

| Etape | Contenu | Prerequis |
|-------|---------|-----------|
| **Etape 1** | Remplacer le loader backend, supprimer fallback | Aucun |
| **Etape 2** | Migrer donnees config → stats, enrichir `runtime`, geler schema | Etape 1 |
| **Etape 3** | Validation croisee skills ↔ status, fail-fast au boot | Etape 2 |
| **Etape 4** | Finaliser holy_dot + 4 todo, corriger DOT fallback/formules | Etape 2 |
| **Etape 5** | Nettoyer runtime, deprecier parsing legacy, eliminer hardcodes | Etape 4 |
| **Etape 6** | Suppression physique (fait), nettoyage front, icones | Etape 3 |
| **Etape 7** | Garde-fous CI | Etape 6 |

---

## Resume des fichiers a modifier

| Fichier | Action | Etape |
|---------|--------|-------|
| `kanarion_database/stats/status_effects.json` | 4 todo→done, 4 mecaniques, enrichir runtime, geler schema | 2, 4 |
| `kanarion_back/server-combat/src/status/status_manager.cpp` | Supprimer fallback, fix DOT MAG/ATK, fix value_override, formules burn/poison, puis data-driven | 1, 4, 5 |
| `kanarion_back/server-combat/src/status/status_effect.hpp` | Ajouter scaling_stat, scaling_behavior, ramp_per_tick, damage_type, flags, stat_mods | 5 |
| `kanarion_back/server-combat/src/skills/skill_executor.cpp` | Verifier value_override DOT, ajouter validation croisee | 3, 4 |
| `kanarion_back/server-combat/src/content/content_loader.cpp` | Deprecier legacy fields, log warnings | 5 |
| `kanarion_database/scripts/validate_status_effects.py` | Nouveau — validation croisee CI | 3 |
| `kanarion_front/scripts/data/db/data_db.gd` | ✅ Deja fait — source unique | — |
| `kanarion_back/content/` | Supprimer (copie obsolete) | 6 |
| `.github/workflows/validate.yml` | Garde-fous CI | 7 |

---

## Validation CTO

> Le plan est valide. On garde `stats/status_effects.json` comme unique source canonique, sans fallback ni merge. Toute reference skill → effect absent ou `impl: todo` doit faire echouer le chargement. Priorite immediate : finaliser holy_dot, heal_over_time, fear, revealed, fixer le runtime des DoT/HoT, puis verrouiller le tout avec validation croisee et CI.

---

## Metriques de succes

- [ ] 0 effect reference par un skill mais absent du registre
- [ ] 0 effect `impl: todo` utilise par un skill actif
- [ ] 0 DOT avec `value = 0` au premier tick
- [ ] Chaque DOT utilise la bonne stat de scaling (MAG ou ATK, pas le fallback generique)
- [ ] `config/status_effects.json` supprime et CI empeche sa reapparition
- [ ] Aucun code runtime ne reference `config/status_effects`
- [ ] Test CI cross-reference skills ↔ status_effects passe a 100%
- [ ] Les 20 tests de la matrice de validation passent
- [ ] Boot serveur = 1 seul fichier charge, 0 fallback silencieux
- [ ] Frontend et backend consomment la meme source canonique
