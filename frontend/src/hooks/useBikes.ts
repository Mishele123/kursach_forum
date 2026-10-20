import { useState, useEffect } from 'react';
import { bikesApi } from '../services/api';
import type { Bike, CreateBikeDto } from '../types';

export const useBikes = () => {
  const [bikes, setBikes] = useState<Bike[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchBikes = async () => {
    try {
      setIsLoading(true);
      const data = await bikesApi.getMyBikes();
      setBikes(data);
      setError(null);
    } catch (err) {
      setError('Не удалось загрузить велосипеды');
      console.error('Failed to fetch bikes:', err);
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    fetchBikes();
  }, []);

  const createBike = async (bikeData: CreateBikeDto): Promise<Bike | null> => {
    try {
      const newBike = await bikesApi.createBike(bikeData);
      setBikes((prev) => [...prev, newBike]);
      return newBike;
    } catch (err) {
      console.error('Failed to create bike:', err);
      throw err;
    }
  };

  return {
    bikes,
    isLoading,
    error,
    refetch: fetchBikes,
    createBike,
  };
};
