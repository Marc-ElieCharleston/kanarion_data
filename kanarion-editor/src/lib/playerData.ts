/**
 * Player Data Mapping Functions
 *
 * Ces fonctions composent les données de plusieurs JSONs pour créer
 * des objets "prêts à afficher" pour la vue Player.
 *
 * Principe: Si le JSON change, on update ICI, pas dans les composants.
 */

// Types pour la vue Player (simplifiés, sans détails techniques)

export interface PlayerStatusEffect {
  id: string;
  name: string;
  category: 'dot' | 'hot' | 'buff' | 'debuff' | 'control' | 'immunity' | 'special';
  categoryLabel: string;
  icon: string;
  description: string;
  type: 'buff' | 'debuff';
  typeLabel: string;
  // Stacking info (simplifié)
  stacking: {
    type: 'stackable' | 'refresh' | 'unique';
    maxStacks?: number;
    explanation: string;
  };
  // Duration info
  duration?: {
    typical: string;
    reducedBy?: string;
  };
  // Counter info (ce qui annule/réduit l'effet)
  counters?: string[];
  // Ce qui cause cet effet
  sources?: string[];
  // Formule (optionnel, pour theorycrafters)
  formula?: string;
}

export interface PlayerStatusCategory {
  id: string;
  name: string;
  icon: string;
  color: string;
  description: string;
  effects: PlayerStatusEffect[];
}

// Icons pour les catégories
const CATEGORY_ICONS: Record<string, string> = {
  dot: '🔥',
  hot: '💚',
  stat_modifiers: '📊',
  tempo: '⚡',
  control: '🔒',
  defensive: '🛡️',
  immunity: '✨',
  aggro: '😤',
  special: '🎯',
};

const CATEGORY_LABELS: Record<string, { fr: string; en: string }> = {
  dot: { fr: 'Dégâts sur la durée', en: 'Damage over Time' },
  hot: { fr: 'Soins sur la durée', en: 'Heal over Time' },
  stat_modifiers: { fr: 'Modificateurs de stats', en: 'Stat Modifiers' },
  tempo: { fr: 'Vitesse', en: 'Speed Effects' },
  control: { fr: 'Contrôle (CC)', en: 'Crowd Control' },
  defensive: { fr: 'Défensif', en: 'Defensive' },
  immunity: { fr: 'Immunités', en: 'Immunities' },
  aggro: { fr: 'Aggro / Menace', en: 'Aggro / Threat' },
  special: { fr: 'Spécial', en: 'Special' },
};

const CATEGORY_COLORS: Record<string, string> = {
  dot: 'text-red-400 border-red-500/30 bg-red-500/10',
  hot: 'text-green-400 border-green-500/30 bg-green-500/10',
  stat_modifiers: 'text-blue-400 border-blue-500/30 bg-blue-500/10',
  tempo: 'text-yellow-400 border-yellow-500/30 bg-yellow-500/10',
  control: 'text-purple-400 border-purple-500/30 bg-purple-500/10',
  defensive: 'text-sky-400 border-sky-500/30 bg-sky-500/10',
  immunity: 'text-emerald-400 border-emerald-500/30 bg-emerald-500/10',
  aggro: 'text-orange-400 border-orange-500/30 bg-orange-500/10',
  special: 'text-amber-400 border-amber-500/30 bg-amber-500/10',
};

const STACKING_EXPLANATIONS: Record<string, { fr: string; en: string }> = {
  stackable: {
    fr: '+10% par stack, max 10 stacks. Réappliquer ajoute des stacks et rafraîchit la durée.',
    en: '+10% per stack, max 10 stacks. Reapplying adds stacks and refreshes duration.'
  },
  refresh: {
    fr: "Réappliquer rafraîchit la durée, l'effet ne se cumule pas.",
    en: 'Reapplying refreshes duration only, effect does not stack.'
  },
  unique: {
    fr: 'Une seule instance peut être active. Réappliquer rafraîchit la durée.',
    en: 'Only one instance can be active. Reapplying refreshes duration.'
  },
};

// Types pour les données JSON brutes
interface RawStatusEffect {
  name_fr: string;
  name_en?: string;
  description_fr?: string;
  description_en?: string;
  polarity: 'buff' | 'debuff';
  stacking?: 'stackable' | 'refresh' | 'unique';
  max_stacks?: number;
  formula?: string;
  sources?: string[];
  impl?: string;
}

interface RawStatusEffectsData {
  effects?: Record<string, Record<string, RawStatusEffect>>;
}

/**
 * Transforme les données brutes des status effects en format Player-friendly
 */
