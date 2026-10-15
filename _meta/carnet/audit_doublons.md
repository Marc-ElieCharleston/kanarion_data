# Audit des doublons : un fait, un seul endroit (2026-10-15)

Demandé par le propriétaire : « toutes les data dupliquées plutôt qu'à un seul endroit, pour éviter les
soucis plus tard ». Lecture seule de la data, du back et du client sur la branche `vac_audit-lot1`, où une
autre session corrige déjà les deux audits précédents. Cette note ne répète pas ces deux audits :
`audit_valeurs_en_dur.md` (13/10, code contre data) et `audit_data_morte.md` (14/10, data morte), tous deux
sur `vac_collections`. Principes : `architecture_data.md` (un fait = un propriétaire, pas de repli silencieux).

Vérifié à la main : PV/Souffle de départ, canaux de chat, rareté des empreintes, écart de niveau. Le reste
vient de trois recherches qui ont lu les deux copies ; revérifier chaque point avant de corriger.

## 1. Contradictions actives (à corriger d'abord)

### Serveur contre data
| # | Fait | Copies | Effet |
|---|---|---|---|
| S1 | PV / Souffle de départ | `character.yaml` starting_hp 100 / mp 50 (`character_manager.cpp:224-228`) vs `stats/class_base_stats.json` (guerrier 120/45, mage 80/85…) | tout personnage d'aventure naît à 100/50 (le tournoi passe par `compute_level_stats`). À vérifier : un recalcul au premier passage de niveau corrige-t-il ? |
| S2 | Canaux de chat | enum `channel.hpp` (GLOBAL 0, ZONE 1… SYSTEM 5) vs `game.json` chat_channels (world 0, say 1… sale 5, lfg 6) | le canal 5 est SYSTEM côté serveur et « vente » côté data |
| S3 | Rareté des empreintes | `combat_host.cpp:4172` 70 common / 25 rare / 4 epic / 1 legendary, jamais uncommon | des empreintes uncommon existent en data et ne tombent jamais. À recouper avec le commit data `0ac4ab6` (rareté 60/25/10/4/1) de l'autre session |
| S4 | Écart de niveau (XP / or) | replis `content_loader.cpp:1602` 3 / 0.2 / 0.95 et `loot_types.hpp:336` 5 / 0.10 / 0.90 vs `rewards.json` 5 / 0.2 / 0.95 (exemples de la data calculés avec 3) | trois jeux de valeurs ; rendre les champs obligatoires |
| S5 | Bonus de groupe en repli | `content_loader.cpp:1594` 0.055 vs `rewards.json` 0.125 | seulement si la clé manque ; rendre obligatoire |
| S6 | Déblocage tier 3 en repli | `character_manager.hpp:227` 40 vs `skill_system.json` 60 (l'économie n'a pas de repli) | deux lecteurs, deux comportements |
| S7 | Zone de retour de l'arène | `pvp_service.cpp:3995,4639` « desert_playtest » vs arène de Dargo au village | probable mauvais retour après un combat d'arène |
| S8 | Matchmaking donjon | `matchmaker.cpp:250` ids `dragon-lair`, `goblin-cave`… inexistants ; `matchmaking.json` 4 joueurs vs 10 | code mort ou faux |
| S9 | Coût en Souffle par niveau | défaut 0 serveur (`content_loader.cpp:437`) vs `skill_system.json` 4 ; formule copiée 5 fois en C++ | 5 sorts du Gardien sans le champ : le client affiche 74, le serveur prend 38 (voir C2) |
| S10 | Passifs chargés deux fois | `combat_host.cpp:6458` et `shared/gameplay/passive_loader.hpp` (ordre et `retired` différents) ; 6 classes en dur dans `innate_passive_processor.cpp:45` | divergence partielle |
| S11 | Rôles de placement en arène | `arena_tactics.hpp:20` vs `config/roles.json` | lame-sort, trickster, sous-classes soigneur et artisan placés différemment |
| S12 | Monnaies | `currency_manager.hpp:14` (gold, premium, pvp_tokens, dungeon_tokens) vs `items/currencies.json` (gold, diamonds compte, souffle_crystal, arena_tokens) ; 4 services écrivent les portefeuilles en SQL direct | modèle différent ; gros chantier |
| S13 | Duel | cooldown 60 s en data (non lu) vs limite de 5 défis par minute au serveur | règle différente |
| S14 | Max attaquants par cible | `combat.json` coordination (mort) et `monster_ai.json` (lu) | même valeur, supprimer la copie morte |

