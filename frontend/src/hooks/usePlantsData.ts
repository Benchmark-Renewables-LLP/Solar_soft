
import { useState, useEffect } from 'react';
import { useQuery } from '@tanstack/react-query';
import { apiClient } from '@/services/api';
import { Plant } from '@/components/plants/PlantsOverview';
import { Device } from '@/types/device';

export const usePlantsData = (userType = 'demo') => {
  const { data: plants = [], isLoading: plantsLoading, error: plantsError } = useQuery({
    queryKey: ['plants', userType],
    queryFn: () => apiClient.getPlants(userType),
    staleTime: 5 * 60 * 1000, // 5 minutes
  });

  const { data: devices = [], isLoading: devicesLoading, error: devicesError } = useQuery({
    queryKey: ['devices', userType],
    queryFn: () => apiClient.getDevices(userType),
    staleTime: 5 * 60 * 1000, // 5 minutes
  });

  return {
    plants: plants as Plant[],
    devices: devices as Device[],
    isLoading: plantsLoading || devicesLoading,
    error: plantsError || devicesError,
  };
};
