# Sceaux (nom provisoire) : effets déclenchés à insérer dans l'équipement

Statut : idée du propriétaire (2026-10-05), à concevoir. Inspiration : les cartes de monstres de
Ragnarok Online (« X % de chance de lancer Météore », « +X % de double attaque »).

## Ce qui existe déjà

- Le moteur de déclencheurs générique **ProcProcessor** (uniques, keystones) : sur coup, critique,
  sort lancé, dégâts reçus, seuil de PV… ; effets : statut, soin, bouclier, bonus de dégâts…
  Un sceau = un petit objet avec un bloc d'effet **au même format que les uniques**.
- Double / triple attaque déjà en combat (`double_attack_chance`, `triple_attack_chance`).
- **Manque** : des **emplacements** sur l'équipement (aucun aujourd'hui).

## Nom

Pas « cartes » (les cartes Koro existent). Proposés : **Sceaux** (recommandé, colle aux noms hébreux
et à la symbolique), Éclats de Souffle (lore : économie des éclats), Runes (simple).

## Proposition

- Emplacements selon la rareté de l'objet : 0 commun, 1 rare, 2 légendaire.
- Insertion à la forge ; retrait contre de l'or (puits d'économie, changer de build).
- Effets horizontaux : X % de chance de lancer un sort (éclair, météore), doubler un sort, voler du
  Souffle, bouclier sous 30 % PV…
- **Garde-fous** : chance faible, **délai interne** par sceau, pas de cumul illimité, plafond de
  double sort ; attention au PvP.
- **Drop sur les monstres**, une espèce = son sceau (rare) : une raison de chasser une espèce précise,
  lien avec le bestiaire et les collections.
- Un **agent d'animations** est prêt : chaque sceau aura un effet visuel de déclenchement.

## À faire

- [ ] Document de conception : liste des sceaux, déclencheurs, garde-fous, emplacements, sources.
