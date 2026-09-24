# Ajouter un donjon ouvert

Premier donjon livré sur ce modèle : **Égouts de Havreden** (`dungeon_rat_den`, difficulté `fissure_1`, 5 étages), le 2026-09-23.

## Paliers de difficulté

Chaque difficulté (`fissure_1`, `fissure_2`, ...) est un palier distinct, avec ses propres zones d'étage et son propre jeu de monstres. Aucun multiplicateur d'instance ne s'applique. Pour les Égouts, `fissure_1` est la **version facile**, celle que propose Varn (contenu 10-14). Les paliers plus durs viendront avec leurs zones. Le jeu est volontairement exigeant : ne pas affaiblir un palier pour le rendre « faisable ».

Un camp compte au plus **10 entités**, mercenaires et invocations compris. Un groupe de monstres en compte donc au plus 10, et le validateur le vérifie. Les invocations d'un boss respectent ce plafond (`Room::summon_monsters`).

**Groupes (Charleston, 2026-09-24).** 8 monstres par groupe, 3 à 5 groupes par salle. L'étoile d'un groupe n'est pas écrite : presence la tire à chaque apparition et réapparition selon `structure.star_weights` (Égouts : 30 % 3★, 40 % 4★, 30 % 5★). Un groupe qui écrit `stars` (le boss, 5★) n'est pas tiré ; un groupe peut aussi porter ses propres `star_weights`.

## Le modèle en une phrase

Un donjon ouvert est une suite de zones d'étage **partagées** (plusieurs joueurs s'y croisent). La progression, elle, est **individuelle** : le serveur la tient en base (`character_dungeon_progress`) et décide de tout. Le client affiche le résultat et se rend là où le serveur l'envoie.

## Règles de parcours (Charleston, 2026-09-23)

| Situation | Effet |
|---|---|
| Victoire contre un groupe de l'étage | Étage validé pour **tous les participants de l'équipe gagnante**, morts compris. Téléportation automatique à l'étage suivant. |
| Dernier étage | Validé seulement si `boss.id` figure parmi les monstres tués. |
| Défaite | Retour au village, reprise à l'étage 1. |
| Sortie volontaire (quitter un étage vers une zone hors donjon) | Reprise à l'étage 1. |
| Déconnexion | Progression conservée. Au retour, entrer à nouveau reprend l'étage atteint. |
| Joueur hors du combat, spectateur | Rien. |

