# Arbre des passifs V2 (brouillon, 2026-10-15)

Statut : **proposition, bras Attaque seul**. Rien n'est branché : la V1 (`classes/passive_tree.json`)
reste celle que lisent le serveur et le client. Data du brouillon : `arbre_v2_attaque.json`.
Simulation : `python -I sim_arbre_v2.py arbre_v2_attaque.json`.

## Pourquoi une V2

Simulation de la V1 avec 100 points : un bras complet coûte 36 à 38 points, et 2 capstones tiennent
dans le budget (72 pts, 6 slots sur 6). Tout le monde finit avec 2 bras complets + des petits nœuds
d'un 3e : environ 40 variantes, et une seule vraiment bonne par rôle. Le all-in n'existe pas.

## Intention du propriétaire

- 100 points : 1 au niveau 1, puis 1 par niveau.
- **All-in** : environ 75 points dans un bras, et au bout un capstone extrêmement puissant.
- **Hybride** : pas de capstone, les points répartis sur 2 ou 3 bras pour un **gameplay différent**,
  pas plus faible. Complexe à équilibrer, mais ça pousse à réfléchir.
- Un all-in ne peut pas être hybride.
- Les doublons de stats entre bras ne gênent pas.
- Mélanger stats flat et stats en % (le % s'applique sur le flat, les deux restent intéressants).
- Le reset coûte de plus en plus cher ; le pass peut offrir un reset gratuit par semaine.

## Règles

| Règle | Valeur |
|---|---|
| Points | 1 au niveau 1 + 1 par niveau = 100 |
| Coûts | petit 1/rang, moyen 3, gros 5, capstone 12, hybride 8 |
| Seuils de palier (points dans le bras) | palier 0 : 0, palier 1 : 6, palier 2 : 18, palier 3 : 36, capstone : 62 |
| Choix | dans un groupe de choix, prendre une option ferme les autres (fourche à N options) |
| Capstone | 1 seul par personnage |
| Hybride | 25 points dans chacun des deux bras, interdit si on a un capstone |

Les seuils remplacent les « slots de grands nœuds par niveau » de la V1. Le niveau limite déjà
naturellement : avec 1 point par niveau, un capstone arrive au plus tôt vers le niveau 74.

Le capstone et l'hybride s'excluent deux fois : par les maths (62 + 12 + 25 + 8 = 107 > 100) et par
une règle explicite, pour le jour où des points bonus apparaîtraient.

## Bras Attaque

| Palier | Seuil | Contenu | Type |
|---|---|---|---|
| 0 Entrée | 0 | Force (+2 atk et +2 mag), Œil vif (+1 % crit), Tranchant (+5 dégâts crit), Visée (+3 précision) ; 3 rangs | flat |
| 1 Style | 6 | **1 voie sur 3**, chacune 3 petits à 3 rangs + 1 moyen | mixte |
| | | Lame : crit, dégâts crit, dégâts % → *Instinct du tueur* (après un crit, +10 % crit 3 s) | |
| | | Brute : atk/mag %, pénétration, dégâts % → *Exécution* (+15 % sous 30 % PV) | |
| | | Cadence : vitesse d'incantation, recharge, dégâts % → *Élan* (+2 % dégâts par sort, 5 cumuls, 6 s) | |
| 2 Spécialisation | 18 | Férocité, Vigueur, Létalité (5 rangs, %) + **1 gros sur 2** : *Allonge* (+1 portée) ou *Acharnement* (+3 % par coup sur la même cible, 5 cumuls) | % |
| 3 Maîtrise | 36 | 4 petits à 5 rangs (dégâts %, pénétration, crit, atk/mag %) + **1 gros sur 2** : *Soif de sang* (+15 % dégâts 5 s après un kill) ou *Brise-garde* (les crits ignorent 25 % armure/RM) | % |
| Capstone | 62 | **1 sur 2**, 12 points, avec contrepartie | |
| | | *Coup Fatal* : crits +50 dégâts crit et −1 s de recharge du sort lancé ; les coups non critiques font −15 % | |
| | | *Déchaînement* : +35 % de dégâts ; −30 % de soins reçus et −15 % de PV max | |

Résultats de la simulation :

- 24 variantes all-in rien que pour Attaque (3 voies × 2 × 2 × 2 capstones). Sur 5 bras : ~120.
- Chemin choisi hors capstone : 69 points, seuil 62 : **7 points de marge** à répartir dans le bras.
- All-in : **74 à 81 points**, il reste 19 à 26 points pour picorer l'entrée et une voie d'un autre bras.
- Chaque seuil de palier est atteignable quelle que soit la combinaison choisie.

## Hybrides

Nœuds entre deux bras voisins, rattachés au tronc du palier 2 de chaque bras (ils ne dépendent pas de
la voie). Puissance visée : environ 60 à 70 % d'un capstone chacun, avec une mécanique qu'on ne
trouve pas ailleurs. Proposés côté Attaque :

- Attaque + Défense : *Riposte* (+40 % sur l'attaque après blocage/parade), *Garde de fer* (au-dessus
  de 70 % PV : +12 % dégâts, −8 % dégâts reçus).
- Affaiblissement + Attaque : *Opportuniste* (+20 % crit contre une cible sous contrôle), *Curée*
  (+20 % dégâts contre une cible avec 3 affaiblissements ou plus).

Formes possibles avec 100 points :

| Forme | Répartition | Coût |
|---|---|---|
| 2 bras | 42 + 42 + 2 hybrides | 100 |
| 3 bras | 25 + 30 + 25 + 2 hybrides | 96 |

## Budget de puissance (à vérifier en jeu)

Un all-in a : 3 gros/moyens de son bras + le capstone + ~25 points (≈ un moyen d'un autre bras).
Un hybride à 2 bras a : 6 gros/moyens + 2 hybrides, sans capstone.
Cible : **capstone ≈ 2 gros + 2 hybrides**. Si les hybrides dominent, on monte le capstone ; si le
all-in domine, on monte les hybrides. Les contreparties des capstones servent à ce qu'il reste un
vrai choix de style, pas juste « plus fort ».

## Reset des points (proposition)

- Gratuit jusqu'au niveau 20.
- Ensuite : `base_gold × niveau × (1 + 0,5 × resets payants récents)` ; le compteur baisse de 1 toutes
  les 2 semaines sans reset payant. `base_gold` à chiffrer avec l'économie.
- Pass : 1 reset gratuit par semaine, non cumulable.

## Ce que la V2 demande au code (après validation de la data)

- Serveur (economy + `passive_draft`) et client (`passive_tree_rules.gd`) : seuils par points dans le
  bras au lieu des slots par niveau ; groupes de choix à N options ; 1 capstone max ; hybrides
  (2 bras à 25, exclus par capstone) ; reset payant progressif.
- `systems/progression.json` : `starting_passive_points: 1`, lu par `level_calc`.
- Nouvelles mécaniques de combat : `stacking_stat_on_event` (Élan), `consecutive_hit_stacks`
  (Acharnement), `crit_ignores_defense` (Brise-garde), `non_crit_damage_modifier` (Coup Fatal),
  `stats_while_hp_above` (Garde de fer), `damage_vs_target_debuff_count` (Curée), événement `kill`
  pour `stat_window_after_event`. Les autres existent déjà (V1, phase 3).
- Migration : rembourser tous les points de l'arbre V1 au passage en V2.

## Questions ouvertes

1. Les 7 points de marge dans le bras all-in : assez, ou faut-il plus de liberté (seuil 58) ?
2. Valeurs des capstones : Déchaînement +35 % est-il « extrêmement puissant » assez ?
3. Un hybride peut-il prendre les 2 hybrides de la même paire (proposé : oui) ?
4. Prix de base du reset.
