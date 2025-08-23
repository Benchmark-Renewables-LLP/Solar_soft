
import { useQuery } from '@tanstack/react-query';
import { apiClient } from '@/services/api';
import { TimeRange } from '@/types/device';

export const useDeviceTimeSeriesData = (deviceId: string, timeRange: TimeRange) => {
  const metrics = ['panel_voltages', 'input_currents', 'output_currents', 'power_generation'];

  const { data, isLoading, error } = useQuery({
    queryKey: ['device-timeseries', deviceId, timeRange],
    queryFn: () => apiClient.getMultipleTimeSeriesData(deviceId, metrics, timeRange),
    enabled: !!deviceId,
    refetchInterval: timeRange === '1h' ? 30000 : 60000, // Real-time updates for 1h view
    staleTime: timeRange === '1h' ? 30000 : 5 * 60 * 1000,
  });

  return {
    timeSeriesData: data || [],
    isLoading,
    error,
  };
};
