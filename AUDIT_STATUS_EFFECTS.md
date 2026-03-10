# Audit Global — Status Effects, Stats, Skills & Autorité Serveur

**Date :** 2026-03-10
**Scope :** Server (C++), Client (GDScript), Game Database (JSON)
**Objectif :** Vérifier que tout est 100% server-authoritative, pas de fallback client, pas de hardcode, et que chaque status effect fonctionne correctement.
**Statut :** Validé par CTO (2 passes) — Phase 1 **bloquante** avant mise en ligne.

---

## Verdict CTO (Review Finale)

### Évaluation globale

> C'est un très bon audit technique pour un MMO indie. Phase pré-release sérieuse, pas un proto bricolé.

**Architecture : Très bonne.** Le moteur a déjà :
- Serveur autoritaire combat
- Pipeline dégâts centralisé (DamageCalculator)
- StatusManager propre (apply/expire/periodic/flags)
- CombatRNG serveur (évite crit cheat, proc cheat, RNG désync)
- Client mostly passif

→ Pas de refonte nécessaire.

### Le vrai problème

> Le problème n'est pas l'architecture. Le problème est : **effets non branchés + data manquante + fallback client restant.** Ce sont des bugs d'intégration, pas des problèmes de design. C'est beaucoup plus simple à corriger.

### Points d'excellence relevés

| Point | Évaluation |
|-------|-----------|
| CombatRNG serveur | Excellent — évite crit cheat, proc cheat, RNG désync |
| DamageCalculator centralisé | Parfait — lifesteal, reflect, thorns, accuracy, armor passent tous par là |
| StatusManager (apply/expire/periodic/flags) | Clean |
| DOT bypass DamageCalculator | Design validé — WoW et FFXIV font pareil |

### 4 vrais blocants uniquement

| # | Blocant | Impact | Effort estimé |
|---|---------|--------|---------------|
| 1 | `confusion` non implémenté | 3 skills complètement inutiles (3 classes) | 3-5h |
| 2 | `disarm` partiellement branché | 3 skills cassés, fix de ~10 lignes | < 1h |
| 3 | `heal_block` / `heal_reduction` | Perte de crédibilité du combat | 1-2h |
| 4 | 5 IDs data manquants | Buffs/debuffs ignorés silencieusement, touche beaucoup de classes | < 1h |

**Total : 18 skills sur 200+ (~9%) partiellement cassés. Le jeu fonctionne déjà bien.**

### Planning recommandé

| Jour | Tâches | Temps estimé |
|------|--------|:------------:|
| **Jour 1** | IDs manquants + disarm + heal_block + heal_reduction | 1-3h |
| **Jour 2** | Confusion (implémentation V1 simple) | 3-5h |
| **Jour 3** | Nettoyage client (randf, silent return, offline logic) | 1-2h |

**→ Vrai travail restant : 1 journée dev max.**

### Risques si non corrigé

- Désync perçue entre ce que voit le joueur et ce que décide le serveur
- Perte de confiance dans le système de combat
- Bugs impossibles à diagnostiquer car silencieux
- Équilibrage faussé parce que certains buffs/debuffs ne s'appliquent jamais
- Le pire bug MMO : client pense A, serveur décide B

### Feu vert pour le playtest

| Condition | Statut |
|-----------|--------|
| disarm OK | ✅ Done — StatusType::DISARM + update_status_flags() |
| heal_block OK | ✅ Done — check avant tout heal (skill, lifesteal, HoT) |
| heal_reduction OK | ✅ Done — heal_reduction_percent dans StatusFlagsComponent |
| confusion OK | ✅ Done — V1 simple, auto-attack random target, MonsterAI random |
| IDs data OK | ✅ Done — 5 IDs ajoutés dans status_effects.json |
| Plus aucun `randf()` client en chemin online | ✅ Done — push_error() guards ajoutés |
| Plus de silent fallback | ✅ Done — push_warning/push_error partout |

**→ Une fois toutes les cases cochées : ouverture du playtest autorisée.**

