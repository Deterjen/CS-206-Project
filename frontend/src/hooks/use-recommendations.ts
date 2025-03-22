"use client";

import { useQuery } from "@tanstack/react-query";
import { getRecommendations } from "@/lib/api";

interface University {
  id: string;
  name: string;
  location: string;
  logo: string;
  matchScore: number;
  images: string[];
  benefits: string[];
  drawbacks: string[];
  suitabilityReasons: string[];
}

interface RecommendationsResponse {
  universities: University[];
}

export const useRecommendations = () => {
  return useQuery<RecommendationsResponse>({
    queryKey: ["recommendations"],
    queryFn: getRecommendations,
  });
};
