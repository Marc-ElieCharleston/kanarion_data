import { Tabs, TabsList, TabsTrigger, TabsContent } from '@/components/ui/tabs';

interface Tab {
  value: string;
  label: string;
  content: React.ReactNode;
}

interface TabsGroupProps {
  tabs: Tab[];
  defaultValue?: string;
  className?: string;
}

export function TabsGroup({ tabs, defaultValue, className }: TabsGroupProps) {
  return (
    <Tabs defaultValue={defaultValue || tabs[0].value} className={className}>
      <TabsList>
        {tabs.map(tab => (
          <TabsTrigger key={tab.value} value={tab.value}>
            {tab.label}
          </TabsTrigger>
        ))}
      </TabsList>
      {tabs.map(tab => (
        <TabsContent key={tab.value} value={tab.value}>
          {tab.content}
        </TabsContent>
      ))}
    </Tabs>
  );
}
