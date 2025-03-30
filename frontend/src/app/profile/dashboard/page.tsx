"use client"

import { useEffect, useState } from "react"
import { useRouter } from "next/navigation"
import { useAuthContext } from "@/providers/AuthProvider"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Progress } from "@/components/ui/progress"
import { getRecommendations, type RecommendationRequest } from "@/api/apiClient"

export default function ProfileDashboardPage() {
  const router = useRouter()
  const { user, isLoading: authLoading } = useAuthContext()
  const [profileData, setProfileData] = useState<RecommendationRequest | null>(null)
  const [profileCompletion, setProfileCompletion] = useState(0)
  const [isLoading, setIsLoading] = useState(true)

  useEffect(() => {
    // First check if user is logged in
    if (!authLoading && !user) {
      // If not logged in, redirect to auth page
      router.push("/auth")
      return
    }

    // Load profile data from localStorage
    if (user?.username) {
      const userProfileKey = `profileData_${user.username}`
      const savedUserData = localStorage.getItem(userProfileKey)
      
      if (savedUserData) {
        try {
          // We have user-specific data - validate it exists
          JSON.parse(savedUserData)
          
          // Also check if we have the formatted data for recommendations
          const formattedData = localStorage.getItem("profileData")
          if (!formattedData) {
            // If we don't have formatted data but have user data,
            // redirect to setup to complete the process
            router.push("/profile/setup")
            return
          }
          
          // Check if the profile was recently submitted - if so, don't redirect
          const wasSubmitted = localStorage.getItem("profileSubmitted") === "true"
          
          // We have both user data and formatted data
          const recommendationData = JSON.parse(formattedData) as RecommendationRequest
          setProfileData(recommendationData)

          // Calculate completion based on filled fields - with more lenient checks
          const requiredFields = [
            // Step 1 - Academic interests
            Boolean(recommendationData.preferred_fields?.length),
            Boolean(recommendationData.learning_style),
            
            // Step 2 - Extracurriculars
            Boolean(recommendationData.interested_activities?.length),
           
            // Step 3 - Professional development
            recommendationData.internship_importance > 0,
            
            // Step 4 - Affordability
            recommendationData.affordability_importance > 0,
            
            // Step 5 - Location
            Boolean(recommendationData.preferred_region),
            
            // Step 6 - Campus
            Boolean(recommendationData.important_facilities?.length),
            
            // Step 7 - Prestige
            recommendationData.ranking_importance > 0,
            
            // Step 8 - Lifestyle
            Boolean(recommendationData.personality_traits?.length)
          ]

          const filledFields = requiredFields.filter(Boolean).length
          const completionPercentage = (filledFields / requiredFields.length) * 100
          setProfileCompletion(completionPercentage)
          
          // Only redirect for severely incomplete profiles and if not recently submitted
          if (completionPercentage < 70 && !wasSubmitted) {
            // Redirect to profile setup to complete the profile
            router.push("/profile/setup")
            return
          }
          
          // Clear the submitted flag after using it
          if (wasSubmitted) {
            localStorage.removeItem("profileSubmitted")
          }
        } catch (error) {
          console.error("Error parsing profile data:", error)
          // If there's an error parsing the data, redirect to setup
          router.push("/profile/setup")
          return
        }
      } else {
        // No profile data exists for this user, redirect to setup
        router.push("/profile/setup")
        return
      }
    }
    
    setIsLoading(false)
  }, [user, authLoading, router])

  const handleFindRecommendations = async () => {
    try {
      if (!user?.username) {
        throw new Error("User not authenticated")
      }

      setIsLoading(true)
      // Get recommendations with 3 results
      await getRecommendations(user.username, 3)
      // Navigate to blurred recommendations page instead
      router.push("/recommendations-blurred")
    } catch (error) {
      console.error("Error getting recommendations:", error)
      alert("Failed to get recommendations. Please try again.")
    } finally {
      setIsLoading(false)
    }
  }

  // Show loading state
  if (isLoading || authLoading) {
    return (
      <div className="container flex h-screen items-center justify-center">
        <div className="text-center">
          <h1 className="text-2xl font-bold mb-4">Loading your profile...</h1>
        </div>
      </div>
    )
  }

  // Show login prompt if not logged in
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
          disabled={isLoading || profileCompletion < 80}
        >
          {isLoading ? "Getting Recommendations..." : "Find Recommendations"}
        </Button>
      </div>
    </div>
  )
}