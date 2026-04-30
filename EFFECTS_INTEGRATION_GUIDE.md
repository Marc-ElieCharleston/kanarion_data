# Effects Integration Guide — tier3 specs et nouveaux effects

**Statut :** rédigé 2026-04-30, vivant. À enrichir au fil des intégrations tier3.
**Contexte :** Phase 3 Option A est merged. Le contrat strict est appliqué partout. Tout nouvel effect doit respecter le décision tree ci-dessous, sinon le combat service refuse de démarrer.

## Décision tree

```
Nouvel effet à ajouter
│
├─ Modifie une stat (atk, mag, armor, damage_taken, etc.) avec un % par stack ?
│  ├─ OUI → CANONICAL stackable
│  │       Ajouter à status_effects.json _meta.canonical_grid + définition dans effects.<category>
│  │       Skill utilise stacks_to_apply
│  │
│  └─ NON → continue
│
├─ Trigger sur événement (on_hit_taken, on_parry, etc.) ou flag de gameplay (immunité, invisibilité) ?
│  ├─ OUI → CUSTOM non-stackable
│  │       Définir dans status_effects.json effects.<category> avec runtime stat_mods/flags
│  │       Skill utilise pas de stacks_to_apply
│  │       Hook combat probablement à coder dans room.cpp ou damage_calculator
│  │
│  └─ NON → continue
│
├─ Mécanique skill spécifique (multi-hit, conditional damage, consume) ?
│  └─ OUI → FIELD METADATA SKILL
│           Ajouter au SkillData (skill.hpp), parser content_loader.cpp, lire dans damage_calculator
│           Pas dans status_effects.json (ce n'est pas un status, c'est un comportement skill)
│
└─ Effet visuel/cosmétique pur ?
   └─ vfx_type dans le skill, pas un effect
```

## Comment ajouter un effect canonical (rare)

1. Choisir `value_per_stack` (5 ou 10 selon force) et `max_stacks` (3 ou 5 selon dangerosité)
2. Ajouter à `stats/status_effects.json` `_meta.canonical_grid.<category>` :
   ```json
   "monstat_up": {"value_per_stack": 5, "unit": "percent", "max_stacks": 5, "total_max": "+25%"}
   ```
3. Ajouter la définition dans `effects.stat_modifiers` :
   ```json
   "monstat_up": {
     "name_fr": "...", "name_en": "...",
     "polarity": "buff", "stacking": "stackable", "max_stacks": 5,
     "impl": "done", "formula": "+5% monstat per stack",
     "runtime": {"stat_mods": {"monstat_percent": "value/100"}, "vfx_type": "..."}
   }
   ```
4. Backend C++ (`status_manager.cpp:115-164`) : ajouter le mapping `effect_id.starts_with("monstat_")` → `StatModType::MONSTAT`. Le `stat_mod_percent` sera override automatiquement par `canonical_grid` (ligne 218-244).
5. `apply_stat_modifications` lit le bon stat (`status_manager.cpp:962-1041`).
6. CI passe automatiquement après regen content_hash.

**Anti-pattern :** ne pas hardcoder une nouvelle stat dans canonical_grid sans aussi l'enregistrer dans `effects.<category>`. Le parser strict throw sinon.

## Comment ajouter un effect custom non-stackable

C'est le cas le plus fréquent pour tes tier3.

1. Définir dans `effects.<category>` (defensive, special, control, etc.) :
   ```json
   "mon_effet": {
     "name_fr": "Mon Effet", "name_en": "My Effect",
     "polarity": "buff", "stacking": "refresh", "max_stacks": 1,
     "impl": "todo", "stealable": false,
     "formula": "...",
     "tooltip_fr": "...", "tooltip_en": "...",
     "description_fr": "...", "description_en": "...",
     "sources": ["Warrior (Bulwark)"],
     "runtime": {
       "stat_mods": {...},  // si modifie des stats fixes
       "on_hit_taken": "...",  // si trigger sur event
       "consume_on_trigger": true|false,
       "vfx_type": "..."
     }
   }
   ```
