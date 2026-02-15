# KanarionDB — Source de Verite

Base de donnees JSON pour **Kanarion Online** — MMORPG mobile 2D avec combat en grille.

Ce repo est la **source de verite unique** pour toutes les donnees de jeu. Il est consomme par le client Godot et le serveur C++ via git submodule (`kanarion-meta/`).

## Version

- **Version**: 3.1.0
- **Schema Version**: 1.0
- **Content Hash**: SHA-256 dans `_meta/version.json` (regenere automatiquement)

## Structure

```
kanarion_data/
├── _meta/          # Metadonnees (version.json, index.json, changelog)
├── classes/        # 6 classes × 4 sous-classes (skills.json + passives.json)
├── combat/         # Targeting, Line of Sight
├── config/         # Combat formulas, game constants, monster AI, status effects
├── entities/       # Monstres, NPCs, boss mechanics, variantes
├── items/          # Equipements, consommables, materiaux, loot tables, affixes
├── stats/          # 40+ stats, class base stats, growth rates
├── systems/        # Economie, progression, guildes, PvP, achievements
├── ui/             # Icons
├── world/          # Zones, quetes, donjons, carte du monde
└── scripts/        # gen_hash.sh, pre-commit hook
```

> **Note** : L'editeur web est dans un repo separe : [`kanarion-tool`](https://github.com/Marc-ElieCharleston/kanarion-tool)

## Workflow : modifier les donnees

```bash
# 1. Editer un JSON
vim entities/monsters.json

# 2. Regenerer le content_hash
./scripts/gen_hash.sh

# 3. Commit (le pre-commit hook verifie que le hash est frais)
git add . && git commit -m "feat: add mob_dragon"

# 4. Push
git push origin master

# 5. Synchroniser front + back
cd ../kanarion_front && ./sync_data.sh
```

Le pre-commit hook bloque tout commit ou le `content_hash` ne correspond pas aux fichiers JSON modifies.

## Editeur web

L'editeur est dans un repo separe : [`kanarion-tool`](https://github.com/Marc-ElieCharleston/kanarion-tool)

```bash
cd kanarion-tool/kanarion-editor
cp .env.example .env   # DB_ROOT=../kanarion_data
npm install
npm run dev            # localhost:3000
```

L'editeur lit/ecrit les fichiers JSON de `kanarion_data` via le chemin configure dans `.env`.

## Consommation par les projets

| Projet | Chemin submodule | Lecture |
|--------|-----------------|---------|
| Client Godot (`kanarion_front`) | `kanarion-meta/` | GDScript `DataDB` charge les JSON au boot |
| Serveur C++ (`kanarion_back`) | `kanarion-meta/` | `ContentLoader` charge les JSON au demarrage |

Les deux repos pinnent le **meme commit exact** — jamais de `--remote`, toujours `git checkout <hash>`.

## Contenu

| Categorie | Contenu |
|-----------|---------|
| Classes | 6 base + 24 sous-classes |
| Monstres | 50+ types avec variantes |
| Skills | 100+ competences |
| Zones | 10 zones MVP (niveaux 1-20) |
| Stats | 40+ statistiques |
| Items | Equipements, materiaux, consommables, loot tables |

## Conventions de nommage

- Monstres: `mob_*`
- Skills: `skill_*`
- Zones: `zone_*`
- Items: `item_*`, `mat_*`, `cons_*`
- NPCs: `npc_*`

## Licence

Proprietaire — Tous droits reserves.