### Client contre data ou serveur
| # | Fait | Copies | Effet |
|---|---|---|---|
| C1 | Prix de vente des équipements | `item_database.gd:246` sell_price 1 par défaut | le client affiche 1 or. Le serveur de `vac_economy-fixes` envoie déjà `sell_value` dans l'inventaire : le client doit l'afficher |
| C2 | Souffle par niveau | `skill.gd:1658` défaut 4 | Gardien : coût affiché faux, `can_use` peut bloquer à tort (voir S9) |
| C3 | « Ignore la première ligne » des voleurs | `combat_system.gd:1887`, `combat_targeting.gd:392` | règle inventée par le client ; le serveur décide par sort (`ignore_los`) |
| C4 | Arme de départ du soigneur | `inventory_screen.gd:1739` sans `wpn_scepter_b1` (serveur `starter_weapon.hpp:29`) | la flèche du tutoriel ne pointe rien pour un soigneur |
| C5 | Objets fantômes | `item_database.gd:62` ~45 objets inventés (`sword_rusty`, `cons_hp_potion_small`…) | visibles dans la boutique de repli et la recherche HDV |
| C6 | Stats des monstres | `monster.gd:75` formule linéaire de `combat.json` monster_scaling (non lu serveur) | IA et menace client sur de fausses stats |
| C7 | Grille du sac | `inventory_screen.gd:39` MAX_SLOTS 80 vs sac 100 | cases 81-100 non dessinées |
| C8 | Fiche de stats | `stats_screen.gd:48` « RM augmente avec DEF » | faux : la RM suit la MAG |
| C9 | Téléport | `teleport_window.gd:114` 50 en dur ; `economy.json` 50 + distance ; `world_map.json` 10 + 5/zone ; serveur 50 en dur | trois sources |
| C10 | Échange | `trade_window.gd` 6 cases, 3 s ; `economy.json` niveau 10 | règles appliquées par le client seul, jamais par le serveur |
| C11 | Groupe plein | `party_manager.gd:416` compte les humains seuls | la data compte familiers et mercenaires |

### Data contre data
| # | Fait | Copies | Effet |
|---|---|---|---|
| D1 | Tour d'Asher | `world_map.json:115` niv. 16-20 (lu par le client) vs `dungeons.json` 60-100 (serveur), boss d'étage niv. 20 | à régler avec la fusion des Tours d'Asher (TODO) |
| D2 | Difficulté de donjon | `dungeons.json` modifiers easy…heroic (mort) vs `rewards.json` normal…inferno (lu) | noms et valeurs différents ; supprimer `modifiers` |
| D3 | Rôle d'une spec | `roles.json` vs `tournament_role_kits.json` (lu par l'économie) | martyr soigneur d'un côté, tank de l'autre |
| D4 | ai_role vers archétype | `monster_ai.json` _meta vs `monster_scaling_model.json` ; catalogue 7 rôles vs 11 | 3 écarts ; formation v2 sans 5 archétypes (67 monstres) |
| D5 | Scaling des monstres | `combat.json` monster_scaling, `monsters.json` balance_note vs modèle V2 | deux formules mortes (lue par le client, voir C6) |
| D6 | Niveaux de spawn | `monsters.json` level_range (non lu) vs aires de spawn de `zones.json` | 98 monstres en désaccord |
| D7 | Zones legacy zone_01…10 | `zones.json` lt_zone_*, `world_map.json`, 27 quêtes (`zone`) | niveaux différents, zones absentes de `zones[]` |
| D8 | Loot par zone | `zones.json` loot_tables / koro_pools (client seul) vs `rewards.json` + `loot_tables.json` | deux modèles d'or et de Koro |
| D9 | Noms des boss | `dungeons.json` / `world_map.json` vs `monsters.json` | « Chef » vs « Seigneur de Guerre Bandit », etc. |
| D10 | Couleurs et noms de rareté | 5 copies (`currencies`, `equipment_stats`, `equipment_scaling`, `loot_tables`, `familiar_balance`), aucune lue ; client en dur | valeurs différentes ; source = `equipment_scaling.rarity_system` |
| D11 | Rareté des pièces de panoplie | `panoplies.json` rarity_at_drop vs `loot_tables.json` piece_rarity (lu) | contradiction ; supprimer la première |
| D12 | Règle de cumul des statuts | `definitions.json` stacking_system (mort) vs `status_effects.json` canonical_grid | 10 % × 10 vs 5 % × 5 |
| D13 | Récompenses d'arène | `pvp.json` « pas de récompense » vs `rewards.json` arena_match (lu) | texte faux |
| D14 | Grille de combat | `game.json` dungeon_formats 4x5 (mort) vs combat_grids 10x6 | supprimer |
| D15 | Quêtes : deux titres | 6 quêtes ont title_/summary_ ET name_/description_ (contenu différent) | supprimer name_/description_ |
| D16 | rank_percent | `pet_books.json` dit « même échelle que Koro » mais les échelles diffèrent | corriger le texte |

## 2. Copies identiques aujourd'hui, sans garde (prochaine dérive)

- **Arbre des classes** (6 / 24 / 48) : `class_registry.json`, `_classes_index.json`, clés des skills.json, repli
  C++ `character_manager.cpp:30`, sous-classes en dur `quest_service.cpp:69`. Lus par des services différents.