---

## Résumé Exécutif

| Catégorie | OK | Problèmes | Critique |
|-----------|----|-----------:|:--------:|
| Status effects serveur | 12/18 | 6 | 3 |
| Autorité client | 5/9 | 4 | 2 |
| Data (IDs manquants) | 112/117 | 5 | 0 |
| **Total** | | **15** | **5** |

---

## 1. STATUS EFFECTS SERVEUR (C++)

### 1.1 Effets Fonctionnels (OK)

| Effet | Catégorie | Implémentation | Notes |
|-------|-----------|----------------|-------|
| `stun` | control | Flag `stunned` + ActionValidator bloque toute action | OK |
| `silence` | control | Flag `silenced` + ActionValidator bloque skills magiques | OK |
| `blind` | control | `-75%` accuracy via `stat_mods` → DamageCalculator accuracy check | **Fixé cette session** |
| `taunt` | aggro | Flag `taunted` + `taunt_source` → MonsterAI force la cible + auto-attack redirect | OK |
| `shield` | defensive | ShieldComponent créé → DamageCalculator absorbe les dégâts | **Fixé cette session** |
| `burn/poison/bleed` | dot | Dégâts périodiques via StatusManager::process_periodic_effects() | OK (voir §1.3) |
| `heal_over_time` | hot | Heal périodique via StatusManager | OK |
| `invulnerable` | immunity | Flag `can_take_damage() = false` | OK |
| `slow` | control | stat_mods speed reduction | OK |
| Stat modifiers (26) | stat_modifiers | ATK/DEF/MAG/crit/armor/evasion up/down | OK — parsing explicite ajouté |
| `mana_regen` | special | Regen MP par tick | OK |
| `lifesteal/thorns/reflect` | special | Intégrés dans DamageCalculator | OK |

### 1.2 Effets NON Fonctionnels (À implémenter)

#### CRITIQUE — Utilisés par des skills existants

| # | Effet | Problème | Skills concernés | Priorité |
|---|-------|----------|-----------------|----------|
| S1 | `confusion` | **Non implémenté.** Pas de flag dans StatusFlagsComponent, pas de logique dans MonsterAI/auto-attack. | `skill_rogue_trickster_confuse`, `skill_archer_ballmaster_pinball`, `skill_mage_card_fate_flip` (3 skills, 3 classes) | **CRITIQUE** |
| S2 | `disarm` | Flag `disarmed` existe + auto-attack bloqué, MAIS `update_status_flags()` ne set jamais le flag (manque case DISARM). Le stat_mod `disarmed: 1` du JSON n'est pas parsé. | `skill_archer_crippling_arrow`, `skill_rogue_trickster_disarm`, `skill_archer_gunslinger_final_volley` (3 skills, 2 classes) | **CRITIQUE** |
| S3 | `heal_block` | **Non implémenté.** Défini dans JSON (`stat_mods: { heal_block: 1 }`) mais le serveur n'a aucun check avant d'appliquer un heal. | `skill_archer_ranger_kill_shot` | **HAUTE** |
| S4 | `heal_reduction` | **Non implémenté.** Même problème que heal_block — aucune réduction de heal côté serveur. | `skill_healer_martyr_zealous_strike`, `artisan/pb_wither` | **HAUTE** |

#### HAUTE — Fonctionnement partiel

| # | Effet | Problème | Impact |
|---|-------|----------|--------|
| S5 | `fear` | **Traité comme STUN** (`status_manager.cpp` line 128: `StatusType::STUN`). Devrait causer un mouvement aléatoire + interdiction d'agir, pas juste un stun. JSON marqué `impl: todo`. | Aucun skill ne l'utilise actuellement — **non bloquant** pour le lancement |
| S6 | DOT (burn/poison/bleed) | Dégâts appliqués **directement sur HP** sans passer par DamageCalculator. Ignore armor, magic_resist, block, parry, damage_reduction. | **Décision CTO : garder tel quel pour la V1 si c'est assumé design.** Cohérent, documenté, identique pour tous = pas un bug critique si intentionnel. |

