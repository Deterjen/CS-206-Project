import { useState, useEffect } from "react";

interface UserPreferences {
  academicInterests?: string;
  careerGoals?: string;
  locationPreferences?: string;
  budget?: string;
}

interface User {
  username: string;
  email: string;
  preferences?: UserPreferences;
  token?: string;
}

export function useAuth() {
  const [user, setUser] = useState<User | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    // Check if user is logged in
    const token = localStorage.getItem("token");
    const username = localStorage.getItem("username");
    const email = localStorage.getItem("email") || ""; // Make email optional
    const preferencesStr = localStorage.getItem("preferences");

    if (token && username) {
      // Only require token and username
      let preferences: UserPreferences | undefined;
      try {
        preferences = preferencesStr ? JSON.parse(preferencesStr) : undefined;
      } catch (error) {
        console.error("Error parsing preferences:", error);
        preferences = undefined;
      }

      setUser({
        username,
        email,
        token,
        preferences,
      });
    }

    setIsLoading(false);
  }, []);

  const login = (userData: User & { token: string }) => {
    localStorage.setItem("token", userData.token);
    localStorage.setItem("username", userData.username);
    localStorage.setItem("email", userData.email || ""); // Handle empty email
    if (userData.preferences) {
      localStorage.setItem("preferences", JSON.stringify(userData.preferences));
    } else {
      localStorage.removeItem("preferences"); // Remove if no preferences
    }
    setUser(userData);
  };

  const logout = () => {
    localStorage.removeItem("token");
    localStorage.removeItem("username");
    localStorage.removeItem("email");
    localStorage.removeItem("preferences");
    setUser(null);
  };

  return {
    user,
    isLoading,
    login,
    logout,
  };
}
