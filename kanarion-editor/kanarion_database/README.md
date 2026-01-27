# KanarionDB

Base de données JSON pour **Kanarion Online** - MMORPG mobile 2D avec combat en grille.

## Version

- **Version**: 0.9.0-alpha
- **Database Version**: 3.0
- **Dernière mise à jour**: 2026-01-20

## Structure

```
kanarion_database/
├── _meta/          # Métadonnées du projet
├── schemas/        # JSON Schemas (validation)
├── config/         # Configuration globale du jeu
├── classes/        # Classes jouables (6 classes)
├── stats/          # Système de statistiques
├── entities/       # Monstres, NPCs, boss
├── items/          # Équipements, consommables, matériaux
├── world/          # Zones, quêtes, carte du monde
├── systems/        # Systèmes de jeu (économie, PvP, guildes...)
└── ui/             # Interface utilisateur
```

## Contenu

| Catégorie | Contenu |
|-----------|---------|
| Classes | 6 base + 24 sous-classes + 48 évolutions tier 3 |
| Monstres | 50+ types uniques avec variantes |
| Skills | 100+ compétences |
| Zones | 10 zones MVP (niveau 1-20) |
| Stats | 40+ statistiques trackées |

## Combat

- **Grille**: 4×4 (16 slots, max 10 joueurs par équipe)
- **Rows**: front, mid_front, mid_back, back
- **Système**: Temps réel avec GCD 2.0s, drag-and-drop
- **Line of Sight**: Auto-attacks bloquées si la cible a des unités devant (même colonne)

## Pour les développeurs

### Validation des données

Les fichiers dans `schemas/` définissent la structure attendue de chaque type de données.
Utilisez un validateur JSON Schema pour vérifier l'intégrité des fichiers.

### Convention de nommage

- Monstres: `mob_*`
- Skills: `skill_*`
- Zones: `zone_*`
- Items: `item_*`, `mat_*`, `cons_*`
- NPCs: `npc_*`

### Fichiers de configuration

- `config/game.json` - Constantes globales du jeu
- `config/combat.json` - Formules et paramètres de combat
- `config/monster_ai.json` - Comportements IA des monstres
- `config/status_effects.json` - Règles des buffs/debuffs

## Licence

Propriétaire - Tous droits réservés.
