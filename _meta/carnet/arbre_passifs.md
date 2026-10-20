# Arbre des passifs V2 : all-in ou hybride

Décidé par le propriétaire le 2026-10-15 (bras Attaque en brouillon). Le 2026-10-16 : les 4 autres bras
et les 3 ponts manquants proposés sur le gabarit d'Attaque (`arbre_v2.json`, à valider).

- **100 points** : 1 au niveau 1, puis 1 par niveau (aujourd'hui le serveur en donne 99).
- Notables placés **à distance du centre** : petits à 15 points, petits moyens à 30, moyens à 50, méga à 75.
- **All-in** : le méga au bout d'un bras (75 points), avec une contrepartie ; un seul méga.
- **Hybride** : pas de méga ; deux moyens à 50, ou si les bras sont voisins deux à 50 et un à 30 (les ponts
  entre voisins font gagner des points). Gameplay différent, **pas plus faible**. Un méga ferme les ponts.
- Doublons de stats entre bras : acceptés. Flat à l'entrée, % en profondeur.
- Reset : de plus en plus cher (niveau et resets enchaînés) ; le pass donne 1 reset gratuit par semaine.

Pourquoi : avec la V1 (bras de 37 points, 6 slots), tout le monde finissait avec 2 bras complets,
environ 40 variantes et une seule bonne par rôle.

Détail, chiffres et simulation : `_meta/conception_passifs/ARBRE_PASSIFS_V2.md`.

**Intégré le 2026-10-20** (branche `feat/passive-tree-v2`, commits locaux) : 6 bras (Arcanes ajouté entre Soin et
Soutien), 6 ponts, graines ATK/MAG au départ des bras, 24 nœuds passés en stats faute de mécanique branchée
(`v2_planned`), 99 points (règle actuelle). Arbre réel : `classes/passive_tree.json`, généré par
`_meta/conception_passifs/gen_arbre_v2.py`.
