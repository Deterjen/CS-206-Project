// src/types/index.ts
import { UserProfile, University } from '../../supabase/functions/shared/types'


// API Request Types
export interface SurveyRequest {
    surveyResponse: UserProfile;
}

export interface EmbeddingRequest {
    type: 'user' | 'university';
    data: UserProfile | University;
}

export interface RecommendationRequest {
    userProfile: UserProfile;
    limit?: number;
    minSatisfaction?: number;
}

// API Response Types
export interface ApiResponse {
    success: boolean;
    error?: string;
}

export interface EmbeddingResponse extends ApiResponse {
    embedding?: number[];
}

export interface ProcessDataResponse extends ApiResponse {
    data?: UserProfile;
    recommendations?: UniversityRecommendation[];
}

export interface UniversityAggregationResponse extends ApiResponse {
    universities?: University[];
}

export interface RecommendationResponse extends ApiResponse {
    recommendations?: UniversityRecommendation[];
}

// Recommendation Types
export interface UniversityRecommendation {
    university_name: string;
    similarity_score: number;
    average_satisfaction: number;
    selectionCriteria: string[];
    universityTags: string[];
}

// Test Types
export interface TestResult {
    name: string;
    success: boolean;
    error?: string;
    details?: any;
}

// CSV Types
export interface CSVSurveyResponse {
    age: string;
    gender: string;
    nationality: string;
    qualification: string;
    highSchoolGPA: string;
    university: string;
    selectionCriteria: string;
    consideredOthers: string;
    secondChoice: string;
    satisfaction: string;
    universityTags: string;
    learningStyle: string;
    populationPreference: string;
    campusSetting: string;
    costImportance: string;
    scholarship: string;
    living: string;
    major: string;
    careerGoal: string;
    internshipImportance: string;
    universityInternship: string;
    familyInfluence: string;
    friendInfluence: string;
    socialMediaInfluence: string;
    rankingInfluence: string;
}

// Utility Types
export type NonNullableFields<T> = {
    [P in keyof T]: NonNullable<T[P]>;
};

export type RequiredFields<T> = {
    [P in keyof T]-?: T[P];
};

// Function Types
export type TestFunction = () => Promise<void>;

// Constants
export const VECTOR_DIMENSIONS = 768;

// Error Types
export class ApiError extends Error {
    constructor(
        message: string,
        public statusCode: number = 400,
        public details?: any
    ) {
        super(message);
        this.name = 'ApiError';
    }
}

// Validation Types
export interface ValidationResult {
    isValid: boolean;
    errors?: string[];
}

// Config Types
export interface DatabaseConfig {
    url: string;
    anonKey: string;
    serviceRoleKey: string;
}

export interface AppConfig {
    database: DatabaseConfig;
    vectorDimensions: number;
    minSatisfactionScore: number;
    defaultRecommendationLimit: number;
}