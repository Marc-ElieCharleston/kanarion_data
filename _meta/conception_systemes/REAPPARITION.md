# Réapparition des monstres du monde ouvert : design (2026-10-13)

Lecture seule. Back lu sur `main` (arbre de travail = main), data sur `master` + `vac_collections`.
Références `fichier:ligne` dans `kanarion_back` sauf mention contraire.

---

## 1. Ce qui existe aujourd'hui

### 1.1 Génération au démarrage (une seule fois)
- `services/presence/src/presence_service.cpp:4119` `load_and_init_zones()` lit `world/zones.json`.
  Havreden (`village`) passe par la branche **multi-bandes** `spawn_areas[]` (`:4645`) : 21 aires `mz_*`
  (`id`, `count`, `level_range`, `max_stars`, `bounds`, `mobs[{id,weight}]`). Aucune n'a `elite_pool` ni `boss`.
- `count` = nombre de **monstres**, pas de meutes : la boucle `while (remaining > 0)` (`:4819`) tire une
  position (rejet : hors `safe_polygon`, dans `area_limit`, 48 essais, `:4828-4851`), une étoile
  (`roll_star_level`, poids `game.json spawner.star_roll_weights` = 15/32/28/15/7/3, plafond `max_stars`
  de l'aire `:4864`), une taille de meute (`encounter_stars.json monster_count` : 0★ 1-2, 1★ 2, 2★ 2-3,
  3★ 3-4, 4★ 4-6, 5★ 9-10), puis élites/boss selon `monster_variants.json star_system.packs`
  (0 ici car pas d'`elite_pool`/`boss`). `remaining -= pack_count` (`:5093`).
- Total Havreden : **806 monstres ≈ 290 meutes** (taille moyenne ≈ 2,7). Chaque meute = un
  `MonsterInstance` leader + `pack_members` cachés (`world/monster_world.hpp:37-77`).
- `MonsterWorld::init_zone` (`monster_world.cpp:66`) écrit chaque meute dans le hash Redis
  `world:<wi>:zone:<z>:monsters` et le cache local. Au redémarrage tout est régénéré plein.

### 1.2 Engagement (clic sur une meute)
- `presence_service.cpp:5431-5476` : la meute doit être `ALIVE`, à ≤ 500 px du joueur, puis verrou Redis
  `SET NX PX 90000` `world:<wi>:monster_lock:<id>` (`:5467`) → refus « Monster already engaged » sinon.
- `on_monster_entered_combat` (`monster_world.cpp:296`) passe la meute `IN_COMBAT` et **la fait disparaître
  pour tout le monde** (`MONSTER_DESPAWNED`, « option A Dofus »).
- Une salle de combat est créée (`max_players = kWorldCombatMaxPlayers = 10`, `:66` et `:5596`) et un
  **marqueur de combat** est posé à la place de la meute (`:5650-5702`, `locked=false`,
  `spectate_allowed=true`, `max_players=10`) : les autres voient la bulle et peuvent **rejoindre/regarder**
  le combat (la meute n'est donc pas partagée en tant que monstre, mais le combat l'est). Je n'ai pas
  relu le chemin client de « rejoindre ».
- Échec de création de salle → verrou relâché + `on_monster_combat_failed` → `ALIVE` (`:5634-5641`).

### 1.3 Mort, défaite et réapparition
- Combat → `handle_world_monster_died` (`presence_service.cpp:5715`) → `on_monsters_died`
  (`monster_world.cpp:335`) : `DEAD`, délai = `roll_respawn_time_ms()` = **uniforme 60-180 s**
  (`monster_world.cpp:41`, `presence.json respawn_time_min/max_seconds`), multiplié par le facteur
  Fissure si une invasion est active sur l'aire (`:384-388`, `fissure_world.cpp:203`). Ajout à la ZSET
  `world:<wi>:respawn_queue` (score = `respawn_at_ms`).
- Défaite/abandon : la meute revient `ALIVE` au même endroit (`presence_service.cpp:5762-5768`).
- `tick()` toutes les **2 s** (`config.hpp:68`, `on_respawn_tick` `:5172`) : `ZPOPMIN` 10 éléments
  max (`monster_world.cpp:125`) → `respawn_monster` (`:502`).
- `respawn_monster` + `pack_generator_` (`presence_service.cpp:5108-5157`) : **clone** la meute :
  même composition, **même position** (`m.x = old_monster->x`, `:540`), **même étoile** (sauf donjons
  `fixed_groups` qui re-tirent, et bonus Fissure). Nouvel `instance_id`, broadcast `MONSTER_SPAWNED`.

### 1.4 Plafonds et données mortes
- Aucun plafond dynamique : la population est fixe (≈ 290 meutes), un emplacement = une meute, à vie.
- Aucun lien avec le nombre de joueurs, le niveau du tueur, le rang de menace, la zone.
- **Données lues par personne** : `village.spawn_config` (`max_active_monsters 1708`, `max_packs 200`,
  `respawn_delay_ms 15000`, `spawn_interval_ms 3000`) n'est lu que pour les zones « plates »
  (`:4729`), pas pour `spawn_areas` ; `game.json spawner.respawn_time_min/max` (90/180),
  `max_active_monsters`, `lazy_load_distance` : aucun lecteur. La vraie valeur est `presence.json` 60-180 s.
- `MonsterState::RESPAWNING` existe (`monster_world.hpp:26`) mais n'est jamais affecté.
- `prefix_id` (« corrupted », « angry ») est transporté jusqu'au client mais **le combat ne le lit pas**.
- Débit max de réapparition : 10 par tick de 2 s = 5/s, largement suffisant.

### 1.5 Conséquences
1. Une meute 5★ reste 5★ au même point pour toujours ; une meute 0★ aussi.
2. Camping trivial : la meute revient exactement là où elle est morte, devant le joueur.
3. 10 joueurs ou 200 joueurs dans les rats : même population, même délai.
4. Un lv60 qui nettoie les rats pour du matériau vide la zone des débutants pendant 1-3 min.

---

## 2. Proposition

### 2.1 Principe
`délai = base(rang) × zone(classe) × étoile(★) × pression(aire) × fissure × jitter(±20 %)`,
borné par `[min_ms, max_ms]` du rang. Le jitter évite les vagues synchronisées.
La population cible d'une aire suit le nombre de joueurs présents (emplacements dormants).
La position de réapparition est re-tirée, loin des joueurs. L'étoile et la composition sont re-tirées.

### 2.2 Rang de la meute (le plus lent l'emporte)
Rang = `threat_tier` le plus élevé parmi leader + membres (`monsters.json` : 14 fodder, 102 standard,
43 tough, 22 elite, 19 boss), relevé par `is_elite` / `is_boss` des membres. Surcharge par monstre
possible (les R/N/L du carnet `vac_collections:_meta/carnet/carte_monstres.md`).

| Rang | Base | Bornes | Raison |
|---|---|---|---|
| fodder | 25 s | 15-45 s | lapins/larves, matériaux de métier bas niveau |
| standard | 45 s | 25-90 s | le gros de la faune |
| tough | 90 s | 50-180 s | meneurs, tanks lourds (Loup Meneur, Bouc…) |
| elite | 7 min | 4-15 min | Reine Araignée, Chef de Gang… : rare, attendu |
| boss (de terrain) | 35 min | 25-50 min | événement, groupe requis ; minuterie persistante |

### 2.3 Classe de zone
| Classe | Mult. | Aires (à confirmer, d'après les tags R/N/L du carnet) |
|---|---|---|
| `farm` | ×0,6 | mz_rats_1_8, mz_scarabees_3_8, mz_sanglier_8_15, mz_prairie_10_20, mz_hyene_9_20, mz_loup_13_23, mz_foret_12_26, mz_marecage_20_30 |
| `normal` | ×1,0 | mz_sangliers-loups_6_15, mz_wolf_25-32, mz_spider_25_30, mz_brigand_35-45, mz_rats_corrompu_40-50, mz_gobelins_50_60, mz_marais_corrompu_60_70, mz_low_demon_61_70, mz_low_abyssal_70_80, mz_demon_80_100, mz_abyssal_85_100 |
| `elite` | ×1,5 | mz_taureaux_16-25_elite, mz_fanatique_45_60_elite |

Exemple : meute standard 2★ en farm → 45 × 0,6 × 1,0 = **27 s** (±20 %). Élite en zone élite → 10,5 min.

### 2.4 Étoiles
- **Re-tirage à chaque réapparition** (poids globaux, plafond `max_stars` de l'aire) : fini le 5★ figé.
- Multiplicateur de délai (une grosse meute vaut plus d'XP/butin et retire plus de monstres d'un coup) :
  0★ ×0,8 · 1★ ×0,9 · 2★ ×1,0 · 3★ ×1,2 · 4★ ×1,5 · 5★ ×2,0.
- Le budget d'aire reste en **monstres** (`count`) : une 5★ consomme 9-10 places, donc l'aire garde la
  même masse de monstres quelle que soit la répartition.

### 2.5 Pression de l'aire (le levier « trop farmée / vide »)
Suivi par aire (fenêtre glissante 5 min) : meutes vivantes / cible, kills par minute, joueurs présents
(positions `player_states_` testées contre les `bounds`, recalcul toutes les 10 s).

| Situation | Facteur | Raison |
|---|---|---|
| Aucun joueur dans l'aire depuis 60 s | ×0,25 | remplir sans que personne ne le voie, l'aire est pleine à l'arrivée |
| Vivantes < 40 % de la cible | ×0,5 | **plancher** : les débutants trouvent toujours des monstres |
| Normal | ×1,0 | |
| Kills/min par joueur présent > 2× le débit nominal (`farm` exclu du durcissement) | ×1,25 → ×2,0 max (`normal`/`elite`) | freine l'enchaînement mécanique et les bots sur les aires rentables |
| Tueur ≥ `level_range[1]` + 10 | ×0,5 sur cette meute | un joueur avancé qui récolte du matériau ne prive pas les débutants |

En `farm`, le facteur est plafonné à ×1,0 : on n'y pénalise jamais la récolte.

### 2.6 Population selon le nombre de joueurs
- Cible de l'aire : `cible = base × min(1 + 0,04 × joueurs_présents, 1,75)` ; `base` = `count`
  autorisé par le bureau (vérité) converti en meutes.
- Plafond de densité anti-encombrement mobile : ≤ 4 meutes / Mpx² (écran ≈ 1,1 Mpx² au zoom min 1,6
  → 3-4 meutes visibles en farm). Aujourd'hui mz_rats ≈ 3,4 meutes/Mpx², mz_prairie ≈ 1,4.
- Implémentation : au démarrage on crée `base × 1,75` emplacements ; les surplus naissent **DORMANT**
  (invisibles, hors file). Un contrôleur (10 s) réveille un dormant si `vivantes + en_file < cible`, et
  n'en fait **jamais** disparaître un vivant : un emplacement en trop qui meurt redevient dormant.
- Ordre de grandeur (combat ≈ 60 s + 15 s de marche, hypothèse) : mz_rats ≈ 27 meutes, 10 joueurs
  solo = 10 kills/min × 27 s ≈ 4,5 meutes mortes → 83 % vivantes. 40 joueurs : cible ×1,75 = 47 meutes,
  40 kills/min × 27 s = 18 mortes → 62 % vivantes, plancher non déclenché. Le design tient sans réglage.

### 2.7 Élites et rares
- Emplacement élite par aire (`elite_slots`, 1 par défaut en `normal`/`elite`, 0 en `farm`) : leader tiré
  parmi les mobs `threat_tier` elite du pool de l'aire (spider_queen, gang_leader, abyssal_archon…),
  réapparition **aléatoire dans la fenêtre** 4-15 min (pas d'horaire fixe = pas de camping de la minute).
- « Rare » : à chaque réapparition standard, 1 % (farm) / 2 % (autres) de chances de forcer l'étoile au
  `max_stars` de l'aire ; au plus 1 rare vivante par aire, recharge 10 min. (On n'utilise pas
  `prefix_id`, que le combat ignore.)

### 2.8 Boss de terrain
- Emplacements fixes déclarés dans la config (aire + liste de points ou « au hasard dans l'aire »).
- Minuterie 25-50 min **persistée dans Redis** (`world:<wi>:boss_next:<slot_id>`) : un redémarrage
  ne fait pas réapparaître tous les boss d'un coup, et ne les remet pas en attente non plus.
- Optionnel (phase 4) : message système de zone « X rôde à nouveau » quand le boss revient.

### 2.9 Anti-camping : position de réapparition
- Re-tirage dans les `bounds` de l'aire avec les mêmes filtres qu'au démarrage (sanctuaire,
  `area_limit`), plus : ≥ 600 px de **tout** joueur (≈ hors écran, la fenêtre AOI est 768 px),
  ≥ 250 px des autres meutes vivantes. 24 essais, sinon le candidat le plus éloigné des joueurs.
- Élites/boss : ≥ 900 px ; points autorisés si déclarés.
- Farm : 400 px seulement (les monstres « vivent » autour des joueurs, la zone reste animée).

---

## 3. Où vit la donnée

**Nouveau fichier `kanarion_database/config/monster_respawn.json`** (le bureau édite `world/zones.json` :
on n'y met que des surcharges optionnelles). Priorité : `zones.json spawn_areas[].respawn` >
`monster_respawn.json areas[id]` > `defaults`. Fichier absent → comportement actuel 60-180 s avec un
`warn` (déploiement sans ordre imposé).

```json
{
  "_meta": { "version": 1, "owner": "presence", "note": "Delais en secondes. Voir _meta/carnet/monstres.md" },
  "jitter_pct": 20,
  "tiers": {
    "fodder":   { "base_s": 25,   "min_s": 15,   "max_s": 45 },
    "standard": { "base_s": 45,   "min_s": 25,   "max_s": 90 },
    "tough":    { "base_s": 90,   "min_s": 50,   "max_s": 180 },
    "elite":    { "base_s": 420,  "min_s": 240,  "max_s": 900 },
    "boss":     { "base_s": 2100, "min_s": 1500, "max_s": 3000 }
  },
  "zone_classes": {
    "farm":   { "delay_mult": 0.6, "pressure_max": 1.0, "respawn_min_player_dist": 400, "elite_slots": 0, "rare_chance": 0.01 },
    "normal": { "delay_mult": 1.0, "pressure_max": 2.0, "respawn_min_player_dist": 600, "elite_slots": 1, "rare_chance": 0.02 },
    "elite":  { "delay_mult": 1.5, "pressure_max": 2.0, "respawn_min_player_dist": 600, "elite_slots": 2, "rare_chance": 0.02 }
  },
  "star_delay_mult": [0.8, 0.9, 1.0, 1.2, 1.5, 2.0],
  "pressure": {
    "window_s": 300, "empty_after_s": 60, "empty_mult": 0.25,
    "floor_alive_ratio": 0.40, "floor_mult": 0.5,
    "overfarm_kills_per_player_min": 2.0,
    "high_level_gap": 10, "high_level_mult": 0.5
  },
  "population": { "per_player": 0.04, "max_mult": 1.75, "max_packs_per_mpx2": 4.0, "controller_period_s": 10 },
  "placement": { "attempts": 24, "min_pack_dist": 250, "elite_boss_min_player_dist": 900 },
  "rare": { "max_alive_per_area": 1, "cooldown_s": 600 },
  "default_zone_class": "normal",
  "areas": {
    "mz_rats_1_8":       { "zone_class": "farm" },
    "mz_scarabees_3_8":  { "zone_class": "farm" },
    "mz_prairie_10_20":  { "zone_class": "farm" },
    "mz_taureaux_16-25_elite": { "zone_class": "elite" },
    "mz_brigand_35-45":  { "zone_class": "normal",
                           "field_bosses": [ { "slot_id": "boss_bandit_warlord_route_sud",
                                               "monster_id": "boss_bandit_warlord", "level": 45,
                                               "points": [[3200, 9800], [3650, 10150]] } ] }
  },
  "monster_overrides": {
    "mob_wolf_packleader": { "tier": "tough" },
    "mob_lievre": { "tier": "fodder" }
  }
}
```

Surcharge optionnelle côté bureau, dans une aire de `zones.json` :
```json
{ "id": "mz_rats_1_8", "count": 55, "...": "...",
  "respawn": { "zone_class": "farm", "delay_mult": 0.8 } }
```
Garde-fou data : un test python (dossier tests du repo data) qui vérifie que chaque clé `areas` et
`field_bosses.monster_id` existe dans `zones.json` / `monsters.json`. Points de boss = coordonnées à
fournir (ceux de l'exemple sont fictifs).

---

## 4. Plan serveur

### 4.1 Fichiers
| Fichier | Changement |
|---|---|
| `services/presence/src/world/respawn_policy.{hpp,cpp}` (nouveau) | Logique **pure** : chargement config + surcharges, `tier_of(pack)`, `delay_ms(ctx, rng)`, facteurs étoile/zone/pression, bornes. Aucun Redis/NATS → testable. |
| `services/presence/src/world/area_population.{hpp,cpp}` (nouveau) | Stats par aire : vivantes, dormantes, kills fenêtrés, joueurs présents, dernier joueur vu ; calcul de la cible. |
| `services/presence/src/world/pack_factory.{hpp,cpp}` (nouveau) | **Extraction** du générateur de démarrage (`presence_service.cpp:4593-5095`, `AreaConfig` + tirage étoile/composition/position) pour le réutiliser à la réapparition. Garde `area_configs_` en mémoire. |
| `world/monster_world.{hpp,cpp}` | `roll_respawn_time_ms` → `RespawnDelayFunc` injectée (garde le facteur Fissure). `respawn_monster` : prend une nouvelle meute + position calculées HORS `world_mutex_`, re-vérifie `DEAD`, échange sous verrou. État `DORMANT` (ou réutiliser `RESPAWNING`, inutilisé). `on_monsters_died` reçoit le niveau du tueur. |
| `presence_service.cpp` | Charge `monster_respawn.json` dans `load_and_init_zones`, crée les emplacements dormants et boss, branche les callbacks, contrôleur de population dans `on_respawn_tick` (toutes les 5 ticks), instantané des positions joueurs pris **avant** `world_mutex_`. Niveau du tueur : à prendre de l'événement de mort (`MonsterDiedEvent` n'a pas de niveau aujourd'hui → soit champ ajouté en fin de table `monster.fbs`, soit lecture du niveau via presence/character). |
| `config/presence.json` + `config.hpp` | `respawn_time_*` devient le repli si le fichier data manque. |
| Data | `config/monster_respawn.json` ; retirer/annoter les champs morts (`village.spawn_config`, `game.json spawner.respawn_*`). |

### 4.2 Tests (ajouter à `services/presence/tests/CMakeLists.txt`, **vérifier le nombre de tests**)
- `test_respawn_policy.cpp` : délai par rang/classe/étoile, bornes min/max, jitter borné (graine fixe),
  plancher 40 %, zone vide ×0,25, tueur haut niveau ×0,5, `farm` jamais > ×1,0, surcharges zones.json >
  fichier > défauts, fichier absent → 60-180 s.
- `test_respawn_placement.cpp` : jamais dans le sanctuaire ni hors `area_limit`, ≥ distance joueurs,
  repli « le plus loin » quand l'aire est saturée de joueurs.
- `test_pack_factory.cpp` : même distribution au démarrage et en réapparition, `max_stars` respecté,
  budget en monstres conservé.
- `test_area_population.cpp` : cible suit les joueurs, dormant réveillé / jamais de vivant supprimé.
- `test_monster_world.cpp` + `test_monster_world_concurrency.cpp` : réapparition avec nouvelle position
  et nouvelle étoile, DORMANT invisible dans `get_zone_monsters*`, course mort/réapparition/engagement
  sous TSan.
- Boss : minuterie Redis respectée après « redémarrage » simulé.
- Test data : cohérence `monster_respawn.json` ↔ `zones.json` / `monsters.json`.

### 4.3 Risques
- **Ordre des verrous** : positions joueurs (map `player_states_`) et `world_mutex_` ; prendre
  l'instantané avant, jamais l'un dans l'autre. Le callback de meute appelle déjà Fissure sous verrou.
- **Extraction du générateur** (≈ 500 lignes) : risque de dériver les tirages du démarrage → le
  test `pack_factory` doit figer la distribution avant/après.
- **Économie** : réapparition plus rapide en farm = plus d'XP/or/matériaux ; à recouper avec l'audit
  or (contrats déjà robinet sans plafond). Les facteurs farm sont dans la donnée, réglables sans déploiement.
- File Redis restante après redémarrage : membres orphelins → `warn` déjà géré (`monster_world.cpp:507`).
- Un emplacement qui ne trouve pas de place (aire minuscule pleine de joueurs) : repli « le plus loin ».
- Sous-module `kanarion-meta` : pousser la data avant le back (règle habituelle).

### 4.4 Effort (par phases livrables séparément)
| Phase | Contenu | Effort |
|---|---|---|
| 1 | Fichier config + `respawn_policy` (rang, classe, étoile, jitter) branché sur le délai | **S** |
| 2 | `pack_factory` : re-tirage étoile/composition + position anti-camping | **M** |
| 3 | Pression d'aire, plancher, zone vide, tueur haut niveau, population selon joueurs (dormants) | **M** |
| 4 | Emplacements élites/rares, boss de terrain + minuterie Redis | **M** |
| Total | | **L** (≈ 6-9 jours) |

### 4.5 Client
Aucun changement obligatoire : `MONSTER_SPAWNED` porte déjà `x/y` et un nouvel `instance_id`,
une meute qui réapparaît ailleurs s'affiche normalement (`scripts/network/sync/monster_sync_manager.gd`).
Optionnels : fondu d'apparition (S) ; annonce de retour du boss (nouveau message ou message système de
chat, S-M) ; aucune minuterie affichée côté client (le serveur reste seul juge).
