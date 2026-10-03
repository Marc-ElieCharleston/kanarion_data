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
- **Agressivité selon l'écart de niveau (propriétaire, 2026-10-03)** : un monstre de **10 niveaux ou
  plus au-dessus du joueur devient agressif** (il attaque de lui-même). Sinon les joueurs se baladent
  partout sans crainte, ce qui casse l'histoire (on ne doit pas atteindre Rochebourg trop tôt). Même si
  un joueur de haut niveau l'accompagne, le joueur de bas niveau doit éviter les aggros. Le serveur de
  combat a `aggro_range` / `is_aggressive` (`components.hpp:593`) ; à vérifier côté monde ouvert
  (presence).
- Serveur V2 complet (branche back `vac_v2-monster-model`), compilé et testé dans WSL.
