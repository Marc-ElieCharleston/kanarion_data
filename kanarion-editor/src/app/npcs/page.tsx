'use client';

import { useEffect, useState } from 'react';
import { useLocale } from '@/i18n/provider';
import { LoadingState } from '@/components/LoadingState';
import { Card } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';

interface ServiceNpc {
  id: string;
  name: string;
  services: string[];
  location: string;
  lore: string;
}

interface QuestNpc {
  id: string;
  name: string;
  services: string[];
  location: string;
  lore: string;
}

interface ClassMaster {
  id: string;
  name: string;
  class: string;
  lore: string;
}

interface ArenaNpc {
  id: string;
  name: string;
  services: string[];
  location: string;
  lore: string;
}

interface AmbientNpc {
  id: string;
  name: string;
  type: string;
  day_night: string;
}

interface NpcsData {
  _meta: { version: string; last_updated: string; description: string };
  types: string[];
  priorities: string[];
  service_npcs: ServiceNpc[];
  quest_npcs: QuestNpc[];
  class_masters: ClassMaster[];
  arena_npcs: ArenaNpc[];
  ambient_npcs: AmbientNpc[];
  services_catalog: Record<string, string>;
  _summary: Record<string, number>;
}

const TABS = [
  { id: 'service', name_fr: 'Services', name_en: 'Services', icon: '🏪', count: 16 },
  { id: 'quest', name_fr: 'Quetes', name_en: 'Quests', icon: '📜', count: 2 },
  { id: 'class_master', name_fr: 'Maitres de Classe', name_en: 'Class Masters', icon: '⚔️', count: 5 },
  { id: 'arena', name_fr: 'Arene', name_en: 'Arena', icon: '🏟️', count: 1 },
  { id: 'ambient', name_fr: 'Ambiance', name_en: 'Ambient', icon: '🌆', count: 10 },
];

function NpcCard({ npc, services, servicesCatalog }: {
  npc: ServiceNpc | QuestNpc | ArenaNpc;
  services?: string[];
  servicesCatalog: Record<string, string>;
}) {
  const { locale } = useLocale();
  const npcServices = services || npc.services;

  return (
    <Card className="p-4 hover:border-zinc-600 transition-colors">
      <div className="flex items-start justify-between mb-3">
        <div>
          <h3 className="font-semibold text-zinc-200">{npc.name}</h3>
          <span className="text-xs text-zinc-500">{npc.location}</span>
        </div>
        <Badge variant="outline" className="text-xs">{npc.id}</Badge>
      </div>

      <p className="text-sm text-zinc-400 italic mb-3">&ldquo;{npc.lore}&rdquo;</p>

      {npcServices && npcServices.length > 0 && (
        <div>
          <span className="text-xs text-zinc-500 block mb-1">{locale === 'en' ? 'Services' : 'Services'}:</span>
          <div className="space-y-1">
            {npcServices.map((service) => (
              <div key={service} className="text-xs bg-zinc-800/50 px-2 py-1 rounded">
                <span className="text-emerald-400 font-medium">{service}</span>
                {servicesCatalog[service] && (
                  <span className="text-zinc-500 ml-2">- {servicesCatalog[service]}</span>
                )}
              </div>
            ))}
          </div>
        </div>
      )}
    </Card>
  );
}

function ServiceNpcsTab({ data }: { data: NpcsData }) {
  const { locale } = useLocale();

  return (
    <div>
      <div className="mb-4">
        <h3 className="text-sm text-zinc-500">
          {data.service_npcs.length} {locale === 'en' ? 'service NPCs' : 'NPCs de service'}
        </h3>
      </div>
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
        {data.service_npcs.map((npc) => (
          <NpcCard key={npc.id} npc={npc} servicesCatalog={data.services_catalog} />
        ))}
      </div>
    </div>
  );
}

function QuestNpcsTab({ data }: { data: NpcsData }) {
  const { locale } = useLocale();

  return (
    <div>
      <div className="mb-4">
        <h3 className="text-sm text-zinc-500">
          {data.quest_npcs.length} {locale === 'en' ? 'quest NPCs' : 'NPCs de quete'}
        </h3>
      </div>
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
        {data.quest_npcs.map((npc) => (
          <NpcCard key={npc.id} npc={npc} servicesCatalog={data.services_catalog} />
        ))}
      </div>
    </div>
  );
}

