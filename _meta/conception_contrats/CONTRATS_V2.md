# Contrats V2 (proposition, 2026-10-15)

Statut : **proposition, rien n'est codé**. Les 80 contrats actuels (`world/quests.json`, `q_contract_*`)
restent en place jusqu'à validation.

## Constat (calcul de l'or par heure, 2026-10-15)

Modèle : data `vac_economy-fixes`, durée de combat de `progression.json` (3 min niv 10 → 20 min niv 100)
+ 1 min entre deux combats, 3 contrats tenus.

| Niveau | Or des monstres/h | Contrats/h | Total/h |
|---|---|---|---|
| 1 | 108 | 1 659 | 1 767 |
| 40 | 784 | 1 214 | 1 998 |
| 80 | 1 018 | 2 489 | 3 507 |
| 100 | 608 | 3 792 | 4 400 |

- Les contrats font 60 à 95 % de l'or ; au niveau 1, 15 fois l'or des monstres.
- L'or des monstres baisse après 80 : `gold_weight` moyen 0,82 en 81-100 contre 1,45 en 61-80.

Abus trouvés (vérifiés dans le code serveur) :

1. **Meute sans bande de niveau** : `update_star_pack_progress` ne regarde que les étoiles. Un niveau 90
   tient Meute S + A + B 81-100 et les remplit avec 3 packs 5 étoiles de niveau 1-20 : 9 600 or.
2. **Arène créditée par les duels** : `pvp_service.cpp` publie la victoire pour tous les types de match
   (duel, salle perso compris). Deux amis qui se laissent gagner : ~28 800 or/h chacun.
3. **Cumul** : 3 contrats de la même famille paient 3 fois les mêmes combats.
4. **Endurance** : un pack de 1 monstre compte comme un pack de 10.

## Décisions du propriétaire (2026-10-15)

- On refait les contrats proprement, par rang.
- **Moins d'or**, compensé par des **potions, des pierres de raffinage et des ressources**.
- Correctifs validés : **1 contrat par famille**, pas de combat contre un monstre seul, `gold_weight` des
  monstres 81-100 remonté.
- **Groupes de 3 étoiles minimum.** Tuer un monstre commun seul n'a pas de sens, même dans le lore.
- Les contrats ont un sens : **entraîner les gens du village**, **partir en expédition**, **nettoyer des
  vagues de monstres**. On simplifie, c'est un jeu.

## Les familles (révision du 2026-10-15)

Les contrats restent affichés sur **le tableau**, mais chacun a un **donneur** : quelqu'un qui en sait un
peu plus que les gens du village.

| Famille | Donneur | Sens | Ce qu'on fait (simplifié) |
|---|---|---|---|
| **Expédition** | Hestia (ancienne exploratrice, connaît chaque recoin) | aller voir un lieu précis | disperser des groupes **3★ et plus dans une zone nommée** (« Expédition au Marais de Havreden ») |
| **Vague** | Aldric (forme les volontaires) | une vague déborde sur les abords, ses volontaires ne suffisent pas | abattre des créatures **dans des groupes 3★ et plus** de la bande ; rang S = refermer une invasion de Fissure |
| **Récupération** | Aldric | équiper les volontaires | rapporter des ressources lâchées par les monstres de la bande (peaux, carapaces…) |
| **Prime** | Varn (chasseur de primes) | un monstre dangereux est repéré | abattre un **élite nommé** de la bande (Rat Alpha, Tortue de Pierre, Scarabée Géant…), qui n'apparaît que dans les groupes 3★ et plus |
| **Donjon** | Varn (connaît chaque vieille porte) | un donjon vaut la descente | terminer un donjon de la bande, difficulté normale ou plus |
| **Arène** | Dargo (Rochebourg) | se mesurer aux autres | gagner des matchs d'**arène classique ou classée** (pas l'entraînement contre des recrues, pas la salle perso, pas le duel) |

Règles :
- 3 contrats au plus, **un par famille** : avec 6 familles, chacun choisit ses 3.
- La **bande de niveau s'applique partout**. Une expédition prend la bande de sa zone (les zones ont déjà la
  leur) : un niveau 100 qui fait l'expédition du Terrier des Rats touche la récompense de 1-8, pas plus.
- Un groupe de moins de 3★ ne compte pour rien.
- Un même combat peut faire avancer plusieurs familles (Expédition, Vague, Prime), jamais deux contrats d'une même famille.
- Récupération : seulement des ressources **qui ne se vendent pas chez un PNJ** (sinon : acheter au PNJ, rendre
  au contrat = or gratuit). L'objet est retiré du sac au rendu. La récompense dépasse un peu sa revente.

## Rangs