Toute nouvelle règle (durée de conservation après déconnexion, clés d'entrée, verrouillage) se décide avec Charleston avant d'être codée.

## Où vit chaque donnée

`world/dungeons.json` est la **seule** source des monstres d'un donjon. `world/zones.json` ne porte que les zones d'étage (porte d'entrée, contour, décor) et **ne redéclare jamais** de monstres.

### Dans `world/dungeons.json`

```jsonc
{
  "id": "dungeon_xxx",
  "type": "open_instance",
  "zone_prefix": "dungeon_xxx",
  "zone_id_pattern": "{zone_prefix}_f{floor}_{difficulty}",
  "min_level": 1,                      // porte d'entrée (vérifiée par le serveur)
  "recommended_party_size": [3, 5],   // affichage seulement
  "exit_zone": "village",              // où l'on revient (sortie, boss vaincu)
  "exit_position": [x, y],             // point d'arrivée dans exit_zone
  "structure": {
    "floor_count": 5,
    "groups_needed_to_advance": 1,
    "boss_floor_index": 4,             // = floor_count - 1
    "spawn_model": "fixed_groups",     // active le contrat décrit ici
    "star_weights": {"3": 30, "4": 40, "5": 30}  // tirage de l'étoile de chaque groupe
  },
  "difficulties": { "fissure_1": { "key_required": null } },
  "floors": [
    {
      "floor": 1,
      "mob_level_range": [8, 9],       // niveau des monstres de l'étage
      "entry_position": [x, y],        // point d'arrivée dans la salle
      "monster_groups": [
        { "id": "f1_...", "position": [x, y],        // étoile tirée (structure.star_weights)
          "members": ["mob_leader", "mob_b", "mob_c"] }   // members[0] = chef du pack
      ]
    },
    // ... dernier étage : un groupe "is_boss": true dont members[0] == boss.id
  ],
  "boss": { "id": "mob_boss", ... }
}
```

### Dans `world/zones.json`, une zone par étage et par difficulté

```jsonc
{
  "id": "dungeon_xxx_f1_fissure_1",
  "type": "dungeon_open",
  "dungeon_id": "dungeon_xxx",
  "floor": 1,
  "level_range": [1, 9],        // [0] = porte joueur = min_level du donjon. Jamais le niveau des monstres.
  "map_path": "res://scenes/world/donjons/xxx/dungeon_xxx_f1.tscn",
  "area_limit": [[x, y], ...],  // contour RoomBounds de la scène
  "combat_backdrop": "xxx_backdrop",
  "respawn_zone": "village"
  // PAS de spawn_areas, PAS de mobs
}
```

## Procédure

1. **Data** (`kanarion_database`) : écrire le donjon et ses zones comme ci-dessus.
2. **Valider** : `python scripts/dungeon_content.py --front ../kanarion_front`. Le script refuse notamment :
   - un boss absent du dernier étage ;
   - une porte d'entrée différente de `min_level` ;
   - des `spawn_areas` dans une zone d'étage ;
   - un point d'arrivée ou un groupe hors du contour de la salle ;
   - un monstre inconnu ;
   - une scène manquante.

   La CI le relance à chaque push.
3. **Hash** puis commit (voir `CLAUDE.md`, section Windows).
4. **Template SQL** : `python scripts/dungeon_content.py --dungeon dungeon_xxx --sql out.sql`, puis copier la sortie dans une **nouvelle** migration de `kanarion_back/tools/db-migrate/` (lister le dossier avant de choisir le numéro). Ne jamais réécrire une migration déjà appliquée. Le test `test_templates_ship_with_the_migrations` vérifie la correspondance avec `--check-sql`.
5. **Client** (`kanarion_front`) :
   - une scène par étage, avec un `RoomBounds` qui correspond à `area_limit` et le nœud `Player` placé sur `entry_position` ;
   - l'image du décor de combat déclarée dans `scripts/combat/visuals/combat_backdrop.gd` (`PATHS`), importée en compression avec perte comme les autres décors peints. Partir de `kanarion_front/tools/combat_backdrops/compose_rat_den_sewer.py` : il calcule le décor depuis le cadrage réel du combat (dalles alignées sur les cases, trottoir fin, espace avant le bord). Les générations IA ne respectent pas cette géométrie ;
   - un point d'entrée dans le monde (un interactable avec `metadata/dungeon_id`).
6. **Pins** : pousser `kanarion_database`, puis aligner `kanarion-meta` dans `kanarion_back` et `kanarion_front`.
7. **Tests** : adapter les constantes de `kanarion_back/tests/integration/test_dungeon_open_run.py` (ou dupliquer le fichier) et lancer la campagne services démarrés (`GATEWAY_TEST_MODE=1`) : `python -m pytest -m dungeon`.

## Pièges connus

- **Niveau de zone et niveau de monstre sont deux choses.** Le `level_range[0]` d'une zone d'étage est lu par presence comme niveau minimal du joueur. Les Égouts l'avaient à 8-13 et refusaient donc les bas niveaux en plein parcours.
- **`is_boss` n'est pas posé sur les packs de donjon.** Il déclenche le variant « field boss » du monde ouvert (PV ×2,2), qui s'ajouterait au palier de menace `boss`. Le serveur reconnaît le boss par son identifiant.
- **Portée et dernier rang.** Un lanceur ennemi placé au rang 0 est à 5 cases de la première ligne des joueurs. Les kits de portée 4 (mage, soigneur) ne l'atteignent qu'en se déplaçant. Un groupe boss composé uniquement de soigneurs et de lanceurs au fond peut devenir très long.
- **Réapparition.** Elle est globale à presence (`respawn_time_min/max_seconds`, 60 à 180 s) et ne se règle pas par donjon. Avec 2 ou 3 groupes par étage partagés, un étage peut se vider temporairement.
