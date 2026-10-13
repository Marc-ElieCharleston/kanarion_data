# Personnages : genre, apparence et vraies animations

Statut : recherche (2026-10-03), rien de décidé. Aujourd'hui les personnages sont faits avec
**PixelLab** (un sprite fixe par classe). Le propriétaire veut de vraies animations, et laisser le
joueur choisir **le genre et l'apparence** de son personnage.

## Recommandation : un « paper doll » en calques

Des sprite sheets superposées (corps / cheveux / tenue / arme) qui partagent **exactement la même
grille d'animation**, plus un **shader de palette** pour les couleurs (peau, cheveux, teintures de
tenue). L'animation squelettique (Spine, Skeleton2D) est à écarter en pixel-art (les rotations
cassent les pixels).

| Approche | Coût | Verdict |
|---|---|---|
| Pack paper-doll commercial (Mana Seed ~20 $, Time Elements 20 $) | faible | **base provisoire recommandée** |
| Générateur LPC | gratuit | possible, mais licences mélangées : **filtrer CC0 / CC-BY / OGA-BY** (CC-BY-SA et GPL posent problème : App Store, share-alike des cosmétiques) |
| Squelette 2D (Spine 69-369 $, Godot gratuit) | moyen | mauvais en pixel-art |
| IA (PixelLab, Retro Diffusion…) | 9-50 $/mois | bon pour **monstres et PNJ** (un sprite complet), **pas de calques alignés** pour un paper doll |
| Base commandée à un artiste | 300-1 200 $ par genre, puis 20-150 $ par tenue | le meilleur, quand la boutique rapporte |

## Minimum sensible (MMO mobile sur grille)

- **4 directions** (bas, haut, côté ; gauche = miroir) : 3 à dessiner.
- **6 animations** : idle (2-4 frames), walk (4-6), attaque (4-5), cast/tir (4-5), hurt (1-2),
  death (3-5, une direction). Environ 60 à 90 frames par base.

## Plan par phases

1. **Maintenant (~0-40 $)** : construire le système dans Godot : calques synchronisés sur le corps
   (signal `frame_changed`), équipement piloté par données, shader de palette, **pré-composition**
   d'un sprite par joueur quand l'équipement change (1 sprite, 1 draw call sur mobile), écran de
   création (genre, peau, cheveux, couleur de tenue). Base provisoire : Mana Seed ou LPC filtré.
   Taille cible : cellules 64×64, personnage de 32-48 px.
2. **Toujours ~0 $** : garder PixelLab pour les monstres et PNJ.
3. **Premiers revenus (~600-1 500 $)** : commander une base propre au jeu (2 genres × 6 animations
   × 4 directions), 4-6 coiffures, 3 tenues, palette prévue pour le swap. **Contrat avec cession des
   droits** et fichiers sources.
4. **Boutique** : tenues et armes commandées au fil de l'eau ; les **teintures** (palette swap)
   multiplient les variantes vendables.

## Pièges de licence

- **Mana Seed** : une licence = un seul jeu ; **chaque item Mana Seed vendu en boutique = un rachat
  du pack** ; **interdit dans l'IA** (ne pas le donner à PixelLab). Vendre en boutique seulement des
  items dessinés par ton artiste.
- **LPC** : éviter CC-BY-SA / GPL ; garder le fichier de crédits et un écran de crédits.
- **IA** : licence commerciale incluse dans les plans payants, mais l'art purement généré est
  difficilement protégeable (à vérifier) et une partie des joueurs le rejette.
- **Artiste** : cession des droits commerciaux, droit de modifier, fichiers sources (.aseprite).

Sources principales : seliel-the-shaper.itch.io/character-base (et sa licence),
github.com/LiberatedPixelCup/Universal-LPC-Spritesheet-Character-Generator, lpc.opengameart.org/content/faq,
pixellab.ai/docs, esotericsoftware.com/spine-godot, godotshaders.com (palette swap).
Prix PixelLab et artistes : indicatifs (articles 2025-2026).