function ClassMastersTab({ data }: { data: NpcsData }) {
  const { locale } = useLocale();

  const classIcons: Record<string, string> = {
    warrior: '🗡️',
    mage: '🔮',
    archer: '🏹',
    rogue: '🗡️',
    healer: '💚',
    artisan: '🔧',
  };

  const classColors: Record<string, string> = {
    warrior: 'border-red-500/30 bg-red-500/10',
    mage: 'border-blue-500/30 bg-blue-500/10',
    archer: 'border-green-500/30 bg-green-500/10',
    rogue: 'border-purple-500/30 bg-purple-500/10',
    healer: 'border-emerald-500/30 bg-emerald-500/10',
    artisan: 'border-orange-500/30 bg-orange-500/10',
  };

  return (
    <div>
      <div className="mb-4">
        <h3 className="text-sm text-zinc-500">
          {data.class_masters.length} {locale === 'en' ? 'class masters' : 'maitres de classe'}
        </h3>
      </div>
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        {data.class_masters.map((master) => (
          <Card key={master.id} className={`p-4 border ${classColors[master.class] || ''}`}>
            <div className="flex items-center gap-3 mb-3">
              <span className="text-3xl">{classIcons[master.class] || '❓'}</span>
              <div>
                <h3 className="font-semibold text-zinc-200">{master.name}</h3>
                <Badge className={`text-xs capitalize ${
                  master.class === 'warrior' ? 'bg-red-500/20 text-red-400' :
                  master.class === 'mage' ? 'bg-blue-500/20 text-blue-400' :
                  master.class === 'archer' ? 'bg-green-500/20 text-green-400' :
                  master.class === 'rogue' ? 'bg-purple-500/20 text-purple-400' :
                  master.class === 'healer' ? 'bg-emerald-500/20 text-emerald-400' :
                  'bg-zinc-500/20 text-zinc-400'
                }`}>
                  {master.class}
                </Badge>
              </div>
            </div>
            <p className="text-sm text-zinc-400 italic">&ldquo;{master.lore}&rdquo;</p>
          </Card>
        ))}
      </div>
    </div>
  );
}

function ArenaNpcsTab({ data }: { data: NpcsData }) {
  const { locale } = useLocale();

  return (
    <div>
      <div className="mb-4">
        <h3 className="text-sm text-zinc-500">
          {data.arena_npcs.length} {locale === 'en' ? 'arena NPCs' : 'NPCs d\'arene'}
        </h3>
      </div>
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
        {data.arena_npcs.map((npc) => (
          <NpcCard key={npc.id} npc={npc} servicesCatalog={data.services_catalog} />
        ))}
      </div>
    </div>
  );
}

function AmbientNpcsTab({ data }: { data: NpcsData }) {
  const { locale } = useLocale();

  const typeIcons: Record<string, string> = {
    standing: '🧍',
    patrol: '🚶',
    running: '🏃',
    idle: '😺',
    wander: '🐕',
    carry: '📦',
    sitting: '🪑',
    kneeling: '🧎',
    fishing: '🎣',
  };

  const dayNightColors: Record<string, string> = {
    day: 'bg-yellow-500/20 text-yellow-400',
    night: 'bg-indigo-500/20 text-indigo-400',
    any: 'bg-zinc-500/20 text-zinc-400',
  };

  return (
    <div>
      <div className="mb-4">
        <h3 className="text-sm text-zinc-500">
          {data.ambient_npcs.length} {locale === 'en' ? 'ambient NPCs' : 'NPCs d\'ambiance'}
        </h3>
      </div>
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-3">
        {data.ambient_npcs.map((npc) => (
          <Card key={npc.id} className="p-3 hover:border-zinc-600 transition-colors">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-2">
                <span className="text-xl">{typeIcons[npc.type] || '👤'}</span>
                <div>
                  <h4 className="font-medium text-zinc-200">{npc.name}</h4>
                  <span className="text-xs text-zinc-500 capitalize">{npc.type}</span>
                </div>
              </div>
              <Badge className={`text-xs capitalize ${dayNightColors[npc.day_night]}`}>
                {npc.day_night === 'any' ? '24/7' : npc.day_night}
              </Badge>
            </div>
          </Card>
        ))}
      </div>
    </div>
  );
}

