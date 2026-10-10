# Carte des monstres : répartition par zone (version 2.1, 2026-10-10)

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