export function getStatusEffectsForPlayer(
  statusEffectsData: RawStatusEffectsData | null,
  configData: unknown,
  statsData: unknown,
  locale: 'fr' | 'en'
): PlayerStatusCategory[] {
  const categories: PlayerStatusCategory[] = [];
  const effects = statusEffectsData?.effects || {};

  // Parcourir chaque catégorie
  Object.entries(effects).forEach(([categoryId, categoryEffects]) => {
    if (categoryId.startsWith('_')) return; // Skip comments

    const categoryEffectsList: PlayerStatusEffect[] = [];
    const effectsInCategory = categoryEffects as Record<string, RawStatusEffect>;

    // Parcourir chaque effet dans la catégorie
    Object.entries(effectsInCategory).forEach(([effectId, effect]) => {
      if (effectId.startsWith('_')) return; // Skip comments

      // Déterminer la catégorie simplifiée
      let simpleCategory: PlayerStatusEffect['category'] = 'special';
      if (categoryId === 'dot') simpleCategory = 'dot';
      else if (categoryId === 'hot') simpleCategory = 'hot';
      else if (categoryId === 'control') simpleCategory = 'control';
      else if (categoryId === 'immunity') simpleCategory = 'immunity';
      else if (categoryId === 'defensive') simpleCategory = 'special';
      else if (effect.polarity === 'buff') simpleCategory = 'buff';
      else if (effect.polarity === 'debuff') simpleCategory = 'debuff';

      // Construire l'explication du stacking
      const stackingType = effect.stacking || 'unique';
      const stackingExplanation = STACKING_EXPLANATIONS[stackingType]?.[locale] || '';

      // Déterminer les counters
      const counters: string[] = [];
      if (categoryId === 'control' || categoryId === 'dot') {
        counters.push(locale === 'fr' ? 'Tenacité (réduit durée)' : 'Tenacity (reduces duration)');
        counters.push(locale === 'fr' ? 'Résist. aux Effets (chance de résister)' : 'Effect Resist (chance to resist)');
      }
      if (categoryId === 'control') {
        counters.push(locale === 'fr' ? 'Cleanse' : 'Cleanse');
        counters.push(locale === 'fr' ? 'Immunité CC' : 'CC Immunity');
      }
      if (effect.polarity === 'debuff' && categoryId === 'stat_modifiers') {
        counters.push(locale === 'fr' ? 'Dispel' : 'Dispel');
      }

      const playerEffect: PlayerStatusEffect = {
        id: effectId,
        name: locale === 'en' && effect.name_en ? effect.name_en : effect.name_fr,
        category: simpleCategory,
        categoryLabel: CATEGORY_LABELS[categoryId]?.[locale] || categoryId,
        icon: CATEGORY_ICONS[categoryId] || '❓',
        description: locale === 'en' && effect.description_en ? effect.description_en : (effect.description_fr || ''),
        type: effect.polarity,
        typeLabel: effect.polarity === 'buff'
          ? (locale === 'fr' ? 'Buff' : 'Buff')
          : (locale === 'fr' ? 'Debuff' : 'Debuff'),
        stacking: {
          type: stackingType,
          maxStacks: effect.max_stacks,
          explanation: effect.max_stacks
            ? `${stackingExplanation} (max ${effect.max_stacks})`
            : stackingExplanation,
        },
        counters: counters.length > 0 ? counters : undefined,
        sources: effect.sources,
        formula: effect.formula,
      };

      categoryEffectsList.push(playerEffect);
    });

    if (categoryEffectsList.length > 0) {
      categories.push({
        id: categoryId,
        name: CATEGORY_LABELS[categoryId]?.[locale] || categoryId,
        icon: CATEGORY_ICONS[categoryId] || '❓',
        color: CATEGORY_COLORS[categoryId] || 'text-zinc-400 border-zinc-500/30',
        description: '',
        effects: categoryEffectsList,
      });
    }
  });

  return categories;
}

/**
 * Récupère un status effect spécifique avec toutes ses infos player-friendly
 */
export function getStatusEffectById(
  statusEffectsData: RawStatusEffectsData | null,
  effectId: string,
  locale: 'fr' | 'en'
): PlayerStatusEffect | null {
  const effects = statusEffectsData?.effects || {};

  for (const [categoryId, categoryEffects] of Object.entries(effects)) {
    if (categoryId.startsWith('_')) continue;

    const effectsInCategory = categoryEffects as Record<string, RawStatusEffect>;
    const effect = effectsInCategory[effectId];
    if (effect) {
      // Réutiliser la logique de transformation
      const allCategories = getStatusEffectsForPlayer(statusEffectsData, null, null, locale);
      for (const cat of allCategories) {
        const found = cat.effects.find(e => e.id === effectId);
        if (found) return found;
      }
    }
  }

  return null;
}

// ============================================
// CLASSES DATA
// ============================================

export interface PlayerClass {
  id: string;
  name: string;
  role: string;
  roleLabel: string;
  icon: string;
  tagline: string;
  description: string;
  lore: string;
  wikiIntro: string;
  difficulty: 'easy' | 'medium' | 'hard';
  difficultyLabel: string;
  playstyleTips: string[];
  primaryStat: string;
  subclasses: PlayerSubclass[];
}