function ServicesCatalogTab({ data }: { data: NpcsData }) {
  const { locale } = useLocale();

  return (
    <div>
      <div className="mb-4">
        <h3 className="text-sm text-zinc-500">
          {Object.keys(data.services_catalog).length} {locale === 'en' ? 'services available' : 'services disponibles'}
        </h3>
      </div>
      <div className="overflow-x-auto">
        <table className="w-full text-sm bg-zinc-900 rounded-lg border border-zinc-800">
          <thead>
            <tr className="border-b border-zinc-700">
              <th className="text-left py-3 px-4 text-zinc-400">{locale === 'en' ? 'Service ID' : 'ID Service'}</th>
              <th className="text-left py-3 px-4 text-zinc-400">{locale === 'en' ? 'Description' : 'Description'}</th>
            </tr>
          </thead>
          <tbody>
            {Object.entries(data.services_catalog).map(([id, desc], i) => (
              <tr key={id} className={`border-b border-zinc-800 ${i % 2 === 0 ? 'bg-zinc-800/20' : ''}`}>
                <td className="py-3 px-4 font-mono text-emerald-400">{id}</td>
                <td className="py-3 px-4 text-zinc-300">{desc}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}

export default function NpcsPage() {
  const [activeTab, setActiveTab] = useState('service');
  const [data, setData] = useState<NpcsData | null>(null);
  const [loading, setLoading] = useState(true);
  const { locale } = useLocale();

  useEffect(() => {
    fetch('/api/npcs')
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
        {locale === 'en' ? 'Failed to load NPCs' : 'Erreur de chargement'}
      </div>
    );
  }

  const tabsWithCounts = [
    { id: 'service', name_fr: 'Services', name_en: 'Services', icon: '🏪', count: data.service_npcs.length },
    { id: 'quest', name_fr: 'Quetes', name_en: 'Quests', icon: '📜', count: data.quest_npcs.length },
    { id: 'class_master', name_fr: 'Maitres de Classe', name_en: 'Class Masters', icon: '⚔️', count: data.class_masters.length },
    { id: 'arena', name_fr: 'Arene', name_en: 'Arena', icon: '🏟️', count: data.arena_npcs.length },
    { id: 'ambient', name_fr: 'Ambiance', name_en: 'Ambient', icon: '🌆', count: data.ambient_npcs.length },
    { id: 'catalog', name_fr: 'Catalogue Services', name_en: 'Services Catalog', icon: '📚', count: Object.keys(data.services_catalog).length },
  ];

  return (
    <div className="flex h-[calc(100vh-4rem)] overflow-hidden">
      {/* Secondary Sidebar */}
      <aside className="w-64 border-r border-zinc-800 overflow-y-auto bg-zinc-900/50">
        <div className="p-4 border-b border-zinc-800">
          <h2 className="text-lg font-semibold">{locale === 'en' ? 'NPCs' : 'NPCs'}</h2>
          <p className="text-xs text-zinc-500">
            {data._summary.total_npcs} {locale === 'en' ? 'total NPCs' : 'NPCs au total'}
          </p>
        </div>
        <nav className="p-2">
          {tabsWithCounts.map((tab) => (
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
                <div className="text-xs text-zinc-500">{tab.count} {locale === 'en' ? 'entries' : 'entrees'}</div>
              </div>
            </button>
          ))}
        </nav>
      </aside>

      {/* Main Content */}
      <main className="flex-1 overflow-y-auto">
        <div className="p-4 md:p-6 lg:p-8">
          {activeTab === 'service' && <ServiceNpcsTab data={data} />}
          {activeTab === 'quest' && <QuestNpcsTab data={data} />}
          {activeTab === 'class_master' && <ClassMastersTab data={data} />}
          {activeTab === 'arena' && <ArenaNpcsTab data={data} />}
          {activeTab === 'ambient' && <AmbientNpcsTab data={data} />}
          {activeTab === 'catalog' && <ServicesCatalogTab data={data} />}
        </div>
      </main>
    </div>
  );
}
