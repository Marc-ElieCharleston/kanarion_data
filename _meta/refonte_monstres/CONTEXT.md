# Contexte commun — refonte des kits de monstres (Kanarion Online, 2026-10-02)

Jeu : MMORPG 2D mobile, combat en TEMPS RÉEL sur grille, GCD 2 s, 10 entités max par équipe.
Le but du joueur est de descendre au SUD (cause des Fissures) : plus on descend (plus le niveau
monte), plus c'est dangereux, en stats ET en mécaniques. Niveaux 1-40 = proches du village, simples.

Dépôts (LECTURE SEULE, ne modifie AUCUN fichier des dépôts) :
- Data : C:\Users\Charl\Documents\Projets\kanarion\kanarion_database (branche master)
  - entities/monsters.json (200 monstres, 166 `roster_status: active`)
  - skills/monster_skills.json (basic_skills = attaques d'espèce ; role_basic_skills = attaque de rôle
    par archétype ; archetype_skills = réserves de 5 compétences pour brute, assassin, tank, healer,
    support, artillery, controller, berserker + boss_rongeur)
  - stats/status_effects.json (effets de statut canoniques)
  - combat/targeting.json (patterns de zone)
- Serveur : C:\Users\Charl\Documents\Projets\kanarion\kanarion_back (C++), chemin canonique des
  compétences : server-combat/src/combat/room.cpp::apply_skill_effects ; chargement :
  server-combat/src/content/content_loader.cpp (load_monster_skills).
- Portraits client : C:\Users\Charl\Documents\Projets\kanarion\kanarion_client\assets\icons\monsters\
  (158 PNG seulement ; tu peux les regarder avec l'outil Read pour juger un monstre).
- Tables de travail dans ce dossier : monster_review.csv (archétype proposé, palier, niveau, kit
  actuel), species_table.csv et species_table.py (espèce de chaque monstre + SPECIES_IDENTITY).

## Formule des monstres (décidée)
stat = profil d'archétype × identité d'espèce × stade (jeune 0.7 … géant 1.5) × courbe de niveau
× palier (fodder/standard/tough/élite/boss) × étoiles × contenu.

## 11 archétypes
tank (encaisse, provoque) · gardien (bouclier de zone, réduction de dégâts en zone) · brute (frappe très
fort, pénètre) · berserker (vol de vie, enrage) · assassin (plonge sur la ligne arrière, burst) · archer
(physique à distance) · mage (burst magique, longues incantations à interrompre) · contrôleur (contrôles,
anti-soin, dissipation) · soigneur (soins, purification) · invocateur (monstres TEMPORAIRES uniquement)
· enchanteur (buffs d'alliés, ex-support).

## Règle des kits (décidée)
| Emplacement | Couche | Qui l'a |
|---|---|---|
| 1. Attaque d'espèce | espèce : nom, visuel, effet secondaire | tous |
| 2. Compétence de rôle | archétype | tous |
| 3. Compétence d'identité | archétype, longue recharge (≥ 20 s), incantation visible | normaux à partir du niveau 40 ; élites toujours |
| 4. Ultime | archétype aux couleurs de l'espèce | boss (+ mécanique de phase à partir du niveau 40) |
Nombre : normal (fodder/standard/tough) 2 avant niv. 40, 3 à partir de 40 ; élite 3 puis 4 ; boss 4.
"tough" est un palier de stats, pas de mécaniques.

## Effet secondaire par espèce (attaque d'espèce)
rat : infection (poison) · serpent : poison · araignée : poison + ralentissement · loup : saignement ·
hyène : réduction de soin · sanglier / bovin / ovin_caprin : étourdissement court (charge, corne) ·
golem / tortue / tatou : ralentissement (écrasement) · corbeau : aveuglement · squelette : saignement ·
spectre : gel léger (chill) · démon : brûlure · vide : drain de Souffle (mana_drain) · abyssal :
malédiction (curse_dot) · effroi : peur · faille : perce-bouclier · humanoïdes : arme de leur rôle,
pas d'effet d'espèce · autres bêtes : à juger avec cohérence (souvent aucun effet, l'attaque de base suffit).

## Compétences à CRÉER (identifiants réservés, à utiliser tels quels)
Identité d'archétype :
- skill_mob_gardien_egide        — bouclier de zone sur les alliés autour du gardien
- skill_mob_gardien_bastion      — réduction de dégâts en zone pour les alliés
- skill_mob_brute_brise_garde    — brise les boucliers de la cible + réduit son armure
- skill_mob_assassin_saut_ombre  — se téléporte sur la ligne arrière + applique exposé
- skill_mob_controleur_malediction — réduction de soin en zone + silence court
- skill_mob_invocateur_appel     — invoque 1-2 monstres temporaires (mécanique du Rongeur : bloc `summon`)
- skill_mob_enchanteur_hymne     — buff d'attaque de groupe + dissipe un buff ennemi
Rôle de base des nouveaux archétypes (s'il manque un équivalent) :
- skill_mob_gardien_coup_bouclier, skill_mob_invocateur_trait, skill_mob_enchanteur_renfort
Attaques d'espèce avec effet (variantes des basic_skills existants) :
- skill_mob_bite_infect (rat), skill_mob_bite_venom (serpent), skill_mob_sting_web (araignée),
  skill_mob_rend_bleed (loup), skill_mob_maul_rot (hyène), skill_mob_slam_crush (golem/tortue/tatou),
  skill_mob_peck_blind (corbeau), skill_mob_slash_bleed (squelette), skill_mob_chill_touch (spectre),
  skill_mob_claw_burn (démon), skill_mob_void_strike (vide), skill_mob_cursed_strike (abyssal),
  skill_mob_dread_howl (effroi), skill_mob_rift_tear (faille)
Les compétences existantes (archetype_skills, role_basic_skills, basic_skills) restent utilisables.

## Contraintes
- N'écris RIEN dans les dépôts. Tes sorties vont uniquement dans ce dossier (scratchpad/kits).
- Combat lisible : avant le niveau 40, kits simples. Les compétences d'identité ont une longue recharge
  et une incantation visible (le joueur peut interrompre).
- Le jeu est mobile, en français : noms FR courts et évocateurs.