export interface PlayerSubclass {
  id: string;
  name: string;
  tagline: string;
  description: string;
  lore: string;
  identity: string;
  signatureSkill: string;
  tier3: { id: string; identity: string; signature: string }[];
}

const CLASS_ICONS: Record<string, string> = {
  warrior: '🗡️',
  mage: '🔮',
  healer: '💚',
  archer: '🏹',
  rogue: '🗡️',
  artisan: '🔧',
};

const ROLE_LABELS: Record<string, { fr: string; en: string }> = {
  tank_melee: { fr: 'Tank / Mêlée', en: 'Tank / Melee' },
  dps_magic: { fr: 'DPS Magique', en: 'Magic DPS' },
  dps_ranged: { fr: 'DPS Distance', en: 'Ranged DPS' },
  dps_melee: { fr: 'DPS Mêlée', en: 'Melee DPS' },
  support_heal: { fr: 'Support / Soin', en: 'Support / Healer' },
  support_utility: { fr: 'Support / Utilitaire', en: 'Support / Utility' },
};

const DIFFICULTY_LABELS: Record<string, { fr: string; en: string }> = {
  easy: { fr: 'Facile', en: 'Easy' },
  medium: { fr: 'Intermédiaire', en: 'Medium' },
  hard: { fr: 'Difficile', en: 'Hard' },
};

const DIFFICULTY_COLORS: Record<string, string> = {
  easy: 'text-green-400 bg-green-500/10 border-green-500/30',
  medium: 'text-yellow-400 bg-yellow-500/10 border-yellow-500/30',
  hard: 'text-red-400 bg-red-500/10 border-red-500/30',
};

interface RawClassData {
  id: string;
  name: string;
  role: string;
  primary_stat: string;
  tagline?: string;
  tagline_en?: string;
  description?: string;
  description_en?: string;
  lore?: string;
  lore_en?: string;
  wiki_intro?: string;
  wiki_intro_en?: string;
  difficulty?: string;
  playstyle_tips?: string[];
  playstyle_tips_en?: string[];
  subclasses?: RawSubclassData[];
}

interface RawSubclassData {
  id: string;
  name: string;
  identity?: string;
  signature_skill?: string;
  tagline?: string;
  tagline_en?: string;
  description?: string;
  description_en?: string;
  lore?: string;
  lore_en?: string;
  tier3?: { id: string; identity: string; signature: string }[];
}

interface RawClassesIndex {
  classes?: RawClassData[];
}

/**
 * Transforme les données brutes des classes en format Player-friendly
 */
export function getClassesForPlayer(
  classesData: RawClassesIndex | null,
  locale: 'fr' | 'en'
): PlayerClass[] {
  const classes = classesData?.classes || [];

  return classes.map((cls): PlayerClass => {
    const subclasses: PlayerSubclass[] = (cls.subclasses || []).map((sub): PlayerSubclass => ({
      id: sub.id,
      name: sub.name,
      tagline: locale === 'en' && sub.tagline_en ? sub.tagline_en : (sub.tagline || ''),
      description: locale === 'en' && sub.description_en ? sub.description_en : (sub.description || ''),
      lore: locale === 'en' && sub.lore_en ? sub.lore_en : (sub.lore || ''),
      identity: sub.identity || '',
      signatureSkill: sub.signature_skill || '',
      tier3: sub.tier3 || [],
    }));

    return {
      id: cls.id,
      name: cls.name,
      role: cls.role,
      roleLabel: ROLE_LABELS[cls.role]?.[locale] || cls.role,
      icon: CLASS_ICONS[cls.id] || '❓',
      tagline: locale === 'en' && cls.tagline_en ? cls.tagline_en : (cls.tagline || ''),
      description: locale === 'en' && cls.description_en ? cls.description_en : (cls.description || ''),
      lore: locale === 'en' && cls.lore_en ? cls.lore_en : (cls.lore || ''),
      wikiIntro: locale === 'en' && cls.wiki_intro_en ? cls.wiki_intro_en : (cls.wiki_intro || ''),
      difficulty: (cls.difficulty as 'easy' | 'medium' | 'hard') || 'medium',
      difficultyLabel: DIFFICULTY_LABELS[cls.difficulty || 'medium']?.[locale] || '',
      playstyleTips: locale === 'en' && cls.playstyle_tips_en ? cls.playstyle_tips_en : (cls.playstyle_tips || []),
      primaryStat: cls.primary_stat,
      subclasses,
    };
  });
}

/**
 * Récupère une classe spécifique
 */
export function getClassById(
  classesData: RawClassesIndex | null,
  classId: string,
  locale: 'fr' | 'en'
): PlayerClass | null {
  const classes = getClassesForPlayer(classesData, locale);
  return classes.find(c => c.id === classId) || null;
}

// Export des constantes pour usage dans les composants
export { CATEGORY_ICONS, CATEGORY_LABELS, CATEGORY_COLORS, CLASS_ICONS, ROLE_LABELS, DIFFICULTY_LABELS, DIFFICULTY_COLORS };