2. Skill applique avec `stacks_to_apply` ABSENT (le parser throw bidirectionnel sinon) :
   ```json
   { "type": "buff", "stat": "mon_effet", "duration": 4.0, "target": "self" }
   ```
3. Backend C++ : si l'effet a un trigger (on_hit_taken, on_parry, etc.) qui n'est pas déjà géré data-driven, ajouter le hook dans `room.cpp` ou `damage_calculator.cpp`. Pour les effets purs stat_mods sans trigger, rien à coder, l'apply_stat_modifications les applique automatiquement via `runtime.stat_mods`.

## Comment ajouter un field metadata skill

Pour les comportements skill (multi-hit, conditional, consume mécanique).

1. Ajouter le field dans `SkillData` (`server-combat/src/skills/skill.hpp`) avec une valeur par défaut.
2. Parser dans `content_loader.cpp parse_skill()` via `skill_json.value("mon_field", default)`.
3. Lire dans `damage_calculator.cpp` ou `skill_executor.cpp` selon ce que le field fait.
4. Whitelist le field dans `kanarion_database/scripts/validate_skills.py` `ALLOWED_METADATA_FIELDS` (sinon CI fail).
5. Documenter dans `kanarion_database/CLAUDE.md` section "Skill Structure" si c'est un field important.

## Cas tier3 en cours

### 1. `replique_active` (Bulwark Warrior) — CUSTOM non-stackable

**Statut :** typo identifié, à créer proprement.

**Définition à ajouter** dans `stats/status_effects.json` `effects.defensive` :
```json
"replique_active": {
  "name_fr": "Réplique",
  "name_en": "Riposte (Bulwark)",
  "polarity": "buff",
  "stacking": "unique",
  "max_stacks": 1,
  "impl": "todo",
  "stealable": false,
  "formula": "Reflects value% of next attack (final_damage > 0 only). Consumed after 1 trigger.",
  "tooltip_fr": "Renvoie une partie des dégâts de la prochaine attaque reçue.",
  "tooltip_en": "Reflects part of the next attack received back to the attacker.",
  "description_fr": "Variante Bulwark de Riposte. Renvoie value% des dégâts de la prochaine attaque reçue. Consommé après 1 déclenchement.",
  "description_en": "Bulwark variant of Riposte. Reflects value% of the next attack's damage. Consumed after 1 trigger.",
  "sources": ["Warrior (Bulwark)"],
  "runtime": {
    "on_hit_taken": "reflect_damage",
    "consume_on_trigger": true,
    "vfx_type": "riposte_flash"
  }
}
```

**Backend C++ :** le hook actuel dans `room.cpp:2357-2400` check `has_effect("riposte_active")` en hardcoded. Deux options :
- **Quick fix (Option A) :** étendre le check à `has_effect("riposte_active") || has_effect("replique_active")`. Lire `find_effect()` correspondant. ~10 lignes.
- **Refacto data-driven (Option B) :** itérer tous les effets actifs sur la cible, pour chaque effet check `runtime.on_hit_taken == "reflect_damage"`, lire `consume_on_trigger`. Permet d'ajouter d'autres ripostes futures sans toucher au code combat.

Recommandation : Option A pour livrer Bulwark vite. Option B en Phase 5 si on accumule des ripostes (Sentinel, etc.).

### 2. `hit_count` + `each_hit_can_crit` + `damage_per_hit_bonus` (Frenzied + Reaver)

**Statut field metadata :**
- `hit_count` : déjà dans `SkillData` (`skill.hpp:115`), parsé, lu par `damage_calculator`
- `each_hit_can_crit` : déjà dans `SkillData` (`skill.hpp:116`), idem
- `damage_per_hit_bonus` : à ajouter

**À ajouter dans `skill.hpp`** :
```cpp
// Multi-hit ramping bonus (Frenzied: each successive hit hits harder)
float damage_per_hit_bonus = 0.0f;  // % bonus damage per extra hit (e.g. 10.0 = +10% per hit)
```

