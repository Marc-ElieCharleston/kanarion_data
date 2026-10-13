# Familiers : livres de passif, déplacements, passifs de lien

Document de CONCEPTION (2026-10-03, vacances). Rien n'est implémenté : à relire et trancher avant
d'écrire la moindre ligne. Les points à décider sont marqués **[À DÉCIDER]**.

## 0. Décisions du propriétaire

2026-10-03, premier passage :
- trois types de livres de familier : compétence (existe), **déplacement**, **passif** ;
- **les passifs fonctionnent exactement comme les compétences actives** : mêmes règles simples ;
- des compétences de déplacement pour les monstres et les familiers ;
- les passifs qui touchent aussi le maître sont très appréciés.

2026-10-03, second passage :
- **rangs de 80 % à 150 %** (au lieu de 100 % → 175 %) ;
- **déplacements choisis parmi les ~30 qui existent déjà en jeu**, selon ce qui convient au
  familier : jamais un soigneur qui échange sa place avec le tank et meurt juste après ;
- **un familier a pour l'instant : 1 passif, 1 passif de lien, 1 déplacement**. Un monstre a
  1 déplacement au plus ;
- **passif de lien** = nouvelle catégorie, un effet sur le familier ET son maître pendant le combat.
  Fonctionnalité pour plus tard ;
- on peut posséder plusieurs fois le même familier : ce sont ses compétences, son passif, etc. qui
  le distinguent ;
- **Célérité** devient une réduction du temps d'incantation ;
- **Carapace et Épines : 8 %**, comme le dit la description (la data dit 12, à corriger : 12 % était
  trop fort).

2026-10-03, troisième passage (questions 1, 2, 4, 5, 6 tranchées) :
- **les compétences obtenues au drop sont aléatoires ET de rang aléatoire** (pas de rang C fixe, pas
  de remontée ×1,25 des valeurs de base) ;
- **les cartes Koro passent aussi à 80 % → 150 %** ;
- **le familier utilise le déplacement de base tel quel** (la compétence de joueur, même recharge) ;
- **monstres de niveau 1 à 10 : uniquement le déplacement de base d'une case** ;
- **les gardiens (monstres) peuvent échanger de place pour protéger** ;
- **signatures uniques par espèce : plus tard** ;
- le chantier familiers est assez chargé comme ça : on s'arrête là pour la conception.

2026-10-03, quatrième passage (précisions) :
- au drop, le familier a **1 ou 2 compétences, la première est TOUJOURS sa signature** (déjà dans le
  code) ; la seconde, s'il y en a une, est aléatoire et de rang aléatoire ;
- **livres de déplacement de familier PLUS RARES que les livres de compétence** ;
- monstres : un déplacement adapté au style de jeu de l'archétype, **recharge longue** (sinon un
  corps-à-corps n'attrape jamais un mage ou un archer qui saute) ;
- **2 emplacements de passif** par familier (le passif + le passif de lien) ; question 3 (légendaires
  qui ont déjà 2 passifs) : ils les gardent, les deux emplacements les accueillent (interprétation à
  confirmer).

---

## 1. Rappel : les livres de compétence (déjà en jeu)

Source : `items/pet_books.json` (`_meta`), `config/familiar_balance.json`.

| Règle | Valeur |
|---|---|
| Rangs aujourd'hui | C 100 %, B 115 %, A 130 %, S 150 %, SS 175 % (`rank_percent`) |
| Enseigner / améliorer | le livre enseigne la compétence, ou la monte à son rang si elle est connue plus bas |
| Emplacements pleins | le joueur choisit la compétence remplacée |
| Hors rôle | ×0,67 ; signatures jamais pénalisées |
| Acquisition | C chez Colette ; B à SS au drop seulement, rang pondéré par le tier du monstre |
| Stockage | le serveur garde la LETTRE du rang (migration 073) et relit le pourcentage dans la data : changer l'échelle s'applique à tous les familiers existants, sans migration |

## 2. Nouvelle échelle de rangs : 80 % → 150 %

| Rang | Aujourd'hui | Proposé |
|---|---|---|
| C | 100 % | **80 %** |
| B | 115 % | **95 %** |
| A | 130 % | **110 %** |
| S | 150 % | **130 %** |
| SS | 175 % | **150 %** |

**[TRANCHÉ : rang aléatoire au drop] 1. Et les compétences obtenues sans livre ?** Aujourd'hui une compétence tirée au
drop agit à 100 %, comme un livre C. Avec C = 80 %, un livre C deviendrait PIRE que la compétence de
départ. Deux options :
- **A (recommandée)** : une compétence tirée au drop compte comme rang C (80 %), et on remonte les
  valeurs de base des compétences de familier de ×1,25. Résultat : un familier sans livre garde sa
  puissance d'aujourd'hui, et un SS vaut ×1,875 un C (au lieu de ×1,75) ;