#### BAS — Pas de skills utilisant ces effets

| Effet | Notes |
|-------|-------|
| `root` | Flag `rooted` + `can_move()` existent mais aucun skill ne l'applique. Pas de validation mouvement dans ActionValidator. **Aucun skill n'utilise root actuellement.** |
| `shield_block` | Défini dans JSON mais pas implémenté côté serveur. Aucun skill ne l'utilise. |

### 1.3 DOT — Décision de Design

Les DOT (burn, poison, bleed) appliquent actuellement des dégâts bruts :
```cpp
// status_manager.cpp, process_periodic_effects()
health.current -= value;  // Pas de DamageCalculator
```

**Décision CTO :** Garder tel quel pour la V1. C'est cohérent avec la majorité des MMOs (WoW, FFXIV). L'important est que ce soit cohérent, documenté, et identique pour tous. Ce n'est pas un bug critique si c'est intentionnel.

---

## 2. VIOLATIONS D'AUTORITÉ CLIENT (GDScript)

### 2.1 Violations Critiques

| # | Fichier | Lignes | Problème | Détail |
|---|---------|--------|----------|--------|
| C1 | `equipment_proc_manager.gd` | 277, 361 | **`randf()` sans CombatRNG** | Utilise `randf()` global pour déterminer si un proc d'équipement se déclenche. Le header dit "Only runs in LOCAL authority mode" mais c'est une violation du pattern RNG. |
| C2 | `status_manager.gd` | 70 | **Fallback `randf()`** | `_randf()` retourne `randf()` si `_combat_rng` n'est pas injecté. Utilisé pour CC immunity (L141), block chance (L707), parry chance (L715). En mode online ces checks sont serveur-side, mais le fallback existe. |

### 2.2 Violations Hautes

| # | Fichier | Lignes | Problème | Détail |
|---|---------|--------|----------|--------|
| C3 | `combat_countdown.gd` | 120-134 | **Logique offline de countdown** | `_are_all_players_ready()` local + timer local pour décider quand le combat commence. Protégé par un `if Game.is_online_world()` return early (L102-118), donc **inactif en online**. Code mort offline à supprimer. |
| C4 | `combat_input.gd` | 489-494 | **Silent return si offline** | `_request_position_swap()` retourne silencieusement si pas online. Pattern de fallback offline — devrait être supprimé ou assertion. |

### 2.3 Directive CTO : Tolérance Zéro sur les Fallbacks Client

> Le pire en prod, ce n'est pas un crash immédiat. Le pire, c'est un comportement qui "semble marcher" mais diverge du serveur.

**Règles :**
- Pas de `randf()` de secours
- Pas de return silencieux
- Pas de logique mixte "online si possible sinon offline"
- En online, si le contexte serveur manque → log/error, jamais de fallback silencieux

### 2.4 Code Client Vérifié OK

| Fichier | Vérifié | Notes |
|---------|---------|-------|
| `monster_ai.gd` | OK | Utilise `_combat_rng.randf()` partout |
| `combat_system.gd` | OK | Utilise `_randf()` → `_combat_rng.randf()` |
| `combat_event_router.gd` | OK | Seul point de modification HP/MP/shield/status |
| `star_encounter_generator.gd` | OK | `randf()` acceptable (pré-combat, pas dans le tick loop) |
| `LocalCombatAuthority` | OK | **Supprimé** — plus dans le codebase |

---

## 3. DATA — IDs MANQUANTS DANS `status_effects.json`

5 effect IDs sont référencés par des skills mais **absents** de `stats/status_effects.json` :

