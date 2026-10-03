# Monstres V2

Détail : `_meta/refonte_monstres/DECISIONS.md`, `kits_tous.csv`, `config/monster_scaling_model.json`.

- Modèle : **espèce × stade × archétype × niveau × tier × étoiles × contenu**.
- **11 archétypes** : tank, guardian, brute, berserker, assassin, archer, mage, controller, healer,
  summoner, enchanter.
- Placement par niveau : animaux 1-40, humains touchés par les Failles 45-55, fanatiques ~55-60, la
  Tour d'Asher à 60, créatures après 60 (voir [carte.md](carte.md)).
- Philosophie : PvE pensé pour le groupe, « mieux vaut trop dur que trop facile », niveaux 1-30
  faciles, danger croissant vers le sud.
- **Déplacements** (décidé) : un déplacement par archétype, adapté à son style, **recharge longue**
  (sinon un corps-à-corps n'attrape jamais un mage ou un archer qui saute). Les gardiens peuvent
  échanger de place pour protéger. Niveaux 1-10 : seulement le déplacement de base d'une case.
- Pas de contrôle dur sur les compétences à recharge courte.
- Serveur V2 complet (branche back `vac_v2-monster-model`), compilé et testé dans WSL.
