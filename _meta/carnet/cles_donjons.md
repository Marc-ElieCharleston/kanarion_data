# Clés de donjon et clé de la tour infinie

Statut : décisions du propriétaire (2026-10-13), en cours d'implémentation (data `vac_dungeon-keys`
`334e634`, serveur `vac_dungeon-keys` en cours).

## Décisions du 2026-10-28

- La clé tombe **par tranche de niveau** (règle du 13/10), **dans le donjon** (les monstres des étages sont
  dans la tranche) et **sur le boss** : `dungeon_key_drops.boss_drops`, un tirage par joueur qui remplace la
  tranche pour ce monstre. Proposition à valider : **25 %** sur le Rongeur (`_pending_boss_drops`).
- **Craft** : `recipe_rune_key_rat_den` (Runiste niveau 10, 2 lingots I + 6 queues + 4 fourrures de rat,
  15 or, 80 XP), à valider. Les métiers sont branchés depuis : la recette est utilisable dès que la clé
  sert à quelque chose.
- **Client** : la fenêtre d'entrée demande au serveur (DUNGEON_ENTRY_STATUS 0x0B2A / 0x0B2B) la clé de
  chaque palier, le nombre possédé, le palier d'avant fini ou non. Les clés sont chargées dans l'inventaire
  (nom, icône, onglet Objets) et ne proposent pas « Utiliser ».
- **CI** : `validate_cross_references.py` [12y] refuse un `key_required`, une règle de drop ou une recette
  qui nomme une clé absente des objets.
- Fort des Bandits : `key_required` passé à `null` (ses clés `key_bandit_fort_*` n'existent pas), intention
  gardée dans `_key_required_planned`. Décision ouverte, comme le Repaire niveau 20 et la Tour d'Asher.
- **Toujours rien d'actif** : aucun palier ouvert ne demande de clé. Les règles restent en `_pending_*`
  jusqu'à la déclaration de `fissure_2`.

## Décisions du 2026-10-15

- **Une seule clé par donjon**, valable pour les paliers fissure 2 et 3 (pas une clé par palier : la
  difficulté vient des monstres ; des clés par palier éclateraient le marché et la règle « jamais sous
  le palier » obligerait à faire tomber la clé fissure 3 sur des monstres qui n'existent que dedans).
- **Un palier s'ouvre quand le joueur a fini le palier d'avant** (`requires_cleared`).
- **3 % par monstre** de la tranche. Un groupe des Égouts compte 8 monstres : environ une clé tous les
  4 à 5 combats dans le donjon, une tous les 11 combats dehors (packs de 3).
- **Recette de clé** (seconde source) : chez le Runiste, avec des ressources de la tranche.
- Repaire des Bandits (ancien donjon 1-20) : **on n'y touche pas** (ses clés restent sans source).
- Fait (branches `vac_dungeon-keys2`) : `key_rat_den`, sa règle de drop en attente du palier 2
  (`_pending_level_band_drops`), `recipe_rune_key_rat_den`, gardes dans `scripts/dungeon_content.py`,
  porte `requires_cleared` dans le dungeon service.
- Reste : les paliers 2 et 3 des Égouts (cartes, au bureau) ; la clé hebdomadaire du pass premium
  (aucun système d'abonnement côté serveur aujourd'hui) ; les métiers ne sont pas encore branchés,
  donc la recette n'est pas encore utilisable.

## Décisions du 2026-10-13 (second passage)

- **Tour infinie : seule la clé utilisée monte de niveau** (les clés hautes restent rares et élitistes,
  comme dans Albion). Au clear de l'étage 20·n, le porteur de la clé reçoit la clé du palier n+1 ; les
  autres rien (avant : chaque membre en recevait une, inflation). **+ faible chance (2 % par membre
  et par étage) de trouver une clé du palier de l'étage.**
- **Clés de donjon : drop par tranche de niveau du monstre** (`loot_tables.json`
  `dungeon_key_drops.level_band_drops`), jamais en dessous du palier du donjon. Vide pour l'instant :
  les paliers 2 et 3 des Égouts sont du contenu de carte (bureau).
- **Les deux anciennes Tours d'Asher sont à retirer** (le vrai donjon a été refait au bureau). Pas
  supprimées ici : quêtes, PNJ, monstres et carte les référencent, tout ça est au bureau → à faire à la
  fusion, avec la version du bureau.

## Difficulté des donjons (proposé)

Comme les Égouts aujourd'hui : **tranche de niveau des monstres par étage + composition des groupes
fixes** (les anciens multiplicateurs PV / dégâts par difficulté sont abandonnés, rien ne les lit).
Paliers fissure 1 / 2 / 3 : niveau de base / +3 à +5 / +6 à +10 ; groupes surtout combattants /
+ soigneurs et contrôleurs / archétypes variés et élites ; étoiles 0-1 / 2-3 / 4-5 ; boss : mécaniques
de base / une phase de plus / toutes les phases. Le modèle V2 fait le reste.

## Déjà en place (inventaire du 2026-10-13)

- **Consommation à l'entrée, une clé par joueur : déjà codée** (dungeon service, erreur 1025 « clé
  manquante », fenêtre client « clé requise »).
- Tour infinie : clés échangeables, consommées par le chef à l'entrée, données au clear des étages 20·n.
- Manque : toute source de clé de donjon ; clés et paliers 2-3 des Égouts ; anciens donjons incohérents
  (doublon Asher, clés inexistantes, zones fantômes, niveaux 9-20).

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
