// supabase/functions/shared/types.ts

export interface UserProfile {
    id?: number;
    age: number;
    gender: string;
    nationality: string;
    qualification: string;
    high_school_gpa: number;
    university: string;
    major: string;
    selection_criteria: string[];
    considered_others: boolean;
    second_choice: string;
    satisfaction: number;
    university_tags: string[];
    learning_style: string;
    population_preference: string;
    campus_setting: string;
    cost_importance: number;
    scholarship: boolean;
    living: string;
    career_goal: string;
    internship_importance: number;
    university_internship: boolean;
    family_influence: number;
    friend_influence: number;
    social_media_influence: number;
    ranking_influence: number;
    user_embedding?: number[];
    created_at?: string;
  }
  
  export interface University {
    id?: number;
    university_name: string;
    selection_criteria: string[];
    average_satisfaction: number;
    university_tags: string[];
    university_embedding?: number[];
    created_at?: string;
  }
  
  export interface ApiResponse {
    success: boolean;
    error?: string;
  }
  
  export interface EmbeddingResponse extends ApiResponse {
    embedding?: number[];
  }
  
  export interface UniversityRecommendation {
    university_name: string;
    similarity_score: number;
    average_satisfaction: number;
    selection_criteria: string[];
    university_tags: string[];
  }