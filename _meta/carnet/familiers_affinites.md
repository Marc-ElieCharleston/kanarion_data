# Familiers : identité et affinités — décisions du 2026-10-13

Ce qu'on capture EST notre familier ; seule la rareté tirée à la capture change (commun → légendaire).
Un familier = **stats d'espèce** (profil de rôle × identité de l'espèce) + **signature** + **affinité**.

## Couche 1 — signature (data)

Une famille de familier par monstre ; sa signature est la compétence unique du monstre capturé, adaptée à un
familier (valeurs plus basses, recharge 4-8 s, pas de contrôle dur). Faite pour les 27 nouveaux monstres
(`vac_monstres-nouveaux`) ; à faire ensuite pour les anciens regroupés (Loup Enragé, Loup Meneur, Loup-Garou → loup ;
Rat Sorcier → rat…).

## Couche 2 — affinité (serveur, à brancher) — version 26 affinités (2026-10-13)

Un passif qui se déclenche tout seul : à **chaque compétence lancée** par le familier, un tirage (un seul par lancement,
pas sur l'attaque de base) ajoute l'effet de son affinité. Pas de délai interne : la faible chance suffit.

**Chance par rareté tirée** (validée) : commun 2 %, uncommon 4 %, rare 6 %, epic 8 %, légendaire 10 %.
Les monstres plus rares doivent naturellement être plus forts : l'écart est voulu.

**Durées** (règle du propriétaire : un debuff dure 4 s = 2 GCD joueur ; 1 s ne sert à rien face au GCD de 2 s) :
debuffs 4 s ; enracinement 4 s en PvE, 2 s en PvP ; Gel 2 s, PvE seulement ; déplacements instantanés, **1 case max** ;
bouclier 4 s. Jamais de déplacement ni d'enracinement sur un boss.

| Affinité | Espèces | Effet |
|---|---|---|
| Meute | loups, chiens | Saignement |
| Charognard | hyènes, chacals | + dégâts si la cible a moins de 50 % de vie |
| Fauve | chats sauvages, belette | coup critique garanti (sinon Critique + 4 s si l'effet n'existe pas) |
| Rusé | renards | Esquive + sur soi |
| Colosse | ours | Armure − sur la cible |
| Charge | sangliers, taureaux, bovins | Repousse d'une case |
| Ramure | cerfs, biches | soin continu sur l'allié le plus blessé |
| Troupeau | chèvres, béliers, moutons, chevaux | réduction de dégâts sur l'allié le plus proche |
| Rongeur | rats, ragondin, lièvre | Poison |
| Venin | serpents, scorpions, araignées | Poison renforcé (2 charges) |
| Carapace | tortues, tatous, hérissons | bouclier sur soi |
| Essaim | scarabées, insectes | Précision − |
| Batracien | grenouilles, crapauds | Attire d'une case |
| Ailé | corbeaux, volatiles | Échange de place avec l'ENNEMI ciblé (1 case ; pas encore codé) |
| Aquatique | loutres, crocodiles | Ralentissement |
| Sylvestre | esprits des bois, créatures végétales | Enracinement |
| Pierre | golems, gardiens de pierre | Armure + aux alliés de la ligne |
| Givre | cristal, variantes de givre | Froid ; Gel en légendaire (PvE) |
| Braise | braise, variantes de braise | Brûlure |
| Faille | faille, bêtes Fissurées et Flétries | Exposé |
| Ombre | effroi | anti-soin |
| Spectre | spectres, revenants | Silence 2 s |
| Vide | vide | vol de Souffle |
| Mort | squelettes, nécromanciens | petit soin sur soi |
| Abysse | abyssaux | dégâts supplémentaires sur ce lancement |
| Déchu | anges déchus (archonte_dechu) | Aveuglement (4 s PvE, 2 s PvP) |
| Démon | démons | Vulnérable |

Le moteur a déjà root, knockback, pull et swap. Un `FamiliarPassiveProcessor` existe déjà en combat (poison, saignement,
silence) : on l'étend plutôt que le moteur des runes. Plan d'implémentation : `_meta/conception_systemes/AFFINITES_FAMILIERS.md`
(écrit avec 9 affinités, à mettre à jour). Correspondance espèce → affinité : en cours.

**Cas douteux tranchés (2026-10-13)** : cochon et vache → Troupeau (les taureaux restent Charge) ; blaireau → Fauve ;
hybride sanglier-loup → Charge ; loup-garou et loup noir → Meute ; cerf obscur → Ombre ; faucheur d'âmes → Mort ;
revenant du Vide → Vide ; dévoreur d'âmes → Démon ; rat sorcier → Rongeur. 27 affinités en tout (avec Déchu).
Les anges déchus n'ont pas encore de familier (lot mis de côté pour le passage sur le lore).

**Poison et PvP** : le poison retire 2 % des PV max par charge et par seconde. Sur les cibles MONSTRES, un plafond existe
déjà (`vac_poison-cap` 1c45a99f : par charge, max(ATK, MAG) × 0,5 de la source). Sur les joueurs, rien : à coder, le même
plafond quand la cible est un joueur et la source un joueur ou un familier (les monstres contre les joueurs gardent les
2 % sans plafond, levier anti-tank voulu).
