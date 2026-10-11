# Carte des monstres : répartition par zone (version 2.1, 2026-10-10)

> **Méthode (propriétaire, 2026-10-11) : on travaille ZONE PAR ZONE.** Les noms des zones restent ceux de
> `world/zones.json` (les renommages de ce document, Roselières, Pâtures, etc., sont des propositions
> RETIRÉES ; les lire comme « Marécage », « Prairie »…).
>
> **Zones VALIDÉES (monstres = la data actuelle) :**
> - **Marécage** `mz_marecage_20_30` « Marais de Havreden » : Grenouille, Grenouille Cornue, Grenouille
>   Soigneuse, Crapaud Cracheur, Loutre. Élite possible (pas obligatoire) : **Tortue de Pierre**.
>   Le Ragondin et le Crocodile proposés plus bas ne sont PAS retenus.
> - **Prairie** `mz_prairie_10_20` « Pâtures d'Havreden » : Chèvre, Cochon, Brebis, Bouc, Vache.
>   (Chien Sauvage et Épouvantail proposés plus bas : non retenus.)
>
> **Décision Bois des Loups** `mz_loup_13_23` (propriétaire, 2026-10-11) : la zone n'a **que des loups
> normaux** (ex. loup blanc, loup noir). Les **loups humanoïdes** (Loup Meneur, Louve soigneuse, Loup
> Corrompu, Loup Alpha) vont dans le **donjon** de la zone (la Tanière). À retirer donc de la zone dans la
> data : `mob_wolf_soigneur`, `mob_wolf_packleader` (travail du bureau, ne pas toucher ici).
> Roster VALIDÉ (2026-10-11), 5 loups : Loup Gris (`mob_wolf`, brute 🟢), Loup Enragé (`mob_frothing_wolf`,
> berserker 🟢), **Loup Noir** (`mob_loup_noir`, assassin), **Loup Blanc** (`mob_loup_blanc`, soutien, hurlement
> qui renforce la meute), **Vieux Loup** (`mob_vieux_loup`, tank). Les 3 nouveaux sont générés dans PixelLab
> (walk + idle) le 2026-10-11 ; data (stats, compétence unique) et intégration au bureau.
>
> **Zones validées au 2026-10-11 : Havreden, Prairie, Marais, Forêt, Bois des Loups.**
> **Sanglier** `mz_sanglier_8_15` (2026-10-11, en cours) : Marcassin (fodder), Sanglier (brute 🟢), Sanglier
> Enragé (berserker 🟢), **Laie** (soutien, protège les marcassins), **Vieux Sanglier** (tank ; nom choisi par le
> propriétaire). Les 3 nouveaux sont générés par le propriétaire (2026-10-11). **Bélier → Taureaux** (validé).
> Note : la **taille des monstres** pourra se régler en jeu par un ratio d'échelle (propriétaire) : un même
> sprite peut servir à une larve ou à un géant.
> **Insectes** `mz_scarabees_3_8` (2026-10-11) : renommée **« Lisière d'Havreden »** (le scorpion n'est pas un
> scarabée ; noms de zone = lieux dans la lignée du jeu, pas de nom de monstre sauf exceptions type Bois des
> Loups). Roster VALIDÉ, 3 monstres : Scarabée (brute 🟢), Scorpion Rocheux (tank 🟢), Scarabée Géant (élite 🟢).
> La Larve peut rester en petit scarabée (ratio d'échelle).
> **Rats** `mz_rats_1_8` (2026-10-11) : renommée **« Abords d'Havreden »**. Constat : Rat, Jeune Rat, Rat Alpha et
> Rat Contaminé affichent TOUS le même sprite (`rat`). Roster : Jeune Rat (sprite du Rat en petit, ratio
> d'échelle), Rat (🟢), **Rat Alpha** (élite, nouveau sprite généré par le propriétaire), et le rat du tutoriel.
> **Le rat du tutoriel reste un rat NORMAL** (pas contaminé à l'écran) : il devient le familier du joueur, un
> familier « contaminé » n'est pas souhaitable ; le propriétaire gérera la contamination dans le lore.
>
> **Sprites PixelLab vérifiés le 2026-10-11** (agent, walk + idle ajoutés si manquants) :
> - Loups : Loup Noir `56136a94` → garder walk-8-v2 (N/S/diagonales) + « walk-v3-ew » (E/O) ; Loup Blanc
>   `c10c868b` → walk-8-v2 ; Vieux Loup `42ce2ff0` → walk-8-v2, à jouer à ~6-7 fps pour une démarche lourde.
>   Anciennes walk-4 gardées (à supprimer si OK). Canevas 80 px : afficher à ~0,82 pour égaler les loups 124 px.
> - Sangliers : Marcassin `bd9aef6a`, Laie `7e839ea3`, Vieux Sanglier `74d4a2fc` : complets, OK.
> - Rats : Rat Alpha `0808264a`, rat du tutoriel `05b1b919` (encore nommé « Rat Contaminé » dans PixelLab) :
>   walk-8 + idle OK ; canevas 80 px contre 120 px pour le rat de base (régler l'échelle).
> - Insectes : OK, mais le Scarabée Géant `673fff5b` est à peine plus grand que le Scarabée → échelle ~1,4.
> - À nettoyer : ligne noire 1 px (x=32) dans la vue sud-ouest du Scarabée Géant et du Sanglier `ae1c4002`.
> - Doublons à supprimer : Loup Noir `43264e67` ; créés par erreur `bdd5ade1`, `97edf87e`, `a5012082`.
>
> **Zones du milieu (2026-10-11)** :
> - `mz_hyene_9_20` → **« Le Bocage »** (validé) : Chat Sauvage, Chat Sauvage Roux, Hérisson, Belette (générés par
>   le propriétaire), Ragondin (déjà dans PixelLab). Pas de chiens errants (doublon avec les loups).
> - `mz_sangliers-loups_6_15` **« Clairière Disputée »** (nom gardé) : zone mixte à tester, les loups du bois voisin
>   chassent les sangliers (Loup Gris, Loup Noir, Sanglier, Laie, Marcassin ; aucune création).
> - `mz_wolf_25-32` **« Meute Corrompue »** (nom gardé) : loups **corrompus**.
> - `mz_spider_25_30` (à gauche, le long du bord) : cerfs et biches corrompus + Gardien de la Forêt ; nom à choisir
>   (« Bois Flétri » ou « Sous-Bois Noirci »).
> - Hyènes → Plaine des Taureaux (proposé ; la zone est petite, 914 × 820 px, l'agrandir ou peu d'hyènes).
> - **Idée du propriétaire : après 30, on reprend les mêmes espèces en version CORROMPUE** (variantes PixelLab du même
>   personnage) jusqu'aux brigands 35-45.
> - Taille de carte jugée bonne (~8 500 × 16 700 px, ~1 min 30 du nord au sud à 180 px/s) : on garde 21 zones.

Statut : **proposition à valider**. Tient compte de la carte **non linéaire** (zones plus hautes près
d'Havreden, voulu), des **noms validés**, de **pas d'ours**, de **5 monstres par zone** (élites et boss à
part) et de l'inventaire des **367 personnages PixelLab** du propriétaire. À recouper avec le travail du
bureau (Tanière des loups).

Règles : PixelLab ne fait que **quadrupèdes et humanoïdes** ; animaux 1-40, humains touchés 45-55, fanatiques
~55-60, Tour 60+, créatures après 60 ; le monde corrompt les espèces existantes.

Légende : 🟢 sprite dans le client ; 🟡 repli sur un stade de la même espèce ; 🟦 seulement dans PixelLab ;
🔴 à faire (prompt plus bas). Réapparition : R rapide (farm), N normale, L lente (élites, boss, gros monstres).

## Les 4 loups de PixelLab = 4 monstres qui existent déjà sans sprite

Chef de meute à lance → `mob_wolf_packleader` (Loup Meneur, enchanteur) ; louve chamane → `mob_wolf_soigneur`
(Louve Matriarche, soigneuse) ; brute corrompue au bouclier de pierre → `mob_wolf_corrupted` (Molosse
Corrompu) ; seigneur alpha à l'espadon → `boss_alpha_wolf` (Loup Alpha). **Il suffit de les exporter.**

## Répartition par zone

| Zone | Niv. | Monstres (archétype, sprite, réapp.) | Élite / boss (réapp. L) |
|---|---|---|---|
| **Havreden** | 1-8 | Jeune Rat 🟡 R · Rat 🟢 R · Rat Contaminé 🟢 R · Lièvre (assassin) 🟢 R · Larve de Scarabée 🟡 R | Rat Alpha 🟡 |
| **Les Friches** | 3-8 | Scarabée 🟢 R · Larve 🟡 R · Lièvre 🟢 R · Renard (assassin) 🟢 R · Marcassin 🟡 R | Scarabée Géant (sprite `giant_hornet`) 🟢 |
| **La Chênaie** | 8-15 | Marcassin 🟡 R · Sanglier (brute) 🟢 R · Sanglier Enragé (berserker) 🟢 R · Blaireau 🟢 R · Biche (soigneuse) 🟢 R | Vieux Solitaire (stade du sanglier) 🟡 |
| **Les Pâtures** (ferme Dorn) | 10-20 | Chèvre 🟢 R · Cochon 🟢 R · Brebis (enchanteur) 🟢 R · Bouc (tank) 🟢 R · Chien Sauvage (assassin, meute) 🟦 R | Vache (gardien) 🟢 ; événement de nuit : Épouvantail Possédé 🟦 (à décider) |
| **La Clairière** | 6-15 | Sanglier 🟢 N · Sanglier Enragé 🟢 N · Loup (assassin) 🟢 N · Loup Enragé (berserker) 🟢 N · Biche 🟢 N | Cerf (gardien) 🟢 |
| **La Lande** | 9-20 | Hyène (assassin) 🟢 R · Charognard des Chemins 🟦 R · Hyène Matriarche (soigneuse) 🔴 N · Bélier (tank) 🟢 R · Renard 🟢 R | Hyène Alpha 🟢 |
| **Le Val aux Loups** | 13-23 | Louveteau 🟡 R · Loup 🟢 R · Loup Enragé 🟢 R · Loup Meneur 🟦 N · Louve Matriarche 🟦 N | boss de la Tanière : Loup Alpha 🟦 ; 5e loup du bureau ? |
| **Le Grand-Bois** | 12-26 | Lièvre 🟢 R · Renard 🟢 R · Biche 🟢 R · Blaireau 🟢 R · Cerf (gardien) 🟢 N | Renard Brumeux (élite rare) 🟢 |
| **Les Herbages** | 16-25 | Cheval Sauvage 🟢 N · Tatou Cuirassé (tank) 🟢 N · Bélier 🟢 N · Chèvre 🟢 R · Hyène 🟢 R | Taureau 🟢 |
| **Les Roselières** | 20-30 | Grenouille Cornue (tank) 🟢 R · Grenouille Soigneuse 🟢 R · Crapaud Cracheur (distance) 🟢 R · Loutre Géante (assassin) 🟢 R · Ragondin (brute) 🟦 R | Tortue de Pierre 🟢 ; rare : Crocodile des Marais 🟦 (anims à finir) |
| **Le Bois Sombre** | 25-30 | Cerf Obscur (assassin) 🟢 N · Cerf Gardien (soigneur) 🔴 N · Renard Brumeux 🟢 N · Blaireau 🟢 N · Sanglier Enragé 🟢 N | boss Gardien de la Forêt (grand cerf ancien) 🔴 |
| **Les Éboulis** (zone élite, camp des sœurs) | 20-28 | Sanglier Enragé 🟢 N · Sanglier Cuirassé (tank) 🟦 N · Chien Sauvage 🟦 N · Bélier ou Scorpion Rocheux 🟢 N · Biche 🟢 N | antre (instance) : **Grande Laie** 🔴 et ses Marcassins 🟡 |
| **Les Crêtes** | 25-32 | Loup Enragé 🟢 N · Molosse Corrompu (tank) 🟦 N · Louve Matriarche 🟦 N · Chèvre 🟢 N · Loup-Garou (berserker) 🟢 N | Loup Meneur 🟦 ; boss Crocmarque 🔴 |
| **La Route du Sud** (+ hameau 30-40) | 35-45 | Bandit (assassin) 🟢 N · Archer Hors-la-loi 🟢 N · Arbalétrier 🟢 N · Mercenaire (tank) 🟢 N · Docteur Pestilent (contrôle) 🟢 N | Chef de Gang 🟢 ; boss Chef de Guerre Bandit 🔴 (cheval de guerre 🟦 en option) |
| **Rochebourg** | ~50 | ville, pas de monstres (événements de Faille) | — |
| **Les Bas-Fonds de Rochebourg** | 40-50 | Rat Sorcier 🟢 N · Rat Soigneur 🟢 N · Rat Assassin 🔴 N · Rat Cuirassé (tank) 🔴 N · Voleur 🟢 N | boss Le Rongeur 🟢 |
| **Le Chemin des Pèlerins** | 45-60 | Fermier, Forgeron (tank), Chasseur (assassin), Archer, Herboriste (soigneuse) Convertis 🟢 N | Ancien Converti 🟢 ; Fanatisé en renfort |
| **Les Mines Basses** | 50-60 | Gobelin 🟢 · Gobelin Guerrier 🟢 · Artificier (distance) 🟢 · Chaman (soigneur) 🟢 · Brute Tribale (tank) 🟢 (N) | Seigneur de Guerre Tribal 🟢 ; boss Roi Gobelin 🔴 |
| **Tour d'Asher** | 60+ | Garde Zélote · Ritualiste Zélote · Prédicateur Exalté · Fanatique de la Tour · Golem Runique 🟢 (instance) | Gardien de la Cloche, Inquisiteur Fanatique 🟢 ; boss Edric 🟢 (`pnj/boss_edric`) |
| **Le Marais de la Faille** | 60-70 | Homme-Lézard · Shaman Lézard · Traqueur de Faille · Cerf Cauchemar · Gardien de Faille 🟢 (N) | Gueule de la Faille, Hybride Sanglier-Loup 🟢 ; rare : Corbeau Charognard 🟢 |
| **Les Brèches** | 61-70 | Larve de l'Abîme 🟢 R · Démon Mineur · Squelette Archer · Moissonneur d'Âmes · Titan du Vide Mineur 🟢 N | Matrone d'Effroi 🟢 ; boss Gueule de l'Abîme 🟢 ; crypte : Liche 🟦 |
| **Le Seuil** | 70-80 | Rejeton du Vide · Écumeur Abyssal · Colosse d'Os · Invocateur du Néant · Prêtre du Vide 🟢 | Traqueur d'Effroi 🟢 |
| **Les Terres Déchirées** | 80-100 | Bourreau du Vide · Chargeur Abyssal · Chien du Vide · Juggernaut Abyssal · Érudit Abyssal 🟢 | Dévoreur d'Âmes 🟢 |
| **L'Abîme** | 85-100 | Séraphin Abyssal · Chevalier Brisé · Paladin Corrompu · Sentinelle Corrompue · Recouseur de Faille 🟢 | Archonte Abyssal 🟢 ; boss Souverain de l'Abîme 🟢 |

**Réserve** (donjons, Failles, tour infinie) : Nécromancien, Guerrier Maudit, Revenant du Vide, Horreur
d'Effroi, Sorcier Abyssal, Prêtre Obscur, Seigneur Cultiste, Loup de Cristal, Chien de Braise, Loup Spectral,
Cheval Cauchemar, Golem.

## Remplacer l'ours : la Grande Laie (à valider)

Une grande laie peut tuer un chasseur : le père des sœurs est « tué par un sanglier ». Sarn a tué ses
marcassins dans ses pièges ; la rage de la mère nourrit la Fissure. **Le marcassin remplace l'ourson** comme
familier. Le Sanglier Cuirassé (déjà dans PixelLab) devient la bête « carapace » (corruption niveau 4).
À réécrire : `histoires/chasseuse_soigneuse.md`, `fruits_de_l_esprit.md`.

## Sprites

**À exporter depuis PixelLab** : les 4 loups ; Ragondin, Sanglier Cuirassé, Liche, Guerrier Maudit (variante).
Anims à finir : Crocodile (2), Épouvantail (3). Anims à faire : Chien Sauvage, Hyène enragée 64 px.
Ragondin, Sanglier Cuirassé, Liche, Crocodile et Épouvantail **n'ont pas de fiche** dans `monsters.json`.

**Prompts PixelLab** (8 directions, 80×80, style du propriétaire ; c'est lui qui génère) :

```
mob_grande_laie — La Grande Laie (boss brute, lv 28, template lion)
Top-down 2D fantasy giant corrupted wild sow matriarch, huge heavy boar body on four thick short legs, coarse dark brown bristled hide streaked with grey, long curved yellowed tusks, faint violet Fissure cracks along the spine and flanks, small furious red eyes, torn ear, protective lowered-head charging stance, pixel art RPG style
```
```
mob_marcassin — Marcassin (fodder brute / familier, lv 8, template cat)
Top-down 2D fantasy wild boar piglet, small round quadruped body on four short legs, soft light brown fur with pale cream stripes along the back, short blunt snout, tiny ears, curious alert stance, pixel art RPG style
```
```
mob_hyene_soigneur — Hyène Matriarche (healer, lv 16, template dog)
Top-down 2D fantasy old hyena matriarch, lean sloping quadruped body on four long legs, faded sandy fur with dark spots turned grey, scarred muzzle, thick mane, pale wise eyes, calm watchful standing stance, pixel art RPG style
```
```
mob_cerf_obscur_soigneur — Cerf Gardien (healer, lv 27, template horse)
Top-down 2D fantasy dark forest guardian stag, slender quadruped body on four fine legs, deep grey-brown coat with pale moss patches, wide branching antlers wrapped in ivy and small pale glowing mushrooms, calm silver eyes, protective standing stance, pixel art RPG style
```
```
boss_forest_guardian — Gardien de la Forêt (boss guardian, lv 30, template horse)
Top-down 2D fantasy ancient corrupted great stag, massive tall quadruped body on four sturdy legs, bark-like grey-brown hide covered in moss and roots, enormous antlers like dead branches with faint violet Fissure crystals growing between them, glowing violet eyes, braced towering stance, pixel art RPG style
```
```
boss_fangmark_den — Crocmarque (boss brute, lv 32, template dog)
Top-down 2D fantasy huge scarred mountain wolf, heavy muscular quadruped body on four powerful legs, shaggy charcoal fur with old claw scars, one torn ear, a deep bite-mark scar across the muzzle, bared yellow fangs, glowing amber eyes, low menacing prowling stance, pixel art RPG style
```
```
mob_rat_assassin — Rat Assassin (assassin, lv 44, humanoid)
Top-down 2D fantasy lean humanoid rat assassin, standing on two hind legs, wiry frame covered in dark sooty fur, long bare tail, narrow snout with sharp incisors, glowing violet eyes, ragged black hood and cloth wraps, two rusty curved daggers held reversed, crouched ready-to-lunge stance, pixel art RPG style
```
```
mob_rat_cuirasse — Rat Cuirassé (tank, lv 45, humanoid)
Top-down 2D fantasy bulky humanoid rat brute, standing on two hind legs, broad frame covered in matted grey-brown fur, long bare tail, scavenged armor of rusted sewer grates and pot lids strapped with leather, dented round iron lid used as a shield, short club, braced immovable stance, pixel art RPG style
```
```
boss_goblin_king — Roi Gobelin (boss brute, lv 60, humanoid)
Top-down 2D fantasy goblin king, short stocky green-skinned humanoid, long pointed ears, wide toothy grin, crooked iron crown, oversized mismatched plate armor taken from miners, fur mantle, huge spiked mining hammer over one shoulder, arrogant dominant stance, pixel art RPG style
```
```
boss_bandit_warlord — Chef de Guerre Bandit (boss enchanter, lv 45, humanoid)
Top-down 2D fantasy bandit warlord, tall scarred human in dark leather and stolen chain armor, red sash and torn road-dust cloak, short black beard, heavy curved saber in one hand, the other raised giving orders, commanding stance, pixel art RPG style
```

**Fusionnés (pas de nouveau sprite)** : Garde d'Élite d'Edric → Sentinelle Corrompue ; Ritualiste d'Edric →
Ritualiste Zélote ; Acolyte Zélote → Fanatique de la Tour ; Guerrier Zélote → Garde Zélote ; Grand Inquisiteur
→ Inquisiteur Fanatique ; Porte-Bannière Gobelin → Gobelin Chaman ; Gardien de Pierre, Golem Corrompu →
Golem ; Pillard d'Os → Guerrier Maudit ; Chacal de la Faille → stade corrompu de la hyène.

## À supprimer

- **PixelLab** : ours des cavernes et 2 oursons, petite araignée, scarabée du désert, 2 corbeaux sombres,
  2 anciens loups, liche v2, chevalier corrompu élite (doublon), bête laineuse « façon bouftou » (copie de
  Dofus, **risque juridique**).
- **Data** : les 3 araignées (+ `boss_mechanics`, zone `mz_spider_25_30`, `mat_spider_*`), `mob_dust_beetle`,
  `mob_serpent`, `mob_sangsue` (→ Ragondin), la famille Ours de l'ancienne proposition.

## Questions ouvertes

1. Grande Laie à la place de la Grande Ourse (père tué par un sanglier, familier marcassin) ?
2. 5e loup de la Tanière ? Le Molosse Corrompu peut-il rester aux Crêtes (25-32) alors que `DECISIONS.md` le
   place après 60 ?
3. Les Bas-Fonds sont-ils les Égouts du Rongeur ? Si oui, son niveau passe de 15 à 40-50.
4. On garde le Scorpion Rocheux (8 pattes, sprite fait) et l'Épouvantail Possédé (événement de nuit) ?
5. Gardien de la Forêt : nouveau sprite, ou recyclage du Cerf Cauchemar ?
6. Chevalier déchu « boss épique » et Cheval de guerre (sans anims) : on s'en sert ou on supprime ?
