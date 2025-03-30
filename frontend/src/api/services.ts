import apiClient from "./apiClient";

export interface LoginCredentials {
  username: string;
  password: string;
}

export interface RegisterData {
  username: string;
  email: string;
  password: string;
}

export interface UserUpdateData {
  new_username?: string;
  new_email?: string;
}

export interface RecommendationRequest {
  preferred_fields: string[];
  learning_style: string;
  career_goals: string;
  further_education: string;
  culture_importance: number;
  interested_activities: string[];
  weekly_extracurricular_hours: string;
  passionate_activities: string;
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

export const authService = {
  login: async (credentials: LoginCredentials) => {
    const formData = new FormData();
    formData.append("username", credentials.username);
    formData.append("password", credentials.password);
    return apiClient.post("/token", formData);
  },

  register: async (data: RegisterData) => {
    return apiClient.post("/register/", data);
  },

  updateUser: async (username: string, data: UserUpdateData) => {
    return apiClient.put(`/user/update/${username}`, data);
  },

  deleteUser: async (username: string) => {
    return apiClient.delete(`/user/delete/${username}`);
  },
};

export const recommendationService = {
  saveQuestionnaire: async (username: string, data: RecommendationRequest) => {
    return apiClient.post(`/save_questionaire/${username}`, data);
  },

  generateRecommendations: async (
    username: string,
    numberOfResults: number
  ) => {
    return apiClient.get(`/recommendation/${username}`, {
      params: { number_of_results: numberOfResults },
    });
  },

  getAllRecommendations: async (username: string) => {
    return apiClient.get(`/recommendation/all_details/${username}`);
  },

  getRecommendationDetail: async (
    username: string,
    recommendationId: number
  ) => {
    return apiClient.get(
      `/recommendation/detail/${username}/${recommendationId}`
    );
  },

  getSimilarStudents: async (username: string, recommendationId: number) => {
    return apiClient.get(
      `/recommendation/similar_student/${username}/${recommendationId}`
    );
  },

  getRecommendationJustification: async (
    username: string,
    recommendationId: number
  ) => {
    return apiClient.get(
      `/recommendation/justification/${username}/${recommendationId}`
    );
  },

  getRecommendationDetails: async (username: string, universityId: number) => {
    return apiClient.get(`/recommendation/${username}/details/${universityId}`);
  },

  getRecommendationJustification: async (
    username: string,
    universityId: number
  ) => {
    return apiClient.get(
      `/recommendation/${username}/justification/${universityId}`
    );
  },
};
