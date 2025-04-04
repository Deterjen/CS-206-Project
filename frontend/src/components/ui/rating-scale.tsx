import { Slider } from "@/components/ui/slider"
import { Label } from "@/components/ui/label"
import { useState, useEffect, useId } from "react"

interface RatingScaleProps {
  value: number;
  onChange: (value: number) => void;
  label: string;
  min?: number;
  max?: number;
  step?: number;
}

export function RatingScale({
  value,
  onChange,
  label,
  min = 1,
  max = 10,
  step = 1,
}: RatingScaleProps) {
  const id = useId();
  // Remove the local state and directly use the value from props
  // This ensures each instance only responds to its own value changes

  const handleChange = (newValue: number[]) => {
    if (newValue[0] !== undefined) {
      onChange(newValue[0]);
    }
  };

  return (
    <div className="space-y-2">
      <Label htmlFor={id}>{label}</Label>
      <div className="flex items-center gap-4">
        <Slider
          id={id}
          value={[value]}
          onValueChange={handleChange}
          min={min}
          max={max}
          step={step}
          className="flex-1"
        />
        <span className="w-8 text-center">{value}</span>
      </div>
    </div>
  );
}
