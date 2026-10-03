# Familiers : livres de passif, déplacements, passifs liés au maître

Document de CONCEPTION (2026-10-03, vacances). Rien n'est implémenté : à relire et trancher avant
d'écrire la moindre ligne. Les points à décider sont marqués **[À DÉCIDER]**.

Décisions déjà prises par le propriétaire (2026-10-03) :
- trois types de livres de familier : compétence (existe), **déplacement**, **passif** ;
- **les passifs fonctionnent exactement comme les compétences actives** : mêmes règles simples, pas de
  système à part ;
- des compétences de déplacement pour les monstres (par archétype) et les familiers (par rôle) ;
- les passifs qui touchent aussi le maître sont très appréciés : en faire davantage.

---

## 1. Rappel : les règles des livres de compétence (déjà en jeu)

Source : `items/pet_books.json` (`_meta`), `config/familiar_balance.json`.

| Règle | Valeur |
|---|---|
| Rangs | C 100 %, B 115 %, A 130 %, S 150 %, SS 175 % (`rank_percent`, même échelle que les cartes Koro) |
| Rareté du livre | C commun, B peu commun, A rare, S épique, SS légendaire |
| Enseigner | le familier apprend la compétence au rang du livre |
| Améliorer | s'il la connaît à un rang inférieur, elle monte au rang du livre |
| Emplacements pleins | le joueur choisit la compétence remplacée |
| Hors rôle | ×0,67 (dégâts, soins, boucliers, valeurs, durées) ; signatures jamais pénalisées |
| Emplacements | par niveau du familier : 2 (niv. 1), 3 (20), 4 (50), 5 (100) |
| Acquisition | rang C achetable chez Colette ; B à SS au drop seulement, rang pondéré par le tier du monstre |

## 2. Les passifs, calqués sur les compétences

### 2.1 Ce qui change par rapport à aujourd'hui

Aujourd'hui (`classes/familiar/passives.json`) : au drop, le familier tire 1 passif (2 en légendaire),
et sa puissance dépend de la rareté (`value_mult` 1,0 / 1,0 / 1,25 / 1,25 / 1,25). Pas de rang, pas de
livre, pas de remplacement.

Proposition, règle pour règle identique aux compétences :

| Règle | Compétences | Passifs (proposé) |
|---|---|---|
| Rang | C → SS, `rank_percent` | **pareil** : C → SS, mêmes pourcentages |
| Ce que le rang augmente | dégâts, soins, valeurs, durées | les `value` et `hp_percent` du passif ; **chances et seuils fixes** (sinon 25 % de chance → 44 %) |
| Livre | enseigne ou améliore | **pareil** |
| Emplacements pleins | le joueur choisit | **pareil** |
| Hors rôle | ×0,67 | **pareil**, selon le `flavor` du passif (tank / dps / heal / utility) ; `universal` jamais pénalisé |
| Signature d'espèce | jamais dans un livre | **pareil** (`fp_sig_*`, comme Porteur de Peste) |
| Au drop | compétences tirées dans le pool du rôle | 1 passif tiré dans le pool, **au rang de la rareté du familier** (commun → C … légendaire → SS) |

Le `value_mult` par rareté disparaît, remplacé par le rang : un seul chiffre à expliquer au joueur.

### 2.2 Emplacements de passif **[À DÉCIDER]**

- **Option A (calquée sur les compétences, recommandée)** : par niveau, 1 (niv. 1), 2 (niv. 50),
  3 (niv. 100). La rareté ne donne plus d'emplacement, mais un meilleur rang de départ.
- **Option B (garde l'existant)** : par rareté, 1 emplacement, 2 en légendaire, plus 1 au niveau 100.

L'option A rend chaque familier optimisable au niveau maximum ; la B garde le légendaire comme seul
moyen d'avoir deux passifs (gros incitatif à la chasse, mais moins de liberté).

### 2.3 Acquisition des livres de passif

- **Passifs de base** (stats simples : Vigueur, Férocité, Carapace, Œil vif, Agilité, Sérénité…) :
  rang C chez Colette, comme les compétences.
- **Passifs recherchés** (à déclencheur, et tous ceux qui touchent le maître) : **jamais vendus**,
  drop uniquement, à partir du rang B ; rang pondéré par le tier du monstre comme les grimoires.
- Volume : 30 passifs hors signature × 5 rangs = **150 livres**, plus les nouveaux passifs (section 4).
  Générés par un script comme `scripts/gen_pet_books.py` (`book_type: "passive"`).

## 3. Les déplacements

### 3.1 Familiers : un emplacement de déplacement dédié

Comme le déplacement signature des joueurs (la Charge du guerrier, accordée automatiquement), chaque
familier a **un déplacement de base selon son rôle**, dans un **emplacement à part** (il ne prend pas
une place de compétence). Un **livre de déplacement** remplace ce déplacement par une variante.

Même échelle de rangs : le rang augmente l'effet secondaire (dégâts, bouclier, soin) ; **portée et
recharge fixes**. Hors rôle ×0,67 comme le reste.

| Déplacement | Rôle de base | Effet | Portée | Recharge |
|---|---|---|---|---|
| **Bond** | Attaque | saute sur un ennemi, petits dégâts | 3 | 12 s |
| **Interposition** | Tank | se place à côté d'un allié attaqué, prend 20 % de ses dégâts pendant 3 s | 4 | 15 s |
| **Retour** | Soin | rejoint le maître, petit soin sur lui | 6 | 15 s |
| **Clignement** | Utilitaire | téléportation sur une case libre | 3 | 12 s |
| Charge (livre) | — | ligne droite vers un ennemi, ralentit 2 s (jamais de contrôle dur) | 4 | 15 s |
| Repli (livre) | — | recule de 2 cases, retire un ralentissement | 2 | 12 s |
| Pas de l'ombre (livre) | — | se place derrière la cible du maître | 4 | 18 s |

L'espèce donne la couleur visuelle et le nom (le loup « bondit », le rat « file », le sanglier
« fonce »), pas une mécanique différente : une seule règle par déplacement.

