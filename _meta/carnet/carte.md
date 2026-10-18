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

**Noms : on garde ceux de la data** (`world/zones.json`, ex. Marécage = « Marais de Havreden », Prairie =
« Pâtures d'Havreden »). Une liste de renommages proposée le 2026-10-10 a été mal lue comme validée :
**retirée** (propriétaire, 2026-10-11). Rochebourg et la Tour d'Asher ont déjà leur zone côté client.

Pas d'ours (le propriétaire n'est pas fan du rendu PixelLab).

## Carte v7 (propriétaire, 2026-10-13) — la référence

Image : [cartes/map_v7.png](cartes/map_v7.png). Répartition détaillée des monstres par zone (proposition
du 11 octobre, à relire avec la v7) : artefact « Carte des monstres de Kanarion »
https://claude.ai/artifact/9huzXAsGHhkx2DgjPvvmsG

| Zone | Niveaux | Note |
|---|---|---|
| Havreden (ville) | 0-100 | ville de départ |
| Abords d'Havreden | 1-8 | |
| Lisière d'Havreden | 3-8 | insectes |
| Fourrés des Sangliers | 8-15 | |
| Prairie | 10-20 | frères Dorn |
| Bocage | 9-20 | |
| Bois des Loups | 13-23 | |
| Forêt Nord | 12-26 | |
| Clairière | 15-25 | |
| Marécage | 20-30 | crapauds + 1 élite |
| Combe aux ours | 20-28 | camp des deux sœurs à côté |
| Bois Flétri | 25-35 | donjon |
| Forêt Sud | 25-35 | le hameau → Mournelle (Dorn, Harlan) |
| Ravin des crocs ? | 35-45 | élite humanoïde (nom provisoire) |
| Route de Rochebourg | 40-50 | brigands |
| Chemin des Pèlerins | 45-60 | |
| Mines Basses | 50-60 | donjon |
| Abords de Rochebourg | 45-50 | monstres corrompus et humanoïdes |
| Rochebourg (ville) | 45-100 | |
| Tour d'Asher | 60+ | donjon (tour infinie 60-100) |
| Terres de Givre | 60-66 | |
| Col d'Asher | 60-68 | monstres de pierre + Béhémoth |
| Lac Gelé | 64-70 | donjon des glaces |
| Terre de braise | 63-70 | |
| Chemin des cendres | ? | le long du bord est |
| La Rivière grise | — | frontière |
| Marais de la Faille | 65-72 | Lanternfen, village du marais |
| Anse des naufragés | 1-100 | (zone de capture des familiers) |
| Plaine fendue | 72-80 | |
| Nécropole ? | 70-78 | |
| Chaussée Brisée | 78-88 | |
| Terres Déchirées | 85-95 | |
| Ville en ruine | ? | (Caer Isthrel dans l'artefact) |
| L'Abîme | 90-100 | |

Points à confirmer : niveaux du Chemin des cendres et de la Ville en ruine ; nom du Ravin des crocs ;
« Nécropole ? ».

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
