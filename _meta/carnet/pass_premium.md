# Pass premium (abonnement)

## 2026-10-17 : deux niveaux (remplace le pass unique ci-dessous)

Demande de Charleston : **Premium ≈ 10 €** et **Premium+ ≈ 16 €**, prix d'exemple à garder en data.
Source unique : `systems/premium.json` (`tiers`, `benefits`, `offer`, `planned`). Valeurs à valider.

| | Premium | Premium+ |
|---|---|---|
| Prix | 1000 diamants | 1600 diamants |
| Durée | 30 jours | 30 jours |
| Régénération hors combat (perso et familier) | ×2 | ×2 |
| Téléportation | gratuite | gratuite |
| Marchands PNJ | −10 % | −15 % |
| Diamants reversés à l'achat | 0 | 300 |

Achat en jeu aux diamants, cumulable (les jours Premium déjà payés passent après les jours Premium+),
réserve plafonnée à 365 jours, comptes invités refusés. Règle inchangée : rien en combat.
2026-10-17 (retour Charleston) : ×3 jugé énorme, Premium+ revient à ×2 ; ce qui le différencie de plus reste à choisir par Charleston.
Pas encore branchés donc **non affichés** : clé de donjon hebdomadaire, reset d'arbre de passifs,
relance de contrat, cosmétique d'abonné (`planned`).
Le `battle_pass` de `boutique.json` n'existe plus : le fichier a été supprimé (commit `0db6b30`).

## Décisions du 2026-10-13 (historique)

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

- `systems/boutique.json` `battle_pass` : il existe un battle pass (45 jours, piste premium `exclusive_elixirs: true`).
  Décision : **un seul pass** → retirer ou fusionner le battle pass ; pas d'élixirs réservés aux payants.
- `qol_shop` (inventaire, banque, emplacements de personnage, changement de nom) : achats ponctuels, compatibles.
- **Clés de donjon** : la data existe (`key_drops` dans `world/dungeons.json`, `dungeon_key_drops` / `zone_drops` dans
  `loot_tables.json`, `keys` dans `systems/tower.json`) mais **aucun code serveur ne lit le drop de clé** (data morte, voir
  `_comment_keys` du donjon des égouts). À câbler : drop des clés sur les monstres, puis porte de donjon qui consomme la clé,
  puis la clé hebdomadaire du pass.
