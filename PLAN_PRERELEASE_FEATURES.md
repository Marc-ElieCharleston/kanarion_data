# Plan Pré-Release — Features Core à Implémenter

**Date :** 2026-03-10
**Scope :** Armor/Magic Penetration, Affixes, Panoplies, Uniques, Duel, Enhancement
**Objectif :** Compléter les systèmes de loot et de stats pour un lancement online crédible.
**Statut :** Validé par CTO (2 passes) — ordre ajusté selon retour produit.

---

## Verdict CTO

> Le plan est bon. La database JSON est complète, les fondations backend sont là, le problème est le branchement.

### Décisions CTO

| Décision | Choix | Raison |
|----------|-------|--------|
| Formule pénétration | **Option B — Pourcentage** | Plus stable long terme, meilleur scaling, moins toxique sur faibles armures, plus sain avec affixes/sets/uniques/enhancement |
| Ordre de priorité | **Pen → Affixes → Tooltips → Duel ou Panoplies → Uniques → Enhancement** | Prioriser ce que le joueur ressent immédiatement |
| Uniques à procs | **Prudence** — passifs et procs simples d'abord, complexes après launch | Risque de boucles de procs dans le tick loop |
| Schema custom_data | **Définir maintenant** le format stable (même champs vides) | Éviter les migrations futures |
| MVP launch | **Sprint 1 + Sprint 2** | Le minimum pour un loot excitant et lisible |
| Launch confort | **+ Sprint 3A (Panoplies simples) ou Sprint 4 (Duel UI)** | Selon focus produit (PvE/loot vs PvP) |

### Ordre révisé (CTO)

