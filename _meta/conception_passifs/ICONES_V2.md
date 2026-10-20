# Icônes de l'arbre des passifs V2

- **Les 40 icônes V2 de la première commande sont livrées** (client `497f7c2a7`, `assets/icons/passives/tree/v2_*.png`)
  et branchées par l'intégration du 2026-10-20. Les nœuds passés en stats gardent leur id, donc leur icône.
- **14 icônes à commander** pour ce que l'intégration a ajouté (6e bras Arcanes, ponts Soin ↔ Arcanes et
  Arcanes ↔ Soutien). En attendant, chaque nœud affiche une icône EXISTANTE proche (`icon`), et le fichier attendu
  est noté dans `icon_planned`. Source : `icones_v2_a_creer.json`, régénéré par `gen_arbre_v2.py`. À la livraison :
  déposer le fichier, retirer l'entrée de `PLACEHOLDER` dans `gen_arbre_v2.py`, relancer le générateur.

## Consigne pour l'agent graphique

- **Format** : PNG 128 × 128, opaque, fond noir, même rendu que `assets/icons/passives/tree/` (peinture dark
  fantasy, un sujet central, une lueur de la couleur du bras). Comparer avec `execution.png`, `rhythm.png`,
  `v2_atk_breach.png`.
- **Lueur** : Arcanes cyan `#4fd1c5` ; ponts : les deux couleurs (Soin vert `#5cc78f`, Soutien or `#f2b84d`).
- **Lisible à 30 px** (téléphone, arbre dézoomé) : silhouette forte, pas de détail fin.
- **Les 2 mégas** : sujet plus imposant, bord doré discret, contrepartie suggérée dans le dessin.
- **Fichier** : `assets/icons/passives/<Fichier>`. Aucun commit de l'agent graphique.

## Liste

| Bras | Type | Nom | Fichier | Remplacement actuel | Sujet proposé |
|---|---|---|---|---|---|
| arcane | notable_15 | Puissance arcanique | `tree/v2_arc_arcane_power.png` | `common/intellect` | un livre ouvert d'ou jaillit une flamme bleu-vert |
| arcane | notable_15 | Incantation vive | `tree/v2_arc_quick_casting.png` | `tree/cast_speed` | une main qui trace un sceau en un eclair, trainees cyan |
| arcane | side | Esprit perçant | `tree/v2_arc_piercing_mind.png` | `common/arcane_piercing` | une aiguille de lumiere cyan qui traverse un bouclier runique |
| arcane | notable_30 | Siphon | `tree/v2_arc_siphon.png` | `tree/spell_vamp` | un tourbillon cyan aspire par une paume ouverte |
| arcane | notable_30 | Torrent | `tree/v2_arc_torrent.png` | `common/breakthrough` | un torrent d'energie cyan qui brise une rune |
| arcane | notable_30 | Maîtrise du temps | `tree/v2_arc_time_mastery.png` | `tree/cooldown_reduction` | un sablier entoure d'anneaux runiques cyan |
| arcane | notable_50 | Archimage | `tree/v2_arc_archmage.png` | `common/focus` | un baton couronne d'un cristal cyan, robe etoilee |
| arcane | notable_50 | Surcharge | `tree/v2_arc_overload.png` | `common/breakthrough` | un cristal fissure qui deborde d'energie cyan |
| arcane | side | Méditation | `tree/v2_arc_meditation.png` | `tree/mp_regen` | une silhouette en tailleur, souffle cyan qui monte |
| arcane | mega | Archonte | `tree/v2_arc_mega_archon.png` | `common/intellect` | un mage immense flottant, couronne de runes, le corps translucide (PV sacrifies) |
| arcane | mega | Tempête arcanique | `tree/v2_arc_mega_storm.png` | `tree/cast_speed` | une tempete d'eclairs cyan, la fiole de Souffle vide a la ceinture |
| healing+arcane | hybrid | Lumière arcanique | `tree/v2_hyb_heal_arc.png` | `tree/heal_power` | une main qui soigne, lumiere verte melee de runes cyan |
| healing+arcane | hybrid | Siphon vital | `tree/v2_hyb_heal_arc_side.png` | `tree/spell_vamp` | un filet de vie verte aspire par un sort cyan |
| arcane+support | hybrid | Résonance | `tree/v2_hyb_arc_sup_side.png` | `tree/buff_duration` | une onde doree et cyan qui se propage en cercles |
