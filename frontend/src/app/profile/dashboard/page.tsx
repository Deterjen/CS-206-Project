"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { useAuthContext } from "@/providers/AuthProvider";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Progress } from "@/components/ui/progress";
import {
  getRecommendations,
  type RecommendationRequest,
} from "@/api/apiClient";
import { profileService } from "@/api/services";

export default function ProfileDashboardPage() {
  const router = useRouter();
  const { user, isLoading: authLoading } = useAuthContext();
  const [profileData, setProfileData] = useState<RecommendationRequest | null>(
    null
  );
  const [profileCompletion, setProfileCompletion] = useState(0);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    // First check if user is logged in
    if (!authLoading && !user) {
      // If not logged in, redirect to auth page
      router.push("/auth");
      return;
    }

    const fetchProfileData = async () => {
      if (user?.username) {
        setIsLoading(true);

        try {
          // Try to get the profile data from the API
          const response = await profileService.getProfile(user.username);
          const apiProfileData = response.data.profile;

          if (apiProfileData) {
            // Format API data for dashboard display
            const formattedData = {
              preferred_fields: apiProfileData.preferred_fields || [],
              learning_style: apiProfileData.learning_style || "",
              career_goals: apiProfileData.career_goals.join(", "),
              further_education: apiProfileData.further_education || "",
              culture_importance: apiProfileData.culture_importance || 0,
              interested_activities: apiProfileData.interested_activities || [],
              weekly_extracurricular_hours:
                apiProfileData.weekly_extracurricular_hours || "",
              passionate_activities: apiProfileData.passionate_activities.join(", "),
              internship_importance: apiProfileData.internship_importance || 0,
              leadership_interest: apiProfileData.leadership_interest || false,
              alumni_network_value: apiProfileData.alumni_network_value || 0,
              affordability_importance:
                apiProfileData.affordability_importance || 0,
              yearly_budget: apiProfileData.yearly_budget || 0,
              financial_aid_interest:
                apiProfileData.financial_aid_interest || false,
              preferred_region: apiProfileData.preferred_region || "",
              preferred_setting: apiProfileData.preferred_setting || "",
              preferred_living_arrangement:
                apiProfileData.preferred_living_arrangement || "",
              important_facilities: apiProfileData.important_facilities || [],
              modern_amenities_importance:
                apiProfileData.modern_amenities_importance || 0,
              ranking_importance: apiProfileData.ranking_importance || 0,
              alumni_testimonial_influence:
                apiProfileData.alumni_testimonial_influence || 0,
              important_selection_factors:
                apiProfileData.important_selection_factors || [],
              personality_traits: apiProfileData.personality_traits || [],
              preferred_student_population:
                apiProfileData.preferred_student_population || "",
              lifestyle_preferences: apiProfileData.lifestyle_preferences || "",
            };

            // Set the profile data
            setProfileData(formattedData);

            // Calculate profile completion using the dashboard's existing logic
            const requiredFields = [
              // Step 1 - Academic interests
              Boolean(formattedData.preferred_fields?.length),
              Boolean(formattedData.learning_style),

              // Step 2 - Extracurriculars
              Boolean(formattedData.interested_activities?.length),

              // Step 3 - Professional development
              formattedData.internship_importance > 0,

              // Step 4 - Affordability
              formattedData.affordability_importance > 0,

              // Step 5 - Location
              Boolean(formattedData.preferred_region),

              // Step 6 - Campus
              Boolean(formattedData.important_facilities?.length),

              // Step 7 - Prestige
              formattedData.ranking_importance > 0,

              // Step 8 - Lifestyle
              Boolean(formattedData.personality_traits?.length),
            ];

            const filledFields = requiredFields.filter(Boolean).length;
            const completionPercentage =
              (filledFields / requiredFields.length) * 100;
            setProfileCompletion(completionPercentage);

            // Store in localStorage for consistency
            localStorage.setItem(
              "profileData",
              JSON.parse(JSON.stringify(formattedData))
            );

            setIsLoading(false);
            return;
          }
        } catch (error) {
          console.error("Error fetching profile from API:", error);
          // If there's an error parsing the data, redirect to setup
          router.push("/profile/setup");
          return;
        }
      } else {
        // No profile data exists for this user, redirect to setup
        router.push("/profile/setup");
        return;
      }
      setIsLoading(false);
    };

    fetchProfileData();
  }, [user, authLoading, router]);

  const handleFindRecommendations = async () => {
    try {
      if (!user?.username) {
        throw new Error("User not authenticated");
      }

      setIsLoading(true);
      // Get recommendations with 3 results
      await getRecommendations(user.username, 3);
      // Navigate to blurred recommendations page instead
      router.push("/recommendations-blurred");
    } catch (error) {
      console.error("Error getting recommendations:", error);
      alert("Failed to get recommendations. Please try again.");
    } finally {
      setIsLoading(false);
    }
  };

  // Show loading state
  if (isLoading || authLoading) {
    return (
      <div className="container flex h-screen items-center justify-center">
        <div className="text-center">
          <h1 className="text-2xl font-bold mb-4">Loading your profile...</h1>
        </div>
      </div>
    );
  }

  // Show login prompt if not logged in
  if (!user) {
    return (
      <div className="container flex h-screen items-center justify-center">
        <div className="text-center">
          <h1 className="text-2xl font-bold mb-4">
            Please log in to view your profile
          </h1>
          <Button asChild>
            <a href="/auth">Log In</a>
          </Button>
        </div>
      </div>
    );
  }

  return (
    <div className="container py-8">
      <div className="grid grid-cols-1 md:grid-cols-2 gap-8 px-8">
        {/* Profile Overview */}
        <Card>
          <CardHeader>
            <CardTitle>Profile Overview</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              <div>
                <h3 className="text-sm font-medium text-muted-foreground">
                  Username
                </h3>
                <p className="text-lg">{user.username}</p>
              </div>
              <div>
                <h3 className="text-sm font-medium text-muted-foreground">
                  Email
                </h3>
                <p className="text-lg">{user.email}</p>
              </div>
              <div>
                <h3 className="text-sm font-medium text-muted-foreground">
                  Profile Completion
                </h3>
                <Progress value={profileCompletion} className="mt-2" />
                <p className="text-sm text-muted-foreground mt-1">
                  {Math.round(profileCompletion)}% complete
                </p>
              </div>
            </div>
          </CardContent>
        </Card>

        {/* Preferences */}
        <Card>
          <CardHeader>
            <CardTitle>Your Preferences</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              <div>
                <h3 className="text-sm font-medium text-muted-foreground">
                  Academic Interests
                </h3>
                <p className="text-lg">
                  {profileData?.preferred_fields?.join(", ") || "Not specified"}
                </p>
              </div>
              <div>
                <h3 className="text-sm font-medium text-muted-foreground">
                  Career Goals
                </h3>
                <p className="text-lg">
                  {profileData?.career_goals || "Not specified"}
                </p>
              </div>
              <div>
                <h3 className="text-sm font-medium text-muted-foreground">
                  Location Preferences
                </h3>
                <p className="text-lg">
                  {profileData?.preferred_region || "Not specified"}
                </p>
              </div>
              <div>
                <h3 className="text-sm font-medium text-muted-foreground">
                  Budget
                </h3>
                <p className="text-lg">
                  {profileData?.yearly_budget
                    ? `$${profileData.yearly_budget.toLocaleString()}`
                    : "Not specified"}
                </p>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>

      <div className="mt-8 px-8 flex gap-4">
        <Button asChild variant="outline">
          <a href="/profile/setup">Edit Profile</a>
        </Button>
        <Button
          onClick={handleFindRecommendations}
          disabled={isLoading || profileCompletion < 80}
        >
          {isLoading ? "Getting Recommendations..." : "Find Recommendations"}
        </Button>
      </div>
    </div>
  );
}
