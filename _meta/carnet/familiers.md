# Familiers

Détail : `_meta/conception_familiers/LIVRES_DEPLACEMENTS_PASSIFS.md`.

## Obtention

- **Par drop** (chance de drop de l'empreinte), **pas de capture** : une fois droppé, il est à toi.
- Au drop : 1 ou 2 compétences ; **la première est toujours sa signature** (déjà dans le code) ; la
  seconde est aléatoire, de rang aléatoire.
- On peut posséder plusieurs fois le même familier.

## Puissance

- Stats = profil du rôle × identité de l'espèce × rareté × niveau.
- **Rareté** (appliqué, data `vac_familiar-species` `4c53e55`) : commun ×1,0, peu commun ×1,07,
  rare ×1,15, épique ×1,3, légendaire ×1,5. Relu à chaque lecture : vaut aussi pour les familiers
  déjà possédés.
- **Passif de race** par espèce, qui croît avec le niveau (paliers 1 / 20 / 50 / 100).
- XP : 90 % de celle du maître (branche back `vac_familiar-xp-90`).

## Livres, rangs, emplacements (décidés, pas implémentés)

- Trois types de livres : compétence (existe), **déplacement** (plus rares), **passif**.
- **Rangs 80 % → 150 %** (proposé C 80, B 95, A 110, S 130, SS 150), Koro compris.
- Les passifs suivent les mêmes règles que les compétences (rang, livre, hors rôle ×0,67).
- **2 emplacements de passif** : le passif + le **passif de lien** (effet sur le familier ET son
  maître ; fonctionnalité pour plus tard). Les légendaires gardent leurs 2 passifs.
- **1 déplacement** : la compétence de base du joueur selon le rôle, telle quelle ; modifiable par
  livre ; règle par type (jamais d'échange de place ni de saut vers l'ennemi pour un soigneur).
- Célérité → réduction du temps d'incantation ; Carapace et Épines à 8 %.

## Passifs en combat

Seuls 6 sur 31 marchaient. Lot 1 fait (8 passifs de stats, back `vac_familiar-passives-combat`,
compilé et testé). Lots 2 et 3 à faire.

## Affichage

- [ ] Montrer en jeu les stats de base, la rareté, le passif de race et les valeurs exactes (sinon les
      joueurs ne le sauront jamais). Le bestiaire peut porter ces infos.