| Effect ID manquant | Skills qui l'utilisent | Classes |
|--------------------|-----------------------|---------|
| `atk_percent_up` | `skill_warrior_berserker_bloodlust`, `skill_warrior_berserker_frenzy` | Warrior (Berserker) |
| `flat_dr_up` | `skill_artisan_blacksmith_metalguard`, `skill_artisan_chef_warming_broth`, `skill_healer_lifewarden_regeneration`, `skill_healer_lightbringer_bless`, `skill_warrior_warlord_rally`, `skill_warrior_warlord_war_banner` | Artisan, Healer, Warrior (6 skills) |
| `flat_dr_down` | `skill_artisan_chef_blazing_aroma`, `skill_warrior_warlord_weakening_roar` | Artisan, Warrior |
| `heal_received_down` | `skill_archer_ranger_piercing_arrow`, `skill_artisan_musician_rallying_melody` | Archer, Artisan |
| `crit_resistance_down` | `skill_archer_ranger_precision_shot` | Archer (Ranger) |

**Impact :** Le serveur (StatusManager) ne trouve pas la définition de ces effets → ils ne s'appliquent jamais. Les skills font leurs dégâts mais les buffs/debuffs associés sont silencieusement ignorés.

**Fix :** Ajouter les 5 définitions dans `stats/status_effects.json`.

---

## 4. PLAN D'ACTION — Validé par CTO

### Architecture recommandée (3 couches)

Le CTO recommande de ne **pas corriger effet par effet en dispersé**, mais via une approche en 3 couches :

#### Couche 1 — Pipeline serveur unique pour les actions
Tout ce qui touche à dégâts, heal, application/expiration de status, procs conditionnels doit passer par des points centraux :
- **Un endroit** pour appliquer un heal
- **Un endroit** pour appliquer un dégât
- **Un endroit** pour recalculer les flags actifs
- **Un endroit** pour résoudre les cibles d'une action

→ `heal_block`, `heal_reduction`, `disarm`, `confusion` deviennent des règles du moteur, pas des rustines dispersées.

#### Couche 2 — Plus aucun fallback client ambigu
- Supprimer les fallbacks offline silencieux
- Remplacer par assertions ou logs d'erreur
- Si un chemin "offline only" existe encore, il doit être explicitement isolé

#### Couche 3 — Validation data au boot
Au démarrage serveur, valider :
- Chaque skill référence des effect IDs existants
- Chaque effect_id a un type connu
- Chaque stat_mod a un parser connu
- Erreur de boot ou gros warning bloquant dans les logs

→ Énorme gain long terme. Sans ça, chaque nouveau skill risque de réintroduire des effets fantômes.

---

### Sprint de Pré-release (BLOQUANT)

**Ordre exact recommandé par le CTO :**

#### Étape 1 — Corriger les données d'abord

**Fichier :** `stats/status_effects.json`

Ajouter les 5 IDs manquants : `atk_percent_up`, `flat_dr_up`, `flat_dr_down`, `heal_received_down`, `crit_resistance_down`.

> Tant que ces IDs n'existent pas, on peut corriger le code autant qu'on veut, les buffs/debuffs concernés ne s'appliqueront jamais.

**En plus :** Ajouter un check au chargement serveur — si un skill référence un effect_id absent ou un stat_mod inconnu → log error + compteur d'erreurs.

#### Étape 2 — Fix disarm (ultra-rapide)

**Fichier principal :** `status_manager.cpp`

Le fix le plus rentable : petit, sûr, impact joueur immédiat.

À faire :
1. Vérifier le mapping `effect_id == "disarm"` → `StatusType::DISARM`
2. Ajouter le `case DISARM` dans `update_status_flags()`
3. Vérifier que `can_auto_attack()` lit bien `flags.disarmed`

**Skills réparés :** Crippling Arrow, Disarm, Final Volley (3 skills, 2 classes)

```cpp
// status_manager.cpp, update_status_flags()
case StatusType::DISARM:
    flags.disarmed = true;
    break;
```

#### Étape 3 — Centraliser le traitement des heals

**Fichiers :** `components.hpp`, `status_manager.cpp`, `room.cpp`, `damage_calculator.cpp`

> Si un joueur utilise une compétence censée empêcher le heal, et que le serveur laisse quand même passer les soins, on casse toute la crédibilité du système PvE/PvP.