| Rang | Expédition (par zone) | Vague | Récupération | Prime | Donjon | Arène |
|---|---|---|---|---|---|---|
| C | 2 groupes 3★ | 10 créatures | 5 ressources | — | — | 1 victoire |
| B | 4 groupes 3★ | 20 créatures | 10 ressources | — | normal | 2 victoires |
| A | 3 groupes 4★ | 35 créatures | 20 ressources | 1 élite nommé | difficile | 3 victoires |
| S | 1 groupe 5★ | 1 invasion de Fissure | — | 1 boss de zone | cauchemar | 5 victoires |

Volume : 21 zones × 4 rangs d'expédition, plus Vague, Récupération et Arène par bande, plus une prime par élite
ou boss nommé, plus un contrat par donjon et par difficulté. Les contrats seront **générés par un script**
à partir des zones, des monstres et des donjons, pas écrits à la main.

## Autres idées (non retenues pour l'instant)

- **Capture** (le dresseur veut un familier de la zone) : l'objectif `capture_familiar` existe déjà.
- **Commande d'artisan** (fabriquer un objet pour un PNJ) : `craft_item` existe ; pour les métiers.
- **Escorte d'un volontaire** (Aldric : emmener un mercenaire en combat) : colle au lore, mais le combat ne
  dit pas encore au service des quêtes qu'un mercenaire était là.

## Récompenses

Or d'un contrat C par bande : **30 / 60 / 120 / 240 / 480** (la moitié d'aujourd'hui), × 1 (C), 2 (B),
3 (A), 5 (S). Les objets compensent :

| Rang | Or | Objets |
|---|---|---|
| C | × 1 | 3 potions de vie du rang de la bande (I à V) |
| B | × 2 | 3 potions de vie + 3 potions de Souffle du rang de la bande |
| A | × 3 | 5 + 5 potions, 1 pierre de raffinage du rang **de la bande − 1** (au moins 1), type tiré au hasard |
| S | × 5 | 1 pierre de raffinage du rang de la bande (type au hasard) + 1 matériau de la bande (réserve des coffres de contrats) |

Pierres : Lame, Bouclier, Puissance, Âme (`even_*_rank_1..5`). Attention, elles se revendent (10 / 40 /
150 / 600 / 2 500) : une pierre de rang 5 vaut à elle seule un contrat S 81-100 en or. C'est pour ça que le
rang A donne une pierre d'un rang en dessous.

Les coffres de contrats (jour et semaine) restent tels quels.

## Chiffrage (jeu normal, que des groupes 3★)

Hypothèses : combat contre un groupe 3★ = durée moyenne × 3,5/2,8 monstres, + 2 min pour le trouver ;
contrats B en Expédition et en Vague ; `gold_weight` 81-100 remonté à 1,45.

| Niveau | Or des monstres/h | Contrats/h | **Total/h** | Avant |
|---|---|---|---|---|
| 10 | 137 | 266 | **403** | 1 444 |
| 50 | 625 | 480 | **1 105** | 2 914 |
| 90 | 802 | 1 025 | **1 828** | 4 896 |
| 100 | 828 | 907 | **1 735** | 4 400 |

Plus l'arène (Entraînement), les coffres et les objets. Les contrats valent maintenant à peu près l'or des
monstres, au lieu de 3 à 15 fois. Tout dépend de la durée réelle des combats : à remesurer en jeu.

## Ce que ça demande au code (après validation)

- Data : réécrire les contrats (`world/quests.json`), `contract_family` sur chaque contrat,
  `contract_limits.max_per_family: 1`, `gold_weight` des monstres 81-100.
- Serveur (quest) : refus à l'acceptation si un contrat de la même famille est tenu ; objectif
  « groupes N★+ dans la bande » (`clear_star_packs` + bande, aujourd'hui sans bande) ; objectif
  « créatures abattues dans des groupes N★+ de la bande » (`kill_mobs` + `min_star`) ; objectif « refermer
  une invasion de Fissure » (l'événement existe déjà pour l'XP, `quest_arena_rewards.cpp`) ; récompense
  « pierre de rang R, type au hasard » (même mécanisme que la réserve des coffres).
- Serveur (pvp) : ne publier la victoire pour les contrats que pour `PvPRoomKind::ArenaTeam` (classique et classée).
- Serveur (quest) : objectif « rapporter N ressources » (retirées du sac au rendu), « terminer un donjon de la bande à la difficulté D », « abattre l'élite X dans la bande », expédition filtrée par `origin_zone_id`.
- Script de génération des contrats à partir de `world/zones.json`, des monstres et des donjons.
- Client : panneau des contrats (familles, rangs), message du refus « déjà un contrat de cette famille ».

## Questions ouvertes

Réglé le 2026-10-15 : donneurs Hestia, Aldric, Varn (et Dargo pour l'arène) ; l'arène compte seulement
classique et classée ; expéditions par zone nommée (les zones ont leur bande).

1. Récupération : quelles ressources ? Proposé : les matériaux lâchés par les monstres de la bande qui ne se
   vendent pas chez un PNJ.
2. Les autres idées (capture, commande d'artisan, escorte) : plus tard, ou une tout de suite ?
