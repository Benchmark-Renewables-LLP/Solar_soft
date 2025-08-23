
import React from 'react';
import { Button } from '@/components/ui/button';

export type TimeRange = '1h' | '24h' | '7d' | '30d';

interface TimeRangeSelectorProps {
  selectedRange: TimeRange;
  onRangeChange: (range: TimeRange) => void;
}

export const TimeRangeSelector: React.FC<TimeRangeSelectorProps> = ({ selectedRange, onRangeChange }) => {
  const ranges: { value: TimeRange; label: string }[] = [
    { value: '1h', label: 'Last Hour' },
    { value: '24h', label: '24 Hours' },
    { value: '7d', label: '7 Days' },
    { value: '30d', label: '30 Days' }
  ];

  return (
    <div className="flex space-x-2">
      {ranges.map((range) => (
        <Button
          key={range.value}
          onClick={() => onRangeChange(range.value)}
          variant={selectedRange === range.value ? 'default' : 'outline'}
          size="sm"
          className={selectedRange === range.value ? 'bg-gradient-to-r from-blue-500 to-cyan-500' : ''}
        >
          {range.label}
        </Button>
      ))}
    </div>
  );
};