**3A. Dans `components.hpp` :**
```cpp
// StatusFlagsComponent
bool heal_blocked = false;
float heal_reduction_percent = 0.0f;  // 0.0 - 1.0
```

**3B. Dans `status_manager.cpp` :**
- `update_status_flags()` : si effet `heal_block` actif → `flags.heal_blocked = true`
- Si effet `heal_reduction` ou `heal_received_down` actif → résoudre le pourcentage dans `flags.heal_reduction_percent`

**3C. Dans `damage_calculator.cpp` :**
Point central pour tout heal :
1. Heal brut calculé
2. Application des restrictions status
3. Clamp final

**3D. Dans `room.cpp` :**
Avant toute application finale d'un heal direct :
```cpp
if (entities.all_of<StatusFlagsComponent>(target)) {
    const auto& flags = entities.get<StatusFlagsComponent>(target);
    if (flags.heal_blocked) {
        heal_amount = 0;
    } else if (flags.heal_reduction_percent > 0) {
        heal_amount = static_cast<int32_t>(
            heal_amount * (1.0f - flags.heal_reduction_percent));
    }
}
```

#### Étape 4 — HoT dans le même pipeline

**Fichier :** `status_manager.cpp`

> Si on corrige les heals directs sans corriger les HoT, on aura un trou logique : `heal_block` bloquera les heals actifs mais pas les HoT.

Dans `process_periodic_effects()`, pour les ticks de heal : passer par le même helper de heal final.

#### Étape 5 — Confusion (version minimale stable)

**Fichiers :** `components.hpp`, `status_manager.cpp`, `room.cpp`, `monster_ai.cpp`

> Le risque ici, ce n'est pas juste un bug ; c'est de créer un comportement instable ou non déterministe si c'est mal branché. L'objectif : **fiabilité > sophistication.**

**Implémentation V1 simple :**

**5A. `components.hpp` :**
```cpp
bool confused = false;
```

**5B. `status_manager.cpp` :**
```cpp
case StatusType::CONFUSION:
    flags.confused = true;
    break;
```

**5C. `room.cpp` (auto-attack) :**
- Si l'attaquant est `confused` → choisir une cible aléatoire valide parmi toutes les entités (allié ou ennemi)
- Exclure soi-même
- Uniquement pour auto-attacks, skills non affectés

**5D. `monster_ai.cpp` :**
- Si monstre `confused` → ignorer taunt, ignorer logique de focus, choisir cible aléatoire valide

**CRITIQUE :** La cible doit être décidée **serveur uniquement**. Pas de logique client, pas de pseudo-random local.

#### Étape 6 — Nettoyage client obligatoire

| Fichier | Action | Détail |
|---------|--------|--------|
| `equipment_proc_manager.gd` | Supprimer/protéger `randf()` | Si strictement offline → documenter et isoler. Sinon → remplacer par CombatRNG |
| `status_manager.gd` | Assertion au lieu de fallback | En online : `assert(_combat_rng)`, pas de `randf()` de secours |
| `combat_countdown.gd` | Supprimer code mort offline | Lignes 120-134 : dead code inactif en online |
| `combat_input.gd` | Supprimer silent return | Remplacer par assertion ou log explicite, jamais de retour silencieux |

#### Étape 7 — Logs obligatoires côté serveur

**Fichiers :** `status_manager.cpp`, `room.cpp`, `damage_calculator.cpp`, `content_loader.cpp`

Logs structurés sur :
```
[STATUS] unknown effect_id=...
[HEAL] blocked target=... source=...
[HEAL] reduced target=... base=... final=...
[CONFUSION] random target selected attacker=... target=...
```

→ Évitera 80% des bugs fantômes en playtest.

---

### Post Sprint — À faire ensuite

