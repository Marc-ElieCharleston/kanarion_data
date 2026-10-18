# Élites/boss rares + mécaniques de cases (2026-10-18)

Note pour l'agent maison : corriger les données mortes (§1), puis implémenter §2 à §5. Design validé par l'owner le 2026-10-18.

## 1. Données jamais lues par le serveur (à brancher ou supprimer, règle « pas de doublon »)

- `entities/monster_variants.json` → `spawn_rules` (`prefix_spawn_chance` 0.15, `elite_spawn_chance` 0.02, `boss_spawn: "scripted_only"`) : jamais lu par le back. ATTENTION : le client le lit et **tire lui-même un préfixe** (`kanarion_client/scripts/actors/monsters/monster.gd:20-31, 315-323`) → aléatoire côté client, désynchronisé du serveur. À supprimer côté client ; si on garde les préfixes, le serveur décide.
- `prefix_id` : jamais affecté dans le back, seulement recopié (`presence_service.cpp`, génération de pack 4840-5065).
- `entities/boss_mechanics.json` (world_bosses, phases, aoe_patterns donut/checkerboard/random_row, mechanic_passives) : jamais chargé par le serveur (cf. `AUDIT_BOSS_MECHANIC_PASSIVES.md`). Le client le charge (`data_db.gd:194`) sans effet de gameplay. → Reprendre le vocabulaire utile dans §3 (targeting.json / monster_skills.json), puis supprimer le fichier et sa lecture client.
- `world/dungeons.json` → `phases` des boss : texte descriptif seulement, rien ne s'exécute.
- `config/monster_ai.json` → `boss_phases` : lu, mais multiplicateurs GLOBAUX (enraged/desperate) pour tous les boss, pas de changement de compétences.
- Balayage complet des clés JSON jamais citées dans le code back + client : **`donnees_jamais_lues.md`** (647 candidats sur 72 fichiers, heuristique : vérifier chaque clé avant de la brancher ou de la supprimer).

## 2. Élites et boss rares dans le monde (décisions owner)

- Déjà en place : verrou « premier groupe arrivé » (`presence_service.cpp:5411-5695`, Redis SET NX, erreur 5 « Monster already engaged ») ; seuls les membres du groupe rejoignent ; en cas de défaite le monstre revient au même endroit, PV pleins (`monster_world.cpp:317-333`).
- À coder : bloc `rare_spawns` par zone dans `world/zones.json` : 1 exemplaire par zone, **réapparition ~1 h** après la mort (délai par zone, dans les données), plusieurs points d'apparition possibles (anti-camping), chemin de respawn propre (pas la file globale 60-180 s qui clone le pack).
- Après une défaite : **réengageable tout de suite par n'importe qui** (comme Dofus). Pas de priorité au groupe perdant.
- Marqueur carte : afficher « engagé » (aujourd'hui toujours `locked=false`).
- Annonce : NON DÉCIDÉ. Reco : pas d'annonce serveur ; au plus un indice discret (rumeur PNJ / message de zone). À rediscuter.
- Combat extrêmement dur, basé sur les mécaniques de cases (§3).

## 3. Mécaniques de cases (briques génériques, data-driven, utilisables aussi par les joueurs)

État actuel : le télégraphe AoE existe (`server-combat/src/combat/room.cpp:3926-4005`, event `AOE_TELEGRAPH`, esquive en sortant de la zone ; ex. `skill_mob_rongeur_deferlante`). Mais le délai = barre d'incantation (annulé si le boss est interrompu).

1. **Zone persistante** (case qui brûle) : durée, `tick_interval`, effet à CHAQUE tick (dégâts ou statut), camp visé. Base possible : `ManeuverZone` (`room.hpp:1441`, `room_maneuvers.cpp`), aujourd'hui effet unique par unité et limité aux `self_move` joueurs.
2. **Frappe différée détachée** : marquer des cases, impact après N s même si le lanceur est interrompu ou mort.
3. **Vrai one-shot** (décision owner) : mécanique de mort garantie pour rendre le jeu difficile (flag execute / dégâts qui tuent quoi qu'il arrive). Lisibilité obligatoire : télégraphe clair, case sûre toujours atteignable.
4. **Cases bloquées** : PAS de nouveau système d'obstacle. L'owner utilisera les **invocations** existantes (`Room::summon_monsters`) : ex. piliers invoqués qui occupent la case, à détruire. Bloquer la ligne de vue : oui quand ce sera le cas (aujourd'hui seules les unités de front bloquent la LoS, `action_validator.cpp:339` → vérifier que les piliers invoqués la bloquent).
5. **Sélecteur de cases boss** : ligne/colonne au hasard, damier, anneau (donut), sous chaque joueur, avec au moins une case sûre. Aujourd'hui l'IA centre toujours sur sa cible (`room.cpp:3932-3943`).
6. **Phases par boss** : changement de kit de compétences à X % PV (données par boss).

Contrainte : déplacements lents (4 s de recharge partagée + coût par case). Délai d'annonce ≥ temps réel pour atteindre une case sûre, sinon c'est injuste et non dur.

## 4. IA : AoE qui maximise les cibles

L'owner va améliorer l'IA : pour certaines compétences, choisir le centre qui **touche le plus de cibles** au lieu de viser la cible principale. Points d'entrée : `ai/behaviors/kit_behavior.cpp:263` (cibles sol), `room.cpp:3932-3943` (centre du cast), `compute_aoe_cells` (`room.cpp:8520`). Prévoir un champ de données par compétence (ex. `aoe_aim: "primary" | "max_targets"`).

## 5. Idées de boss (3e donjon et suivants ; l'owner fait les donjons 1-2 sans)

- **Braise** : à chaque phase une ligne de plus brûle en permanence, l'arène rétrécit ; damier one-shot toutes les ~30 s.
- **Lac Gelé** : une case piétinée se fissure, puis devient un trou (pilier/obstacle invoqué) → gérer ses déplacements sur tout le combat.
- **Défilé** : rochers invoqués qui bloquent des cases, puis frappe en ligne → trouver le passage à temps.
- **Boss de guilde** (idée owner) : mode de jeu futur construit sur ces mêmes briques.
