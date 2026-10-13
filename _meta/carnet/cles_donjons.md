# Clés de donjon et clé de la tour infinie

Statut : décisions du propriétaire (2026-10-13), inventaire en cours, plan à venir.

## Clés de donjon (comme Dofus)

- **Une clé par joueur, consommée à l'entrée.** Chaque membre du groupe en a besoin.
- **Drop sur des monstres pertinents, jamais en dessous du palier** : la clé d'un donjon niveau 100
  ne tombe que sur les monstres de la tranche 81-100.
- **Échangeables** : hôtel des ventes et échange direct.

Avis (2026-10-13) : d'accord ; parades à la friction de groupe :
- **une seconde source : une recette de clé** à partir de ressources de la zone (comme dans Dofus) —
  utile aux artisans ;
- **un mode histoire sans clé** pour la quête principale (les quêtes ont déjà des modes histoire /
  normal), pour ne jamais bloquer un nouveau joueur dans l'histoire.

## Clé de la tour infinie (comme Albion)

- **Une clé par groupe**, portée par le **chef de groupe**.
- **Réussir X étages fait monter la clé de niveau** ; **un échec la détruit**.
- Fait tourner l'économie : une clé haut niveau est un objet de valeur qui se revend ; les échecs la
  retirent du marché et maintiennent la valeur des clés hautes.

Points à trancher : chef qui quitte en cours de route (la clé reste engagée et perdue) ; niveau de
clé maximal utilisable selon le niveau des joueurs (anti-abus).

## Existant (première lecture)

- `world/dungeons.json` `dungeon_rat_den` (Égouts de Havreden) : 3 paliers tous ouverts, car **le drop
  des clés n'est branché nulle part côté serveur** (`dungeon_key_drops` / `zone_drops` de
  `items/loot_tables.json` = data morte).
- Clés dans `items/consumables.json` ; design dans `world/DONJONS_OUVERTS.md` ; `systems/tower.json`.
