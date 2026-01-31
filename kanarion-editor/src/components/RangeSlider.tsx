import { Slider } from '@/components/ui/slider';
import { Label } from '@/components/ui/label';

interface RangeSliderProps {
  value: number;
  onChange: (value: number) => void;
  min: number;
  max: number;
  label: string;
  showValue?: boolean;
}

export function RangeSlider({ value, onChange, min, max, label, showValue = true }: RangeSliderProps) {
  return (
    <div className="space-y-2">
      <div className="flex justify-between items-center">
        <Label>{label}</Label>
        {showValue && <span className="text-sm text-zinc-400">{value}</span>}
      </div>
      <Slider
        value={[value]}
        onValueChange={(vals) => onChange(vals[0])}
        min={min}
        max={max}
        step={1}
      />
    </div>
  );
}
