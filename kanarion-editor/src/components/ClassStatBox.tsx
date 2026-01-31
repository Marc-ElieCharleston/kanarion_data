import { Card } from '@/components/ui/card';

interface ClassStatBoxProps {
  label: string;
  value: string | number;
  color?: string;
}

export function ClassStatBox({ label, value, color }: ClassStatBoxProps) {
  return (
    <Card className="bg-zinc-900/50 p-1.5 sm:p-2 text-center">
      <div className={`text-base sm:text-lg font-bold ${color || ''}`}>{value}</div>
      <div className="text-[9px] sm:text-[10px] text-zinc-500">{label}</div>
    </Card>
  );
}
