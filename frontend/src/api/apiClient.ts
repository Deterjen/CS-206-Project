import axios, { AxiosInstance, InternalAxiosRequestConfig } from "axios";

const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://127.0.0.1:8000";

const apiClient: AxiosInstance = axios.create({
  baseURL: API_URL,
  headers: {
    "Content-Type": "application/json",
  },
});

apiClient.interceptors.request.use((config: InternalAxiosRequestConfig) => {
  const token = localStorage.getItem("token");
  if (token) {
    config.headers.set("Authorization", `Bearer ${token}`);
  }
  return config;
});

// Types for the questionnaire data
export interface RecommendationRequest {
  algorithm?: string;
  num_results?: number;
  preferred_fields: string[];
  learning_style: string;
  career_goals: string[];
  further_education: string;
  culture_importance: number;
  interested_activities: string[];
  weekly_extracurricular_hours: number;
  passionate_activities: string[];
  internship_importance: number;
  leadership_interest: boolean;
  alumni_network_value: number;
  affordability_importance: number;
  yearly_budget: number;
  financial_aid_interest: boolean;
  preferred_region: string;
  preferred_setting: string;
  preferred_living_arrangement: string;
  important_facilities: string[];
  modern_amenities_importance: number;
  ranking_importance: number;
  alumni_testimonial_influence: number;
  important_selection_factors: string[];
  personality_traits: string[];
  preferred_student_population: string;
  lifestyle_preferences: string;
}

// Types for the recommendation response
export interface RecommendationResponse {
  id: number;
  university_id: string;
  overall_score: number;
}

export interface UniversityDetails {
  university_name: string;
  location: string;
  logo_url: string;
  images: string[];
  benefits: string[];
  drawbacks: string[];
  suitability_reasons: string[];
}

export interface AllRecommendationDetailsResponse {
  [key: string]: UniversityDetails;
}

// API endpoints
export const saveQuestionnaire = async (
  username: string,
  data: RecommendationRequest
) => {
  return apiClient.post(`/save_questionaire/${username}`, data);
};

export const getRecommendations = async (
  username: string,
  numResults: number = 5
) => {
  return apiClient.get<RecommendationResponse[]>(
    `/recommendation/${username}`,
    {
      params: { number_of_results: numResults },
    }
  );
};

export const getRecommendationDetails = async (
  username: string,
  recommendationId: number
) => {
  return apiClient.get(
    `/recommendation/detail/${username}/${recommendationId}`
  );
};

export const getRecommendationJustification = async (
  username: string,
  recommendationId: number
) => {
  return apiClient.get(
    `/recommendation/justification/${username}/${recommendationId}`
  );
};

export const getSimilarStudents = async (
  username: string,
  recommendationId: number
) => {
  return apiClient.get(
    `/recommendation/similar_student/${username}/${recommendationId}`
  );
};

export const getAllRecommendationDetails = async (username: string) => {
  return apiClient.get<AllRecommendationDetailsResponse>(
    `/recommendation/all_details/${username}`
  );
};

export default apiClient;
