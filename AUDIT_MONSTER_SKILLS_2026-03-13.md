# Audit Monster Skills — 2026-03-13

## Etat actuel

### Archétypes existants (8 rôles, 44 skills)
Chaque archétype a 4 pool + 1 signature = 5 skills.

| Archétype | Pool skills | Signature | Feeling combat |
|-----------|-------------|-----------|----------------|
| **brute** | heavy_slam, cleave (AoE+bleed), charge (col+knockback), execute | ground_slam (cross+knockdown) | OK — varié |
| **assassin** | quick_strike, poison_blade (DoT), shadow_strike (backline), ambush (+crit) | death_mark (+50% dmg taken) | OK — varié |
| **tank** | shield_bash (stun), defensive_stance (+DEF), taunt_roar (row_3), shield_wall (+DR+block) | fortress (DEF+CC immune+reflect) | OK — varié |
| **healer** | heal (single), smite (dmg), group_heal (row_3), dispel (cleanse) | resurrection (revive) | OK |
| **support** | haste (+speed ally), weaken (-ATK), shield_barrier (shield ally), dispel_magic (purge enemy) | bloodlust (+ATK +speed all) | OK |
| **artillery** | fire_bolt, fireball (rect_2x2+burn), lightning_bolt (chain_3), frost_nova (AoE+freeze) | meteor (rect_2x3, must interrupt) | OK — le plus varié |
| **controller** | shackle (stun), slow (row_3), fear (row_3), silence | mind_control (charm, must interrupt) | OK |
| **berserker** | wild_swing, blood_frenzy (self -HP +ATK), rampage (row_3), execution (+dmg low HP) | blood_ritual (drop 10% HP, mega buff) | OK |

### Basic skills (4 — le problème)
| Skill | Scaling | Pattern | CC/Effet |
|-------|---------|---------|----------|
| skill_mob_bite | 100% ATK | single | rien |
| skill_mob_slam | 110% ATK | single | rien |
| skill_mob_shoot | 95% ATK | single | rien |
| skill_mob_slash | 105% ATK | single | rien |

**Problème :** Les 4 sont identiques — single target, physical, no effect. Que le monstre soit un rat ou un chevalier, le filler est le même. C'est ce qui rend les combats répétitifs.

### Distribution monstres par rôle (79 total)
| Rôle | Monstres | % |
|------|----------|---|
| brute | 20 | 25% |
| assassin | 16 | 20% |
| tank | 13 | 16% |
| tactician | 9 | 11% |
| support | 8 | 10% |
| artillery | 7 | 9% |
| healer | 6 | 8% |

**Observation :** brute + assassin = 45%. Si on ne différencie pas leurs skills, la moitié des combats se ressemble.

---

## Regles de design

### Budget de complexité par tier
| Tier monstre | Effets notables max | Exemple |
|-------------|---------------------|---------|
| **normal** | 0 à 1 | hit simple OU hit + petit bleed |
| **elite** | 1 à 2 | hit + bleed + AoE |
| **boss** | plusieurs | vraie mécanique, patterns forts |

Les basic skills qu'on ajoute sont des skills de **tier normal**. Sobriété obligatoire.

### Effets autorisés sur les basics monstres (liste fermée)
| Catégorie | Effets OK |
|-----------|-----------|
| DoT léger | bleed (1 stack), poison (1 stack) |
| Debuff stat | atk_down, def_down (petit %, courte durée) |
| CC léger | slow (courte durée) |
| Defensif self | DR self (petit %, courte durée) |
| Soin | heal single allié (faible) |
| Buff allié | +ATK single allié (faible, courte durée) |

**Interdit sur les basics normaux :** stun, silence, confusion, fear, gros heal groupe, cleanse, shield, lifesteal, drain, multi-layer effects.
Ces effets restent réservés aux **archetype pool skills** (déjà existants) et aux **boss signatures**.

### Assignation déterministe — kits par rôle
Chaque rôle a un **kit de 2 basics** (pas plus). Chaque monstre du rôle reçoit :
- **basic_1** : toujours assigné (le filler principal du rôle)
- **basic_2** : assigné si le monstre a `danger_level >= 2` ou est elite/boss

Pas de tirage aléatoire. Même monstre = même kit = joueur apprend les ennemis.

Les 4 anciens basic skills (`bite`, `slam`, `shoot`, `slash`) restent comme **fallback** pour les monstres sans rôle clair ou `danger_level 0`.

### Distinction healer vs support (pas de chevauchement)
| Rôle | Identité basics | Ce qu'il NE fait PAS |
|------|-----------------|----------------------|
| **healer** | petit soin mono + petit dps | pas de buff, pas de cleanse, pas de shield |
| **support** | petit buff allié + petit debuff ennemi | pas de vrai soin |

---

## Plan de correction

### Etape 1 — Ajouter 2 basic skills par rôle (PRIORITE)

**+16 skills** (8 rôles × 2 basics). Inspirés de skills joueurs, renommés, simplifiés, 1 effet max.

#### Brute — 2 basics (pression front simple)
| ID | Nom FR / EN | Effet | Pourquoi |
|----|-------------|-------|----------|
| `skill_mob_brute_smash` | Fracas / Smash | 120% ATK single + 1 bleed | Pression + DoT léger, identité "coups lourds" |
| `skill_mob_brute_sweep` | Balayage / Sweep | 100% ATK row_2 | AoE faible sans effet, pression de zone |

