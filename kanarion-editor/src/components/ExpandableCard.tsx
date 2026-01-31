'use client';
import { useState } from 'react';
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/card';
import { ChevronDown } from 'lucide-react';

interface ExpandableCardProps {
  title: string;
  children: React.ReactNode;
  defaultOpen?: boolean;
}

export function ExpandableCard({ title, children, defaultOpen = false }: ExpandableCardProps) {
  const [isOpen, setIsOpen] = useState(defaultOpen);

  return (
    <Card>
      <CardHeader
        className="cursor-pointer hover:bg-zinc-800/50 transition-colors"
        onClick={() => setIsOpen(!isOpen)}
      >
        <CardTitle className="flex justify-between items-center">
          {title}
          <ChevronDown className={`transition-transform ${isOpen ? 'rotate-180' : ''}`} />
        </CardTitle>
      </CardHeader>
      {isOpen && <CardContent>{children}</CardContent>}
    </Card>
  );
}
