"use client";

import axios from "axios";

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    "Content-Type": "application/json",
  },
  withCredentials: true,
});

// Add auth token to requests if it exists
api.interceptors.request.use((config) => {
  const token = localStorage.getItem("token");
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

export interface LoginCredentials {
  username: string;
  password: string;
}

export interface RegisterData extends LoginCredentials {
  email: string;
  fullName: string;
}

export interface AuthResponse {
  token: string;
  user: {
    id: string;
    username: string;
    email: string;
    fullName: string;
  };
}

export const auth = {
  async login(credentials: LoginCredentials): Promise<AuthResponse> {
    const response = await api.post("/api/auth/login", credentials);
    if (response.data.token) {
      localStorage.setItem("token", response.data.token);
    }
    return response.data;
  },

  async register(data: RegisterData): Promise<AuthResponse> {
    const response = await api.post("/api/auth/register", data);
    if (response.data.token) {
      localStorage.setItem("token", response.data.token);
    }
    return response.data;
  },

  async logout() {
    localStorage.removeItem("token");
  },

  async getProfile() {
    const response = await api.get("/api/auth/profile");
    return response.data;
  },
};

export interface University {
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

export const recommendations = {
  async getRecommendations(): Promise<University[]> {
    const response = await api.get("/api/recommendations");
    return response.data.universities;
  },
};

export default api;