| # | Action | Notes |
|---|--------|-------|
| S5 | Implémenter `fear` correctement (mouvement aléatoire) | Aucun skill ne l'utilise actuellement — **non bloquant** |
| S6 | Documenter que DOT bypass DamageCalculator = intentionnel | Design decision validée CTO |
| | Nettoyer le code offline mort | Tout chemin offline résiduel |
| | Ajouter validation data au boot serveur | Couche 3 de l'architecture recommandée |
| | Ajouter tests de régression de combat | Voir §6 |

---

## 5. MATRICE SKILLS ↔ STATUS EFFECTS

### Skills utilisant des effets non fonctionnels

| Classe | Sous-classe | Skill | Effet cassé | Impact joueur |
|--------|-------------|-------|-------------|---------------|
| Rogue | Trickster | Confuse | `confusion` | Le skill fait 0 damage + 0 CC effect = inutile |
| Archer | Ballmaster | Pinball | `confusion` | Idem |
| Mage | Cardmaster | Fate Flip | `confusion` | Idem |
| Archer | (base) | Crippling Arrow | `disarm` | Le debuff ne s'applique pas |
| Rogue | Trickster | Disarm | `disarm` | Idem |
| Archer | Gunslinger | Final Volley | `disarm` | Idem |
| Archer | Ranger | Kill Shot | `heal_block` | L'execute ne bloque pas le heal |
| Healer | Martyr | Zealous Strike | `heal_reduction` | La réduction de heal ne s'applique pas |
| Warrior | Berserker | Bloodlust, Frenzy | `atk_percent_up` | Le buff ATK ne s'applique pas (ID manquant) |
| Warrior | Warlord | Rally, War Banner, Weakening Roar | `flat_dr_up/down` | Les buffs/debuffs DR ne s'appliquent pas |
| Healer | Lifewarden | Regeneration | `flat_dr_up` | Le buff DR ne s'applique pas |
| Healer | Lightbringer | Bless | `flat_dr_up` | Idem |
| Artisan | Blacksmith | Metalguard | `flat_dr_up` | Idem |
| Artisan | Chef | Warming Broth, Blazing Aroma | `flat_dr_up/down` | Idem |
| Archer | Ranger | Piercing Arrow, Precision Shot | `heal_received_down`, `crit_resistance_down` | Les debuffs ne s'appliquent pas |

**Total : 18 skills affectés sur ~200+ skills = ~9% des skills sont partiellement cassés.**

---

## 6. TESTS DE RÉGRESSION OBLIGATOIRES (avant ouverture)

6 tests manuels minimaux recommandés par le CTO :

| # | Test | Résultat attendu |
|---|------|------------------|
| 1 | Skill disarm sur cible | La cible ne peut plus auto-attack |
| 2 | heal_block sur cible | Heal direct doit faire 0 |
| 3 | heal_reduction sur cible | Heal direct réduit du bon pourcentage |
| 4 | HoT sous heal_block | Tick = 0 |
| 5 | HoT sous heal_reduction | Tick réduit correctement |
| 6 | Confusion sur cible | Auto-attack choisit une cible aléatoire valide, skills restent utilisables normalement |

---

## 7. CE QUI A ÉTÉ FIXÉ CETTE SESSION

| Fix | Fichiers modifiés | Détail |
|-----|-------------------|--------|
| BLIND/Accuracy | `status_manager.cpp`, `damage_calculator.cpp`, `damage_calculator.hpp` | Parsing stat_mods pour toutes les catégories + accuracy check dans DamageCalculator |
| Shields | `status_manager.cpp`, `room.cpp`, `combat_host.cpp`, `skill_executor.cpp` | Création ShieldComponent, absorption dégâts, snapshot FlatBuffers |
| Shield client | `pve_combat_manager.gd`, `combat_event_router.gd` | Parsing fields 10-12 snapshot, shield_amount dans STATUS_APPLIED |
| Effect scaling | `skill.hpp`, `content_loader.cpp`, `skill_executor.cpp` | Parsing scaling field, calcul % du stat du caster |

---

*Rapport généré par Claude Code — audit automatisé du codebase Kanarion Online.*
*Retour CTO intégré le 2026-03-10.*
