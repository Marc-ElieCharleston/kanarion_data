# Kits humanoïdes : décisions et problèmes

62 monstres : 58 des 10 espèces, plus 4 humanoïdes sans espèce (shelved).

## Conventions
- Attaque d'arme : `slash` (lame), `slam` (masse ou bouclier), `shoot` (arc ou bombe), `feint` (voleur).
- Les lanceurs utilisent comme arme le 2e basique de leur rôle.
- Le rôle enchanteur reprend `support_bolster` à la place de `enchanteur_renfort`.

## Archétypes corrigés (15)
- **Enchanteur** : Chef Bandit, Seigneur tribal, boss Seigneur Bandit. Leurs phases sont des ordres et des cris.
- **Soigneur** : Chaman gobelin, Shaman lézard, Ritualiste d'Edric.
- **Mage** : Ancien Converti (portrait flamme).
- **Contrôleur** : Docteur Pestilent, Tisseur de Cauchemars.
- **Brute** : Chef de Gang, Edric (deux fiches), écho du Seigneur Bandit.
- **Berserker** : Acolyte Zélote, Chevalier Brisé.

## À remonter
1. **Doublons de boss.** Le serveur ignore `base_monster`, donc `mob_bandit_warlord` et `mob_edric_warlord` doublonnent les `boss_*`. Deux donjons « Tour d'Asher » existent, avec deux boss Edric. Les noms FR divergent de ceux des donjons.
2. **Kits actuels.** Une douzaine de lanceurs n'ont que des compétences de brute. Les soigneurs gobelin et lézard n'ont aucun soin. Des signatures sont données dès le niveau 7.
3. **MAG** nulle ou absente sur plusieurs lanceurs.
4. **Ids trompeurs** : `goblin_witch`, `bandit_hunter`, `bandit_warchief` (tous tribaux), `goblin_warior`.
5. **Boss gobelins** de niveau 10-12 pour des troupes de niveau 20-23. Aucun n'est placé.
6. **Portrait du Fanatique de la Tour** : un guerrier à hache, alors que la fiche en fait un lanceur.
7. **Doublons** : Voleur et Coupe-Bourse, Pillard et Bandit, archers.

## Manques
- Une identité berserker et une identité mage avec une recharge d'au moins 20 s.
- Une « Fiole pestilente ».
- La phase du Seigneur Cultiste.
