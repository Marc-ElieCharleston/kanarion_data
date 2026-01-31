'use client';

import { useEffect, useState } from 'react';
import { useLocale } from '@/i18n/provider';
import { LoadingState } from '@/components/LoadingState';
import { Card } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';

interface CombatSettings {
  base_attack_interval: number;
  min_damage_percent: number;
  armor_effectiveness: number;
  default_crit_chance: number;
  default_crit_dmg: number;
  gcd_duration: number;
  hit_flee: Record<string, number>;
  effects: Record<string, number>;
  damage: Record<string, number>;
  double_hit: Record<string, number>;
  sustain: Record<string, number>;
  luck: Record<string, number>;
  abilities: Record<string, number>;
  defensive: Record<string, number>;
}

interface CombatFormulas {
  damage_pipeline: { order_of_operations: string[] };
  hit_flee_system: Record<string, unknown>;
  physical_damage: Record<string, unknown>;
  magic_damage: Record<string, unknown>;
}

interface IntelligenceLevel {
  name: string;
  target_selection: string;
  skill_usage: boolean;
  coordination: boolean;
  recognizes_roles: boolean;
  avoids_tanks: boolean;
  reaction_delay: number;
  has_phases?: boolean;
}

interface AiRole {
  name: string;
  description: string;
  priority_weights: Record<string, number>;
  behavior: Record<string, number>;
  target_priority?: string[];
  preferred_skills: string[];
}

interface GameConfig {
  _meta: Record<string, unknown>;
  high_concept: { genre: string[]; pitch: string; mvp_scope: string };
  implementation_status: Record<string, Record<string, string>>;
  game_constants: Record<string, number>;
  entity_defaults: Record<string, Record<string, number>>;
  camera: Record<string, number>;
  combat_camera: Record<string, number>;
  ui_sizes: Record<string, number>;
}

interface ConfigData {
  combat: { _meta: unknown; settings: CombatSettings; formulas: CombatFormulas };
  monsterAi: { _meta: unknown; intelligence_levels: Record<string, IntelligenceLevel>; ai_roles: Record<string, AiRole> };
  gameConfig: GameConfig;
}

const TABS = [
  { id: 'combat', name_fr: 'Formules Combat', name_en: 'Combat Formulas', icon: '⚔️' },
  { id: 'monster-ai', name_fr: 'IA Monstres', name_en: 'Monster AI', icon: '🧠' },
  { id: 'game', name_fr: 'Constantes Jeu', name_en: 'Game Constants', icon: '⚙️' },
];

