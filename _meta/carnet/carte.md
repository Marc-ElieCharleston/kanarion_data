# Carte et niveaux

Carte en jeu en cours de développement (capture du 2026-10-03). Havreden est presque fini,
Rochebourg pas encore ; le propriétaire cherche un artiste.

## Intention de design : une carte NON linéaire (propriétaire, 2026-10-10)

Des zones plus hautes **volontairement placées au nord, près du village** (Marécage 20-30, Prairie, la
Forêt entre les deux), pour casser la linéarité, **comme Canaan Online**. Le débutant voit tout de suite
qu'il existe plus fort que lui, et il reviendra.
- Ça s'appuie sur la règle d'**agressivité** : un monstre ≥ 10 niveaux au-dessus attaque de lui-même (pas de
  mur invisible, le danger se sent).
- Jeu mobile : **XP assez rapide**, mais jeu **difficile**.
- **Besoin de ressources de monstres de bas niveau** pour les joueurs avancés (artisanat : quelques matériaux
  de rangs inférieurs dans les recettes de haut rang), pour voir du monde partout **sans empêcher les bas
  niveaux de farmer**. Précautions :
  1. rencontres **par joueur ou par groupe** (ou réapparition rapide), sinon les joueurs avancés vident les
     zones des débutants ;
  2. pas d'XP pour un joueur avancé sur un monstre faible (écart de niveau), mais **ses ressources oui**.
- Noms : **naturels autour d'Havreden** (la campagne n'est pas hostile vue du village) ; noms inquiétants
  seulement **après Rochebourg**. Le chemin de la quête principale **serpente** entre les zones.

Propositions de noms (2026-10-10, à valider) : Les Friches (3-8), La Chênaie (Sanglier 8-15), Les Pâtures
(Prairie 10-20, ferme des Dorn), La Clairière (6-15), La Lande (Hyène 9-20), Le Val aux Loups (Loup 13-23),
Le Grand-Bois (Forêt 12-26), Les Herbages (16-25), Les Roselières (Marécage 20-30), Le Bois Sombre (25-30,
ex-araignées), Les Éboulis (« Ours » 20-28 : plus d'ours, camp des deux sœurs à côté), Les Crêtes (« Wolf »
25-32), La Route du Sud (Brigand 35-45, hameau à côté) ; puis Rochebourg (~50, à ajouter), Les Bas-Fonds de
Rochebourg (Rats corrompus 40-50), Le Chemin des Pèlerins (Fanatique 45-60), Les Mines Basses (Gobelins
50-60), la Tour d'Asher (60+, à ajouter), Le Marais de la Faille (60-70), Les Brèches (61-70), Le Seuil
(70-80), Les Terres Déchirées (80-100), L'Abîme (85-100).

Pas d'ours (le propriétaire n'est pas fan du rendu PixelLab).

## Grandes régions (propriétaire)

| Niveaux | Lieu | Ambiance |
|---|---|---|
| 1-20 | **Havreden** et ses alentours | paisible, très peu de Fissures |
| 20-50 | **la route du sud** | les Fissures se multiplient en descendant |
| ~50+ | **Rochebourg** | la Tour, les fanatiques, les bandits |
| 60+ | **la Tour d'Asher** | volontairement dure : un joueur seul de niveau 60 ne passe pas |
| fin de jeu | **tout en bas : une ville en guerre permanente** | factions, version simple (pas d'artiste) |

## Zones visibles sur la carte (capture)

| Zone | Niveaux |
|---|---|
| Havreden (village) | 1-8 |
| (sans nom) | 3-8 |
| Sanglier | 8-15 |
| Prairie | 10-20 |
| (sans nom) | 6-15 |
| Hyène | 9-20 |
| Forêt | 12-26 |
| Loup | 13-23 |
| (sans nom) | 16-25 |
| Marécage | 20-30 |
| Ours | 20-28 |
| (sans nom) | 25-30 |
| Wolf | 25-32 |
| Brigand | 35-45 |
| Rats corrompus | 40-50 |
| Fanatique | 45-60 |
| Gobelins | 50-60 |
| Marais corrompu | 60-70 |
| Low Demon | 61-70 |
| Low Abyssal | 70-80 |
| Demon | 80-100 |
| Abyssal | 85-100 |

Tranches de couleur de la carte : 1-20, 21-40, 41-60, 61-80, 81-100.

## Monstres par tranche (refonte V2, `DECISIONS.md`)

Animaux 1-40 ; humains touchés par les Failles 45-55 ; fanatiques ~55-60 ; la Tour d'Asher à 60 ;
après 60 les créatures (ni animaux ni humains). La carte est aussi une **carte morale** : plus on
descend, plus les choix humains ont été mauvais, plus le monde est déchiré (voir
[fissures.md](fissures.md)).

## Questions

- [ ] Où est Rochebourg sur la carte (près de Fanatique 45-60 ?)
- [x] **Le hameau de la forêt** (frères Dorn, Harlan) : **sous la forêt, à droite de la zone Brigand,
      niveaux 30-40** (propriétaire, 2026-10-03), plus proche de Rochebourg que d'Havreden. Les premiers
      niveaux montent vite.
- [ ] Le lore d'avril fait tomber la Tour au niveau 20 : à recaler sur 60+.
