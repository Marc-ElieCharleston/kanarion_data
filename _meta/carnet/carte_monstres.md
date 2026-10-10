# Carte des monstres : répartition par zone (version 2, 2026-10-10)

Statut : **proposition à valider**. Tient compte de la carte **non linéaire** (zones plus hautes près
d'Havreden, voulu), des **noms validés**, de **pas d'ours**, de **~5 monstres par zone** et de l'inventaire
des **367 personnages PixelLab** du propriétaire. À recouper avec le travail du bureau (Tanière des loups).

Règles : PixelLab ne fait que **quadrupèdes et humanoïdes** ; animaux 1-40, humains touchés 45-55, fanatiques
~55-60, Tour 60+, créatures après 60 ; le monde corrompt les espèces existantes.

Légende : 🟢 sprite dans le client ; 🟦 seulement dans PixelLab (à exporter ou à animer) ; 🟡 repli sur la
famille (un stade) ; 🔴 sprite à faire. Réapparition : R rapide, N normale, L lente.

## La bonne nouvelle : les 4 loups de PixelLab

Les 4 loups humanoïdes de PixelLab correspondent exactement à **4 monstres qui existent déjà** dans la data
sans sprite propre : chef de meute → `mob_wolf_packleader` (Loup Meneur, enchanteur) ; louve chamane →
`mob_wolf_soigneur` (Louve Matriarche, soigneuse) ; loup corrompu au bouclier de pierre → `mob_wolf_corrupted`
(Molosse Corrompu, à renommer « Loup Corrompu » ?) ; seigneur de guerre alpha → `boss_alpha_wolf` (Loup Alpha,
boss). **Il suffit de les exporter vers le client.**

## Répartition par zone

| Zone | Niv. | Monstres (archétype, sprite, réapparition) | Élite / boss |
|---|---|---|---|
| **Havreden** | 1-8 | Jeune Rat (🟡 R), Rat (🟢 R), Rat Contaminé (tutoriel 🟢 R), Lièvre (assassin 🟢 R) | Rat Alpha (🟡 L) |
| **Les Friches** | 3-8 | Larve de Scarabée (🟡 R), Scarabée (brute 🟢 R), Chien Sauvage (brute 🟦 N), Scorpion Rocheux (tank 🟢 N) | Scarabée Géant (sprite `giant_hornet` 🟢 L) |
| **La Chênaie** | 8-15 | Marcassin (nouvel id 🟡 R), Sanglier (brute 🟢 R), Sanglier Enragé (berserker 🟢 N), Biche (soigneuse 🟢 N) | Vieux Sanglier (stade alpha 🟡 L) |
| **Les Pâtures** (ferme Dorn) | 10-20 | Chèvre (🟢 R), Cochon (🟢 R), Brebis (enchanteur 🟢 R), Bouc (tank 🟢 N) | Vache (gardien 🟢 L) ; option : Épouvantail Possédé (🟦, événement de Faille) |
| **La Clairière** | 6-15 | Lièvre (🟢 R), Sanglier (🟢 R), Sanglier Enragé (🟢 N), Loup (🟢 R), Loup Enragé (🟢 N) | Louve Matriarche (🟦 L) |
| **La Lande** | 9-20 | Hyène (🟢 R), Charognard des Chemins (🟦 R), Chien Sauvage (🟦 R), Hyène Matriarche (soigneuse 🔴 N) | Hyène Alpha (🟢 L) |
| **Le Val aux Loups** | 13-23 | Loup (🟢 R), Loup Enragé (🟢 R), Louve Matriarche (🟦 N), Loup Meneur (🟦 N) | Tanière (instance) : Loup Corrompu (🟦) ; boss Loup Alpha (🟦 L) ; 5e loup du bureau ? |
| **Le Grand-Bois** | 12-26 | Lièvre, Renard (🟢 R), Blaireau (🟢 R), Biche (🟢 N), Cerf (gardien 🟢 N) | Renard Brumeux (élite rare 🟢 L) |
| **Les Herbages** | 16-25 | Cheval Sauvage (🟢 R), Bélier (🟢 R), Tatou Cuirassé (🟢 N), Brebis (🟢 R) | Taureau (🟢 L) |
| **Les Roselières** | 20-30 | Grenouille (🟢 R), Ragondin (🟦 R), Grenouille Cornue (🟢 N), Grenouille Soigneuse (🟢 N), Crapaud Cracheur (🟢 N), Loutre Géante (🟢 N) | Tortue de Pierre (🟢 L) ; Crocodile des Roseaux (élite rare 🟦, 2 animations, L) |
| **Le Bois Sombre** | 25-30 | Cerf Obscur (🟢 N), Cerf Gardien (soigneur 🔴 N), Renard Brumeux (🟢 N), Tatou (🟢 N), Blaireau (🟢 R) | boss Gardien de la Forêt (🔴, ou reprendre le sprite Cerf Cauchemar 🟢) |
| **Les Éboulis** (zone élite, camp des sœurs) | 20-28 | Sanglier Cuirassé (tank 🟦 N), Sanglier Enragé (🟢 N), Laie (soigneuse 🟡 N), Marcassins en escorte (🟡 R), Scorpion Rocheux (🟢 N), Bouc (🟢 N) | antre (instance) : **Grande Laie** (🔴 L), remplace la Grande Ourse |
| **Les Crêtes** | 25-32 | Loup Enragé (🟢 R), Loup Corrompu (🟦 N), Louve Matriarche (🟦 N), Loup Meneur (🟦 N), Bouc et Bélier (🟢 R) | Loup-Garou (🟢 L, si gardé avant 60) ; Crocmarque (🔴, ou fusion avec le Loup Alpha) |
| **La Route du Sud** (+ hameau 30-40) | 35-45 | Bandit (🟢 R), Voleur (🟢 R), Archer Hors-la-loi (🟢 R), Arbalétrier (🟢 N), Mercenaire (tank 🟢 N), Docteur Pestilent (contrôleur 🟢 N), Sorcier Bandit (soigneur 🔴 N) | Chef de Gang (🟢 L) ; Chef de Guerre Bandit (🟡 L) sur un Destrier caparaçonné (🟦 L) |
| **Rochebourg** | ~50 | ville, pas de monstres | — |
| **Les Bas-Fonds de Rochebourg** | 40-50 | Rat Corrompu (🟡 R), Rat Assassin (🔴 N), Rat Cuirassé (🔴 N), Rat Sorcier (🟢 N), Rat Soigneur (🟢 N), Prêtre Obscur (🟢 N) | Rat Alpha (🟡 L) ; Le Rongeur (🟢 L) ; Seigneur Cultiste (🟢 L) |
| **Le Chemin des Pèlerins** | 45-60 | 45-55 Convertis 🟢 (Fermier, Forgeron, Herboriste, Chasseur, Archer, Fanatisé) + Chevalier Brisé (🟢) ; 55-60 Zélotes 🟢 (Prédicateur, Garde, Ritualiste, Fanatique de la Tour) | Ancien Converti, Inquisiteur Fanatique, Paladin Corrompu (🟢 L) |
| **Les Mines Basses** | 50-60 | Gobelin, Gobelin Guerrier (🟢 R), Artificier, Chaman (🟢 N), Porte-Bannière (🔴 N), Brute Tribale (🟢 N), Chasseur Tribal (🟦 guerrier masqué) | Seigneur de Guerre Gobelin, Roi Gobelin (🟡 L), Seigneur de Guerre Tribal (🟢 L) |
| **Tour d'Asher** | 60+ | Acolyte, Guerrier Zélote, Garde d'Élite et Ritualiste d'Edric (🔴) ; Golem, Golem Runique, Gardien de la Cloche (🟢) | Edric (🟢, dans `pnj/`), Grand Inquisiteur (🔴), Ezra Perdu (🟢) |
| **Le Marais de la Faille** | 60-70 | Homme-Lézard, Shaman Lézard, Gueule de la Faille, Traqueur de Faille, Recouseur de Faille, Gardien de Faille, Cheval Cauchemar, Hybride Sanglier-Loup, Loup de Cristal (🟢) | Corbeau Charognard (🟢 L) |
| **Les Brèches** | 61-70 | Larve de l'Abîme, Démon Mineur, Squelette Archer, Guerrier Maudit, Nécromancien, Revenant du Vide, Horreur d'Effroi, Moissonneur d'Âmes, Titan du Vide Mineur, Chien de Braise, Loup Spectral (🟢) | Matrone d'Effroi (🟢) ; Champion Maudit (🟦) ; Liche (🟦) ; boss Gueule de l'Abîme (🟢) |
| **Le Seuil** | 70-80 | série Vide / Abîme / Effroi déjà dessinée (🟢) | Dévoreur d'Âmes, Archonte Abyssal (🟢) |
| **Les Terres Déchirées** | 80-100 | Sentinelle Creuse, Sentinelle en Deuil, Archonte Courroucé (🔴) ; en attendant le lot du Seuil | Souverain de l'Abîme (🟢) |
| **L'Abîme** | 85-100 | archontes déchus humanoïdes (🔴, lot mis de côté), Sentinelle du Trône (🔴) | Souverain de l'Abîme, puis les boss mis de côté |

Note : au-delà de 60, les zones ont plus de 5 monstres possibles ; à réduire à ~5 au moment de figer.

## Remplacer l'ours : la Grande Laie (recommandée)

PixelLab fait bien les sangliers ; le « Sanglier Cuirassé » existe déjà (stade corrompu « carapace », le
niveau 4 de corruption prévu pour l'ours) ; le **marcassin** devient le familier ; une laie qui charge pour
défendre ses petits est crédible, et les pièges de Sarn collent à la chasse au sanglier. Il faudra réécrire
« père tué par un ours » → « par un sanglier », Grande Ourse → Grande Laie, ourson → marcassin
(`histoires/chasseuse_soigneuse.md`, `fruits_de_l_esprit.md`). Autres choix : Grande Biche (faon, plus doux,
mais explique mal la mort du père), Grande Louve (doublon avec le Val aux Loups).

## Sprites

**À exporter de PixelLab vers le client** (aucun crédit) : les 4 loups, le Ragondin, le Sanglier Cuirassé, le
Guerrier Skull Maudit (Champion Maudit), la Liche.

**Animations à compléter dans PixelLab** (le personnage existe) : Chien Sauvage, Charognard des Chemins
(hyène 64 px, à mettre à l'échelle), Crocodile (2 animations), Épouvantail (3), Destrier caparaçonné,
Guerrier masqué.

**À créer** : Grande Laie ; Hyène Matriarche (humanoïde chamane, comme la louve et le rat) ; Cerf Gardien ;
Gardien de la Forêt (ou reprise du Cerf Cauchemar) ; Rat Assassin et Rat Cuirassé (série des rats
humanoïdes) ; Sorcier Bandit ; Gobelin Porte-Bannière ; Tour d'Asher (Acolyte, Guerrier Zélote, Garde d'Élite
et Ritualiste d'Edric, Grand Inquisiteur) ; 5e loup de la Tanière si besoin ; Crocmarque (sauf fusion) ;
après 80 les sentinelles et archontes. → **Prompts PixelLab à écrire dans le style du propriétaire**, c'est
lui qui génère.

## À supprimer / fusionner

- Supprimer : les 3 araignées (+ mécaniques de boss, zone `mz_spider_25_30`, matériaux `mat_spider_*`),
  Scarabée de Poussière, Serpent.
- Dans PixelLab, à ignorer ou supprimer : ours des cavernes et 2 oursons, petite araignée, scarabée du désert,
  bête « façon bouftou » (copie de Dofus, **risque juridique**), 2 corbeaux sombres, 2 anciens loups, rat
  sorcier 64 px, liche v2.
- Fusionner : Braconnier → Archer Hors-la-loi ; Déserteur → Mercenaire ; les 7 bandits du Fort (sosies) →
  Bandit, Voleur, Archer, Mercenaire ; Crocmarque → Loup Alpha (option).

## Questions ouvertes

1. Matriarche des Éboulis : Grande Laie (recommandée), Grande Biche ou Grande Louve ?
2. Tanière des loups : quel est le 5e loup du bureau ? Crocmarque fusionne-t-il avec le Loup Alpha ?
3. Exceptions avant 60 : garder le Loup-Garou (Crêtes), l'Épouvantail Possédé (événement aux Pâtures), le
   Scorpion Rocheux (arachnide) ?
4. Liche et Champion Maudit : élites de monde des Brèches, ou boss d'un donjon squelette ?
5. Tribaux : avec les gobelins aux Mines Basses, ou supprimés ?
6. Brigands à 35-45 (carte) alors que la règle place les humains à 45-55 : garder la carte (recommandé) ?