- **Niveaux 20 / 60 / 100 et Koro 40** : 3 à 5 copies chacun (skill_system, progression, milestone_hints, game,
  tower, koro, quêtes, PNJ), lus par le serveur ou par le client selon la copie.
- **Listes en C++** : emplacements d'équipement (6 copies), raretés ordonnées (4, en partie corrigées sur
  `vac_economy-fixes` par `shared/domain/rarity.hpp`), armes de départ (2), quête de sous-classe, rat d'Aldric.
- **Valeurs serveur absentes de la data** : courrier (30 or, 30 jours, 10 pièces jointes), bonus fondateur
  1000 diamants, emplacements de personnage (5 / 15 / 500 / 1000 diamants), niveau max d'un sort 10,
  boucliers de l'arbre de passifs (6 s / 5 s), magnitudes de predation / predators_focus / berserk.
- **Client** : plafond de collection de familiers 50 (le serveur l'envoie déjà), respec, plafond de 3 contrats,
  coût de création de guilde et taille 30, niveaux max des sorts et passifs (replis 5, 10, 20), murmures.
- **Prix Koro** dans `npcs.json` (non lu), durée des nourritures (consumables et world_buffs), 48 pièces de
  tournoi (equipment et panoplies), ratio de revente 0.35 × 3 (non lu).
- **Tests qui figent une valeur de data** au lieu de la lire : storage, contract_limit, fissure, coffres, tour,
  keystones, enhancement.

## 3. Comptes et résumés périmés

`_summary` faux dans `npcs.json` (46 vs 83), `quests.json` (72 vs 147), `panoplies.json` (38 vs 33),
`monster_skills.json` (60 vs 134), `monsters.json` (71 vs 227), `dungeons.json` (2 vs 4). `CLAUDE.md` de la
data aussi (raretés des familiers, 134 archétypes, grille 4x5, 7 archétypes). Proposition : supprimer les
comptes écrits à la main, ou les faire générer et vérifier par la CI.

## 4. Copies générées (acceptables avec un `--check` en CI)

| Copie | Générateur | État | En CI |
|---|---|---|---|
| `koro_cards.json` | generate_koro_catalog.py | à jour | oui |
| `tower_floors.json` | generate_tower.py | à jour | oui |
| `pet_books.json` | gen_pet_books.py | **périmé : 560 écarts de description** | **non** |
| empreintes de `consumables.json` | gen_familiar_traces.py | à jour | non |
| monstres V2 (espèces, kits) | apply_monster_v2.py | à jour | non |
| familiers par espèce | apply_familiar_species.py | à jour | non |
| prix de revente PNJ | reprice_npc_resale.py | sur `vac_economy-fixes` | à ajouter |
| `content_hash` | hash_content.py | pre-commit + CI | oui |

`pet_books.json` est le risque n°1 de cette liste : la prochaine régénération écrase les textes corrigés à la
main, ou l'inverse. Ajouter tous les `--check` à la CI.

## 5. Déjà corrigé sur mes branches (`vac_economy-fixes`, non fusionnées)

Planches de contrats en dur (coffres et plafond lisent `contract_limits.boards`), replis de capacité sac et
banque (`economy.yaml` 100 / 1000 retirés), liste des raretés (header partagé), courbe de revente lue dans
`rewards.json`, prix de revente envoyé au client (`sell_value`).

## 6. Lots proposés

1. **Bugs visibles** (petits) : S1 PV de départ, S2 canaux, S3 empreintes, S7 arène, C2 + S9 Souffle par
   niveau, C3 voleurs, C4 arme du soigneur, C7 grille 80, C8 fiche RM.
2. **Replis serveur faux** → champs obligatoires : S4, S5, S6, S9 (et la formule de Souffle dans
   `skill_resolver.hpp` seulement).
3. **Data morte en double** : D2, D5, D11, D12, D13, D14, D15, `combat.json` coordination et monster_scaling,
   `monsters.json` level_range et base_xp, `world_map.json` dungeons, prix Koro des PNJ, `x_companion` répliques.
4. **Client qui recopie** : C1 (afficher `sell_value`), C5 objets fantômes, C6 stats monstres, C9 téléport,
   C10 échange (règles au serveur), plafonds envoyés par le serveur, code mort (`damage_resolver.gd`,
   `balance_config.gd`, `.tres` de classes).
5. **Tables uniques** : raretés (couleurs, noms, ordre) dans `equipment_scaling`, arbre des classes dans
   `class_registry.json`, niveaux de déblocage, emplacements d'équipement ; un check CI d'égalité pour chaque
   copie qui doit rester.
6. **Gros chantiers** à planifier : monnaies (S12), zones legacy et Tour d'Asher (D1, D7, D8), rôles (D3, D4, S11).

Coordination : l'autre session corrige les lots de `audit_data_morte.md` sur `vac_audit-lot1`. Lui passer cette
liste ou attendre qu'elle ait fini, pour ne pas toucher les mêmes fichiers en même temps.