| Priorité | Contenu | Justification |
|:--------:|---------|---------------|
| 1 | Penetration | Stats existent, classes en ont de base, aujourd'hui inutiles = fausse profondeur |
| 2 | Affixes + rarity multiplier + affichage + couleurs + tooltips | Coeur loot du lancement — sans ça la rareté est cosmétique |
| 3 | Tooltips / comparaison d'items | Ce que le joueur ressent immédiatement |
| 4 | Duel UI **ou** Panoplies simples (selon focus produit) | PvP playtest → Duel / Loot playtest → Panoplies |
| 5 | Uniques à procs (passifs d'abord, complexes ensuite) | Risque 4 réel, prudence requise |
| 6 | Enhancement / Crafting | Post-launch |

> Pour un lancement online crédible, le minimum ce n'est pas enhancement, 25 panoplies, 14 uniques complexes. Le minimum c'est que **le loot soit enfin excitant et lisible** : pénétration fonctionnelle, rareté qui change les stats, affixes visibles, drops qui donnent envie d'équiper/comparer.

---

## Résumé Exécutif

| Feature | Data (JSON) | Backend (C++) | Frontend (GDScript) | Priorité |
|---------|:-----------:|:-------------:|:-------------------:|:--------:|
| Armor/Magic Penetration | 100% | **0%** | N/A | **Sprint 1** |
| Affixes + rarity + display | 100% | **0%** | **0%** | **Sprint 2** |
| Tooltips / comparaison | — | — | **0%** | **Sprint 2 bis** |
| Panoplies (set bonuses) | 100% | **10%** | **0%** | **Sprint 3** (optionnel pre-launch) |
| Uniques passifs | 100% | **30%** | **0%** | **Sprint 3** (optionnel pre-launch) |
| Duel UI | 100% | **90%** | **70%** | **Sprint 4** (optionnel pre-launch) |
| Uniques à procs complexes | 100% | **0%** | **0%** | **Post-launch** |
| Enhancement/Crafting | 100% | **0%** | **0%** | **Post-launch** |

**Constat global :** La database JSON est complète et bien structurée pour TOUS les systèmes. Le backend a les fondations (LootRoller, registries, ItemTemplate). Le problème est le **branchement** — les données existent mais ne sont pas connectées au runtime.

---

## Sprint 1 — Armor/Magic Penetration (~30min)

### Audit

**Problème :** `armor_pen` et `magic_pen` sont définis dans la database (cap 70%), dans les stats de base des classes (Mage: 5 magic_pen, Archer/Rogue: 5 armor_pen), mais **jamais utilisés** dans le DamageCalculator.

**Code actuel (damage_calculator.cpp) :**
```cpp
// Physique — armor_pen IGNORÉ
if (target_stats.armor > 0) {
    damage *= calc_reduction_factor(target_stats.armor);  // Devrait soustraire armor_pen
}

// Magique — magic_pen IGNORÉ
if (target_stats.magic_resist > 0) {
    damage *= calc_reduction_factor(target_stats.magic_resist);  // Devrait soustraire magic_pen
}
```

**Incohérence data :** Deux formules documentées qui ne sont pas d'accord :
- `definitions.json` : `effective_armor = target.armor × (1 - armor_pen/100)` (pourcentage)
- `combat.json` : `effective_armor = max(0, target.armor - attacker.armor_pen)` (soustraction plate)

**StatsComponent :** Les champs `armor_pen` et `magic_pen` sont **absents** du struct C++.

### Plan d'implémentation

| # | Action | Fichier | Détail |
|---|--------|---------|--------|
| 1 | Ajouter `armor_pen` et `magic_pen` à StatsComponent | `components.hpp` | `int32_t armor_pen = 0; int32_t magic_pen = 0;` |
| 2 | Parser ces stats depuis les données de jeu | `content_loader.cpp` ou `room.cpp` | Là où les stats de base sont chargées |
| 3 | Appliquer la pénétration dans DamageCalculator | `damage_calculator.cpp` | Avant `calc_reduction_factor()` |
| 4 | Clamper à 70% max | `damage_calculator.cpp` | `std::clamp(armor_pen, 0, 70)` |

**Décision CTO : Option B — Pourcentage** (validé)

```
effective_armor = armor × (1 - clamp(armor_pen, 0, 70) / 100)
effective_mr    = magic_resist × (1 - clamp(magic_pen, 0, 70) / 100)
```

**Raisons :**
- Plus stable à long terme
- Meilleur scaling (proportionnel, pas linéaire)
- Moins toxique sur les faibles armures
- Plus sain quand on empile gear + affixes + passifs + uniques + buffs
- Standard MMO (LoL, WoW)

**Action :** Mettre à jour `combat.json` pour refléter la formule pourcentage (aligner avec `definitions.json`).

### Impact

- 3 classes deviennent plus efficaces (Mage, Archer, Rogue — base pen non-zéro)
- Items avec armor_pen/magic_pen deviennent fonctionnels
- Passifs qui donnent de la pénétration deviennent fonctionnels

---

## Sprint 2 — Affixes & Génération d'Items (~1-2 jours)

### Audit

**Données existantes (100% complètes) :**

| Composant | Fichier | Contenu |
|-----------|---------|---------|
| 13 affixes | `items/affixes.json` | 6 prefixes + 7 suffixes, weights, level ranges, min/max rolls |
| 155+ items de base | `items/equipment.json` | 10 slots, 4 brackets (lvl 1-20), base_stats par item |
| 5 rarities | `items/equipment.json` | Common→Legendary, base_mult (1.0x→2.0x), affix_min/max (0→4) |
| Loot tables | `items/loot_tables.json` | Rarity weights par danger_level, drop chances par monster_state |

**Backend existant (30%) :**

| Composant | Status | Détail |
|-----------|--------|--------|
| `ItemTemplate` + `ItemStatBonus` | OK | 25 stats, chargement depuis JSON |
| `ItemTemplateRegistry` | OK | Charge equipment.json, query par ID |
| `LootRoller` | OK | Roll gold, XP, drops, enhancement stones |
| `LootRoller::roll_equipment()` | **STUB** | Roll rarity OK, mais retourne un item basique sans affixes |
| `ItemInstance.custom_data` | OK | Champ JSON libre — peut stocker les affixes |
| Chargement des affixes | **MANQUANT** | `affixes.json` jamais lu par le backend |
| Affix rolling | **MANQUANT** | Aucun code de sélection/roll d'affixes |
| Rarity multiplier | **MANQUANT** | `base_mult` (1.0x→2.0x) jamais appliqué aux stats |

**Frontend existant (10%) :**

| Composant | Status | Détail |
|-----------|--------|--------|
| `inventory_screen.gd` | OK | Grille 80 slots, paperdoll 10 slots, tabs, drag/drop |
| Affichage affixes | **MANQUANT** | Aucun affichage de préfixes/suffixes |
| Couleurs de rareté | **MANQUANT** | Pas de color-coding par rareté |
| Tooltip de comparaison | **MANQUANT** | Pas de "current vs. new item" |

### Architecture proposée

```
                         ┌─────────────────┐
                         │  affixes.json    │
                         │  (13 affixes)    │
                         └────────┬────────┘
                                  │ load
                         ┌────────▼────────┐
                         │  AffixRegistry   │
                         │  (index by slot, │
                         │   level, weight) │
                         └────────┬────────┘
                                  │ query
┌──────────┐   roll_equipment()  ┌▼─────────────┐   roll_affixes()   ┌──────────────┐
│LootRoller├────────────────────►│ ItemGenerator │◄──────────────────►│ AffixRoller  │
│          │                     │               │                    │ (weight-based │
└──────────┘                     │ 1. Pick base  │                    │  selection +  │
                                 │ 2. Roll rarity│                    │  value roll)  │
                                 │ 3. Apply mult │                    └──────────────┘
                                 │ 4. Roll affixes│
                                 │ 5. Pack into  │
                                 │    custom_data│
                                 └───────────────┘
```

### Plan d'implémentation

#### Étape 2.1 — AffixRegistry (backend)

**Nouveau fichier :** `services/economy/src/inventory/affix_registry.hpp/cpp`

```cpp
struct AffixData {
    std::string id;
    std::string type;       // "prefix" ou "suffix"
    std::string stat;       // "atk", "crit_chance", etc.
    int32_t min_value;
    int32_t max_value;
    int32_t weight;
    int32_t min_level;
    int32_t max_level;
    std::vector<std::string> allowed_slots;
};

class AffixRegistry {
    void load_from_file(const std::string& path);
    std::vector<const AffixData*> get_eligible(
        const std::string& slot, int32_t item_level, const std::string& type);
    // Retourne les affixes éligibles filtrés par slot, level, type
};
```

#### Étape 2.2 — AffixRoller (backend)

**Nouveau fichier :** `services/economy/src/inventory/affix_roller.hpp/cpp`

```cpp
struct RolledAffix {
    std::string affix_id;
    std::string stat;
    int32_t rolled_value;   // Entre min et max
};

class AffixRoller {
    std::vector<RolledAffix> roll(
        const AffixRegistry& registry,
        const std::string& slot,
        int32_t item_level,
        int32_t affix_count,   // Déterminé par rareté (0-4)
        std::mt19937& rng);    // RNG serveur
};
```

**Algorithme :**
1. Filtrer les affixes éligibles (slot + level)
2. Séparer prefixes et suffixes
3. Pour chaque slot d'affix :
   - Weighted random selection (poids du pool filtré)
   - Roll value entre min et max (uniform)
   - Interdire les doublons (`no_duplicate_affix_id: true`)
4. Retourner la liste des affixes rollés

#### Étape 2.3 — Intégration LootRoller

**Modifier :** `services/economy/src/loot/loot_roller.cpp`

Dans `roll_equipment()` :
1. Roll rarity (existant — rarity weights par danger_level)
2. Pick base item (existant — slot weights)
3. **NOUVEAU :** Appliquer `base_mult` de la rareté aux stats de base
4. **NOUVEAU :** Déterminer `affix_count` (rareté → `affix_min`/`affix_max`, roll entre les deux)
5. **NOUVEAU :** Appeler `AffixRoller::roll()` pour générer les affixes
6. **NOUVEAU :** Stocker dans `ItemInstance.custom_data` :
```json
{
    "rarity": "rare",
    "base_mult": 1.25,
    "affixes": [
        {"id": "pre_brutal", "stat": "atk", "value": 5},
        {"id": "suf_vigor", "stat": "hp", "value": 35}
    ]
}
```

#### Étape 2.4 — Stat aggregation (combat)

**Modifier :** `server-combat/` ou `services/economy/`

Quand un personnage entre en combat, ses stats d'équipement doivent inclure :
- Stats de base de l'item × `base_mult` de la rareté
- Stats des affixes (valeurs rollées)

**Point d'intégration :** Au moment du `CREATE_ROOM`, quand les `StatsComponent` sont initialisés.

#### Étape 2.5 — Frontend display

**Modifier :** `inventory_screen.gd` + nouveau composant tooltip

- Parser `custom_data` des items reçus du serveur
- Afficher le nom avec couleur de rareté (Common=#FFF, Uncommon=#1EFF00, Rare=#0070DD, Epic=#A335EE, Legendary=#FF8000)
- Afficher les affixes sous les stats de base (vert pour buff)
- Tooltip de comparaison : stats actuelles vs nouvel item

### Affixes disponibles (référence)

| ID | Type | Stat | Roll | Weight | Niveaux |
|----|------|------|------|--------|---------|
| `pre_strong` | prefix | ATK | +1 à +4 | 18 | 1-20 |
| `pre_agile` | prefix | crit_chance | +1 à +4 | 18 | 1-20 |
| `pre_arcane` | prefix | MAG | +1 à +5 | 18 | 1-20 |
| `pre_sharp` | prefix | crit_chance | +1 à +5 | 14 | 6-20 |
| `pre_brutal` | prefix | ATK | +3 à +8 | 12 | 11-20 |
| `pre_mystic` | prefix | MAG | +3 à +7 | 12 | 11-20 |
| `suf_vigor` | suffix | HP | +5 à +60 | 22 | 1-20 |
| `suf_guarding` | suffix | DEF | +1 à +7 | 22 | 1-20 |
| `suf_warding` | suffix | magic_resist | +1 à +7 | 16 | 6-20 |
| `suf_precision` | suffix | accuracy | +1 à +6 | 16 | 6-20 |
| `suf_evasion` | suffix | flee | +1 à +6 | 16 | 6-20 |
| `suf_slaying` | suffix | crit_damage | +5 à +15 | 10 | 11-20 |
| `suf_fortitude` | suffix | HP | +20 à +80 | 10 | 11-20 |

### Rarity → Affix Count

| Rareté | Multiplicateur stats | Affixes min | Affixes max | Couleur |
|--------|:-------------------:|:-----------:|:-----------:|---------|
| Common | 1.0x | 0 | 1 | #FFFFFF |
| Uncommon | 1.1x | 1 | 1 | #1EFF00 |
| Rare | 1.25x | 1 | 2 | #0070DD |
| Epic | 1.5x | 2 | 3 | #A335EE |
| Legendary | 2.0x | 3 | 4 | #FF8000 |

---

## Sprint 2 bis — Tooltips & Comparaison d'Items (~0.5 jour)

### Directive CTO

> Sans affichage propre, le système sera techniquement là mais peu ressenti. Le joueur doit **voir** la différence entre un Common et un Legendary.

### Plan d'implémentation

| # | Action | Détail |
|---|--------|--------|
| 1 | **Couleurs de rareté** | Nom de l'item coloré : Common=#FFF, Uncommon=#1EFF00, Rare=#0070DD, Epic=#A335EE, Legendary=#FF8000 |
| 2 | **Tooltip stats** | Stats de base (blanc) + affixes (vert) + bonus de set (jaune, futur) |
| 3 | **Comparaison simple** | "Current vs. New" — flèches vertes/rouges sur les stats qui changent |
| 4 | **Nom généré** | Format : "[Prefix] Nom de Base [Suffix]" — ex: "Brutal Iron Sword of Vigor" |

**Critique pour la sensation joueur :** C'est ce qui fait que le loot "paie" immédiatement. Un Legendary sans affichage distinctif = pas d'excitation.

---

## Sprint 3 — Panoplies & Uniques (~1 jour)

### 3A — Panoplies (Set Bonuses)

#### Audit

**25 sets définis** avec un système de rangs (Dofus-style) :

| Taille | Nombre | Exemples |
|--------|--------|----------|
| 2 pièces | 7 sets | Kesher (lifesteal), Ot (crit), Chayim (HP) |
| 4 pièces | 8 sets | Ruach (cast_speed), Kavod (ATK), Anan (evasion) |
| 6 pièces | 6 sets | Tzel (mag), Orim (heal), Eshal (multi-hit) |
| 8 pièces | 4 sets | Shomer (tank), Tzayad (archer), Neshamah (heal) |

**Système de rangs :**
| Rang | Niveaux | Multiplicateur |
|------|---------|:--------------:|
| Rang 1 (Apprenti) | 1-19 | 0.5x |
| Rang 2 (Adepte) | 20-39 | 1.0x (base) |
| Rang 3 (Expert) | 40-59 | 1.5x |
| Rang 4 (Maître) | 60-100 | 2.0x |

**Backend :** Aucune intégration. `panoplies.json` n'est pas chargé.

#### Plan d'implémentation

| # | Action | Détail |
|---|--------|--------|
| 1 | **PanoplieRegistry** | Charger `panoplies.json`, index par set_id et par item_id |
| 2 | **Set detection** | Quand un item est équipé, compter le nombre de pièces du même set |
| 3 | **Bonus calculation** | Appliquer les bonus du set (2pc, 4pc, etc.) avec le rang approprié |
| 4 | **Combat integration** | Ajouter les bonus de set aux StatsComponent au CREATE_ROOM |
| 5 | **Frontend** | Afficher le nom du set, le nombre de pièces, les bonus actifs/inactifs |

**Architecture serveur :**
```
Équipement → PanoplieRegistry.detect_sets(equipped_items[])
           → [{set_id, piece_count, rank}]
           → PanoplieRegistry.get_bonuses(set_id, piece_count, rank)
           → StatsComponent += bonuses
```

### 3B — Uniques (Items Nommés)

#### Audit

**14 uniques définis** avec procs spéciaux :

| Catégorie | Items | Exemples |
|-----------|-------|----------|
| Offensif | 5 | Dam Rishon (crit buff 8s), Etzem HaTzayad (multi-hit escalation) |
| Défensif | 4 | Magen HaSela (shield on block), Keter Barzel (DR per enemy) |
| Support | 3 | Neshimat Chayim (heal on buff), Ruach HaRefuah (CD reduction on heal) |
| Utilitaire | 2 | Tzel HaMidbar (attack speed on dodge), Ein HaTzofeh (MR→MAG convert) |

**Sources :** 12 drops de monstres (0.5-0.8% chance base), 2 récompenses de quêtes.

**Backend :** `UniqueItemRegistry` charge les uniques mais `LootRoller` ne l'appelle jamais.

#### Plan d'implémentation

| # | Action | Détail |
|---|--------|--------|
| 1 | **Intégrer au LootRoller** | Après roll_equipment(), tenter un roll unique (chance × monster_state × stars) |
| 2 | **Rank scaling** | Appliquer rank_multiplier (0.7x→1.6x) aux valeurs des effets |
| 3 | **Proc system serveur** | Nouveau `UniqueProcProcessor` dans le combat service — écoute les triggers (on_hit, on_kill, on_block, etc.) |
| 4 | **ItemInstance storage** | Stocker l'unique_id + rolled_rank + substats dans custom_data |
| 5 | **Frontend** | Tooltip spécial avec nom unique (orange), effet proc, substats |

**Triggers définis :**
- `on_combat_start`, `on_kill`, `on_hit`, `on_take_damage`, `on_block`
- `on_buff_applied`, `on_heal`, `on_dodge`, `on_ability_use`
- `permanent` (passif toujours actif)

---

## Sprint 4 — Duel PvP 1v1 (~0.5-1 jour)

### Audit — Correction Importante

**Le duel est déjà implémenté à 90%.** L'audit initial disait que le Social Service manquait les handlers, mais en réalité le **Gateway route les duels vers le PvP Service** (pas Social), et le PvP Service a **tous les handlers** :

| Composant | Status | Détail |
|-----------|--------|--------|
| Protocol (FlatBuffers) | **100%** | 8 messages (0x0530-0x0537) définis dans `social.fbs` |
| GDScript serializers | **100%** | `social_payloads.gd` — build + parse pour tous les messages |
| DuelManager (client) | **100%** | Envoie challenges, accept/decline, écoute les events |
| Gateway routing | **100%** | Route vers `kanarion.pvp.duel.*` |
| PvP Service handlers | **100%** | `handle_duel_challenge/accept/decline/ready/end()` tous implémentés |
| Combat room creation | **100%** | `request_pvp_combat_room()` → combat service crée la room 1v1 |
| Elo rating | **100%** | `update_elo_rating(mode="duel_1v1")` après chaque duel |
| Offline cleanup | **100%** | Écoute `kanarion.presence.event.offline`, nettoie les challenges/duels |
| Rate limiting | **100%** | 5 challenges/min par joueur |

### Ce qui manque (10%)

| Manque | Sévérité | Détail |
|--------|----------|--------|
| **UI d'invitation** | HAUTE | Pas de popup quand on reçoit un challenge |
| **UI d'arène** | MOYENNE | Pas d'écran "prêt" avant le combat |
| **Persistance** | BASSE | Challenges en mémoire, perdus au restart du PvP service |
| **Leaderboard duel** | BASSE | Mélangé avec le PvP group, pas de filtre duel-specific |

### Plan d'implémentation

| # | Action | Détail |
|---|--------|--------|
| 1 | **Popup d'invitation** | Scène GDScript : nom adverse + boutons Accept/Decline + timer 30s |
| 2 | **Écran "prêt"** | Afficher adversaire + bouton Ready, attendre `DUEL_STARTED` du serveur |
| 3 | **Filtre leaderboard** | Ajouter `mode` filter au PvP leaderboard (group vs duel) |
| 4 | **Persistance Redis** (optionnel) | Stocker `pending_challenges` dans Redis avec TTL 60s |

**Estimation réduite :** Comme le backend est déjà fait, c'est essentiellement du frontend UI.

---

## Sprint 5 — Enhancement / Crafting (post-launch)

### Audit

**Data existante :**
- `systems/enhancement.json` — Système d'upgrade d'items (+1 à +20)
- `items/substat_crafting_system.json` — Système de reroll de substats
- Enhancement stones : 5 rangs (minor→supreme), déjà droppés par le LootRoller

**Backend :** Aucune implémentation.

### Plan d'implémentation (esquisse)

| # | Action | Détail |
|---|--------|--------|
| 1 | **Enhancement service** | +1 à +20 avec chance de succès décroissante, consume des pierres |
| 2 | **Substat reroll** | Forge qui permet de reroller 1 substat d'un item |
| 3 | **UI Forge** | Écran de craft : sélection item + pierre → résultat |
| 4 | **Affix transfer** | Transférer un affix d'un item à un autre (late game) |

**Non bloquant pour le lancement.** Les pierres d'enhancement drop déjà, le système peut être patché après.

---

## Estimation Globale (révisée CTO)

| Priorité | Sprint | Contenu | Backend | Frontend | Total |
|:--------:|--------|---------|:-------:|:--------:|:-----:|
| 1 | Sprint 1 | Penetration | 30min | — | **30min** |
| 2 | Sprint 2 | Affixes + rarity mult + roll | 1-1.5j | — | **1-1.5j** |
| 3 | Sprint 2bis | Tooltips + couleurs + comparaison | — | 0.5j | **0.5j** |
| 4a | Sprint 3A | Panoplies simples (si focus PvE/loot) | 0.5j | 0.25j | **0.75j** |
| 4b | Sprint 4 | Duel UI (si focus PvP) | — | 0.5j | **0.5j** |
| 5 | Sprint 3B | Uniques passifs | 0.5j | 0.25j | **0.75j** |
| 6 | — | Uniques à procs complexes | 1j | 0.5j | **1.5j** |
| 7 | Sprint 5 | Enhancement/Crafting | 1-2j | 0.5j | **1.5-2.5j** |

**MVP Launch (Sprints 1 + 2 + 2bis) : ~2-2.5 jours**
**Launch confort (+ Sprint 3A ou 4) : ~3-3.5 jours**
**Complet (tout sauf enhancement) : ~5-6 jours**

---

## Dépendances entre Sprints

```
Sprint 1 (Penetration)       Sprint 4 (Duel UI)
    │                              │
    │  Indépendants ──────────────┘
    │
    ▼
Sprint 2 (Affixes + rarity)
    │
    ├──► Sprint 2bis (Tooltips/comparaison)
    │
    ├──► Sprint 3A (Panoplies simples)
    │
    └──► Sprint 3B (Uniques passifs)
              │
              ├──► Uniques à procs complexes (post-launch)
              │
              └──► Sprint 5 (Enhancement) (post-launch)
```

**Sprint 1 et Sprint 4 sont indépendants** — peuvent être faits en parallèle.
**Sprint 2bis dépend de Sprint 2** — afficher des affixes requiert qu'ils existent.
**Sprint 3 dépend de Sprint 2** — les panoplies et uniques sont des items avec affixes.
**Sprint 5 dépend de tout le reste.**

---

## Risques Identifiés

### Risque 1 — Incohérence formule de pénétration

~~`definitions.json` dit pourcentage, `combat.json` dit flat. **Décision CTO requise** avant implémentation.~~

**RÉSOLU :** CTO a choisi Option B (pourcentage). Mettre à jour `combat.json` pour aligner.

### Risque 2 — Sérialisation des affixes (CRITIQUE)

Les affixes sont stockés dans `ItemInstance.custom_data` (JSON blob). Si le format change, migration requise.

**Décision CTO : Définir le schema stable maintenant.** Format canonique :

```json
{
    "rarity": "rare",
    "base_mult": 1.25,
    "affixes": [
        {"id": "pre_brutal", "value": 5},
        {"id": "suf_vigor", "value": 35}
    ],
    "unique": {
        "id": "",
        "rank": 0
    },
    "set_id": "",
    "enhancement": {
        "level": 0
    },
    "crafted_substats": []
}
```

Tous les champs présents dès le début, même vides. Ça évite les migrations futures.

### Risque 3 — Performance du LootRoller

Avec affixes + uniques + panoplies, chaque monster kill fait ~5-10 rolls RNG. À 10,000 CCU avec combats fréquents, le LootRoller doit rester < 1ms. **Benchmark nécessaire.**

### Risque 4 — Unique procs dans le tick loop (VALIDÉ CRITIQUE par CTO)

Les procs d'uniques (on_hit, on_block, etc.) s'exécutent dans le tick loop 10Hz. Si un proc déclenche un autre proc → boucle infinie potentielle.

**Règles fermes (CTO) :**
- `max_procs_per_tick` obligatoire
- `internal_cooldown` sur chaque proc
- **Un proc ne peut PAS reproc lui-même**
- **Pas de chaînes infinies** (proc A → proc B → proc A interdit)
- Commencer par uniques **passifs** et procs **très simples avec cooldown strict**
- Procs exotiques = post-launch

### Risque 5 — Économie déstabilisée

Les affixes augmentent la variance de puissance des items. Un Legendary avec 4 affixes parfaits peut être beaucoup plus fort qu'attendu. **Les caps de stats (crit 100%, armor_pen 70%, DR 75%) doivent s'appliquer APRÈS les bonus d'affixes.**

---

## Tests de Validation par Sprint

### Sprint 1 — Penetration
| Test | Attendu |
|------|---------|
| Archer (5 armor_pen) vs cible 100 armor | Dégâts > dégâts sans pen |
| Mage (5 magic_pen) vs cible 100 magic_resist | Dégâts > dégâts sans pen |
| 70 armor_pen vs 100 armor | effective_armor = 30 (pourcentage) ou 30 (flat) |
| 0 armor_pen vs 100 armor | Même résultat qu'avant le patch |

### Sprint 2 — Affixes
| Test | Attendu |
|------|---------|
| Kill monstre danger_1 | Drop Common (0-1 affix) |
| Kill boss danger_6 | Drop possible Legendary (3-4 affixes) |
| Item Rare avec 2 affixes | Stats de base × 1.25 + 2 affixes visibles |
| Pas de doublon d'affix | Jamais 2x le même affix_id sur un item |
| Affixe level-gated | `pre_brutal` (lvl 11+) jamais sur item bracket b1 |

### Sprint 3 — Panoplies & Uniques
| Test | Attendu |
|------|---------|
| Équiper 2 pièces du set Kesher | Bonus lifesteal + spell_vamp actif |
| Déséquiper 1 pièce | Bonus désactivé |
| Drop unique Dam Rishon | Effet proc visible, substats random |
| Unique rang 4 vs rang 1 | Valeurs d'effet × 1.6 vs × 0.7 |

### Sprint 4 — Duel
| Test | Attendu |
|------|---------|
| Envoyer un duel challenge | Adversaire reçoit popup |
| Accepter le duel | Room combat créée, les deux joueurs y entrent |
| Gagner le duel | Elo mis à jour, DUEL_ENDED reçu |
| Aller offline avec duel pending | Challenge nettoyé côté serveur |

---

## Checklist Go/No-Go (validée CTO)

### MVP Launch (obligatoire)

| Condition | Sprint | Statut |
|-----------|--------|--------|
| Penetration dans DamageCalculator (formule %) | 1 | ⬜ À faire |
| Affixes fonctionnels (roll serveur) | 2 | ⬜ À faire |
| Rarity multiplier appliqué aux stats de base | 2 | ⬜ À faire |
| Schema custom_data stable défini | 2 | ⬜ À faire |
| Couleurs de rareté dans l'inventaire | 2bis | ⬜ À faire |
| Tooltip avec affixes visibles | 2bis | ⬜ À faire |
| Comparaison simple current vs new | 2bis | ⬜ À faire |

### Launch Confort (recommandé, pas bloquant)

| Condition | Sprint | Statut |
|-----------|--------|--------|
| Panoplies simples (bonus passifs) | 3A | ⬜ Optionnel |
| Duel UI (popup + ready screen) | 4 | ⬜ Optionnel |

### Post-Launch

| Condition | Sprint | Statut |
|-----------|--------|--------|
| Uniques passifs | 3B | ⬜ Après launch |
| Uniques à procs complexes (avec cooldown strict) | — | ⬜ Après launch |
| Enhancement / Crafting | 5 | ⬜ Après launch |

---

**MVP Launch : Sprints 1 + 2 + 2bis complétés (~2-2.5 jours).**
**Launch confort : + Sprint 3A ou 4 selon focus produit (~3-3.5 jours).**

> Le joueur doit sentir immédiatement : pénétration fonctionnelle, rareté qui change les stats, affixes visibles, drops qui donnent envie d'équiper/comparer. C'est ça le coeur du loot loop.

---

*Plan généré par Claude Code — audit automatisé du codebase Kanarion Online.*
*Validé par CTO — 2026-03-10.*
