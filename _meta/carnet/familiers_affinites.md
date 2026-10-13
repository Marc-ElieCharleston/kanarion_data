# Familiers : identité et affinités — décisions du 2026-10-13

Ce qu'on capture EST notre familier ; seule la rareté tirée à la capture change (commun → légendaire).
Un familier = **stats d'espèce** (profil de rôle × identité de l'espèce) + **signature** + **affinité**.

## Couche 1 — signature (data)

Une famille de familier par monstre ; sa signature est la compétence unique du monstre capturé, adaptée à un
familier (valeurs plus basses, recharge 4-8 s, pas de contrôle dur). Faite pour les 27 nouveaux monstres
(`vac_monstres-nouveaux`) ; à faire ensuite pour les anciens regroupés (Loup Enragé, Loup Meneur, Loup-Garou → loup ;
Rat Sorcier → rat…).

## Couche 2 — affinité (serveur, à brancher)

Un passif qui se déclenche **à chaque compétence lancée** par le familier. Familles tirées de `monster_species` :

| Affinité | Espèces | Effet |
|---|---|---|
| Sauvage | loups, sangliers, ours, cervidés, félins, rongeurs… | Saignement |
| Givre | cristal | Froid (ralentit) ; Gel complet réservé aux légendaires |
| Braise | braise | Brûlure |
| Faille | faille, variantes Fissurées | Exposé |
| Ombre | spectre, effroi | soins reçus par la cible réduits |
| Pierre | golem, tortue, scarabée | petit bouclier sur soi |
| Vide | vide | vol de Souffle |
| Mort | squelettes, nécromanciens | petit soin sur soi |
| Abysse | abyssal, démons | dégâts supplémentaires |

**Chance par rareté** (validée 2026-10-13) : commun 2 %, uncommon 4 %, rare 6 %, epic 8 %, légendaire 10 %.
Les monstres plus rares doivent naturellement être plus forts (décision du propriétaire) : l'écart est voulu.

Aujourd'hui les passifs de familier ne font que des stats (hp / mp / atk / mag / armor / magic_resist) : il faut brancher
les procs côté serveur, sans doute en réutilisant le moteur des runes, qui fait déjà ce genre d'effet. Vérifier en PvP
(Froid et anti-soin) avant d'ouvrir.
