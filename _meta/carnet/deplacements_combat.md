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
- Agrandir la grille d'un rang par équipe (12×6) : **étude d'impact en cours**.

## À vérifier

- [ ] La téléportation au contact d'un ennemi (« Pas de l'Ombre », portée 20) ignore-t-elle les cases
      occupées ? C'est la vraie menace pour la dernière ligne.
- [ ] Le serveur sait-il modifier la portée d'UN sort et la recharge d'UN sort (pour les runes) ?
