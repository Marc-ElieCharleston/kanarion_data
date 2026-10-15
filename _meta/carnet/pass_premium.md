# Pass premium (abonnement) — décisions du 2026-10-13

Modèle **Dofus** : jeu ouvert et illimité pour tous, **un seul pass** mensuel (prix de l'abonnement Dofus, ~5-6 €/mois).
Règle : **aucune stat, aucun bonus en combat, aucun contenu fermé aux non-abonnés**. Le pass fait gagner du temps et du confort.

## Contenu validé

| Bonus | Détail | Pourquoi ce n'est pas pay to win |
|---|---|---|
| Régénération hors combat ×2 | vie et Souffle, hors combat seulement | gain de temps entre deux combats, aucun effet en combat |
| Téléportation gratuite | entre les points de téléportation | gain de temps, pas d'accès en plus |
| −10 % à l'achat chez les marchands PNJ | | petit confort ; reste un puits d'or |
| 1 clé de donjon par semaine | façon clés Bouftou | les clés se lootent aussi sur les monstres pour tout le monde |

Écarté : **+10 % à la revente** (chaque revente crée de l'or : les abonnés feraient entrer plus d'or dans l'économie).
Plus tard : auras, ailes, cosmétiques faits par un vrai artiste (aujourd'hui les skins sont faits par IA).

## À corriger / à brancher

- ~~`systems/boutique.json` `battle_pass`~~ : **retiré** (2026-10-15, propriétaire : pas prévu pour le moment). Le
  fichier entier, mort, est supprimé sur `vac_audit-lot1` (`0db6b30`), battle pass compris.
- `qol_shop` (inventaire, banque, emplacements de personnage, changement de nom) : achats ponctuels, compatibles.
- **Clés de donjon** : la data existe (`key_drops` dans `world/dungeons.json`, `dungeon_key_drops` / `zone_drops` dans
  `loot_tables.json`, `keys` dans `systems/tower.json`) mais **aucun code serveur ne lit le drop de clé** (data morte, voir
  `_comment_keys` du donjon des égouts). À câbler : drop des clés sur les monstres, puis porte de donjon qui consomme la clé,
  puis la clé hebdomadaire du pass. Drop et porte faits le 2026-10-15 (voir `cles_donjons.md`) ; la clé
  hebdomadaire attend un système d'abonnement, qui n'existe pas encore côté serveur.
