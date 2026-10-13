# Le Panthéon (les premiers du serveur)

Statut : idée du propriétaire (2026-10-03), jugée pertinente. À concevoir.

## Principe

Un Panthéon des **premiers** : premier joueur niveau 100, premier à faire X, premier par métier,
premier avec un familier niveau 100, etc. Une grosse liste.

- **Prestige horizontal** (titres, place au Panthéon), jamais de puissance.
- **Base existante** : le système de succès et de titres marche de bout en bout
  (`systems/achievements.json`, table `achievement_unlocks`). Il faut un succès « premier du
  serveur » qu'**un seul joueur** peut obtenir (la première insertion gagne), plus un écran Panthéon
  et une annonce à tout le serveur.

## Précautions

- **Ne pas mourir une fois les places prises** : paliers (10 premiers, 100 premiers) et un **Panthéon
  de saison** à côté du Panthéon éternel.
- **Triche** (bugs, multi-comptes) : pouvoir retirer une entrée.
- **Pas de spoil** : les entrées liées à l'histoire restent **cachées** jusqu'à ce que quelqu'un les
  obtienne (ex. « premier à sauver Ezra »).
- **Récompenses cosmétiques** : titres exclusifs, couleur de nom, nom gravé en ville (statue ?).

## La liste (proposée)

| Catégorie | Entrées |
|---|---|
| Progression | 1er niveau 20 / 50 / 100 ; 1er niveau 100 de chaque classe et sous-classe |
| Métiers | 1er maître de chaque métier ; 1er objet légendaire fabriqué |
| Familiers | 1er familier niveau 100 ; 1er légendaire de chaque espèce ; 1er à posséder les 65 espèces |
| Koro | 1re carte SS ; 1er album Koro complet |
| Donjons et boss | 1er à vaincre chaque donjon ; chaque boss de monde ; 1er groupe à vaincre un pack 5 étoiles |
| Tour d'Asher | 1er groupe à la vaincre |
| Tour infinie | record d'étage (classement) |
| Collections | 1er livre d'histoire complet ; les 10 livres ; 1er bestiaire complet |
| Histoire (cachées) | 1er à sauver Ezra ; 1er à refermer une Fissure par la compassion ; 1er à vaincre Harlan |
| PvP | 1er champion de chaque saison d'arène |
| Guildes | 1re guilde niveau max ; 1re guilde à vaincre la Tour |

## Questions

- [ ] « Premier joueur avec un invok les 100 » : compris comme « familier niveau 100 », à confirmer.
- [ ] Panthéon de saison : oui ou non ? Quelle durée de saison ?
- [ ] Nom gravé en ville : une statue / un mur à Havreden ?
