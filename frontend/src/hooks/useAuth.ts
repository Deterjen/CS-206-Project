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
    const email = localStorage.getItem("email");
    const preferences = localStorage.getItem("preferences");

    if (token && username && email) {
      setUser({
        username,
        email,
        token,
        preferences: preferences ? JSON.parse(preferences) : undefined,
      });
    }

    setIsLoading(false);
  }, []);

  const login = (userData: User & { token: string }) => {
    localStorage.setItem("token", userData.token);
    localStorage.setItem("username", userData.username);
    localStorage.setItem("email", userData.email);
    if (userData.preferences) {
      localStorage.setItem("preferences", JSON.stringify(userData.preferences));
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
