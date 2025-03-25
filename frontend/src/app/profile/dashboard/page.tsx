"use client"

import { useState, useEffect } from "react"
import { useRouter } from "next/navigation"
import { useAuthContext } from "@/providers/AuthProvider"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Progress } from "@/components/ui/progress"
import { getRecommendations, type RecommendationRequest } from "@/api/apiClient"

export default function ProfileDashboardPage() {
  const router = useRouter()
  const { user } = useAuthContext()
  const [profileData, setProfileData] = useState<RecommendationRequest | null>(null)
  const [profileCompletion, setProfileCompletion] = useState(0)
  const [isLoading, setIsLoading] = useState(false)

  useEffect(() => {
    // Load profile data from localStorage
    const savedData = localStorage.getItem("profileData")
    if (savedData) {
      const data = JSON.parse(savedData) as RecommendationRequest
      setProfileData(data)

      // Calculate completion based on filled fields
      const requiredFields = [
        data.preferred_fields?.length > 0,
        data.learning_style,
        data.career_goals?.length > 0,
        data.further_education,
        data.interested_activities?.length > 0,
        data.weekly_extracurricular_hours > 0,
        data.passionate_activities?.length > 0,
        data.internship_importance > 0,
        data.leadership_interest !== undefined,
        data.alumni_network_value > 0,
        data.affordability_importance > 0,
        data.yearly_budget > 0,
        data.financial_aid_interest !== undefined,
        data.preferred_region,
        data.preferred_setting,
        data.preferred_living_arrangement,
        data.important_facilities?.length > 0,
        data.modern_amenities_importance > 0,
        data.ranking_importance > 0,
        data.alumni_testimonial_influence > 0,
        data.important_selection_factors?.length > 0,
        data.personality_traits?.length > 0,
        data.preferred_student_population,
        data.lifestyle_preferences
      ]

      const filledFields = requiredFields.filter(Boolean).length
      setProfileCompletion((filledFields / requiredFields.length) * 100)
    }
  }, [])

  const handleFindRecommendations = async () => {
    try {
      if (!user?.username) {
        throw new Error("User not authenticated")
      }

      setIsLoading(true)
      // Get recommendations with 3 results
      await getRecommendations(user.username, 3)
      // Navigate to recommendations page
      router.push("/recommendations")
    } catch (error) {
      console.error("Error getting recommendations:", error)
      alert("Failed to get recommendations. Please try again.")
    } finally {
      setIsLoading(false)
    }
  }

  if (!user) {
    return (
      <div className="container flex h-screen items-center justify-center">
        <div className="text-center">
          <h1 className="text-2xl font-bold mb-4">Please log in to view your profile</h1>
          <Button asChild>
            <a href="/auth">Log In</a>
          </Button>
        </div>
      </div>
    )
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
                <h3 className="text-sm font-medium text-muted-foreground">Username</h3>
                <p className="text-lg">{user.username}</p>
              </div>
              <div>
                <h3 className="text-sm font-medium text-muted-foreground">Email</h3>
                <p className="text-lg">{user.email}</p>
              </div>
              <div>
                <h3 className="text-sm font-medium text-muted-foreground">Profile Completion</h3>
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
                <h3 className="text-sm font-medium text-muted-foreground">Academic Interests</h3>
                <p className="text-lg">
                  {profileData?.preferred_fields?.join(", ") || "Not specified"}
                </p>
              </div>
              <div>
                <h3 className="text-sm font-medium text-muted-foreground">Career Goals</h3>
                <p className="text-lg">
                  {profileData?.career_goals?.join(", ") || "Not specified"}
                </p>
              </div>
              <div>
                <h3 className="text-sm font-medium text-muted-foreground">Location Preferences</h3>
                <p className="text-lg">
                  {profileData?.preferred_region || "Not specified"}
                </p>
              </div>
              <div>
                <h3 className="text-sm font-medium text-muted-foreground">Budget</h3>
                <p className="text-lg">
                  {profileData?.yearly_budget ? `$${profileData.yearly_budget.toLocaleString()}` : "Not specified"}
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
          disabled={isLoading || profileCompletion < 100}
        >
          {isLoading ? "Getting Recommendations..." : "Find Recommendations"}
        </Button>
      </div>
    </div>
  )
}