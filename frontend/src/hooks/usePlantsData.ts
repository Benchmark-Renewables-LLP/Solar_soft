
import { useState, useEffect } from 'react';
import { useQuery } from '@tanstack/react-query';
import { apiClient } from '@/services/api';
import { Plant, Device } from '@/components/plants/PlantsOverview';

export const usePlantsData = () => {
  const { data: plants = [], isLoading: plantsLoading, error: plantsError } = useQuery({
    queryKey: ['plants'],
    queryFn: () => apiClient.getPlants(),
    staleTime: 5 * 60 * 1000, // 5 minutes
  });

  const { data: devices = [], isLoading: devicesLoading, error: devicesError } = useQuery({
    queryKey: ['devices'],
    queryFn: () => apiClient.getDevices(),
    staleTime: 5 * 60 * 1000, // 5 minutes
  });

  return {
    plants: plants as Plant[],
    devices: devices as Device[],
    isLoading: plantsLoading || devicesLoading,
    error: plantsError || devicesError,
  };
};
