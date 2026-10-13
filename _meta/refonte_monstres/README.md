# Refonte des monstres — travail des agents (2026-10-02)

Revue des 200 monstres par 4 agents relecteurs (un lot de familles chacun) et conception des
nouvelles compétences par un agent dédié, à partir du contexte commun `CONTEXT.md`
(règles : espèce × stade × archétype, 11 archétypes, kits 2/3/4 selon palier et niveau 40).
Rien n'est encore appliqué à `entities/monsters.json` ni à `skills/monster_skills.json`.

| Fichier | Contenu |
|---|---|
| `CONTEXT.md` | Règles données aux agents |
| `kits_tous.csv` | Les 200 monstres fusionnés : lot, espèce, stade, archétype final, palier, niveau, kit proposé (ids ordonnés, `\|`), raison, anomalies de stats / compétences, compétences manquantes |
| `kits_betes_a.*`, `kits_betes_b.*`, `kits_humanoides.*`, `kits_sud.*` | Tableau et rapport de chaque relecteur |
| `new_skills.json` | Les 24 nouvelles compétences (7 identités, 3 rôles, 14 attaques d'espèce) au format de `monster_skills.json` ; à ranger dans `basic_skills` / `role_basic_skills` / `archetype_skills` |
| `new_skills_report.md` | Mécanique et preuve serveur (fichier:ligne) de chaque compétence, limites, code serveur nécessaire |

Les actions qui en découlent sont dans `_meta/TODO_RETOUR.md`.
