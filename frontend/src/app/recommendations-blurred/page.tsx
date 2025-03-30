"use client"

import { useEffect, useState } from "react"
import { useRouter } from "next/navigation"
import { useToast } from "@/components/ui/use-toast"
import { getRecommendations, getRecommendationDetails, getRecommendationJustification } from "@/api/apiClient"
import { useAuthContext } from "@/providers/AuthProvider"
import { Button } from "@/components/ui/button"
import dynamic from "next/dynamic"

// Dynamically import the payment popup component
const PaymentPopup = dynamic(() => import("@/components/payment"), { ssr: false })

interface University {
  id: string
  name: string
  location: string
  logo: string
  match_score: number
  images: string[]
  benefits: string[]
  drawbacks: string[]
  suitabilityReasons: string[]
  hasLogoFallback?: boolean
  hasImageFallback?: boolean
}

export default function RecommendationsBlurredPage() {
  const router = useRouter()
  const { user, isLoading: isAuthLoading } = useAuthContext()
  const { toast } = useToast()
  const [universities, setUniversities] = useState<University[]>([])
  const [selectedUniversity, setSelectedUniversity] = useState<University | null>(null)
  const [isLoading, setIsLoading] = useState(false)
  const [hasAttemptedLoad, setHasAttemptedLoad] = useState(false)
  const [isPaymentOpen, setIsPaymentOpen] = useState(false)

  const loadRecommendations = async () => {
    if (!user?.username) {
      if (!isAuthLoading && hasAttemptedLoad) {
        toast({
          title: "Error",
          description: "Please log in to view recommendations",
          variant: "destructive",
        })
        router.push('/auth')
      }
      return
    }

    setIsLoading(true)
    try {
      // Get recommendations first
      const response = await getRecommendations(user.username, 5)
      if (!response.data) {
        throw new Error("No recommendations data received")
      }
      
      const recommendations = response.data
      
      // Fetch details for each recommendation
      const universitiesWithDetails = await Promise.all(
        recommendations.map(async (rec) => {
          try {
            // Get both details and justification
            const [detailsResponse, justificationResponse] = await Promise.all([
              getRecommendationDetails(user.username, rec.id),
              getRecommendationJustification(user.username, rec.id)
            ])
            
            const details = detailsResponse.data || {}
            const justification = justificationResponse.data || {}
            
            // Extract university details
            const universityDetails = details.university || {}
            
            // Extract justification data
            let benefits = []
            let drawbacks = []
            let suitabilityReasons = []
            
            // Handle case where the response might be nested
            const justData = justification.data || justification
            
            // Process benefits (Pros)
            if (Array.isArray(justData.Pros)) {
              benefits = justData.Pros
            } else if (justData.Pros) {
              benefits = [justData.Pros]
            } else if (Array.isArray(justData.pros)) {
              benefits = justData.pros
            } else if (justData.pros) {
              benefits = [justData.pros]
            }
            
            // Process drawbacks (Cons)
            if (Array.isArray(justData.Cons)) {
              drawbacks = justData.Cons
            } else if (justData.Cons) {
              drawbacks = [justData.Cons]
            } else if (Array.isArray(justData.cons)) {
              drawbacks = justData.cons
            } else if (justData.cons) {
              drawbacks = [justData.cons]
            }
            
            // Process suitability reasons (Conclusion)
            if (Array.isArray(justData.Conclusion)) {
              suitabilityReasons = justData.Conclusion
            } else if (justData.Conclusion) {
              suitabilityReasons = [justData.Conclusion]
            } else if (Array.isArray(justData.conclusion)) {
              suitabilityReasons = justData.conclusion
            } else if (justData.conclusion) {
              suitabilityReasons = [justData.conclusion]
            }
            
            // Ensure we have arrays
            const finalBenefits = Array.isArray(benefits) ? benefits : []
            const finalDrawbacks = Array.isArray(drawbacks) ? drawbacks : []
            const finalSuitabilityReasons = Array.isArray(suitabilityReasons) ? suitabilityReasons : []
            
            return {
              id: rec.id.toString(),
              name: universityDetails.name || "Unknown University",
              location: universityDetails.location || "Location not specified",
              logo: universityDetails.logo_url || "/placeholder-logo.svg",
              match_score: rec.overall_score * 100, // Convert to percentage
              images: Array.isArray(universityDetails.images) ? universityDetails.images : [],
              benefits: finalBenefits,
              drawbacks: finalDrawbacks,
              suitabilityReasons: finalSuitabilityReasons,
              hasLogoFallback: false,
              hasImageFallback: false
            }
          } catch (error) {
            console.error(`Error fetching details for university ${rec.university_id}:`, error)
            return {
              id: rec.id.toString(),
              name: "Unknown University",
              location: "Location not specified",
              logo: "/placeholder-logo.svg",
              match_score: rec.overall_score * 100,
              images: [],
              benefits: [],
              drawbacks: [],
              suitabilityReasons: [],
              hasLogoFallback: true,
              hasImageFallback: true
            }
          }
        })
      )
      
      setUniversities(universitiesWithDetails)
      if (universitiesWithDetails.length > 0) {
        setSelectedUniversity(universitiesWithDetails[0])
      } else {
        toast({
          title: "No Recommendations",
          description: "No university recommendations found. Please try again.",
          variant: "destructive",
        })
      }
    } catch (err) {
      console.error("Error loading recommendations:", err)
      toast({
        title: "Error",
        description: "Failed to load recommendations. Please try again.",
        variant: "destructive",
      })
    } finally {
      setIsLoading(false)
      setHasAttemptedLoad(true)
    }
  }

  useEffect(() => {
    if (!isAuthLoading) {
      if (user?.username) {
        loadRecommendations()
      } else if (hasAttemptedLoad) {
        router.push('/auth')
      }
    }
  }, [user?.username, isAuthLoading])

  const handleSelectPlan = (plan: "quarterly" | "annual" | null) => {
    setIsPaymentOpen(false)
    if (plan) {
      // Record subscription choice
      localStorage.setItem("subscriptionPlan", plan)
      // Navigate to full recommendations
      router.push("/recommendations")
    }
  }

  const handleUniversityClick = (university: University, index: number) => {
    // For top 3, show payment popup
    if (index < 3) {
      setIsPaymentOpen(true)
    } else {
      // For others, just select them
      setSelectedUniversity(university)
    }
  }

  // Show loading spinner while auth is initializing or during first load
  if (isAuthLoading || (!hasAttemptedLoad && !user)) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-primary"></div>
      </div>
    )
  }

  // Only show login prompt if we're sure auth has finished and we've tried loading
  if (!user && hasAttemptedLoad) {
    return (
      <div className="container flex h-screen items-center justify-center">
          <div className="text-center">
          <h1 className="text-2xl font-bold mb-4">Please log in to view recommendations</h1>
          <Button asChild>
            <a href="/auth">Log In</a>
          </Button>
        </div>
      </div>
    )
  }

  if (isLoading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-primary"></div>
      </div>
    )
  }

  return (
    <div className="flex h-screen bg-gray-100">
      {/* Sidebar */}
      <div className="w-1/4 bg-white shadow-lg overflow-y-auto">
        {/* Banner at the top of sidebar */}
        <div className="bg-primary/10 p-4 border-l-4 border-primary mb-4">
          <div className="flex items-center justify-between">
            <div>
              <h3 className="font-semibold">Unlock Full Access</h3>
              <p className="text-sm text-muted-foreground">
                Top 3 universities are premium
              </p>
            </div>
            <Button
              onClick={() => router.push('/recommendations')}
              variant="outline"
              size="sm"
            >
              Free Trial
            </Button>
          </div>
        </div>

        <div className="p-4">
          <h2 className="text-xl font-semibold mb-4">Recommended Universities</h2>
            <div className="space-y-2">
              {universities.map((university, index) => (
              <div key={university.id} className="relative">
                <button
                  onClick={() => handleUniversityClick(university, index)}
                  className={`w-full text-left p-3 rounded-lg transition-colors ${
                    selectedUniversity?.id === university.id
                      ? "bg-primary text-white"
                      : "hover:bg-gray-100"
                  }`}
                >
                  <div className="flex items-center space-x-3">
                    <img
                      src={university.logo}
                        alt={`${university.name} logo`}
                      className="w-8 h-8 rounded-full"
                      onError={(e) => {
                        const target = e.target as HTMLImageElement;
                        const uni = universities.find(u => u.id === university.id);
                        if (uni && !uni.hasLogoFallback) {
                          uni.hasLogoFallback = true;
                          target.src = "/placeholder-logo.svg";
                        }
                      }}
                    />
                    <div className={index < 3 ? "blur-sm" : ""}>
                      <div className="font-medium">{university.name}</div>
                      <div className="text-sm opacity-75">
                        Match Score: {Math.round(university.match_score)}%
                      </div>
                    </div>
            </div>
                </button>
                
                {/* Premium badge */}
                {index < 3 && (
                  <div className="absolute right-2 top-2 bg-primary text-primary-foreground text-xs px-2 py-1 rounded-full">
                    Premium
                </div>
                )}
              </div>
            ))}
          </div>
        </div>
          </div>

      {/* Main Content */}
      <div className="flex-1 p-8 overflow-y-auto">
        {selectedUniversity ? (
          <div className="max-w-4xl mx-auto">
            <div className="bg-white rounded-lg shadow-lg p-6">
              <div className="flex items-center justify-between mb-6">
                  <div>
                  <h1 className="text-3xl font-bold">{selectedUniversity.name}</h1>
                  <p className="text-gray-600">{selectedUniversity.location}</p>
                </div>
                <div className="text-right">
                  <div className="text-2xl font-bold text-primary">
                    {Math.round(selectedUniversity.match_score)}%
                  </div>
                  <div className="text-sm text-gray-600">Match Score</div>
                  </div>
                </div>

                {/* Image Carousel */}
                {selectedUniversity.images && selectedUniversity.images.length > 0 && (
                <div className="relative h-64 mb-6 rounded-lg overflow-hidden">
                    <img
                    src={selectedUniversity.images[0]}
                    alt={selectedUniversity.name}
                      className="w-full h-full object-cover"
                    onError={(e) => {
                      const target = e.target as HTMLImageElement;
                      if (!selectedUniversity.hasImageFallback) {
                        selectedUniversity.hasImageFallback = true;
                        target.src = "/placeholder-university.svg";
                      }
                    }}
                    />
                  </div>
                )}

              {/* Check if this is a premium university */}
              {universities.indexOf(selectedUniversity) < 3 ? (
                // Premium university content (blurred)
                <div className="relative">
                  {/* Blur overlay for premium content */}
                  <div className="blur-lg">
                    <div className="mb-6">
                      <h2 className="text-xl font-semibold mb-3">Benefits</h2>
                      <ul className="space-y-2">
                            {selectedUniversity.benefits.map((benefit, index) => (
                          <li key={index} className="flex items-start">
                            <span className="text-green-500 mr-2">✓</span>
                            {benefit}
                          </li>
                            ))}
                          </ul>
                    </div>

                    <div className="mb-6">
                      <h2 className="text-xl font-semibold mb-3">Drawbacks</h2>
                      <ul className="space-y-2">
                            {selectedUniversity.drawbacks.map((drawback, index) => (
                          <li key={index} className="flex items-start">
                            <span className="text-red-500 text-lg mr-2">✗</span>
                            {drawback}
                          </li>
                            ))}
                          </ul>
                    </div>

                    <div>
                      <h2 className="text-xl font-semibold mb-3">Why This University?</h2>
                      <ul className="space-y-2">
                        {selectedUniversity.suitabilityReasons.map((reason, index) => (
                          <li key={index} className="flex items-start">
                            <span className="text-blue-500 mr-2">•</span>
                            {reason}
                          </li>
                          ))}
                        </ul>
                    </div>
                  </div>

                  {/* Premium CTA overlay */}
                  <div className="absolute inset-0 flex flex-col items-center justify-center bg-white/70 rounded-lg">
                    <h3 className="text-xl font-bold mb-4">
                      Premium Content
                    </h3>
                    <p className="text-center max-w-md mb-6">
                      Unlock full access to view detailed insights for this premium university match.
                    </p>
                    <div className="flex gap-4">
                      <Button 
                        onClick={() => setIsPaymentOpen(true)}
                        className="px-6"
                      >
                        Get Full Access
                      </Button>
                      <Button
                        variant="outline"
                        onClick={() => router.push('/recommendations')}
                      >
                        Free Trial
                      </Button>
                    </div>
                  </div>
                </div>
              ) : (
                // Regular university content (fully visible)
                <>
                  <div className="mb-6">
                    <h2 className="text-xl font-semibold mb-3">Benefits</h2>
                    {selectedUniversity.benefits && selectedUniversity.benefits.length > 0 ? (
                      <ul className="space-y-2">
                        {selectedUniversity.benefits.map((benefit, index) => (
                          <li key={index} className="flex items-start">
                            <span className="text-green-500 mr-2">✓</span>
                            {benefit}
                          </li>
                              ))}
                            </ul>
                    ) : (
                      <p className="text-gray-500">No specific benefits listed for this university.</p>
                    )}
                  </div>

                  <div className="mb-6">
                    <h2 className="text-xl font-semibold mb-3">Drawbacks</h2>
                    {selectedUniversity.drawbacks && selectedUniversity.drawbacks.length > 0 ? (
                      <ul className="space-y-2">
                        {selectedUniversity.drawbacks.map((drawback, index) => (
                          <li key={index} className="flex items-start">
                            <span className="text-red-500 text-lg mr-2">✗</span>
                            {drawback}
                          </li>
                              ))}
                            </ul>
                    ) : (
                      <p className="text-gray-500">No specific drawbacks listed for this university.</p>
                    )}
                            </div>

                            <div>
                    <h2 className="text-xl font-semibold mb-3">Why This University?</h2>
                    {selectedUniversity.suitabilityReasons && selectedUniversity.suitabilityReasons.length > 0 ? (
                      <ul className="space-y-2">
                        {selectedUniversity.suitabilityReasons.map((reason, index) => (
                          <li key={index} className="flex items-start">
                            <span className="text-blue-500 mr-2">•</span>
                            {reason}
                          </li>
                        ))}
                      </ul>
                    ) : (
                      <p className="text-gray-500">No specific suitability reasons listed for this university.</p>
                    )}
                  </div>
                  </>
                )}
              </div>
          </div>
        ) : (
          <div className="flex flex-col items-center justify-center h-full">
            <p className="text-xl text-gray-600 mb-4">
              No recommendations available yet
            </p>
            <Button
              onClick={() => loadRecommendations()}
              className="px-6 py-2 bg-primary text-white rounded-lg hover:bg-primary/90 transition-colors"
            >
              Find Recommendations
            </Button>
          </div>
        )}
        </div>

      {/* Payment Popup */}
      <PaymentPopup 
        isOpen={isPaymentOpen} 
        onClose={() => setIsPaymentOpen(false)} 
        onSelectPlan={handleSelectPlan} 
      />
    </div>
  )
}

