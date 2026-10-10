# Déplacements en combat

Statut : décisions du propriétaire (2026-10-10) + étude en cours (grille 12×6).

## Ce qui existe

- Grille **10 rangs × 6 colonnes**, 5 rangs par équipe (`config/game.json` `combat_grids.default`,
  le nombre de rangs doit être pair). Un **12×6** est prévu dans la data.
- **4 emplacements de sort de déplacement** par personnage, en général **1 case / 2 cases / 1 case /
  spécial**. Le spécial porte l'identité de la classe : le gardien invoque un bloc, l'ombre crée un
  clone.

## Le problème

Enchaîner 1 + 2 + 1 = 4 rangs en quelques secondes : on traverse toute la ligne ennemie, les mages et
archers sont en danger immédiatement (sauf en 1 contre 1). « Avant / arrière » n'a plus de sens face
à une ombre qui se téléporte dans le dos.

## Décisions (2026-10-10)

- **Temps de recharge global de 4 s réservé aux sorts de déplacement** : après un déplacement, les
  autres déplacements sont bloqués 4 s ; les autres sorts ne sont pas touchés.
- **Les runes peuvent modifier la portée d'un déplacement**, à condition d'avoir une contrepartie
  (ex. +1 portée sur le déplacement, +15 % de recharge sur ce sort).
- Agrandir la grille : « +1 » = un rang de plus **de chaque côté** (12×6), « +2 » = 14×6. Les portées ne
  changent pas : une grille plus longue étire les combats et permet de les découper. **Étude d'impact en
  cours.**
- **Plus d'enracinements** (4 / 6 / 8, voire 10 s), **plus de repoussements et d'attractions**, moins
  d'étourdissements : atteindre un mage ou un soigneur en deux déplacements alors qu'il ne peut plus
  reculer, c'est « moyen ».

## Contrôles : ce qui existe (2026-10-10)

| Mécanique | État |
|---|---|
| Attirer un ennemi (`pull`) | codé et testé |
| Attirer tout le monde vers un point (`pull_to_center`) | codé et testé : **Treuil gravitationnel** de l'artisan forgeron, en jeu |
| Repousser | très limité : seul « Rebond d'évasion » (ballmaster) repousse 1 ennemi adjacent d'une case ; **pas de vrai « repousser la cible de N cases »** (à ajouter : le symétrique de `pull`) |
| Enracinement | le statut existe mais **3 sorts seulement** (2 de familier 3 s, déplacement du Martyr 1 s) ; contre **19 étourdissements** |

Garde-fous proposés pour les enracinements longs :
- un enracinement long **se brise après un montant de dégâts** (sinon un corps-à-corps ne joue plus en
  10 contre 10) ;
- **rendements décroissants en PvP** (la stat de ténacité existe déjà) ;
- durées longues sur les sorts à longue recharge, courtes (4 s) sur les sorts fréquents.

## Étude : grille 12×6 (2026-10-10)

- **Technique : facile.** Serveur et client lisent les dimensions (le client a même déjà un test 12×6) ;
  **0 test cassé** si on change seulement la data. Data : `game.json` + 2 compétences de monstre « toute la
  grille » (portée 12 → 16 : `skill_mob_assassin_shadow_strike`, `skill_mob_rongeur_deferlante`).
- **Client : moyen.** Le zoom caméra (1.8) déborde de l'écran en 12×6 → ~1.6 (personnages ~11 % plus
  petits) ; les **fonds peints** sont composés pour 10×6 → à recomposer ou vérifier.
- **Équilibrage : moyen à grand.** Depuis le dernier rang, l'archer (portée 5) ne touche plus le front
  ennemi, le mage (portée 4) doit avancer ; un déplacement de base coûte 8 s par case ; PvE plus lent ;
  en PvP à petit effectif, deux joueurs repliés au fond peuvent se fuir (~11 cases).
- **Une grille par mode n'existe pas encore** (une seule grille globale), mais c'est un petit chantier :
  chaque type de combat applique déjà la grille à un endroit précis.
- **Recommandé** : une grille **par mode** (`combat_grids.by_mode`, ex. 12×6 seulement pour le 10 contre
  10 PvP), le reste en 10×6 ; mesurer avec les bancs (`arena_balance_probe`) ; ajuster les portées ;
  basculer le défaut seulement ensuite.
- Bug existant repéré (sans lien) : la ligne de vue de l'IA joueur utilise encore l'ancien repère
  (`ai/player_ai.cpp:637-646`).

## À vérifier

- [ ] La téléportation au contact d'un ennemi (« Pas de l'Ombre », portée 20) ignore-t-elle les cases
      occupées ? C'est la vraie menace pour la dernière ligne.
- [ ] Le serveur sait-il modifier la portée d'UN sort et la recharge d'UN sort (pour les runes) ?