**Parser** dans `content_loader.cpp` (chercher où `hit_count` est parsé, ajouter à côté) :
```cpp
skill.damage_per_hit_bonus = skill_json.value("damage_per_hit_bonus", 0.0f);
```

**Damage calculator** dans `damage_calculator.cpp` ou `room.cpp` (chercher la boucle multi-hit) :
```cpp
for (int hit_index = 0; hit_index < skill.hit_count; ++hit_index) {
    float bonus_multiplier = 1.0f + (hit_index * skill.damage_per_hit_bonus / 100.0f);
    int32_t hit_damage = static_cast<int32_t>(base_damage * bonus_multiplier);
    // ... apply hit_damage
}
```

**Whitelist Python** (`validate_skills.py`) : `damage_per_hit_bonus` à ajouter à `ALLOWED_METADATA_FIELDS`.

### 3. `consumes_bleed_stacks` (Reaver Exécution) — FIELD METADATA SKILL

**Statut :** à créer entièrement, parallèle à `consumes_charges`.

**À ajouter dans `skill.hpp`** :
```cpp
// Reaver: skill consumes all bleed stacks on target after damage, optionally amplifying
bool consumes_bleed_stacks = false;
float bleed_consume_damage_per_stack = 0.0f;  // % bonus damage per consumed stack (optional)
```

**Parser** dans `content_loader.cpp` :
```cpp
skill.consumes_bleed_stacks = skill_json.value("consumes_bleed_stacks", false);
skill.bleed_consume_damage_per_stack = skill_json.value("bleed_consume_damage_per_stack", 0.0f);
```

**Damage calculator / skill_executor** (post-damage, avant cleanup) :
```cpp
if (skill.consumes_bleed_stacks &&
    entities.all_of<StatusEffectsComponent>(target)) {
    auto& effects = entities.get<StatusEffectsComponent>(target);
    auto* bleed = effects.find_effect("bleed");
    if (bleed != nullptr) {
        int32_t consumed = bleed->stacks;
        // Optionally amplify damage: bonus = consumed × bleed_consume_damage_per_stack / 100
        if (skill.bleed_consume_damage_per_stack > 0) {
            int32_t bonus = static_cast<int32_t>(base_damage * consumed * skill.bleed_consume_damage_per_stack / 100.0f);
            // apply bonus damage
        }
        status_manager_.remove_effect(entities, target, "bleed", current_tick, event_buffer);
    }
}
```

**Whitelist Python** : ajouter `consumes_bleed_stacks`, `bleed_consume_damage_per_stack`.

### 4. `armor_up` / `magic_resist_up` symétrie

**Statut :** déjà dans `canonical_grid` (5%/stack × 5 = ±25%). Le parser strict les accepte. Reste à vérifier que le runtime `apply_stat_modifications` les applique correctement.

**À vérifier** :
1. `armor_up stacks_to_apply: 5` sur entity → la `armor` stat augmente de 25% ?
2. Symétrie avec `armor_down` : si on applique armor_up + armor_down sur même entity, les deux s'annulent-ils ? Probablement non (deux instances d'effets distinctes), mais le résultat net est 0 modification stat.
3. `magic_resist_up`/`magic_resist_down` idem.

**Test à ajouter** (en Phase 4.1 ou maintenant) : un test unitaire `test_canonical_armor_buffs.cpp` qui applique armor_up avec 3 stacks, vérifie que `entity.stats.armor` est incrémenté de 15% du base.

### 5. `fear` canonical CC behavior

**Statut :** présent dans `effects.control` (ligne 1039+). `cc_type: "stun"` avec tags `["fear"]`. Tous les `blocks_*` sont true → comportement = stun avec tag distinct.

