# Plan de Refactorisation — Alignement DB / Serveur / Combat

**Date :** 2026-03-13
**Version :** 2.1 — Final CTO
**Auteur :** Marc-Elie Charleston
**Scope :** kanarion_database + kanarion_back (server-combat)
**Audits source :** `AUDIT_NORMALIZE_EFFECTS_2026-03-13.md`, `AUDIT_MONSTER_SKILLS_2026-03-13.md`, `AUDIT_PLAYER_SKILLS_2026-03-13.md`

---

## 1. Pourquoi ce chantier

### Constat

Le serveur combat est server-authoritative par design. Mais aujourd'hui, **~75% des mécaniques de sous-classes ne fonctionnent pas côté serveur**. Le parser C++ (`content_loader.cpp`) ignore silencieusement la majorité des champs custom des skills.

| Catégorie | Skills impactés | Exemples de mécaniques mortes |
|-----------|----------------|-------------------------------|
| DoT non-bleed (burn, toxin, chill, corruption) | 18 skills | `applies_burn_stacks` ignoré |
| Utility (cleanse, purge, steal, mana, resurrect) | 22 skills | Aucun handler C++ |
| Execution modifiers (execute, armor_pen, hit_count) | 21 skills | Champs ignorés |
| Systèmes complexes (charges, momentum, bounce, reflect) | 25+ skills | Composants ECS absents |
| **Total** | **~130 skills** | **22 features C++ manquantes** |

**Résultat concret :** sur les 24 sous-classes du jeu, la plupart ont des skills qui "existent" dans le JSON mais ne produisent aucun effet en combat. Les 4 sous-classes mage sont les plus touchées (système de charges entièrement mort).

### Risque si on ne fait rien

- Chaque nouvelle feature combat s'empile sur un socle incohérent
- Le JSON contient des données que le serveur ignore → fausse impression de complétude
- Les tests unitaires (707) et intégration (431) passent mais ne couvrent pas les mécaniques mortes
- La dette s'accumule exponentiellement à chaque sous-classe ajoutée

### Risque de la refacto elle-même

