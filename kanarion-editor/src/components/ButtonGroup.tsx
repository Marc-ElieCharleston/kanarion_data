import { Button } from '@/components/ui/button';

interface ButtonOption {
  value: string;
  label: string;
  count?: number;
}

interface ButtonGroupProps {
  options: ButtonOption[];
  value: string;
  onChange: (value: string) => void;
  variant?: 'default' | 'outline';
}

export function ButtonGroup({ options, value, onChange, variant = 'outline' }: ButtonGroupProps) {
  return (
    <div className="flex flex-wrap gap-2">
      {options.map(option => (
        <Button
          key={option.value}
          variant={value === option.value ? 'default' : variant}
          onClick={() => onChange(option.value)}
          size="sm"
        >
          {option.label}
          {option.count !== undefined && (
            <span className="ml-1.5 text-xs opacity-70">({option.count})</span>
          )}
        </Button>
      ))}
    </div>
  );
}
