# Runes : effets déclenchés à insérer dans l'équipement

Statut : idée du propriétaire (2026-10-05), à concevoir. Inspiration : les cartes de monstres de
Ragnarok Online. **Nom retenu : Runes** (le propriétaire ; simple et compris de tous).

## Principe

Une rune = **déclencheur × chance × effet**. Exemples du propriétaire :
- 10 % lors d'un critique : double attaque ;
- 5 % lors d'un critique : lancer une boule de feu ;
- 5 % lors d'un critique reçu : se lancer un soin sur la durée.

Quasi infini et facile à produire : un **script** peut générer les runes depuis un tableau (comme les
grimoires de familier). À garder sous contrôle : une sélection (30-50 au départ), pas des milliers.

## Ce que le moteur sait déjà faire (ProcProcessor, uniques et keystones)

- 24 déclencheurs, dont : sur critique, sur coup, sur esquive, sur blocage / parade, dégâts reçus,
  seuil de PV, sort lancé, tous les N sorts, contrôle reçu…
- ~30 effets, dont : appliquer un statut (poison, saignement, silence, soin sur la durée…), soin,
  bouclier, bonus de dégâts du prochain coup, critique garanti au prochain sort, réduction de
  recharge, vol / restauration de Souffle, purification…
- Double / triple attaque déjà en combat.

| Exemple | Faisable aujourd'hui ? |
|---|---|
| critique → double attaque | ✅ |
| critique **reçu** → soin sur la durée | ⚠️ manque le déclencheur « critique reçu » (il y a « dégâts reçus ») : petit ajout |
| critique → lancer une boule de feu | ❌ manque l'effet **« lancer un sort »** (auto-cast) : à ajouter une fois, il servira à toutes les runes de ce type |

Vérifié le 2026-10-05 sur le back de la maison (`main` du 2026-10-01) : `ProcProcessor::on_damage_resolved`
ne lance que « dégâts reçus » / blocage / esquive pour le défenseur (le résultat porte pourtant
`is_crit` : ajout de quelques lignes) ; aucun effet ne lance un autre sort (le plus proche : le
sort gratuit tous les N sorts de l'arbre de passifs, `free_cast_every_n`). Le propriétaire pense que
ces déclencheurs existent : **à revérifier sur la version du PC du bureau** (travail non poussé).

## Visuels : discrets (lisibilité en 10 contre 10)

Le propriétaire a beaucoup d'animations : il ne faut pas en rajouter partout.
- **Une rune n'a jamais sa propre grosse animation.**
- Un **petit éclat d'icône générique** au-dessus du personnage quand une rune se déclenche (couleur de
  la rune).
- Une rune qui lance un sort réutilise **l'animation du sort**, éventuellement réduite.
- L'agent d'animations n'a donc qu'**un effet générique** à faire.

## Horizontal, pas vertical (propriétaire, 2026-10-10 : « que le jeu reste le plus longtemps possible horizontal »)

Ajouter des runes ne suffit pas : si chaque nouvelle rune est un peu plus forte, c'est du vertical
déguisé (power creep). Règles :
1. **Budget de puissance fixe par emplacement** : toutes les runes valent à peu près autant ; une
   nouvelle rune = une autre façon de jouer, jamais une meilleure. Vérifié au banc
   `item_power_combat_probe` (fourchette, ex. ±10 % de dégâts ou de survie).
2. **Pas de rangs qui montent sans fin** : une rune peut suivre le niveau du personnage, pas de
   « +1, +2, +3 ».
3. **Nombre d'emplacements fixe et bas** (0 / 1 / 2) et **jamais augmenté** par la suite.
4. **Runes situationnelles** (boss, groupes, soin, PvP) plutôt qu'une « meilleure rune ».
5. **Compromis** : certaines runes ont un coût (ex. plus fort mais moins d'armure).
6. **Rareté ≠ puissance** : une rune rare est plus originale, pas plus forte.
7. Pas de cumul de la même rune ; délai interne.

Le vertical reste la progression 1 → 100 (niveaux, bandes d'équipement). **Après 100, tout est
horizontal** (runes, passifs, livres, builds, collections, Panthéon, cosmétiques) : c'est aussi la
réponse à l'« alternative horizontale au Paragon ». Garder des objectifs (collections, Panthéon,
histoires, saisons) pour que l'horizontal ne manque pas de buts.

## Deux sortes de runes (2026-10-10)

| Sorte | Exemple | Rang ? |
|---|---|---|
| **Style** (comportement + contrepartie) | +1 portée / −10 % dégâts ; +1 portée au déplacement / +15 % de recharge de ce sort | non (au plus un niveau minimum) : +1 portée vaut pareil au niveau 20 et 100 |
| **Déclenchement** (chiffres) | 5 % sur critique : boule de feu | oui, **I à V calés sur les bandes**, plafond V : un rang suit le niveau, il ne donne pas plus de puissance relative |

Une rune de style peut modifier la portée d'un déplacement **avec une contrepartie** (propriétaire). Voir
[déplacements en combat](deplacements_combat.md).

**Règle d'or** : le plafond de puissance est atteint au niveau 100, équipement de rang V au +20, et ne
bouge plus jamais (pas de rang VI ni de +25) ; les mises à jour ajoutent des alternatives.

## Proposition de règles

- Emplacements selon la rareté de l'objet : 0 commun, 1 rare, 2 légendaire.
- Insertion à la forge ; retrait contre de l'or.
- **Garde-fous** : chance faible, **délai interne** par rune, pas de cumul illimité de la même rune,
  plafond de double sort ; attention au PvP.
- Drop sur les monstres : une espèce = sa rune (rare) ; lien avec le bestiaire et les collections.
- Il manque les **emplacements** sur l'équipement (aucun aujourd'hui).

## À faire

- [ ] Document de conception : la liste des runes (tableau déclencheur × chance × effet), les garde-fous,
      les emplacements, les sources de drop.
- [ ] Serveur : déclencheur « critique reçu », effet « lancer un sort », emplacements + insertion à la
      forge.
