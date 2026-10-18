# Contrats V2 (2026-10-15)

Statut : **codé le 2026-10-15, pas encore joué**. Branches `vac_contracts-v2` dans la data, le serveur, le
client et le protocole client (voir « Où c'est codé » en bas). Les 80 contrats `q_contract_*` sont retirés
de `world/quests.json` sur cette branche.

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
| **Récupération** | celui à qui la ressource sert : forgeron (minerais, carapaces), marchand (peaux, cuirs), alchimiste (herbes, essences)… | une commande à remplir | rapporter des ressources lâchées par les monstres de la bande |
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

## Le tableau : 3 offres, tirées selon le niveau (décidé le 2026-10-15)

- Le tableau **affiche 3 contrats**, tirés pour le joueur. On accepte ceux qu'on veut (toujours 3 tenus au plus,
  un par famille).
- Une offre **acceptée garde son emplacement** jusqu'au rendu ou à l'abandon : on ne relance que les autres.
  Le contrat se rend au tableau (ou à son donneur) ; l'emplacement libéré reçoit une nouvelle offre.
- **Relance** : chaque jour (5 h, heure de Paris) **tout le monde a 1 relance gratuite** ; ensuite le
  **pass** donne 1 relance gratuite par emplacement et par jour ; ensuite on paie en or (provisoire :
  20 / 40 / 80 / 160 / 320 selon la bande). **Pas de renouvellement automatique à 5 h** : rendre après 5 h ne
  fait rien perdre, ni la relance ni le contrat.
- Les offres suivent **le niveau du joueur** : un niveau 10 ne voit pas de contrat dans une zone de rang III.
  - Tableau de **Havreden** : la bande du joueur.
  - Tableau de **Rochebourg** : contrats de rang **IV minimum** (bandes 61-100).
- Une expédition tire une **zone qui couvre le niveau du joueur** ; une prime tire un élite de ces zones ;
  un donjon, un donjon de la bande.

**Pas de liste de centaines de contrats écrits ou générés à l'avance** : la data décrit des **modèles**
(famille × rang : objectif, quantité, récompense par bande) et le serveur fabrique l'offre au tirage, avec la
zone, l'élite ou la ressource qui correspondent au niveau du joueur. Une nouvelle zone entre dans les tirages
dès qu'elle a sa bande, sans toucher aux contrats.

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
| A | × 3 | 5 + 5 potions, 1 pierre de raffinage **au choix** (Lame, Bouclier, Puissance, Âme) du rang **de la bande − 1** (au moins 1) |
| S | × 5 | 5 + 5 potions, 1 pierre de raffinage **au choix** du rang de la bande |

Changement au codage : la pierre est **choisie** par le joueur au rendu (le mécanisme des récompenses au
choix existe déjà) au lieu d'être tirée au hasard. Le matériau de bande du rang S n'est pas mis : à rajouter
si tu le veux.

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

## Où c'est codé (2026-10-15)

- **Data** (`vac_contracts-v2`) : bloc `contract_board` de `world/quests.json` (familles, rangs, récompenses,
  relances, tableaux), `contract_limits.max_per_family: 1`, 80 contrats retirés, `gold_weight` des 22
  monstres 81-100 alignés sur leur palier.
- **Serveur** (`vac_contracts-v2`) :
  - `services/quest/src/db/contract_board.hpp` : lecture des modèles et du monde (aires, monstres, matériaux
    lâchés et métier qui les utilise, donjons, boutiques des PNJ), définitions `ct_<famille>_<rang>_b<bande>`,
    tirage, relance. Test `test_contract_board` sur la vraie data.
  - `quest_contract_board.cpp` : tableau (0x0A13), relance (0x0A15), livraison des ressources au rendu,
    expédition par aire, invasion refermée.
  - Acceptation d'une offre (QUEST_ACCEPT + tableau + emplacement), un contrat par famille, emplacement
    bloqué ; libéré au rendu et à l'abandon. Migration `113_contract_board.sql`.
  - Le combat envoie l'**aire du groupe** (`origin_area_id`), le donjon envoie la **difficulté**, l'invasion
    envoie son **aire** ; l'arène n'envoie plus les **duels, salles perso, tournois**, et les contrats ne
    comptent que l'arène classique et classée (la quête de Dargo accepte aussi l'arène contre recrues).
- **Protocole client** (`vac_contracts-v2`) : messages 0x0A13-0x0A16, lecture des offres, acceptation d'une
  offre.
- **Client** (`vac_contracts-v2`) : le tableau affiche les offres du serveur (plus de tirage local), bouton
  Relancer, rendu au tableau avec le choix de la pierre ; les définitions `ct_*` sont reconstruites depuis
  `contract_board` pour le journal.

Pas encore fait : le pass côté serveur (la relance du pass est câblée mais jamais accordée), le prix réel
de la relance, Godot n'a pas tourné sur le client (GDScript non vérifié).

## Questions ouvertes

Réglé le 2026-10-15 : donneurs Hestia, Aldric, Varn, Dargo ; Récupération donnée par le métier qui en a
besoin ; arène classique et classée seulement ; expéditions par zone nommée ; tableau à 3 offres tirées selon
le niveau, relance payante, 1 relance gratuite par offre avec le pass ; on garde les 6 familles (escorte et
commande d'artisan : bonnes idées pour plus tard).

Réglé aussi : l'offre acceptée bloque son emplacement ; 1 relance gratuite par jour pour tout le monde ;
pas de renouvellement à 5 h.

1. Prix de la relance (en attente de l'échelle de l'or).
2. Les nouvelles zones (carte du 11-13 octobre) ne sont pas encore dans `world/zones.json` : le tirage les
   prendra dès qu'elles y seront, avec `level_range`, `max_stars` et leurs monstres.
