# Loot et ressources

## Rythme (propriétaire, 2026-10-03)

- **Régler le loot pour qu'on ne soit pas équipé trop vite.**
- Idem pour les **ressources**, surtout les ratios en **donjon** et en groupes **4 et 5 étoiles**.
- Le contenu est volontairement dur (un joueur seul de niveau 60 ne passe pas la Tour d'Asher).

## Loot partagé, comme Dofus (propriétaire, 2026-10-13)

- **Un butin commun par combat**, puis **partagé**. Avant : loot personnel (un tirage par joueur, chacun
  garde le sien).
- Taille du pot : on garde **un tirage par joueur** mis en commun (un groupe n'est pas puni).
- **Répartition en aléatoire PUR, comme Dofus** : chaque objet (empreintes de familier comprises) va
  à un joueur tiré au sort, indépendamment des autres. Pas d'équilibrage : un joueur peut avoir 3 objets
  et un autre 0 (le tour de rôle ± 1 a été refusé). Pas de stat de prospection (une stat « chance »
  plus tard, peut-être).
- **Seuls les joueurs comptent** : familiers et mercenaires ne prennent pas de part.
- **XP et or restent personnels** ; seuls les objets passent par le pot.
- Serveur : branche back `vac_shared-loot` (`418b9273`, pas encore compilée).

## Tables de loot (2026-10-13)

- **Commun à tous les monstres** (`loot_tables.json` `base_drops` + catégories globales) : or, XP,
  consommables de base, pierres de forge ; et par combat : équipement (par thème, `equipment_affinity`),
  panoplies, uniques, grimoires, keystones, cartes Koro, clés de donjon (par tranche de niveau).
- **Une table par monstre** (`monster_loot_tables`) : les ressources de l'espèce.
- **Plus de table « default »** (propriétaire) : les 37 monstres qui y retombaient ont leur table, faite
  des matériaux existants de leur espèce (data `vac_monster-loot` `a7f4013`). Le validateur exige une
  table pour chaque monstre (liste vide explicite permise). Le serveur ne retombe plus sur « default »
  (back `vac_integration-all` `96e51de5`).
- **Un autre agent du propriétaire ajuste les ressources pour qu'elles servent les métiers d'artisanat :
  ses choix priment sur ces premières tables.**

## Cible

- Niveau maximum en 2 semaines à 1 mois, sans système d'énergie.
- Progression horizontale plutôt que verticale.

## Questions

- [ ] Mesurer les taux actuels (donjons, étoiles) avant de régler.