**Confirmation :** `fear` se comporte comme un stun pour le runtime (impossible d'agir), mais avec un tag spécifique pour les immunités/passifs spéciaux qui veulent réagir aux peurs spécifiquement.

Si tu veux un comportement "fear = fuir" (mouvement forcé loin de la source) au lieu de "stun-like", il faut :
- Ajouter `runtime.action: "flee"` dans la définition fear
- Coder le comportement dans `monster_ai.cpp` ou `combat_movement.cpp` : quand un entity a `fear` actif, override le target pour "fuir le caster" pendant la durée

Recommandation : laisser fear comme stun-like pour l'instant. Comportement "flee" est plus complexe et peut casser l'équilibrage 4x4 grid. À reconsidérer avec design Warlord.

### 6. Aures Warlord (futur)

**Statut :** pas urgent, en attente design.

À l'intégration, ces effets seront probablement :
- `commander_aura` : custom buff aura (le porteur émet un effet sur les alliés proches en grid). Stacking refresh, runtime `is_aura: true`, `aura_radius`, `aura_effect_target` (ally), etc. Voir `cc_immune_zone` pour le pattern.
- `intimidate_aura` : idem mais émis sur ennemis (debuff aura).
- `damage_vs_feared` : field metadata skill (`bonus_damage_vs_feared: 50` dans le skill, lu dans `damage_calculator` quand target a `fear` actif).

Designer la mécanique exacte et revenir ici quand tu codes Warlord.

### 7. Auto-fix artisan en background

**Statut :** mentionné mais pas claire. Si tu parles d'un système qui fix les buffs/heals des artisans automatiquement via timer, c'est un `is_aura: true` + `tick_heal` runtime dans status_effects.json. Voir `war_banner` pour le pattern.

Si c'est autre chose (process serveur qui répare le state combat), à clarifier.

## Validation checklist (avant commit)

À chaque ajout d'effect ou skill :

1. [ ] `python scripts/validate_skills.py` passe (0 erreur)
2. [ ] `_meta/version.json` content_hash regen via la commande Python documentée dans `kanarion_database/CLAUDE.md`
3. [ ] Si nouveau effect_id : il existe dans `stats/status_effects.json` (sinon le test `AllSkillsEffectsTest.AllAppliedEffectsExist` échoue et le combat service refuse de démarrer)
4. [ ] Si effet canonical : `stacks_to_apply` est dans range `[1, max_stacks]`
5. [ ] Si nouveau field metadata skill : whitelist dans `validate_skills.py` `ALLOWED_METADATA_FIELDS`
6. [ ] Backend C++ : si nouveau hook combat (on_hit_taken etc.), code en place et test unitaire en place
7. [ ] Build C++ passe (`./build.sh Debug`)
8. [ ] Tests unitaires combat passent (`./test-unit.sh`)
9. [ ] Smoke test : appliquer le nouvel effet dans un combat et vérifier le comportement

## Anti-patterns à ne pas reproduire

- Réintroduire `value` ou `value_override` sur un effet canonical (parser throw)
- Hardcoder un effect_id dans `effects.X` sans le déclarer dans `_meta.canonical_grid` ET dans `effects.<category>` si stackable canonical
- Référencer un effect_id dans un skill sans le créer dans `status_effects.json` (combat refuse de démarrer)
- Oublier de regen content_hash après modif JSON
- Coder un trigger via `if (effect_id == "X")` au lieu de lire `runtime.<trigger>` data-driven (dette future)
- Sauter la whitelist Python pour un nouveau field skill (CI fail à la prochaine PR)

## Pour aller plus loin

- Catalogue complet des effets actuels : `stats/status_effects.json` (105 effects)
- Grille canonique : `stats/status_effects.json` `_meta.canonical_grid` (46 effects stackables)
- Code C++ qui charge tout : `server-combat/src/skills/canonical_grid.{hpp,cpp}` + `server-combat/src/status/status_manager.cpp`
- Validation strict : `server-combat/src/content/content_loader.cpp parse_skill()` + `server-combat/src/skills/skill_validator.cpp`
- Hooks combat existants à imiter : `room.cpp` (riposte_active, en_garde_stance, predation, savoir_faire)