**IA du familier** (règles simples) : Interposition quand un allié à portée est frappé ; Bond quand
la cible est hors de portée ; Retour quand le maître est à plus de 4 cases ou sous 50 % PV ;
Clignement pour sortir d'une case menacée.

### 3.2 Monstres : par archétype

Pas un déplacement pour tout le monde, sinon s'éloigner ne sert plus à rien.

| Archétype | Déplacement | Recharge |
|---|---|---|
| brute, berserker, assassin | rapprochement (Bond / Charge) | 12-15 s |
| tank, guardian | interposition pour un allié | 15 s |
| archer, mage | désengagement (Repli, 2-3 cases) | 12 s |
| healer, controller, enchanter, summoner | aucun (petit repositionnement possible) | — |

Les rapprochements sont **signalés** (court temps d'incantation visible) pour que le joueur puisse
réagir. Aujourd'hui 15 monstres sur 200 seulement en ont un. Le serveur sait déjà faire lancer un
déplacement hostile à l'IA (branche back `vac_v2-monster-model`, `4f2ba397`).

**[À DÉCIDER]** : les monstres de niveau 1-10 (zone facile) en ont-ils ? Proposition : non, à partir
du niveau 10, pour garder le début simple.

## 4. Passifs qui touchent le maître (nouveaux, « recherchés »)

Existants : Lien Vital (25 % des soins du familier soignent aussi le maître), Garde du Corps
(15 % des dégâts du maître redirigés vers le familier), Meute (+6 % ATK au maître tant que le
familier vit).

Propositions (toutes passent par les accroches du lot 3 côté serveur) :

| Passif | Rôle | Effet (rang C) |
|---|---|---|
| **Écho de soin** | soin | quand le familier est soigné, 30 % du soin devient un soin sur la durée (4 s) sur l'allié le plus blessé à 3 cases |
| **Dernier rempart** | tank | quand le maître passe sous 30 % PV, il reçoit un bouclier de 15 % de ses PV max (1 fois par combat) |
| **Fidélité** | universel | tant que le familier est à 2 cases ou moins du maître, le maître gagne +5 % armure et RM |
| **Vengeance** | attaque | quand le maître subit un coup critique, la prochaine attaque du familier fait +25 % |
| **Relais de Souffle** | soin | 10 % du Souffle dépensé par le familier est rendu au maître |
| **Purification** | utilitaire | quand le maître reçoit un contrôle, le familier le dissipe (recharge 20 s) |
| **Instinct de meute** | attaque | le maître fait +6 % de dégâts sur la cible du familier |
| **Sacrifice** | tank | un coup qui tuerait le maître est pris par le familier à sa place (le familier tombe ; 1 fois par combat) |

Sacrifice et Dernier rempart sont des candidats « graal » (drop rare uniquement, rang B minimum).

## 5. Ordre d'implémentation (après validation)

1. Serveur : finir l'activation des passifs existants (lots 2 et 3, branche back
   `vac_familiar-passives-combat`, lot 1 fait). Le lot 3 apporte les accroches (après un soin, avant
   la mort, aura, sur contrôle reçu) dont les passifs de la section 4 ont besoin.
2. Data + service familier : rang sur les passifs (remplace `value_mult`), emplacements, livres de
   passif générés.
3. Déplacements des familiers : 4 de base + 3 en livre, emplacement dédié, IA.
4. Déplacements des monstres par archétype (data `kits` + IA existante).
5. Nouveaux passifs liés au maître.
6. Affichage en jeu : rang, effet exact et valeurs de chaque passif (sinon les joueurs ne le
   sauront jamais).

## 6. Questions ouvertes (récapitulatif)

- [ ] Emplacements de passif : option A (par niveau) ou B (par rareté) ?
- [ ] Monstres de niveau 1-10 : déplacement ou non ?
- [ ] Les 8 passifs « liés au maître » : lesquels garder, valeurs ?
- [ ] Familiers déjà possédés : leur passif actuel devient-il un rang selon leur rareté (proposé) ?
- [ ] Célérité (+10 % vitesse d'action, sans effet depuis la fin des auto-attaques) : la transformer
      en −10 % de temps d'incantation (proposé) ?
- [ ] Carapace et Épines : descriptions « 8 % » mais valeur 12 dans la data ; garder 12 (proposé) ?