- **B** : la compétence tirée reste à 100 % (≈ entre B et A), les livres C et B ne servent qu'à
  apprendre une compétence qu'on n'a pas.

**[TRANCHÉ : oui, Koro aussi] 2. Les cartes Koro** utilisent la même échelle (C 100 % → SS 175 %). Les passer aussi à
80 % → 150 %, ou ne toucher qu'aux familiers ?

## 3. Le passif, calqué sur les compétences

Aujourd'hui (`classes/familiar/passives.json`) : au drop, 1 passif tiré (2 en légendaire), puissance
selon la rareté (`value_mult` 1,0 / 1,0 / 1,25 / 1,25 / 1,25). Pas de rang, pas de livre.

| Règle | Compétences | Passif (proposé) |
|---|---|---|
| Nombre | 2 à 5 emplacements selon le niveau | **2 emplacements** : le passif + le passif de lien (décidé) |
| Rang | C → SS | **pareil** |
| Ce que le rang augmente | dégâts, soins, valeurs, durées | `value` et `hp_percent` ; **chances et seuils fixes** (sinon 25 % de chance → 37,5 %) |
| Livre | enseigne ou améliore | **pareil** ; s'il y a déjà un autre passif, il est remplacé (confirmation demandée) |
| Hors rôle | ×0,67 | **pareil**, selon le `flavor` (tank / dps / heal / utility) ; `universal` jamais pénalisé |
| Au drop | tirées dans le pool du rôle, **rang aléatoire** (décidé) | 1 passif tiré dans le pool, **rang aléatoire** comme les compétences (pondération par la rareté : à décider à l'implémentation) |

Conséquences :
- le `value_mult` par rareté disparaît, remplacé par le rang ;
- le légendaire perd son 2e passif (1 seul emplacement) ;
- **[TRANCHÉ : ils les gardent, à confirmer] 3.** les légendaires déjà possédés avec 2 passifs : on garde le premier, on laisse
  le choix au joueur, ou on les laisse tels quels (exception historique) ?

Acquisition des livres de passif :
- passifs simples (stats : Vigueur, Férocité, Carapace, Œil vif, Agilité, Sérénité…) : rang C chez
  Colette, comme les compétences ;
- passifs à déclencheur : drop uniquement, à partir du rang B ;
- volume : 30 passifs hors signature × 5 rangs = **150 livres**, générés comme
  `scripts/gen_pet_books.py` (`book_type: "passive"`).

## 4. Le passif de lien (plus tard)

Emplacement séparé du passif. Un effet sur le familier ET son maître pendant le combat. Les passifs
existants qui touchent le maître y migreraient : Lien Vital, Garde du Corps, Meute. Idées pour la
suite :

| Passif de lien | Effet (rang C, avant la nouvelle échelle) |
|---|---|
| Écho de soin | quand le familier est soigné, 30 % du soin devient un soin sur la durée (4 s) sur l'allié le plus blessé à 3 cases |
| Dernier rempart | maître sous 30 % PV : bouclier de 15 % de ses PV max (1 fois par combat) |
| Fidélité | familier à 2 cases ou moins du maître : +5 % armure et RM pour les deux |
| Vengeance | le maître subit un critique : la prochaine attaque du familier fait +25 % |
| Relais de Souffle | 10 % du Souffle dépensé par le familier est rendu au maître |
| Purification | le maître reçoit un contrôle : le familier le dissipe (recharge 20 s) |
| Instinct de meute | les deux font +6 % de dégâts sur la même cible |
| Sacrifice | un coup qui tuerait le maître est pris par le familier (1 fois par combat) |

Mêmes règles que le passif (rang, livre, drop). Côté serveur, ils demandent les accroches du lot 3.

## 5. Le déplacement

### 5.1 Principe

Un emplacement de déplacement **dédié** : il ne prend pas la place d'une compétence. Le
déplacement est **choisi parmi ceux qui existent déjà en jeu** (32 déplacements de joueur, plus 4 de
monstre). Un livre de déplacement le remplace. Les règles de rang sont les mêmes que pour les
compétences.

**La règle de sécurité est par TYPE de déplacement, pas par liste** : le serveur et les scripts
refusent un déplacement interdit au rôle, ce qui couvre aussi les futurs déplacements.

| Type de déplacement | Exemples | Attaque | Tank | Soin | Utilitaire |
|---|---|---|---|---|---|
| Vers un ennemi (`dash_line`, `adjacent_enemy`, arrivée « enemies ») | Charge, Pas de l'Ombre, Percée furieuse, Abordage, Entrée en force, Pas de givre, Pas toxique, Ancrage | ✅ | ✅ | ❌ | ❌ |
| Échange de place (`swap`) | Relève lumineuse, Permutation | ❌ | ✅ | ❌ | ❌ |
| Rejoindre un allié (`teleport_adjacent` allié, arrivée « allies ») | Garde, Pas protecteur, Pas de renouveau, Pas cadencé, Service rapide, Pas en mesure | ❌ | ✅ | ✅ | ✅ |
| Libre / repli (`self_move` libre, `recoil`) | Clignement, Bond en arrière, Porté par le faucon, Carte de repli, Pas de côté, Pas de garde, Double d'ombre, Pas de lame, Pas mécanique, Rebond d'évasion, Tir de recul | ✅ | ✅ | ✅ | ✅ |
| Zone au départ (`origin_zone`) | Repli piégé (racine), Trace maudite (anti-soin) | ✅ | ❌ | ❌ | ✅ |
| Attraction (`pull_to_center`) | Treuil gravitationnel | ❌ | ✅ | ❌ | ✅ |

Exclus : Disparition et Voile d'Ombre (furtivité, pas de déplacement).

### 5.2 Déplacement de base par rôle (avant tout livre)

| Rôle | Déplacement de base | Pourquoi |
|---|---|---|
| Attaque | Charge (`skill_warrior_charge`) | aller au contact |
| Tank | Pas protecteur (`skill_warrior_guardian_maneuver`) | se placer contre un allié |
| Soin | Pas de renouveau (`skill_healer_lifewarden_maneuver`) | rejoindre le groupe sans s'exposer |
| Utilitaire | Clignement (`skill_mage_blink`) | sortir d'une case menacée |

**[TRANCHÉ : telle quelle] 4.** Le familier utilise la compétence de joueur telle quelle (même recharge,
20 à 30 s, et même effet), ou une copie adaptée au familier ?

IA du familier : rapprochement quand la cible est hors de portée ; rejoindre le maître quand il est
à plus de 4 cases ou sous 50 % PV ; repli quand le familier est sur une case menacée.

### 5.3 Monstres : 1 déplacement au plus, par archétype

| Archétype | Type de déplacement | Exemples existants |
|---|---|---|
| brute, berserker, assassin | vers un ennemi | Ruée Brutale, Bond, Saut de l'Ombre, Coup de boutoir |
| tank | rejoindre un allié | Pas protecteur |
| guardian | rejoindre un allié OU **échanger de place** pour protéger (décidé) | Pas protecteur, Relève lumineuse, Permutation |
| archer, mage | repli | Bond en arrière, Clignement |
| healer, controller, enchanter, summoner | aucun | — |

Les rapprochements sont signalés (court temps d'incantation visible). 15 monstres sur 200 en ont un
aujourd'hui ; le serveur sait déjà faire lancer un déplacement hostile à l'IA (back
`vac_v2-monster-model`, `4f2ba397`).

**[TRANCHÉ : déplacement de base d'une case seulement] 5.** Monstres de niveau 1 à 10 : sans déplacement (proposé), pour garder le début
simple ?

## 6. Ce qui distingue un familier d'un autre

**Entre deux espèces** (fixé par l'espèce) :
- le rôle ;
- les stats de base (profil du rôle × identité de l'espèce) ;
- le passif de race (`species_passives`, croît avec le niveau) ;
- la signature : un modèle partagé par famille, PAS unique par espèce. Exemples : `bite_bleed`
  (14 familiers), `charge_stun` (14), `shell_guard` (13). 134 familiers, 65 espèces ;
- le pool de compétences tirées.

**Entre deux exemplaires de la même espèce** :
- la rareté (stats ×1,0 à ×1,5, et rang de départ du passif) ;
- le passif tiré, et son rang ;
- les compétences apprises, et leurs rangs ;
- le passif de lien (plus tard) ;
- le déplacement ;
- le niveau.

**[TRANCHÉ : plus tard] 6.** Faut-il une signature unique par espèce, au moins pour les espèces rares ?
Sinon, deux espèces de la même famille ne se distinguent que par leurs stats et leur passif de race.

## 7. Ordre d'implémentation (après validation)

1. Serveur : finir l'activation des passifs existants (lots 2 et 3, back
   `vac_familiar-passives-combat`, lot 1 fait).
2. Data : nouvelle échelle de rangs, Carapace et Épines à 8, Célérité en temps d'incantation.
3. Service familier : rang du passif (remplace `value_mult`), 1 emplacement, livres de passif.
4. Déplacement des familiers : emplacement dédié, règle par type, base par rôle, livres, IA.
5. Déplacement des monstres par archétype.
6. Passifs de lien (plus tard).
7. Affichage en jeu : rang, effet exact et valeurs (sinon les joueurs ne le sauront jamais).
