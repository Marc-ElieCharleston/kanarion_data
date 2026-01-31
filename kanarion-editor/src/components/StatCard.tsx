import Link from 'next/link';
import { Card, CardContent } from '@/components/ui/card';

interface StatCardProps {
  label: string;
  value: string;
  href: string;
  icon: string;
}

export function StatCard({ label, value, href, icon }: StatCardProps) {
  return (
    <Link href={href}>
      <Card className="hover:border-zinc-600 transition-colors cursor-pointer h-full">
        <CardContent className="p-4">
          <div className="text-2xl mb-2">{icon}</div>
          <div className="text-2xl font-bold text-white">{value}</div>
          <div className="text-sm text-zinc-500">{label}</div>
        </CardContent>
      </Card>
    </Link>
  );
}
