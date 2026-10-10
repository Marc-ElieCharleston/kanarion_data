# Carte des monstres : proposition de répartition finale (2026-10-10)

Statut : **proposition à discuter** (agent, lecture seule). À recouper avec le travail non poussé du
bureau (nouvelle carte, zones, quêtes, **Tanière des loups + 5 nouveaux loups**).

Contraintes du propriétaire : PixelLab ne fait que **quadrupèdes et humanoïdes** ; araignées supprimées ;
progression animaux 1-40, humains touchés 45-55, fanatiques ~55-60, Tour 60+, créatures après 60 ; le lore
corrompt les espèces existantes plutôt que d'en inventer.

## Chiffres

| Indicateur | Nombre |
|---|---|
| Monstres | 200 (162 actifs, 38 mis de côté) |
| Actifs avec un sprite propre | 109 (75 animation + icône, 34 animation seule) |
| Actifs en repli de famille | 34 (11 stades acceptables, **23 « sosies »** : même visuel qu'un autre monstre) |
| Actifs sans aucun sprite | **19** |
| Actifs placés nulle part | **57** |
| Actifs ni quadrupèdes ni humanoïdes | 6 (3 scarabées, Serpent, Scorpion, Corbeau) + Gardien de la Forêt incertain |

Repli de famille = le client (`SpriteResolver`) prend le sprite de la famille (`rat_alpha` → `rat`).

## À supprimer / transformer

| Monstre | Recommandation |
|---|---|
| Petite Araignée, Reine Araignée, Reine Araignée des Cavernes | **supprimer** (+ `boss_mechanics`, zone `mz_spider_25_30`, matériaux `mat_spider_*`) ; le sprite `spider_queen` (silhouette humanoïde) pourrait être recyclé après 60 |
| Scarabée de Poussière | supprimer (doublon) |
| Serpent | supprimer (aucun sprite, seulement au Repaire) |
| Scarabée (+ Larve, Géant) | garder (sprites faits, le lore cite le « scarabée irritable ») ; le sprite inutilisé `giant_hornet` est en fait un scarabée, donc sprite propre du Géant ; ou option 100 % quadrupèdes |
| Scorpion Rocheux | garder (sprite fait, cité par le guide d'artiste) ou supprimer s'il ne doit rester aucun arachnide |
| Corbeau Charognard | garder (sprite fait), faune de Faille après 60, à confirmer en regardant le sprite |
| Gardien de la Forêt | quadrupède : grand cerf ancien corrompu (sa mécanique part déjà de `mob_cerf_obscur`) ; sprite à faire |
| Mis de côté « flous » (chérubin, chœur, éclat, Première Fissure…) | imposer un corps humanoïde, ou fusionner |

23 sosies : Louve et Hyène Matriarches, Charognard des Chemins, Chacal de la Faille, Rat Assassin, Rat
Cuirassé, Cerf Gardien, Porte-Bannière, 7 bandits du Fort + Pillard, 3 tribaux (qui affichent même le
**mauvais** sprite), Traqueur de Poussière (affiche un sanglier), Gardien de Pierre, Golem Corrompu, Pillard
d'Os. Sprite à faire, ou fusion. Astuce : renommer `boss_alpha_wolf` en `boss_wolf_alpha` suffit pour qu'il
reprenne le sprite du loup.

## Répartition proposée par zone

🟢 sprite propre, 🟡 repli acceptable (stade), 🔴 sprite à faire.

| Zone | Niv. | Monstres | Élite / boss |
|---|---|---|---|
| Havreden village (`rats_1_8`) | 1-8 | Jeune Rat 🟡, Rat 🟢, Lièvre 🟢 | Rat Alpha 🟡 |
| sans nom (`scarabees_3_8`, « Nid de Scarabées ») | 3-8 | A : Larve 🟡, Scarabée 🟢, Scorpion 🟢 ; B (quadrupèdes) : Marcassin 🟡, Lièvre 🟢, Renard 🟢 | Scarabée Géant 🟡 |
| Sanglier | 8-15 | Marcassin 🟡 (nouvel id), Sanglier 🟢, Sanglier Enragé 🟢, Bélier 🟢 | — |
| Prairie | 10-20 | Chèvre 🟢, Cochon 🟢, Brebis 🟢, Bouc 🟢 | Vache 🟢 |
| sans nom (« Clairière disputée ») | 6-15 | Sanglier, Sanglier Enragé, Loup, Loup Enragé 🟢 | Louve Matriarche 🟡→🔴 |
| Hyène | 9-20 | Hyène 🟢, Hyène Matriarche 🔴 | Hyène Alpha 🟢 (retirer le Charognard des Chemins, doublon) |
| Forêt | 12-26 | Lièvre, Renard, Biche, Blaireau 🟢 | Cerf 🟢 ; Renard Brumeux 🟢 élite rare |
| Loup | 13-23 | Loup, Loup Enragé 🟢, Louve Matriarche | Loup Meneur 🟡 ; boss Loup Alpha 🔴 (⚠️ Tanière du bureau) |
| sans nom (« Plaine des Taureaux ») | 16-25 | Cheval Sauvage 🟢, Tatou 🟢, Bélier 🟢 | Taureau 🟢 |
| Marécage | 20-30 | Grenouille, Grenouille Cornue, Grenouille Soigneuse, Crapaud Cracheur, Loutre 🟢 | Tortue de Pierre 🟢 |
| Ours | 20-28 | **famille Ours 🔴** (Ourson, Ours brun, Ourse) ; en attendant Blaireau, Tatou | Ours à carapace 🔴 (cité par le lore, niveau 4 de corruption) |
| sans nom, ex-araignées (« Bois Obscur ») | 25-30 | Cerf Obscur 🟢, Cerf Gardien 🔴, Renard Brumeux 🟢, Tatou 🟢 | boss Gardien de la Forêt 🔴 |
| Wolf (« Meute Corrompue ») | 25-32 | Loup Enragé, Molosse Corrompu 🔴, Loup de Cristal 🟢, Chien de Braise 🟢, Louve | Loup Meneur ; Loup-Garou 🟢 ; boss Crocmarque 🔴 |
| trou 32-35 + hameau 30-40 | 30-40 | à décider | |
| Brigand | 35-45 | Bandit, Archer Hors-la-loi, Arbalétrier, Mercenaire, Docteur Pestilent 🟢 (Voleur ?) | Chef de Gang 🟢 ; Chef de Guerre Bandit 🟡 |
| Rats corrompus | 40-50 | Rat Corrompu 🟡, Rat Assassin, Rat Cuirassé, Rat Sorcier 🟢, Rat Soigneur 🟢 | Rat Alpha 🟡 |
| Fanatique | 45-60 | 45-55 Convertis 🟢 ; 55-60 Zélotes 🟢 | Ancien Converti, Inquisiteur 🟢 |
| Gobelins | 50-60 | Gobelin, Guerrier, Artificier, Chaman 🟢, Porte-Bannière | Roi / Seigneur de Guerre Gobelin 🟡 (à recaler) |
| Rochebourg / approches de la Tour | 50-60 | Chevalier Brisé, Sentinelle Corrompue, Prêtre Obscur, Recouseur de Faille, Bourreau du Vide, Érudit Abyssal (sprites faits, non placés) | Paladin Corrompu ; Seigneur Cultiste |
| Tour d'Asher | 60+ | Acolyte, Guerrier Zélote, gardes d'Edric 🔴 ; Gardien de la Cloche, Golem Runique 🟢 | Edric, Grand Inquisiteur 🔴 |
| Marais corrompu | 60-70 | Homme-Lézard, Shaman Lézard, Gueule de la Faille, Cerf Cauchemar, Cheval Cauchemar, Hybride Sanglier-Loup | Corbeau Charognard |
| Low Demon | 61-70 | Larve de l'Abîme, Démon Mineur, Squelette Archer, Nécromancien, Moissonneur d'Âmes | Matrone d'Effroi ; boss Gueule de l'Abîme |
| Low Abyssal | 70-80 | Chargeur Abyssal, Traqueur d'Effroi, Invocateur du Néant, Prêtre du Vide, Sorcier Abyssal, Juggernaut | Colosse d'Os |
| Demon | 80-100 | Rejeton du Vide, Écumeur, Titan du Vide Mineur, Archonte Abyssal, Horreur d'Effroi | Dévoreur d'Âmes ; boss Souverain |
| Abyssal | 85-100 | cible : archontes déchus (humanoïdes ailés) 🔴 ; en attendant le lot actuel | Souverain |

## Sprites à faire en priorité (zones 1-60)

Famille **Ours** (3-4), Gardien de la Forêt, Loup Alpha, Crocmarque, Molosse Corrompu, Louve et Hyène
Matriarches, Cerf Gardien, Porte-Bannière, Rat Assassin, Rat Cuirassé, Sorcier Bandit, tribaux, Acolyte et
Guerrier Zélote, gardes d'Edric, Edric ×2.

## Simplifications permises par le lore

Cristal et braise en **stades** (« loup / cristal », « chien / braise ») ; Chacal de la Faille = « hyène /
corrupted » ; Rat Corrompu = « rat / corrupted » ; Hybride Sanglier-Loup au niveau 5 « Fusionné ».

## Questions ouvertes

1. Noms des 3 zones sans nom, et option A ou B pour 3-8.
2. Zone 25-30 ex-araignées en « Bois Obscur » (cervidés corrompus + Gardien de la Forêt) ?
3. Lancer la famille Ours sur PixelLab ?
4. Loup de Cristal, Chien de Braise, Loup-Garou : 25-32 (lore) ou après 60 (lot 4) ?
5. Brigand 35-45 (carte) contre humains 45-55 (décisions) ?
6. Trou 32-35 et hameau 30-40 : quels monstres ?
7. Marais corrompu : lézards + faune de Faille ? Squelettes en Low Demon ?
8. Démons / abyssaux / archontes sans sprite : humanoïdes par défaut ?
9. Tribaux : ogres (avec les gobelins) ou humains (avec les brigands) ?
10. Golems : Tour d'Asher ou Low Abyssal ?
11. Niveaux des donjons à recaler (Fort 9-13, deux Tour d'Asher 16-20 en doublon, Repaire 1-20, expéditions).
12. Tanière des loups (bureau) : pousser les 5 loups avant de figer Loup et Wolf.
13. Scorpion et Corbeau : garder (sprite fait) ou tout supprimer hors quadrupèdes / humanoïdes ?