**Ce chantier touche le pipeline de données combat. Tout peut casser.** La stratégie de migration est conçue pour minimiser ce risque :
- Coexistence temporaire ancien/nouveau format
- Chaque phase est un livrable testable indépendamment
- Rollback possible à chaque étape (les champs custom restent jusqu'à confirmation)
- Aucune phase ne casse le comportement existant — on ajoute avant de supprimer

---

## 2. Décisions d'architecture — Gravées, non négociables

Ces 8 décisions ont été validées par le CTO. Elles ne se rouvrent plus.

### Décision 1 — Le serveur est l'unique source de vérité gameplay

Pas de logique client. Pas de fallback. Pas de "le client complète si le serveur ne répond pas". Le client envoie des intentions, reçoit des résultats, affiche. Point.

### Décision 2 — Toute donnée gameplay vient de la DB, jamais du client, jamais d'un hardcode C++

Le C++ connaît les **mécaniques** (comment appliquer un DoT, comment calculer un execute). Il ne connaît jamais le **contenu** (quel skill fait quoi, quel monstre a quelles stats).

### Décision 3 — Toute mécanique de skill appartient soit à `effects[]`, soit à SkillData metadata, jamais ailleurs

**Frontière définitive :**

| Va dans `effects[]` | Reste top-level dans SkillData |
|---------------------|-------------------------------|
| DoT (bleed, burn, toxin, corruption, chill) | `ignore_los` |
| HoT (heal_over_time) | `hit_count` |
| Buffs / debuffs stats | `execute_threshold` + `execute_bonus_percent` |
| Shield | `armor_pen` / `shield_break` |
| Cleanse / purge / interrupt | `conditional_bonus` (object) |
| Mana steal / mana restore / mana regen | `chain_bounces` / `damage_per_bounce` |
| Lifesteal per-skill | `generates_charges` / `consumes_charges` |
| Resurrect | `generates_momentum` |
| Buff steal | `double_hit_chance` |
| | `guaranteed_crit` / `cd_reset_on_kill` |
| | `counter_chance` / `reflects_damage` |
| | `sacrifice_hp_percent` / `drain_to_all_allies` |
| | `random_buffs_*` / `random_debuffs_*` pools |
| | `damage_per_bleed_stack` / `bonus_damage_per_debuff` |
| | `redirect_to` |

**Règle :** `effects[]` = status effects appliqués sur une entité. Top-level = modificateurs du comportement du skill lui-même. Cette frontière ne bouge plus.

### Décision 4 — Aucun champ inconnu ou handler manquant n'est toléré

- Champ JSON inconnu → erreur CI **ou** boot fail
- `effects[].type` sans handler C++ → boot fail
- `effects[].stat` sans entrée dans `status_effects.json` → erreur CI
- Pas de "best effort". Pas de "on ignore si pas supporté". **Champ inconnu = erreur.**

### Décision 5 — Migration data par script one-shot, pas manuelle

Les skills JSON sont éditées à la main aujourd'hui. Pour la migration Phase 1 (~53 skills), on écrit un script Python jetable qui :
1. Lit chaque `classes/*/skills.json`
2. Détecte les champs custom legacy
3. Génère les entrées `effects[]` correspondantes
4. Conserve les champs custom temporairement (coexistence)
5. Produit un diff reviewable

On ne maintient pas le script. On le jette après la migration.

### Décision 6 — Séquentiel strict, pas de parallélisme

Équipe = 1 personne + IA. Pas de vrai parallélisme possible. Ordre unique :

```
Bloc 0 → Bloc 1 → Bloc 2 → Bloc 3 → Bloc 4 → Bloc 5
```

Chaque bloc est terminé avant de passer au suivant. Pas d'entremêlement.

### Décision 7 — Charges/momentum = minimum propre, pas framework générique

```cpp
// OUI — minimum propre
struct ChargesComponent {
    int arcane_charges = 0;     // Mage
    int momentum = 0;           // Spellblade
    int max_arcane_charges = 5; // Depuis config classe/subclass
    int max_momentum = 3;       // Depuis config classe/subclass
};

// NON — over-engineering interdit
struct SecondaryResource { std::string id; int current; int max; ... };
struct ResourcePoolComponent { std::vector<SecondaryResource> resources; };
```

2 compteurs typés. On généralisera si et seulement si un 3ème cas apparaît. Les caps viennent de la config classe si stable, sinon constantes locales au départ, externalisation plus tard si utile.

### Décision 8 — Le chantier n'est terminé qu'après suppression TOTALE du legacy

On n'arrête pas quand "ça marche". On arrête quand :
- 0 champ custom legacy dans le JSON
- 0 parsing legacy dans content_loader.cpp
- CI bloque toute réintroduction
- Boot refuse toute donnée invalide

---

## 3. Architecture cible — Version finale, pas intermédiaire

### Pipeline de chargement en 5 étapes

```
Étape 1 — PARSE       Lecture brute du JSON
                       ↓
Étape 2 — VALIDATE    Refuse : type inconnu, champ inconnu, ref manquante,
                       valeur incohérente, metadata incompatible,
                       skill/monster/zone orphelin,
                       contradiction legacy + nouveau = REJET
                       ↓
Étape 3 — NORMALIZE   Transforme vers les structs runtime (SkillData, MonsterTemplate, etc.)
                       ↓
Étape 4 — FREEZE      Enregistre dans les registries immuables
                       ↓
Étape 5 — RUNTIME     Le combat lit UNIQUEMENT les registries
                       Jamais de JSON brut. Jamais de fallback. Jamais de "best effort".
```

### Ce qui existe déjà (on ne repart pas de zéro)

| Composant | Fichier | État |
|-----------|---------|------|
| `SkillData` struct | `server-combat/src/skills/skill.hpp` | Existe, incomplet (manque ~13 champs) |
| `SkillRegistry` | `server-combat/src/skills/skill_registry.hpp/cpp` | Existe, fonctionnel |
| `PatternRegistry` | `server-combat/src/skills/pattern_registry.hpp/cpp` | Existe, fonctionnel |
| `StatusEffectData` | `server-combat/src/status/status_effect.hpp` | Existe, 13 types d'effets |
| `StatusManager` | `server-combat/src/status/status_manager.hpp` | Existe, `cleanse()` présent mais non utilisé |
| `DamageCalculator` | `server-combat/src/combat/damage_calculator.hpp/cpp` | Existe, pipeline complet mais sans overrides per-skill |
| `ContentLoader` | `server-combat/src/content/content_loader.hpp/cpp` | Existe, parse ~40% des champs |
| `MonsterTemplate` | `server-combat/src/content/content_loader.hpp` | Existe, pas de registry dédié |

**On n'introduit PAS de nouvelles abstractions** (`CompiledSkill`, `CompiledMonster`). On **étend les structs existantes** et on rend le parser exhaustif. C'est plus simple, moins risqué, et suffit.

---

## 4. Stratégie de migration — Zéro impact gameplay visible

### Question CTO : "Refacto sans impact visible ou on accepte des changements temporaires en staging ?"

**Réponse : zéro impact visible, même en staging.**

La coexistence ancien/nouveau format rend ça possible. À aucun moment le comportement observable ne change. On ajoute avant de supprimer. Si on accepte des "changements temporaires", on merge du code qui casse en se disant "on fixera après" — c'est exactement comme ça qu'on crée du legacy supplémentaire.

### Principe : coexistence puis nettoyage

```
Étape 1 : Ajouter effects[] EN PARALLÈLE des champs custom (script one-shot)
          → Le backend parse les deux (nouveau format PRIORITAIRE)
          → Rien ne casse
          → Si contradiction legacy + nouveau = REJET (pas de résolution silencieuse)

Étape 2 : Confirmer que le nouveau parsing fonctionne
          → Unit tests C++ sur chaque type d'effet
          → Integration tests sur les skills migrées
          → Tests existants toujours verts

Étape 3 : Supprimer les champs custom du JSON
          → CI lint rejette les anciens champs
          → PR de nettoyage

Étape 4 : Supprimer le parsing legacy du C++
          → content_loader.cpp ne lit plus les champs custom
          → Champ custom restant = erreur de parsing
```

**À chaque étape, le jeu reste fonctionnel.** On ne casse jamais le comportement existant avant d'avoir confirmé le nouveau.

---

## 5. Validation et CI — Renforcée AVANT la migration

### Question CTO : "Vous avez déjà un validateur CI ou tout passe par le boot ?"

**Réponse :** On a une base CI (`validate.yml` : syntax JSON + content_hash + cross-refs items/effects). Le plan étend cette CI phase par phase. Le boot serveur reste le filet de sécurité final.

### Ce qu'on ajoute immédiatement (Bloc 0)

| Validation | Où | Quand |
|-----------|-----|-------|
| Whitelist des `effects[].type` autorisés | CI | Bloc 0 |
| Whitelist des metadata top-level autorisés | CI | Bloc 0 |
| `effects[].stat` → existe dans `status_effects.json` | CI | Bloc 0 |
| Champ JSON inconnu dans une skill = erreur | CI | Bloc 0 |
| Contradiction legacy + nouveau = erreur | CI | Bloc 0 |
| Handler runtime existe pour chaque `effects[].type` | Boot serveur | Bloc 0 |
| Ref monstre/skill/zone manquante | CI | Bloc 4 |

### Validateur de contenu complet (cible finale)

```
Vérifications automatiques :
├── JSON syntax valide (EXISTE)
├── Content hash (EXISTE)
├── Cross-refs items → loot tables (EXISTE)
├── Cross-refs effects[].stat → status_effects.json (BLOC 0 — NOUVEAU)
├── Whitelist effects[].type (BLOC 0 — NOUVEAU)
├── Whitelist metadata top-level (BLOC 0 — NOUVEAU)
├── Rejet champs inconnus (BLOC 0 — NOUVEAU)
├── Rejet contradiction legacy/nouveau (BLOC 0 — NOUVEAU)
├── Cross-refs monster skill refs (BLOC 4 — NOUVEAU)
├── Cross-refs zone monster refs (BLOC 4 — NOUVEAU)
├── Lint anti-legacy : aucun champ custom interdit (BLOC 5 — NOUVEAU)
└── Chaque skill a effects[] OU est explicitement "no effect" (BLOC 5 — NOUVEAU)
```

### Assertions runtime (boot du serveur)

Le serveur DOIT refuser de démarrer si :
- Une skill référence un `effects[].type` inconnu
- Un `effects[].stat` n'a pas de handler identifié
- Un monstre référence une skill inexistante
- Un `ai_role` n'a pas de mapping dans le système AI
- Une formation produit une collision de slot
- Un status effect n'a pas de handler

**Chaque échec = log explicite + crash propre. Jamais silencieux.**

---

## 6. Plan d'exécution — 6 blocs séquentiels

### Vue d'ensemble

```
Bloc 0 — Contrat de contenu         Verrouiller la validation, les whitelists, les schémas
    ↓
Bloc 1 — Skills player (JSON)       Migrer 53 skills vers effects[] (script one-shot)
    ↓
Bloc 2 — Runtime combat (C++)       22 skills utility + metadata haute prio
    ↓
Bloc 3 — Charges/momentum (C++)     15+ skills mage, PR isolé
    ↓
Bloc 4 — Monstres/zones/formations  Consolider la data, ajouter les refs manquantes
    ↓
Bloc 5 — Nettoyage final legacy     Supprimer TOUT le legacy, CI bloquante définitive
```

**Chaque bloc est terminé, testé, mergé avant de passer au suivant.**

---

## 7. Bloc 0 — Contrat de contenu

**Objectif :** Avant toute migration, figer les règles du jeu. Le validateur CI et le boot serveur doivent pouvoir rejeter toute donnée non conforme.

### 0.1 — Schéma final des skills (figé)

**Ce qui va dans `effects[]` :** DoT, HoT, buffs, debuffs, shield, cleanse, purge, interrupt, resurrect, lifesteal, mana steal, mana restore, mana regen, buff steal.

**Ce qui reste top-level dans SkillData :** ignore_los, hit_count, execute_threshold, execute_bonus_percent, armor_pen, shield_break, conditional_bonus, chain_bounces, damage_per_bounce, generates_charges, consumes_charges, max_charges_consumed, generates_momentum, double_hit_chance, guaranteed_crit, cd_reset_on_kill, counter_chance, reflects_damage, sacrifice_hp_percent, drain_to_all_allies, dot_heals_lowest_ally, random_buffs_*, random_debuffs_*, redirect_to, damage_per_bleed_stack, bonus_damage_per_debuff, damage_per_missing_hp_percent, stealth_bonus_damage.

**Cette frontière ne bouge plus.**

### 0.2 — Schéma final des monstres (figé)

Chaque monstre doit avoir au minimum : `id`, `base_stats` (complets), `ai_role`, `archetype`, `skill_pool`, `drops`, `spawn_tags`.

### 0.3 — Schéma final des zones (figé)

Chaque zone doit avoir : refs monstres valides, `spawn_config` explicite, règles de formation.

### 0.4 — Implémenter les validations CI et boot

- Whitelist `effects[].type` : `buff`, `debuff`, `utility`
- Whitelist `effects[].stat` : cross-ref vers `status_effects.json`
- Whitelist metadata top-level : liste fermée des champs autorisés
- Rejet champ inconnu dans une skill
- Rejet contradiction si effects[] et champ custom décrivent la même mécanique avec des valeurs différentes
- Boot serveur : assertion handler existe pour chaque type parsé

### Bloc 0 — Definition of Done

- [ ] Schémas skills/monstres/zones documentés et figés (ce document)
- [ ] CI étendue : whitelist types, whitelist stats, rejet champs inconnus
- [ ] Boot validation : assertion handler sur chaque type d'effet
- [ ] Tests existants toujours verts (707 unit + 431 intégration)

---

## 8. Bloc 1 — Skills player (migration JSON)

**Effort :** ~53 skills
**Changement C++ :** Adaptation mineure du parser (lire `effects[]` en priorité, fallback legacy)
**Risque :** Très faible — le backend parse déjà `effects[]` et les DoT
**Méthode :** Script Python one-shot pour la transformation, diff reviewable

### 1.1 — DoT stacks → effects[] (27 skills)

Migrer `applies_X_stacks` vers le format `effects[]` standard.

| Champ custom | Format cible | Skills | Prérequis |
|-------------|-------------|--------|-----------|
| `applies_bleed_stacks: N` | `{"type":"debuff","stat":"bleed","value":N,"duration":X}` | 9 | Aucun (bleed déjà parsé) |
| `applies_burn_stacks: N` | `{"type":"debuff","stat":"burn","value":N,"duration":X}` | 10 | Vérifier `burn` dans status_effects.json catégorie "dot" |
| `applies_toxin_stacks: N` | `{"type":"debuff","stat":"toxin","value":N,"duration":X}` | 5 | ⚠️ `toxin` est en catégorie "special", pas "dot" — à déplacer |
| `applies_corruption_stacks: N` | `{"type":"debuff","stat":"corruption","value":N,"duration":X}` | 1 | ⚠️ Même problème que toxin |
| `applies_chill_stacks: N` | `{"type":"debuff","stat":"chill","value":N,"duration":X}` | 2 | ⚠️ Même problème que toxin |

**Prérequis :** Déplacer `toxin`, `corruption`, `chill` de catégorie "special" vers "dot" dans `stats/status_effects.json` si le `StatusManager` ne tick pas les effets "special" comme des DoT.

### 1.2 — Buffs/debuffs simples → effects[] (4 skills)

| Champ custom | Format cible | Skill |
|-------------|-------------|-------|
| `buff_value_atk: 30` | `{"type":"buff","stat":"atk","value":30,"duration":X}` | berserker_frenzy |
| `buff_value_speed: 20` | `{"type":"buff","stat":"speed","value":20,"duration":X}` | berserker_frenzy |
| `buff_scaling_percent: 15` | `{"type":"buff","stat":"atk","value":15,"duration":X}` | berserker_bloodlust |
| `defense_reduction: 25` | `{"type":"debuff","stat":"def","value":-25,"duration":X}` | duelist_expose_weakness |

### 1.3 — HoT → effects[] (~10 skills)

Le backend parse déjà `hot_percent` + `hot_duration` via un chemin custom (`effect_values["_hot_percent"]`). Migration vers le format standard `effects[]`.

**Format cible :**
```json
{"type": "buff", "stat": "heal_over_time", "value": 15, "duration": 8.0, "scaling": "max_hp"}
```

**Action C++ :** Adapter `content_loader.cpp` pour lire `effects[]` avec `stat: "heal_over_time"` en priorité, fallback sur `hot_percent` pendant la coexistence.

### 1.4 — Shield → effects[] (~12 skills)

Même logique que HoT.

**Format cible :**
```json
{"type": "buff", "stat": "shield", "value": 20, "duration": 10.0, "scaling": "mag"}
```

**Action C++ :** Même adaptation parser que 1.3.

### Bloc 1 — Definition of Done

- [ ] Script Python one-shot écrit et exécuté
- [ ] 53 skills migrées vers effects[] (diff reviewé)
- [ ] Champs custom conservés temporairement (coexistence)
- [ ] Parser C++ lit effects[] en priorité
- [ ] Unit tests verts pour chaque type (DoT, buff, debuff, HoT, shield)
- [ ] Integration tests existants toujours verts
- [ ] CI cross-ref : chaque `effects[].stat` existe dans `status_effects.json`

---

## 9. Bloc 2 — Runtime combat (C++ requis)

**Effort :** ~55 skills (22 utility + 33 metadata haute/moyenne prio)
**Risque :** Modéré — nouveau code serveur, mais mécaniques isolées

### Partie A — Utility effects (22 skills, 9 features C++)

Toutes ces mécaniques utilisent un nouveau type dans effects[] :
```json
{"type": "utility", "stat": "<mechanic>", "value": N}
```

#### 2.1 — Cleanse (6 skills)

Retire N debuffs d'un allié. `StatusManager::cleanse()` **existe déjà** mais n'est pas branché.

**C++ :** Brancher `cleanse()` dans le pipeline d'exécution quand `effects[].stat == "cleanse"`.
**Skills :** healer_purify, lifewarden_regrowth, lightbringer_cleanse_wave, cantor_sacred_ward, guardian_protect_ally, artisan_dispel.

#### 2.2 — Purge (3 skills)

Retire N buffs d'un ennemi.

**C++ :** `StatusManager::purge(entity, count)` — nouveau, miroir de cleanse.
**Skills :** warlord_weakening_roar, occ_soul_rend, gunslinger_suppressing_fire.

#### 2.3 — Mana Steal (3 skills)

Vole du mana à la cible (flat ou %).

**C++ :** Réduire MP cible, augmenter MP caster. Vérifier bornes [0, max_mp].
**Skills :** mage_arcane_siphon (30%), corsair_plunder (15 flat), corsair_raid (10%).

#### 2.4 — Mana Regen + Mana Restore (3 skills)

Regen = buff qui tick du mana. Restore = instant.

**C++ :** Mana regen → tick dans `StatusManager::process_tick()`. Restore → instant dans `apply_skill_effects()`.
**Skills :** cantor_hymn_of_vigor, artisan_tool_support (regen + restore instant).

#### 2.5 — Lifesteal per-skill (3 skills)

Le caster se soigne d'un % des dégâts infligés par CE skill.

**C++ :** Après `DamageCalculator::calculate()`, heal caster de `damage * value%`. Distinct du lifesteal stat global.
**Skills :** occ_life_drain (30%), occ_shadow_pact (25%), martyr_restorative_strike (60%).

#### 2.6 — Resurrect (1 skill)

Ramène un allié mort avec X% HP.

**C++ :** Vérifie cible morte, remet HP à `max_hp * value%`, retire l'état mort.
**Skills :** cantor_requiem (40%).

#### 2.7 — Interrupt (1 skill)

Interrompt le cast en cours de la cible.

**C++ :** Brancher sur `effects[].stat == "interrupt"`. `Room::cancel_cast(target)` existe probablement déjà.
**Skills :** gunslinger_quickshot.

#### 2.8 — Buff Steal (2 skills)

Vole N buffs d'un ennemi → les applique sur soi.

**C++ :** Purge + apply sur caster. Transférer duration restante.
**Skills :** trickster_grand_swindle (2), corsair_raid (99=all).

### Partie B — Skill metadata haute/moyenne prio (33 skills, 6 features C++)

Ces champs modifient le COMPORTEMENT du skill. Ils restent top-level dans le JSON et sont stockés dans `SkillData`.

#### 2.9 — ignore_los (15 skills)

**C++ :** Ajouter `bool ignore_los = false` dans SkillData. Check dans `validate_action()`.

#### 2.10 — execute_threshold + execute_bonus_percent (3 skills)

**C++ :** Ajouter dans SkillData. Check dans `DamageCalculator` : si `target.hp/max_hp < threshold`, bonus dmg.

#### 2.11 — armor_pen / shield_break (3 skills)

**C++ :** Ajouter dans SkillData. Override dans `DamageCalculator` pipeline.

#### 2.12 — hit_count (2 skills)

**C++ :** Loop dans `apply_skill_effects()`. Chaque hit = pipeline complet.

#### 2.13 — conditional_bonus (5 skills)

**C++ :** Parser l'objet condition. Évaluer pendant l'exécution.

#### 2.14 — chain_bounces / damage_per_bounce (5 skills)

**C++ :** Loop de bounce avec Manhattan distance. Partiellement implémenté côté targeting.

### Bloc 2 — Definition of Done

- [ ] 55 skills fonctionnelles côté serveur
- [ ] 15 features C++ implémentées (9 utility + 6 metadata)
- [ ] Chaque feature a au moins 1 unit test C++ dédié
- [ ] Integration test : skill produit l'effet attendu en combat réel
- [ ] SkillData étendu avec : ignore_los, execute_threshold, execute_bonus_percent, armor_pen, shield_break, hit_count, conditional_bonus, chain_bounces, damage_per_bounce
- [ ] StatusManager supporte : cleanse, purge, mana_steal, mana_regen, mana_restore, lifesteal, resurrect, interrupt, steal_buff
- [ ] DamageCalculator supporte : execute, armor_pen, shield_break

---

## 10. Bloc 3 — Charges / Momentum (PR isolé)

**Effort :** 15+ skills, effort ÉLEVÉ
**C'est le plus gros morceau.** Les 4 sous-classes mage dépendent des charges arcanes.

### Architecture

```cpp
struct ChargesComponent {
    int arcane_charges = 0;     // Mage resource
    int momentum = 0;           // Spellblade resource
    int max_arcane_charges = 5; // Depuis config classe/subclass
    int max_momentum = 3;       // Depuis config classe/subclass
};
```

**Minimum propre, pas framework générique.** 2 compteurs typés. Caps depuis la config si stable, constantes locales sinon. On généralisera si et seulement si un 3ème cas apparaît.

### Features

| Feature | Changement C++ |
|---------|---------------|
| `generates_charges` | Incrémente `arcane_charges` au cast. Ajouter dans SkillData + parsing. |
| `consumes_charges` | Lit et consume charges. Scaling de l'effet par nombre consommé. |
| `max_charges_consumed` | Cap de consommation par cast. |
| `generates_momentum` | Incrémente `momentum` au cast. Même pattern que charges. |

### Bloc 3 — Definition of Done

- [ ] ChargesComponent ECS implémenté
- [ ] Parsing dans content_loader.cpp
- [ ] Exécution dans apply_skill_effects()
- [ ] 15+ skills mage fonctionnelles
- [ ] Unit tests dédiés (generate, consume, cap, scaling)
- [ ] Integration test : combo charge → consume → damage scaling correct
- [ ] **Ce PR ne contient RIEN d'autre que le système de charges**

---

## 11. Bloc 4 — Monstres / Zones / Formations

**Décalé après le combat player.** La vraie dette critique est que le serveur ignore les mécaniques de skill. Les monstres/formations c'est du contenu — important mais pas bloquant.

### 4.1 — Unification données monstres

| Action | Détail |
|--------|--------|
| Fusionner `healer_support_monsters.json` | Intégrer dans `entities/monsters.json` principal |
| Compléter `monster_archetype_assignments.json` | Chaque monstre doit avoir un archétype assigné |
| Créer `entities/monster_skills.json` | Associer skills spécifiques par monstre/archétype |
| Ajouter `skill_pool_ids` dans MonsterTemplate | Le serveur sait quelles skills chaque monstre peut utiliser |

**Règle :** Aucun fichier d'exception ne contourne le modèle principal. 1 source unique par monstre.

### 4.2 — Formations et spawn

| Action | Détail |
|--------|--------|
| Créer `combat/formations.json` | Règles de placement par rôle (front/back/mid) |
| Implémenter `FormationResolver` C++ | `resolve(monsters, grid, rules) → positions[]` — déterministe, aucune collision |
| Ajouter `spawn_config` par zone | `max_active`, `respawn_time`, `elite_diversity`, `pack_size` |
| Ajouter `floor_difficulty_modifier` | Scaling donjons par étage |

### 4.3 — Validation CI monstres

| Vérification | Bloquante |
|-------------|-----------|
| Chaque monstre a un `ai_role` reconnu | Oui |
| Chaque `ai_role` a un archétype dans `monster_archetype_assignments.json` | Oui |
| Chaque skill référencée dans `monster_skills.json` existe | Oui |
| Chaque monstre a `base_stats` complets (hp, mp, atk, def, mag, mag_resist, speed) | Oui |
| Chaque zone référence des monstres existants | Oui |

### Bloc 4 — Definition of Done

- [ ] 1 source unique par monstre (plus de fichiers parallèles)
- [ ] Chaque monstre a : id, base_stats, ai_role, archetype, skill_pool, drops, spawn_tags
- [ ] FormationResolver déterministe implémenté
- [ ] spawn_config présent pour chaque zone
- [ ] CI bloquante sur incohérences monstres/zones

---

## 12. Bloc 5 — Nettoyage final legacy

**C'est ici qu'on ferme définitivement la porte.**

### 5.1 — Supprimer les champs custom du JSON

PR de nettoyage : retirer tous les `applies_X_stacks`, `hot_percent`, `shield_scaling_percent`, `buff_value_*`, etc. de tous les `skills.json`.

### 5.2 — Supprimer le parsing legacy du C++

`content_loader.cpp` ne lit plus les champs custom. Un champ custom restant = erreur de parsing.

### 5.3 — CI lint anti-legacy

Ajouter un lint qui rejette tout champ de la blacklist :

```
applies_bleed_stacks, applies_burn_stacks, applies_toxin_stacks,
applies_corruption_stacks, applies_chill_stacks, hot_percent,
hot_duration, shield_scaling_percent, shield_duration,
self_shield_scaling_percent, buff_value_atk, buff_value_speed,
buff_scaling_percent, defense_reduction, mana_steal_percent,
mana_steal_flat, lifesteal_percent (per-skill field),
purge_count, cleanse_count, interrupts_cast
```

### 5.4 — Mécaniques basse prio restantes

| Feature | Skills | Effort |
|---------|--------|--------|
| `sacrifice_hp_percent` / `drain_to_all_allies` / `dot_heals_lowest_ally` | 3 (martyr) | Moyen |
| `damage_per_bleed_stack` / `bonus_damage_per_debuff` / `damage_per_missing_hp_percent` | 5 | Moyen |
| `double_hit_chance` | 2 (cardmaster) | Faible |
| `random_buffs` / `random_debuffs` pools | 3 (cardmaster) | Moyen |
| `guaranteed_crit` / `cd_reset_on_kill` | 2 | Faible |
| `counter_chance` / `reflects_damage` | 2 (duelist) | **Élevé** |
| `redirect_to` | 1 (trickster) | Moyen |
| `stealth_bonus_damage` | 1 (shadowblade) | Faible |

### Bloc 5 — Definition of Done

- [ ] 0 champ custom legacy dans le JSON
- [ ] 0 parsing legacy dans content_loader.cpp
- [ ] CI lint anti-legacy actif et bloquant
- [ ] Toutes les mécaniques basse prio implémentées
- [ ] 24/24 sous-classes entièrement fonctionnelles côté serveur

---

## 13. Règles absolues — Permanentes, pas juste pendant la refacto

### 8 règles gravées

**1. Aucun champ JSON inconnu n'est toléré.**
Pas de "best effort". Pas de "on ignore si pas supporté". Champ inconnu = erreur CI ou boot fail.

**2. Aucun handler manquant n'est toléré.**
Chaque `effects[].type` et chaque mécanique supportée doivent avoir un handler identifié. Sinon le serveur ne démarre pas.

**3. Aucun contenu n'est codé en dur.**
```cpp
// INTERDIT — le code connaît le contenu
if (skill.id == "skill_warrior_heavy_strike") { /* logique spéciale */ }
if (monster.id == "mob_dragon") { /* bonus caché */ }

// AUTORISÉ — le code connaît les mécaniques
if (skill.execute_threshold > 0 && target_hp_percent < skill.execute_threshold) {
    damage *= (1.0 + skill.execute_bonus_percent / 100.0);
}
```
**La différence :** le premier code connaît le contenu. Le second connaît les mécaniques.

**4. Aucun fallback client. Jamais.**
Le client envoie des intentions, reçoit des résultats, affiche. Il ne complète rien, ne génère rien, ne corrige rien, ne décide rien.

**5. Aucune refacto large sans test dédié.**
Chaque famille de mécanique = unit tests + au moins un test intégration.

**6. Pas de nouvelle abstraction si la struct existante suffit.**
On étend `SkillData`, `MonsterTemplate`, `StatusEffectData`. On ne crée pas `CompiledSkill`, `CompiledMonster`, `CompiledStatusEffect`.

**7. 1 PR = 1 feature ou 1 famille. Pas de PR mixte.**
Une PR ne mélange JAMAIS parser + runtime + nettoyage + contenu. Chaque PR doit être :
- **Lisible** — un reviewer comprend le scope en 2 minutes
- **Testable** — les tests couvrent exactement ce que la PR change
- **Rollbackable** — on peut revert sans casser autre chose

Exemples de découpage correct :
```
PR "Bloc 1.1 — DoT stacks JSON"        → JSON only (script migration)
PR "Bloc 1.3 — HoT parser adaptation"   → C++ parser only
PR "Bloc 2.1 — Cleanse handler"         → C++ runtime only (StatusManager)
PR "Bloc 5.1 — Suppression legacy JSON" → JSON nettoyage only
```

Exemples de PR **interdites** :
```
PR "Migration DoT + parser + cleanse + nettoyage"   → TROP LARGE, impossible à review
PR "Fix skills + ajout formation resolver"           → 2 domaines mélangés
```

**8. Observabilité combat obligatoire en staging.**
Chaque mécanique migrée doit être observable dans les logs serveur. Pas de boîte noire. En staging au minimum, les événements suivants doivent être loggés :

| Événement | Log level | Contenu minimum |
|-----------|-----------|-----------------|
| Skill cast reçue | DEBUG | `entity_id`, `skill_id`, `target_id` |
| Validation rejetée | WARN | `entity_id`, `skill_id`, `reason` (mana, cooldown, range, stun, etc.) |
| Effect appliqué | DEBUG | `source_id`, `target_id`, `effect_type`, `effect_stat`, `value`, `duration` |
| Effect refusé | WARN | `source_id`, `target_id`, `effect_type`, `reason` (immunité, cap, handler manquant) |
| Charges generate/consume | DEBUG | `entity_id`, `resource` (arcane/momentum), `old_value`, `new_value` |
| Bounce/multi-hit | DEBUG | `skill_id`, `hit_index`, `target_id`, `damage` |
| Execute déclenché | DEBUG | `skill_id`, `target_id`, `target_hp_percent`, `bonus_percent` |
| Damage pipeline complet | TRACE | `base → crit → pen → armor → shield → final` (breakdown complet) |

**Pourquoi :** sur ce type de chantier, les bugs se manifestent par des effets silencieusement non appliqués. Sans logs, on debug à l'aveugle. Avec logs, on voit immédiatement quelle étape du pipeline a échoué.

**Règle :** en production, les logs DEBUG/TRACE peuvent être désactivés. En staging, ils sont **toujours actifs**. Les logs WARN restent actifs partout.

---

## 14. Zéro hardcode de contenu — Exemples concrets

### Ce qu'on supprime (dette existante)

```cpp
if (skill_id == "skill_warrior_charge") { apply_knockback(); }
if (monster_id.starts_with("mob_boss_")) { damage *= 1.5; }
if (zone_name == "desert_playtest") { max_mobs = 10; }
if (subclass.empty()) { /* fallback custom */ }
if (is_special_mob) { /* hidden bonus */ }
```

### Ce qu'on garde (moteur générique)

```cpp
// Le moteur lit la donnée et exécute
for (const auto& effect : skill.applied_effects) {
    status_manager.apply_effect(target, effect);
}

if (skill.hit_count > 1) {
    for (int i = 0; i < skill.hit_count; ++i) {
        apply_damage_pipeline(caster, target, skill);
    }
}

if (skill.armor_pen > 0) {
    effective_armor = std::max(0.0, target_armor - skill.armor_pen);
}
```

---

## 15. Definition of Done — Chantier complet

Le chantier n'est **pas terminé** tant que TOUTES ces conditions ne sont pas remplies :

- [ ] **130 skills** migrées vers le format canonique effects[] / metadata
- [ ] **22 features C++** implémentées et testées
- [ ] **0 champ custom legacy** dans le JSON
- [ ] **0 parsing legacy** dans content_loader.cpp
- [ ] **0 hardcode de contenu** dans le C++
- [ ] **CI bloquante** sur toute incohérence JSON (whitelists, cross-refs, lint anti-legacy)
- [ ] **Boot validation** refuse les données invalides (assertions handler, refs)
- [ ] **24/24 sous-classes** ont leurs mécaniques fonctionnelles côté serveur
- [ ] **707+ unit tests** verts (existants + nouveaux)
- [ ] **431+ integration tests** verts (existants + nouveaux)
- [ ] **Client inchangé** (aucune logique compensatoire ajoutée)
- [ ] **Monstres unifiés** (1 source, archétypes complets, skills assignés)
- [ ] **Formations déterministes** implémentées
- [ ] **Spawn configs** présents pour chaque zone

---

## 16. Matrice de risques

| Risque | Probabilité | Impact | Mitigation |
|--------|------------|--------|------------|
| Régression combat existant | Moyenne | **Critique** | Coexistence ancien/nouveau + tests avant suppression legacy |
| Phase 3C (charges) trop complexe | Haute | Élevé | PR isolé, design doc dédié avant implémentation |
| Scope creep pendant la refacto | Haute | Moyen | Chaque PR = 1 feature, pas de bonus |
| Parser C++ trop fragile pour edge cases | Moyenne | Élevé | Validation stricte au boot, pas de "best effort" |
| Script migration introduit des erreurs | Moyenne | Moyen | Diff reviewable, tests avant/après, coexistence |
| Bloc 0 (validation) prend trop de temps | Faible | Moyen | Scope limité : whitelists + cross-ref, pas un framework |

---

## 17. Métriques de suivi

| Métrique | Avant refacto | Après Bloc 1 | Après Bloc 2 | Après Bloc 3 | Cible finale |
|----------|--------------|-------------|-------------|-------------|-------------|
| Skills fonctionnelles serveur | ~25% | ~65% | ~85% | ~95% | **100%** |
| Champs custom legacy (JSON) | ~50 types | ~50 (coexistence) | ~50 (coexistence) | ~50 (coexistence) | **0** |
| Types d'effets StatusManager | ~5 | ~5 | 14+ | 14+ | **14+** |
| Features parsées content_loader | ~40% | ~55% | ~90% | ~95% | **100%** |
| Sous-classes jouables (tout OK) | ~6/24 | ~10/24 | ~18/24 | ~22/24 | **24/24** |

---

## Annexes

### A. Documents de référence

| Document | Rôle |
|----------|------|
| `AUDIT_NORMALIZE_EFFECTS_2026-03-13.md` | Inventaire complet des champs custom, catégorisation, plan de migration détaillé |
| `AUDIT_MONSTER_SKILLS_2026-03-13.md` | État des skills monstres, archétypes, rules de design |
| `AUDIT_PLAYER_SKILLS_2026-03-13.md` | Corrections description/data déjà appliquées, issues restantes |
| `kanarion_back/CLAUDE.md` | Architecture backend, conventions, pièges connus |
| `kanarion_database/CLAUDE.md` | Structure DB, conventions JSON, schémas |

### B. Fichiers C++ principaux impactés

| Fichier | Changements attendus |
|---------|---------------------|
| `skill.hpp` | +13 champs dans SkillData (ignore_los, hit_count, execute_threshold, armor_pen, shield_break, charges fields, conditional_bonus, chain_bounces, etc.) |
| `content_loader.cpp` | Parser exhaustif pour tous les champs SkillData + validation stricte + rejet champs inconnus |
| `status_manager.hpp/cpp` | +9 handlers (purge, mana_steal, mana_regen, mana_restore, lifesteal, resurrect, interrupt, steal_buff, brancher cleanse existant) |
| `damage_calculator.cpp` | +4 overrides (execute, armor_pen, shield_break, conditional scaling) |
| `room.cpp` / `skill_executor.cpp` | Exécution des nouveaux types (multi-hit, bounce, charges, sacrifice) |
| Nouveau: `charges_component.hpp` | Composant ECS pour charges arcanes / momentum (2 compteurs, pas de framework) |

### C. Fichiers JSON principaux impactés

| Fichier | Changements attendus |
|---------|---------------------|
| `classes/*/skills.json` (6 fichiers) | Migration effects[] (script one-shot), puis suppression champs custom (Bloc 5) |
| `stats/status_effects.json` | Déplacer toxin/corruption/chill vers catégorie "dot" si nécessaire |
| `config/status_effects.json` | Ajouter règles pour les nouveaux types d'effets |
| `entities/monsters.json` | Ajout skill_pool_ids, archetype consolidation (Bloc 4) |
| `entities/monster_skills.json` | Nouveau fichier — skills par archétype (Bloc 4) |
| `combat/formations.json` | Nouveau fichier — règles de placement (Bloc 4) |

### D. Matrice de traçabilité — Migration complète

Chaque mécanique est tracée de bout en bout. Aucun trou de migration possible.

#### Bloc 1 — DoT / Buff / Debuff / HoT / Shield (JSON pur)

| Mécanique | Champ legacy source | Format canonique cible | Parser C++ | Handler runtime | Test associé | PR nettoyage |
|-----------|--------------------|-----------------------|------------|-----------------|-------------|-------------|
| Bleed stacks | `applies_bleed_stacks` | `effects[]: {type:debuff, stat:bleed}` | `content_loader.cpp` (existe) | `StatusManager::apply_effect()` (existe) | Unit: DoT tick bleed | Bloc 5 — PR suppression legacy JSON |
| Burn stacks | `applies_burn_stacks` | `effects[]: {type:debuff, stat:burn}` | `content_loader.cpp` (existe) | `StatusManager::apply_effect()` (existe) | Unit: DoT tick burn | Bloc 5 |
| Toxin stacks | `applies_toxin_stacks` | `effects[]: {type:debuff, stat:toxin}` | `content_loader.cpp` (existe) | `StatusManager::apply_effect()` ⚠️ vérifier catégorie "dot" | Unit: DoT tick toxin | Bloc 5 |
| Corruption stacks | `applies_corruption_stacks` | `effects[]: {type:debuff, stat:corruption}` | `content_loader.cpp` (existe) | `StatusManager::apply_effect()` ⚠️ même que toxin | Unit: DoT tick corruption | Bloc 5 |
| Chill stacks | `applies_chill_stacks` | `effects[]: {type:debuff, stat:chill}` | `content_loader.cpp` (existe) | `StatusManager::apply_effect()` ⚠️ même que toxin | Unit: DoT tick chill | Bloc 5 |
| Buff ATK/speed | `buff_value_atk`, `buff_value_speed` | `effects[]: {type:buff, stat:atk/speed}` | `content_loader.cpp` (existe) | `StatusManager::apply_effect()` (existe) | Unit: buff stat modifier | Bloc 5 |
| Debuff DEF | `defense_reduction` | `effects[]: {type:debuff, stat:def}` | `content_loader.cpp` (existe) | `StatusManager::apply_effect()` (existe) | Unit: debuff stat modifier | Bloc 5 |
| HoT | `hot_percent` + `hot_duration` | `effects[]: {type:buff, stat:heal_over_time}` | `content_loader.cpp` (adapter) | `StatusManager::process_tick()` (existe) | Unit: HoT tick heal | Bloc 5 |
| Shield | `shield_scaling_percent` + `shield_duration` | `effects[]: {type:buff, stat:shield}` | `content_loader.cpp` (adapter) | `StatusManager::apply_effect()` (existe) | Unit: shield absorb | Bloc 5 |

#### Bloc 2A — Utility effects (C++ nouveau)

| Mécanique | Champ legacy source | Format canonique cible | Parser C++ | Handler runtime | Test associé | PR nettoyage |
|-----------|--------------------|-----------------------|------------|-----------------|-------------|-------------|
| Cleanse | `cleanse_count` | `effects[]: {type:utility, stat:cleanse, value:N}` | `content_loader.cpp` (ajouter) | `StatusManager::cleanse()` (existe, brancher) | Unit: remove N debuffs | Bloc 5 |
| Purge | `purge_count` | `effects[]: {type:utility, stat:purge, value:N}` | `content_loader.cpp` (ajouter) | `StatusManager::purge()` (NOUVEAU) | Unit: remove N buffs | Bloc 5 |
| Mana steal | `mana_steal_percent`, `mana_steal_flat` | `effects[]: {type:utility, stat:mana_steal}` | `content_loader.cpp` (ajouter) | `apply_skill_effects()` (NOUVEAU) | Unit: MP transfer both entities | Bloc 5 |
| Mana regen | N/A (pas de legacy) | `effects[]: {type:buff, stat:mana_regen}` | `content_loader.cpp` (ajouter) | `StatusManager::process_tick()` (NOUVEAU) | Unit: MP tick regen | N/A |
| Mana restore | N/A (pas de legacy) | `effects[]: {type:utility, stat:mana_restore}` | `content_loader.cpp` (ajouter) | `apply_skill_effects()` (NOUVEAU) | Unit: instant MP restore | N/A |
| Lifesteal per-skill | `lifesteal_percent` | `effects[]: {type:utility, stat:lifesteal}` | `content_loader.cpp` (ajouter) | `apply_skill_effects()` post-damage (NOUVEAU) | Unit: heal caster % damage | Bloc 5 |
| Resurrect | `resurrect` | `effects[]: {type:utility, stat:resurrect, value:40}` | `content_loader.cpp` (ajouter) | `apply_skill_effects()` (NOUVEAU) | Unit: dead → alive at X% HP | Bloc 5 |
| Interrupt | `interrupts_cast` | `effects[]: {type:utility, stat:interrupt}` | `content_loader.cpp` (ajouter) | `Room::cancel_cast()` (brancher) | Unit: cancel active cast | Bloc 5 |
| Buff steal | N/A (pas de legacy simple) | `effects[]: {type:utility, stat:steal_buff, value:N}` | `content_loader.cpp` (ajouter) | `StatusManager::steal_buff()` (NOUVEAU) | Unit: transfer N buffs | N/A |

#### Bloc 2B — Skill metadata (top-level SkillData)

| Mécanique | Champ JSON (reste tel quel) | Stockage C++ | Handler runtime | Test associé |
|-----------|---------------------------|-------------|-----------------|-------------|
| Ignore LoS | `ignore_los: true` | `SkillData::ignore_los` (AJOUTER) | `validate_action()` skip LoS check | Unit: skill cast through LoS blocker |
| Execute | `execute_threshold`, `execute_bonus_percent` | `SkillData::execute_*` (AJOUTER) | `DamageCalculator` bonus dmg | Unit: bonus at X% HP, no bonus above |
| Armor pen | `armor_pen` | `SkillData::armor_pen` (AJOUTER) | `DamageCalculator` reduce effective armor | Unit: damage increase vs armored target |
| Shield break | `shield_break` | `SkillData::shield_break` (AJOUTER) | `DamageCalculator` bypass shield % | Unit: damage through shield |
| Multi-hit | `hit_count` | `SkillData::hit_count` (AJOUTER) | `apply_skill_effects()` loop | Unit: N damage events on single cast |
| Conditional bonus | `conditional_bonus: {condition, bonus}` | `SkillData::conditional_bonus` (AJOUTER) | `apply_skill_effects()` eval condition | Unit: bonus when condition met, none when not |
| Chain bounce | `chain_bounces`, `damage_per_bounce` | `SkillData::chain_*` (AJOUTER) | `apply_skill_effects()` bounce loop | Unit: N bounces, correct target selection |

#### Bloc 3 — Charges / Momentum

| Mécanique | Champ JSON (reste tel quel) | Stockage C++ | Handler runtime | Test associé |
|-----------|---------------------------|-------------|-----------------|-------------|
| Generate charges | `generates_charges: N` | `SkillData::generates_charges` + `ChargesComponent` | `apply_skill_effects()` increment | Unit: charges increment, cap respected |
| Consume charges | `consumes_charges: true` | `SkillData::consumes_charges` + `ChargesComponent` | `apply_skill_effects()` consume + scale | Unit: consume → bonus, 0 charges → no consume |
| Max consumed | `max_charges_consumed: N` | `SkillData::max_charges_consumed` | `apply_skill_effects()` cap | Unit: consume capped at N |
| Momentum | `generates_momentum: N` | `SkillData::generates_momentum` + `ChargesComponent` | `apply_skill_effects()` increment | Unit: momentum increment + cap |

#### Bloc 5 — Mécaniques basse prio

| Mécanique | Champ JSON | Handler runtime | Test associé |
|-----------|-----------|-----------------|-------------|
| Sacrifice HP | `sacrifice_hp_percent` | `apply_skill_effects()` self-damage | Unit: caster HP reduced by % |
| Drain to allies | `drain_to_all_allies` | `apply_skill_effects()` redistribute | Unit: damage split as heal to team |
| DoT heals ally | `dot_heals_lowest_ally` | `StatusManager::process_tick()` special | Unit: DoT tick → heal lowest ally |
| Damage per bleed | `damage_per_bleed_stack` | `DamageCalculator` scaling | Unit: bonus per stack on target |
| Bonus per debuff | `bonus_damage_per_debuff` | `DamageCalculator` scaling | Unit: bonus per active debuff |
| Damage per missing HP | `damage_per_missing_hp_percent` | `DamageCalculator` scaling | Unit: bonus scales with missing HP |
| Double hit | `double_hit_chance` | `apply_skill_effects()` RNG roll | Unit: second hit probability correct |
| Random buffs/debuffs | `random_buffs_*`, `random_debuffs_*` | `apply_skill_effects()` RNG pool | Unit: N effects from pool, within bounds |
| Guaranteed crit | `guaranteed_crit` | `DamageCalculator` override | Unit: always crits |
| CD reset on kill | `cd_reset_on_kill` | `Room` post-kill hook | Unit: cooldown reset when target dies |
| Counter/reflect | `counter_chance`, `reflects_damage` | Tick loop event listener | Unit: counter triggers on hit received |
| Redirect | `redirect_to` | `apply_skill_effects()` target swap | Unit: damage redirected to correct entity |
| Stealth bonus | `stealth_bonus_damage` | `DamageCalculator` conditional | Unit: bonus from stealth, none without |

### E. Réponses aux questions CTO (pour référence)

| Question | Réponse |
|----------|---------|
| Impact gameplay visible pendant la migration ? | **Non.** Coexistence ancien/nouveau format. Zéro changement observable à chaque étape. |
| Validateur CI existant ? | **Oui, partiel.** Syntax + hash + cross-refs items/effects. Étendu en Bloc 0 (whitelists, rejet inconnus). Boot serveur = filet final. |
| Skills éditées à la main ou générées ? | **À la main** (avec database editor). Migration Phase 1 via **script Python one-shot** jetable. |
| Charges : générique ou minimum ? | **Minimum propre.** 2 compteurs typés dans un composant ECS. Pas de framework. |
| Même équipe Track A et B ? | **Oui (1 personne + IA).** Track B décalé après Bloc 2. Séquentiel strict. |
| Format plan ? | **Ce document = validation CTO.** Découpage en PRs numérotés directement exploitable. |