function CombatTab({ data }: { data: ConfigData['combat'] }) {
  const { locale } = useLocale();
  const settings = data.settings;
  const formulas = data.formulas;

  return (
    <div className="space-y-6">
      {/* Damage Pipeline */}
      <Card className="p-5">
        <h3 className="text-lg font-semibold mb-4 text-zinc-200">
          {locale === 'en' ? 'Damage Pipeline' : 'Pipeline de Degats'}
        </h3>
        <div className="space-y-2">
          {formulas.damage_pipeline.order_of_operations.map((step, i) => (
            <div key={i} className="flex items-start gap-3 p-2 bg-zinc-800/50 rounded">
              <span className="w-6 h-6 rounded-full bg-violet-500/20 text-violet-400 flex items-center justify-center text-xs shrink-0">
                {i + 1}
              </span>
              <span className="text-sm text-zinc-300">{step}</span>
            </div>
          ))}
        </div>
      </Card>

      {/* Core Settings */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        <Card className="p-5">
          <h3 className="text-lg font-semibold mb-4 text-zinc-200">
            {locale === 'en' ? 'Core Settings' : 'Parametres de Base'}
          </h3>
          <div className="space-y-2">
            <div className="flex justify-between text-sm">
              <span className="text-zinc-400">GCD Duration</span>
              <span className="text-zinc-200">{settings.gcd_duration}s</span>
            </div>
            <div className="flex justify-between text-sm">
              <span className="text-zinc-400">Base Attack Interval</span>
              <span className="text-zinc-200">{settings.base_attack_interval}s</span>
            </div>
            <div className="flex justify-between text-sm">
              <span className="text-zinc-400">Default Crit Chance</span>
              <span className="text-zinc-200">{settings.default_crit_chance}%</span>
            </div>
            <div className="flex justify-between text-sm">
              <span className="text-zinc-400">Default Crit Damage</span>
              <span className="text-zinc-200">{settings.default_crit_dmg}%</span>
            </div>
            <div className="flex justify-between text-sm">
              <span className="text-zinc-400">Min Damage</span>
              <span className="text-zinc-200">{settings.min_damage_percent * 100}%</span>
            </div>
          </div>
        </Card>

        <Card className="p-5">
          <h3 className="text-lg font-semibold mb-4 text-zinc-200">
            {locale === 'en' ? 'Hit/Flee System' : 'Systeme Hit/Flee'}
          </h3>
          <div className="space-y-2">
            {Object.entries(settings.hit_flee).map(([key, value]) => (
              <div key={key} className="flex justify-between text-sm">
                <span className="text-zinc-400">{key.replace(/_/g, ' ')}</span>
                <span className="text-zinc-200">{value}</span>
              </div>
            ))}
          </div>
        </Card>
      </div>

      {/* Caps */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <Card className="p-4">
          <h4 className="font-medium mb-3 text-zinc-200">{locale === 'en' ? 'Damage Caps' : 'Caps Degats'}</h4>
          <div className="space-y-2 text-sm">
            {Object.entries(settings.damage).map(([key, value]) => (
              <div key={key} className="flex justify-between">
                <span className="text-zinc-400">{key.replace(/_/g, ' ')}</span>
                <span className="text-red-400">{value}{key.includes('cap') ? '%' : ''}</span>
              </div>
            ))}
          </div>
        </Card>

        <Card className="p-4">
          <h4 className="font-medium mb-3 text-zinc-200">{locale === 'en' ? 'Sustain Caps' : 'Caps Sustain'}</h4>
          <div className="space-y-2 text-sm">
            {Object.entries(settings.sustain).map(([key, value]) => (
              <div key={key} className="flex justify-between">
                <span className="text-zinc-400">{key.replace(/_/g, ' ')}</span>
                <span className="text-green-400">{value}{key.includes('cap') ? '%' : ''}</span>
              </div>
            ))}
          </div>
        </Card>

        <Card className="p-4">
          <h4 className="font-medium mb-3 text-zinc-200">{locale === 'en' ? 'Defensive Caps' : 'Caps Defensifs'}</h4>
          <div className="space-y-2 text-sm">
            {Object.entries(settings.defensive).map(([key, value]) => (
              <div key={key} className="flex justify-between">
                <span className="text-zinc-400">{key.replace(/_/g, ' ')}</span>
                <span className="text-blue-400">{value}{key.includes('cap') || key.includes('reduction') ? '%' : ''}</span>
              </div>
            ))}
          </div>
        </Card>
      </div>

      {/* Effect System */}
      <Card className="p-5">
        <h3 className="text-lg font-semibold mb-4 text-zinc-200">
          {locale === 'en' ? 'Effect System' : 'Systeme d\'Effets'}
        </h3>
        <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
          {Object.entries(settings.effects).map(([key, value]) => (
            <div key={key} className="bg-zinc-800/50 p-3 rounded text-center">
              <div className="text-xs text-zinc-500 capitalize">{key.replace(/_/g, ' ')}</div>
              <div className="text-lg font-mono text-purple-400">{value}{key.includes('cap') || key.includes('minimum') ? '%' : ''}</div>
            </div>
          ))}
        </div>
      </Card>
    </div>
  );
}

function MonsterAiTab({ data }: { data: ConfigData['monsterAi'] }) {
  const { locale } = useLocale();
  const intelligenceLevels = data.intelligence_levels;
  const aiRoles = data.ai_roles;

  return (
    <div className="space-y-6">
      {/* Intelligence Levels */}
      <div>
        <h3 className="text-lg font-semibold mb-4 text-zinc-200">
          {locale === 'en' ? 'Intelligence Levels' : 'Niveaux d\'Intelligence'}
        </h3>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {Object.entries(intelligenceLevels).map(([level, data]) => (
            <Card key={level} className="p-4">
              <div className="flex items-center gap-2 mb-3">
                <span className="w-8 h-8 rounded-full bg-violet-500/20 text-violet-400 flex items-center justify-center font-bold">
                  {level}
                </span>
                <h4 className="font-medium text-zinc-200">{data.name}</h4>
              </div>
              <div className="space-y-2 text-sm">
                <div className="flex justify-between">
                  <span className="text-zinc-400">{locale === 'en' ? 'Target Selection' : 'Selection Cible'}</span>
                  <span className="text-zinc-300">{data.target_selection}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-zinc-400">{locale === 'en' ? 'Reaction Delay' : 'Delai Reaction'}</span>
                  <span className="text-zinc-300">{data.reaction_delay}s</span>
                </div>
                <div className="flex flex-wrap gap-1 mt-2">
                  {data.skill_usage && <Badge className="bg-green-500/20 text-green-400 text-xs">Skills</Badge>}
                  {data.coordination && <Badge className="bg-blue-500/20 text-blue-400 text-xs">Coordination</Badge>}
                  {data.recognizes_roles && <Badge className="bg-purple-500/20 text-purple-400 text-xs">Roles</Badge>}
                  {data.avoids_tanks && <Badge className="bg-orange-500/20 text-orange-400 text-xs">Avoids Tanks</Badge>}
                  {data.has_phases && <Badge className="bg-red-500/20 text-red-400 text-xs">Phases</Badge>}
                </div>
              </div>
            </Card>
          ))}
        </div>
      </div>

      {/* AI Roles */}
      <div>
        <h3 className="text-lg font-semibold mb-4 text-zinc-200">
          {locale === 'en' ? 'AI Roles' : 'Roles d\'IA'}
        </h3>
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
          {Object.entries(aiRoles).map(([roleId, role]) => (
            <Card key={roleId} className="p-4">
              <div className="flex items-center justify-between mb-2">
                <h4 className="font-semibold text-zinc-200">{role.name}</h4>
                <Badge variant="outline" className="text-xs capitalize">{roleId}</Badge>
              </div>
              <p className="text-sm text-zinc-400 mb-3">{role.description}</p>

              {/* Behavior */}
              <div className="mb-3">
                <span className="text-xs text-zinc-500">{locale === 'en' ? 'Behavior' : 'Comportement'}:</span>
                <div className="flex gap-2 mt-1">
                  {Object.entries(role.behavior).map(([key, value]) => (
                    <div key={key} className="bg-zinc-800/50 px-2 py-1 rounded text-xs">
                      <span className="text-zinc-400 capitalize">{key.replace(/_/g, ' ')}</span>
                      <span className="text-zinc-200 ml-1">{(value * 100).toFixed(0)}%</span>
                    </div>
                  ))}
                </div>
              </div>

              {/* Priority Weights */}
              <div className="mb-3">
                <span className="text-xs text-zinc-500">{locale === 'en' ? 'Priority Weights' : 'Poids Priorite'}:</span>
                <div className="flex flex-wrap gap-1 mt-1">
                  {Object.entries(role.priority_weights).map(([key, value]) => (
                    <span key={key} className="text-xs bg-violet-500/20 text-violet-400 px-2 py-0.5 rounded">
                      {key.replace('attack_', '')}: {value}%
                    </span>
                  ))}
                </div>
              </div>

              {/* Preferred Skills */}
              <div>
                <span className="text-xs text-zinc-500">{locale === 'en' ? 'Preferred Skills' : 'Skills Preferes'}:</span>
                <div className="flex flex-wrap gap-1 mt-1">
                  {role.preferred_skills.map((skill) => (
                    <span key={skill} className="text-xs bg-emerald-500/20 text-emerald-400 px-2 py-0.5 rounded">
                      {skill}
                    </span>
                  ))}
                </div>
              </div>
            </Card>
          ))}
        </div>
      </div>
    </div>
  );
}

function GameTab({ data }: { data: ConfigData['gameConfig'] }) {
  const { locale } = useLocale();

  return (
    <div className="space-y-6">
      {/* High Concept */}
      <Card className="p-5">
        <h3 className="text-lg font-semibold mb-4 text-zinc-200">
          {locale === 'en' ? 'High Concept' : 'Concept'}
        </h3>
        <div className="space-y-3">
          <div className="flex flex-wrap gap-2">
            {data.high_concept.genre.map((g) => (
              <Badge key={g} className="bg-violet-500/20 text-violet-400">{g}</Badge>
            ))}
          </div>
          <p className="text-sm text-zinc-300">{data.high_concept.pitch}</p>
          <p className="text-xs text-zinc-500">MVP: {data.high_concept.mvp_scope}</p>
        </div>
      </Card>

      {/* Game Constants */}
      <Card className="p-5">
        <h3 className="text-lg font-semibold mb-4 text-zinc-200">
          {locale === 'en' ? 'Game Constants' : 'Constantes de Jeu'}
        </h3>
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          {Object.entries(data.game_constants).map(([key, value]) => (
            <div key={key} className="bg-zinc-800/50 p-3 rounded text-center">
              <div className="text-xs text-zinc-500 capitalize">{key.replace(/_/g, ' ')}</div>
              <div className="text-xl font-mono text-emerald-400">{value}</div>
            </div>
          ))}
        </div>
      </Card>

      {/* Implementation Status */}
      <Card className="p-5">
        <h3 className="text-lg font-semibold mb-4 text-zinc-200">
          {locale === 'en' ? 'Implementation Status' : 'Statut Implementation'}
        </h3>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
          {Object.entries(data.implementation_status).filter(([key]) => key !== '_comment').map(([category, features]) => (
            <div key={category} className="bg-zinc-800/50 p-3 rounded">
              <h4 className="font-medium text-zinc-200 capitalize mb-2">{category.replace(/_/g, ' ')}</h4>
              <div className="space-y-1">
                {Object.entries(features).map(([feature, status]) => (
                  <div key={feature} className="flex items-center justify-between text-xs">
                    <span className="text-zinc-400 capitalize">{feature.replace(/_/g, ' ')}</span>
                    <Badge className={`text-xs ${
                      status === 'implemented' ? 'bg-green-500/20 text-green-400' :
                      status === 'partial' ? 'bg-yellow-500/20 text-yellow-400' :
                      'bg-zinc-700 text-zinc-400'
                    }`}>
                      {status}
                    </Badge>
                  </div>
                ))}
              </div>
            </div>
          ))}
        </div>
      </Card>

      {/* Entity Defaults */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        {Object.entries(data.entity_defaults).filter(([key]) => key !== '_comment').map(([entity, defaults]) => (
          <Card key={entity} className="p-4">
            <h4 className="font-medium text-zinc-200 capitalize mb-3">{entity} {locale === 'en' ? 'Defaults' : 'Par Defaut'}</h4>
            <div className="space-y-2 text-sm">
              {Object.entries(defaults).map(([key, value]) => (
                <div key={key} className="flex justify-between">
                  <span className="text-zinc-400 capitalize">{key.replace(/_/g, ' ')}</span>
                  <span className="text-zinc-200">{value}</span>
                </div>
              ))}
            </div>
          </Card>
        ))}
      </div>

      {/* Camera Settings */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        <Card className="p-4">
          <h4 className="font-medium text-zinc-200 mb-3">{locale === 'en' ? 'World Camera' : 'Camera Monde'}</h4>
          <div className="space-y-2 text-sm">
            {Object.entries(data.camera).map(([key, value]) => (
              <div key={key} className="flex justify-between">
                <span className="text-zinc-400 capitalize">{key.replace(/_/g, ' ')}</span>
                <span className="text-zinc-200">{value}</span>
              </div>
            ))}
          </div>
        </Card>
        <Card className="p-4">
          <h4 className="font-medium text-zinc-200 mb-3">{locale === 'en' ? 'Combat Camera' : 'Camera Combat'}</h4>
          <div className="space-y-2 text-sm">
            {Object.entries(data.combat_camera).filter(([key]) => key !== '_comment').map(([key, value]) => (
              <div key={key} className="flex justify-between">
                <span className="text-zinc-400 capitalize">{key.replace(/_/g, ' ')}</span>
                <span className="text-zinc-200">{value}</span>
              </div>
            ))}
          </div>
        </Card>
      </div>
    </div>
  );
}

export default function ConfigPage() {
  const [activeTab, setActiveTab] = useState('combat');
  const [data, setData] = useState<ConfigData | null>(null);
  const [loading, setLoading] = useState(true);
  const { locale } = useLocale();

  useEffect(() => {
    fetch('/api/config')
      .then((res) => res.json())
      .then((data) => {
        setData(data);
        setLoading(false);
      })
      .catch(() => setLoading(false));
  }, []);

  if (loading) {
    return (
      <div className="flex h-[calc(100vh-4rem)] items-center justify-center">
        <LoadingState />
      </div>
    );
  }

  if (!data) {
    return (
      <div className="flex h-[calc(100vh-4rem)] items-center justify-center text-red-400">
        {locale === 'en' ? 'Failed to load config' : 'Erreur de chargement'}
      </div>
    );
  }

  return (
    <div className="flex h-[calc(100vh-4rem)] overflow-hidden">
      {/* Secondary Sidebar */}
      <aside className="w-64 border-r border-zinc-800 overflow-y-auto bg-zinc-900/50">
        <div className="p-4 border-b border-zinc-800">
          <h2 className="text-lg font-semibold">{locale === 'en' ? 'Config' : 'Config'}</h2>
          <p className="text-xs text-zinc-500">{locale === 'en' ? 'Game configuration' : 'Configuration du jeu'}</p>
        </div>
        <nav className="p-2">
          {TABS.map((tab) => (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id)}
              className={`w-full flex items-center gap-3 px-3 py-2.5 rounded-lg transition-colors text-left ${
                activeTab === tab.id
                  ? 'bg-violet-500/20 text-violet-300 border border-violet-500/30'
                  : 'text-zinc-400 hover:bg-zinc-800/50 hover:text-white'
              }`}
            >
              <span className="text-xl">{tab.icon}</span>
              <div className="flex-1 min-w-0">
                <div className="text-sm font-medium truncate">{locale === 'en' ? tab.name_en : tab.name_fr}</div>
                <div className="text-xs text-zinc-500 truncate">{locale === 'en' ? tab.name_fr : tab.name_en}</div>
              </div>
            </button>
          ))}
        </nav>
      </aside>

      {/* Main Content */}
      <main className="flex-1 overflow-y-auto">
        <div className="p-4 md:p-6 lg:p-8">
          {activeTab === 'combat' && <CombatTab data={data.combat} />}
          {activeTab === 'monster-ai' && <MonsterAiTab data={data.monsterAi} />}
          {activeTab === 'game' && <GameTab data={data.gameConfig} />}
        </div>
      </main>
    </div>
  );
}