#### Assassin — 2 basics (mono-cible rapide)
| ID | Nom FR / EN | Effet | Pourquoi |
|----|-------------|-------|----------|
| `skill_mob_assassin_lunge` | Bond / Lunge | 130% ATK single | Hit rapide, pas d'effet (CD court) |
| `skill_mob_assassin_venom` | Morsure Venimeuse / Venom Bite | 100% ATK single + 1 poison | Pression DoT, identité "vicieux" |

#### Tank — 2 basics (contrôle + survie)
| ID | Nom FR / EN | Effet | Pourquoi |
|----|-------------|-------|----------|
| `skill_mob_tank_slam` | Coup Pesant / Heavy Blow | 80% ATK single + slow 3s | Ralentit, pas de stun (stun = archetype pool) |
| `skill_mob_tank_brace` | Posture Ferme / Brace | self +20% DR 5s | Survie simple |

#### Healer — 2 basics (soin ponctuel + petit dps)
| ID | Nom FR / EN | Effet | Pourquoi |
|----|-------------|-------|----------|
| `skill_mob_healer_mend` | Soin Mineur / Minor Mend | heal 80% MAG single allié | Petit soin, pas oppressant |
| `skill_mob_healer_bolt` | Trait Sacré / Sacred Bolt | 90% MAG single | DPS pur, pas d'effet (le healer doit aussi taper) |

#### Support — 2 basics (buff allié + debuff ennemi)
| ID | Nom FR / EN | Effet | Pourquoi |
|----|-------------|-------|----------|
| `skill_mob_support_bolster` | Renforcement / Bolster | +15% ATK 1 allié 5s | Buff simple, distingue du healer |
| `skill_mob_support_hex` | Malédiction / Hex | 60% MAG single + -15% ATK 5s | Debuff simple |

#### Artillery — 2 basics (dps magique)
| ID | Nom FR / EN | Effet | Pourquoi |
|----|-------------|-------|----------|
| `skill_mob_artillery_bolt` | Trait de Feu / Fire Bolt | 110% MAG single | DPS simple |
| `skill_mob_artillery_barrage` | Salve / Barrage | 80% MAG row_2 | AoE faible, pression de zone |

#### Controller — 2 basics (CC léger)
| ID | Nom FR / EN | Effet | Pourquoi |
|----|-------------|-------|----------|
| `skill_mob_controller_jinx` | Maléfice / Jinx | 70% MAG single + slow 3s | CC léger (pas confusion — trop fort pour un basic) |
| `skill_mob_controller_zap` | Décharge / Zap | 90% MAG single | DPS simple (les vrais CC sont dans le pool archetype) |

#### Berserker — 2 basics (agressivité conditionnelle)
| ID | Nom FR / EN | Effet | Pourquoi |
|----|-------------|-------|----------|
| `skill_mob_berserker_rage_hit` | Frappe Enragée / Rage Hit | 130% ATK single, +30% si <50% HP | Conditionnel simple |
| `skill_mob_berserker_rend` | Déchirure / Rend | 110% ATK single + 1 bleed | DoT léger |

**Tactician** n'a pas de basics propres — il utilise le pool controller (CC léger) car son identité vient de l'IA (coordination, interrupt priority), pas de ses fillers.

---

### Etape 2 — Normaliser effects[]

Migrer les champs custom (`applies_bleed_stacks`, `mana_steal_percent`, etc.) vers des entrées `effects[]` standardisées. Skills joueurs ET monstres. Pipeline unique côté serveur.

**Quasi obligatoire** après l'étape 1 — tant que les effets sont répartis entre champs custom et `effects[]`, risque d'incohérences.

---

### Etape 3 — Corriger les ~15 medium issues du skill audit joueur

Incohérences description/data, scaling manquants. Liste à générer après étape 1.

---

### Etape 4 — Boss signatures uniques

Donner aux boss nommés des mécaniques uniques au lieu de juste des stats gonflées.

| Boss | Mécanique proposée |
|------|--------------------|
| mob_tortue_de_pierre | **Carapace** : à 50% HP, gagne 80% DR pendant 5s + taunt all |
| mob_cerf_obscur | **Charge Obscure** : dash vers le healer + silence 3s |
| mob_golem | **Sismique** : tous les 3 cast, AoE cross obligatoire |
| mob_spider_queen | **Toile** : slow 50% sur rect_2x3, empêche le cleanse pendant 4s |

A designer après que la base (étapes 1-3) soit stable.

---

### Etape 5 — Check passives innées monstres

Vérifier si les passives monster (`monster_archetypes.json`) sont cohérentes avec les rôles et les boss mécaniques.

---

## Priorisation

```
1. Basic skills par rôle (+16 skills)    ← diversifie 80% des combats
2. Normaliser effects[]                  ← cohérence pipeline serveur
3. Medium issues skill audit joueur      ← polish
4. Boss signatures                       ← endgame feel
5. Check passives innées                 ← équilibrage fin
```

## Impact attendu

- **Combats normaux** : un pack brute+assassin+tank aura des skills visiblement différents (bleed vs poison vs slow+DR)
- **Lisibilité** : le joueur identifie le rôle en quelques secondes (le tank ralentit et se buff, l'assassin empoisonne, le brute fait saigner en AoE)
- **Healer vs Support** : le joueur sent la différence (un soigne, l'autre buff/debuff)
- **Apprentissage** : même monstre = même kit = le joueur apprend les ennemis
- **Zéro risque** : les anciens basic skills restent comme fallback, les archetype pool skills ne changent pas
