// recommendations/page.tsx - Replace with this optimized version

"use client"

import { useEffect, useState } from "react"
import { useRouter } from "next/navigation"
import { useToast } from "@/components/ui/use-toast"
import { getRecommendations, getRecommendationDetails, getRecommendationJustification } from "@/api/apiClient"
import { useAuthContext } from "@/providers/AuthProvider"
import { Button } from "@/components/ui/button"

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

export default function RecommendationsPage() {
  const router = useRouter()
  const { user, isLoading: isAuthLoading } = useAuthContext()
  const { toast } = useToast()
  const [universities, setUniversities] = useState<University[]>([])
  const [selectedUniversity, setSelectedUniversity] = useState<University | null>(null)
  const [isLoading, setIsLoading] = useState(false)
  const [loadingStage, setLoadingStage] = useState<string>("") // Track loading stages
  const [hasAttemptedLoad, setHasAttemptedLoad] = useState(false)

  // Array of engaging loading messages to cycle through
  const loadingMessages = [
    // Initial analysis phase
    "Analyzing your academic preferences...",
    "Evaluating your extracurricular interests...",
    "Processing your career aspirations...",
    "Examining financial parameters...",
    
    // Matching phase
    "Identifying universities with matching programs...",
    "Finding similar student profiles...",
    "Calculating cultural fit scores...",
    "Running geographic preference analysis...",
    "Evaluating campus facilities that match your needs...",
    
    // Recommendation finalization phase
    "Ranking universities by overall compatibility...",
    "Generating personalized match scores...",
    "Preparing your customized university insights...",
    "Finalizing top recommendations for you...",
    "Gathering insights from similar students..."
  ];

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

    // Immediately display any cached recommendations without delay
    try {
      const cachedRecommendations = localStorage.getItem("cachedRecommendations")
      if (cachedRecommendations) {
        console.log("Using cached recommendations")
        const parsedRecommendations = JSON.parse(cachedRecommendations)
        setUniversities(parsedRecommendations)
        if (parsedRecommendations.length > 0) {
          setSelectedUniversity(parsedRecommendations[0])
        }
        // Don't clear the cache immediately - we'll do it after a brief delay
        // to ensure smooth rendering first
        setTimeout(() => localStorage.removeItem("cachedRecommendations"), 2000)
        setHasAttemptedLoad(true)
        // Even with cached data, we can still return now - no need to fetch fresh data
        return
      }
    } catch (error) {
      console.error("Error reading cached recommendations:", error)
      // Continue with API call if cache read fails
    }

    // If we reach here, there was no cache or an error reading it
    setIsLoading(true)
    setLoadingStage(loadingMessages[0]);
    
    try {
      // Get recommendations first
      setLoadingStage(loadingMessages[1]);
      const response = await getRecommendations(user.username, 5)
      if (!response.data) {
        throw new Error("No recommendations data received")
      }
      
      const recommendations = response.data
      
      // Optimize fetching details by processing in batches rather than all at once
      setLoadingStage(loadingMessages[2]);
      const universitiesWithDetails: University[] = []
      
      // Process in smaller batches to show progress faster
      const batchSize = 2; // Process 2 universities at a time
      for (let i = 0; i < recommendations.length; i += batchSize) {
        const batch = recommendations.slice(i, i + batchSize)
        
        const messageIndex = Math.min(
          3 + Math.floor((i / recommendations.length) * (loadingMessages.length - 3)),
          loadingMessages.length - 1
        );
        setLoadingStage(loadingMessages[messageIndex]);
        
        // Process each batch in parallel
        const batchResults = await Promise.all(
          batch.map(async (rec) => {
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
              
              // Extract justification data using simplified processing
              const justData = justification.data || justification
              
              // Extract data more efficiently
              const extractArray = (data: any, keys: string[]): string[] => {
                for (const key of keys) {
                  if (Array.isArray(data[key])) return data[key];
                  if (data[key] && typeof data[key] === 'string') return [data[key]];
                }
                return [];
              };
              
              const benefits = extractArray(justData, ['Pros', 'pros']);
              const drawbacks = extractArray(justData, ['Cons', 'cons']);
              const suitabilityReasons = extractArray(justData, ['Conclusion', 'conclusion']);
              
              return {
                id: rec.id.toString(),
                name: universityDetails.name || "Unknown University",
                location: universityDetails.location || "Location not specified",
                logo: universityDetails.logo_url || "/placeholder-logo.svg",
                match_score: rec.overall_score * 100,
                images: Array.isArray(universityDetails.images) ? universityDetails.images : [],
                benefits,
                drawbacks,
                suitabilityReasons,
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
        
        // Add batch results to our array and update UI immediately with progress
        universitiesWithDetails.push(...batchResults)
        
        // Update UI with what we have so far
        if (universitiesWithDetails.length > 0 && universities.length === 0) {
          setUniversities([...universitiesWithDetails])
          setSelectedUniversity(universitiesWithDetails[0])
        }
      }
      
      setLoadingStage("Preparing your personalized recommendations...");

      // Final update with all universities
      setUniversities(universitiesWithDetails)
      
      // Store for future use
      try {
        localStorage.setItem("cachedRecommendations", JSON.stringify(universitiesWithDetails))
      } catch (error) {
        console.error("Error storing recommendations in localStorage:", error)
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
      setLoadingStage("")
      setHasAttemptedLoad(true)
    }
  }

  useEffect(() => {
    // Only load if auth is done loading and we have a user
    if (!isAuthLoading) {
      if (user?.username) {
        loadRecommendations()
      } else if (hasAttemptedLoad) {
        // Only redirect if we've tried loading at least once
        router.push('/auth')
      }
    }
  }, [user?.username, isAuthLoading])

  const handleFindRecommendations = async () => {
    await loadRecommendations()
  }

  // Show loading spinner while auth is initializing or during first load
  if (isAuthLoading || (!hasAttemptedLoad && !user)) {
    return (
      <div className="flex flex-col items-center justify-center min-h-screen">
        <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-primary mb-4"></div>
        <p className="text-gray-500">Initializing...</p>
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
      <div className="flex flex-col items-center justify-center min-h-screen">
        <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-primary mb-4"></div>
        <p className="text-gray-500">{loadingStage || "Loading recommendations..."}</p>
      </div>
    )
  }

  return (
    <div className="flex h-screen bg-gray-100">
      {/* Sidebar */}
      <div className="w-1/4 bg-white shadow-lg overflow-y-auto">
        {/* Premium Banner */}
        <div className="bg-green-50 p-4 border-l-4 border-green-500">
          <div className="flex items-center">
            <div className="flex-shrink-0">
              <svg className="h-5 w-5 text-green-500" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor">
                <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
              </svg>
            </div>
            <div className="ml-3">
              <p className="text-sm leading-5 font-medium text-green-800">
                Full Access Unlocked
              </p>
            </div>
          </div>
        </div>
        
        <div className="p-4">
          <h2 className="text-xl font-semibold mb-4">Recommended Universities</h2>
          {universities.length > 0 ? (
            <div className="space-y-2">
              {universities.map((university) => (
                <button
                  key={university.id}
                  onClick={() => setSelectedUniversity(university)}
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
                    <div>
                      <div className="font-medium">{university.name}</div>
                      <div className="text-sm opacity-75">
                        Match Score: {Math.round(university.match_score)}%
                      </div>
                    </div>
                  </div>
                </button>
              ))}
            </div>
          ) : (
            <div className="text-center p-6 text-gray-500">
              <p>No recommendations found</p>
              <Button variant="outline" className="mt-4" onClick={handleFindRecommendations}>
                Refresh
              </Button>
            </div>
          )}
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

              {/* Benefits */}
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

              {/* Drawbacks */}
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

              {/* Suitability Reasons */}
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
            </div>
          </div>
        ) : (
          <div className="flex flex-col items-center justify-center h-full">
            <p className="text-xl text-gray-600 mb-4">
              No recommendations available yet
            </p>
            <button
              onClick={handleFindRecommendations}
              className="px-6 py-2 bg-primary text-white rounded-lg hover:bg-primary/90 transition-colors"
            >
              Find Recommendations
            </button>
          </div>
        )}
      </div>
    </div>
  )
}