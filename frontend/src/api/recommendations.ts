import api from "./axios";
import { RecommendationResponse } from "@/types";

export const generateRecommendations = async (data: {
  calculation_ids: number[];
  focus_areas?: string[];
}): Promise<RecommendationResponse> => {
  const response = await api.post<RecommendationResponse>("/v1/recommendations/generate", data);
  return response.data;
};
