# Kanarion Editor

Editeur web Next.js 16 pour visualiser et modifier la base de donnees JSON de Kanarion Online.

## Setup

```bash
cp .env.example .env   # Configurer DB_ROOT (defaut: ..)
npm install
npm run dev            # localhost:3000
```

### Variable d'environnement

| Variable | Defaut | Description |
|----------|--------|-------------|
| `DB_ROOT` | `..` | Chemin relatif ou absolu vers la racine de la DB (le dossier contenant `_meta/`, `classes/`, etc.) |

## Commandes

```bash
npm run dev      # Serveur de dev (localhost:3000)
npm run build    # Build production (prebuild copie les JSON)
npm run lint     # ESLint
```

## Architecture

- **Pages** (`src/app/*/page.tsx`) : Classes, stats, effects, skills, loot, equipment, systems, ideas
- **API Routes** (`src/app/api/*/route.ts`) : Lecture des fichiers JSON cote serveur
- **Database** (`src/lib/database.ts`) : I/O JSON centralise, utilise `DB_ROOT` pour localiser les fichiers
- **UI** : shadcn/ui + composants custom (Sidebar, AoeGrid, SkillCard, StatsDisplay)

## Path Alias

`@/*` mappe vers `./src/*` (tsconfig.json).
