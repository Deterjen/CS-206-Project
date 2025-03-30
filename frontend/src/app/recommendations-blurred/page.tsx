"use client"

import { useEffect, useState } from "react"
import { useRouter } from "next/navigation"
import { Loader2 } from "lucide-react"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Header } from "@/components/ui/header"
import { recommendationService } from "@/api/services"

interface University {
  id: string
  name: string
  location: string
  logo: string
  match_score: number
  images: string[]
  benefits: string[]
  drawbacks: string[]
  suitability_reasons: string[]
  details?: {
    description: string
    programs: string[]
    admission_requirements: string[]
    tuition_fees: string
    campus_life: string
  }
  justification?: {
    academic_match: string
    cultural_fit: string
    financial_fit: string
    overall_assessment: string
  }
}

export default function RecommendationsPage() {
  const router = useRouter()
  const [universities, setUniversities] = useState<University[]>([])
  const [selectedUniversity, setSelectedUniversity] = useState<University | null>(null)
  const [isLoading, setIsLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [isLoadingDetails, setIsLoadingDetails] = useState(false)
  const [detailsError, setDetailsError] = useState<string | null>(null)

  useEffect(() => {
    fetchRecommendations()
  }, [])

  const fetchRecommendations = async () => {
    try {
      const username = localStorage.getItem("username")
      if (!username) {
        router.push("/auth")
        return
      }

      const response = await recommendationService.generateRecommendations(username)
      setUniversities(response.data)
      if (response.data.length > 0) {
        setSelectedUniversity(response.data[0])
        fetchUniversityDetails(response.data[0].id)
      }
    } catch (error) {
      console.error("Error fetching recommendations:", error)
      setError("Failed to load recommendations. Please try again.")
    } finally {
      setIsLoading(false)
    }
  }

  const fetchUniversityDetails = async (universityId: string) => {
    setIsLoadingDetails(true)
    setDetailsError(null)
    try {
      const username = localStorage.getItem("username")
      if (!username) return

      const [detailsResponse, justificationResponse] = await Promise.all([
        recommendationService.getRecommendationDetails(username, universityId),
        recommendationService.getRecommendationJustification(username, universityId),
      ])

      setUniversities((prev) =>
        prev.map((uni) =>
          uni.id === universityId
            ? {
                ...uni,
                details: detailsResponse.data,
                justification: justificationResponse.data,
              }
            : uni,
        ),
      )

      setSelectedUniversity((prev) =>
        prev?.id === universityId
          ? {
              ...prev,
              details: detailsResponse.data,
              justification: justificationResponse.data,
            }
          : prev,
      )
    } catch (error) {
      console.error("Error fetching university details:", error)
      setDetailsError("Failed to load university details. Please try again.")
    } finally {
      setIsLoadingDetails(false)
    }
  }

  const handleLogout = () => {
    localStorage.removeItem("token")
    localStorage.removeItem("username")
    router.push("/auth")
  }

  if (isLoading) {
    return (
      <div className="flex flex-col min-h-screen">
        <Header isAuthenticated={true} onLogout={handleLogout} />
        <div className="flex-1 flex items-center justify-center">
          <Loader2 className="h-8 w-8 animate-spin" />
        </div>
      </div>
    )
  }

  if (error) {
    return (
      <div className="flex flex-col min-h-screen">
        <Header isAuthenticated={true} onLogout={handleLogout} />
        <div className="flex-1 flex items-center justify-center">
          <div className="text-center">
            <p className="text-red-500 mb-4">{error}</p>
            <Button onClick={fetchRecommendations}>Try Again</Button>
          </div>
        </div>
      </div>
    )
  }

  if (universities.length === 0) {
    return (
      <div className="flex flex-col min-h-screen">
        <Header isAuthenticated={true} onLogout={handleLogout} />
        <div className="flex-1 flex items-center justify-center">
          <div className="text-center">
            <p className="text-muted-foreground mb-4">No recommendations available yet.</p>
            <Button onClick={() => router.push("/profile/setup")}>Complete Your Profile</Button>
          </div>
        </div>
      </div>
    )
  }

  return (
    <div className="flex flex-col min-h-screen">
      <Header isAuthenticated={true} onLogout={handleLogout} />

      <main className="flex-1 container mx-auto py-8">
        <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
          {/* University List */}
          <div className="md:col-span-1 space-y-4 relative">
            <h2 className="text-2xl font-bold mb-4">Your Matches</h2>
            <div className="space-y-2">
              {universities.map((university, index) => (
                <Card
                  key={university.id}
                  className={`cursor-pointer transition-colors ${
                    selectedUniversity?.id === university.id ? "border-primary" : "hover:border-primary/50"
                  }`}
                  onClick={() => {
                    setSelectedUniversity(university)
                    fetchUniversityDetails(university.id)
                  }}
                >
                  <CardContent className={`p-4 ${index < 3 ? "blur-lg" : ""}`}>
                    <div className="flex items-center gap-4">
                      <img
                        src={university.logo || "/placeholder.svg"}
                        alt={`${university.name} logo`}
                        className="w-12 h-12 object-contain"
                      />
                      <div>
                        <h3 className="font-semibold">{university.name}</h3>
                        <p className="text-sm text-muted-foreground">{university.location}</p>
                        <div className="mt-1">
                          <div className="flex items-center gap-1">
                            <div className="w-16 h-2 bg-gray-200 rounded-full">
                              <div
                                className="h-full bg-primary rounded-full"
                                style={{ width: `${university.match_score * 10}%` }}
                              />
                            </div>
                            <span className="text-sm text-muted-foreground">
                              {Math.round(university.match_score * 10)}% match
                            </span>
                          </div>
                        </div>
                      </div>
                    </div>
                  </CardContent>
                </Card>
              ))}
            </div>
            {universities.slice(0, 3).map((university, index) => (
              <div
                key={`premium-${university.id}`}
                className="absolute top-0 left-0 w-full h-full flex items-center justify-center pointer-events-none"
                style={{
                  top: `${index * (4 + 16 + 76)}px`, // Approximating the position based on card height and gap
                  height: "76px",
                }}
              >
                <div className="bg-primary/80 text-primary-foreground px-3 py-1 rounded-md text-sm font-medium">
                  Premium Match
                </div>
              </div>
            ))}
          </div>

          {/* Selected University Details */}
          <div className="md:col-span-2">
            {selectedUniversity && (
              <div className="space-y-6">
                <div className="flex items-center gap-4">
                  <img
                    src={selectedUniversity.logo || "/placeholder.svg"}
                    alt={`${selectedUniversity.name} logo`}
                    className="w-16 h-16 object-contain"
                  />
                  <div>
                    <h2 className="text-3xl font-bold">{selectedUniversity.name}</h2>
                    <p className="text-muted-foreground">{selectedUniversity.location}</p>
                  </div>
                </div>

                {/* Image Carousel */}
                {selectedUniversity.images && selectedUniversity.images.length > 0 && (
                  <div className="relative h-64 rounded-lg overflow-hidden">
                    <img
                      src={selectedUniversity.images[0] || "/placeholder.svg"}
                      alt={`${selectedUniversity.name} campus`}
                      className="w-full h-full object-cover"
                    />
                  </div>
                )}

                {isLoadingDetails ? (
                  <div className="flex items-center justify-center py-8">
                    <Loader2 className="h-8 w-8 animate-spin" />
                  </div>
                ) : detailsError ? (
                  <div className="text-red-500 text-center py-8">{detailsError}</div>
                ) : (
                  <>
                    {/* Benefits and Drawbacks */}
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                      <Card>
                        <CardHeader>
                          <CardTitle>Benefits</CardTitle>
                        </CardHeader>
                        <CardContent>
                          <ul className="list-disc list-inside space-y-2">
                            {selectedUniversity.benefits.map((benefit, index) => (
                              <li key={index}>{benefit}</li>
                            ))}
                          </ul>
                        </CardContent>
                      </Card>

                      <Card>
                        <CardHeader>
                          <CardTitle>Drawbacks</CardTitle>
                        </CardHeader>
                        <CardContent>
                          <ul className="list-disc list-inside space-y-2">
                            {selectedUniversity.drawbacks.map((drawback, index) => (
                              <li key={index}>{drawback}</li>
                            ))}
                          </ul>
                        </CardContent>
                      </Card>
                    </div>

                    {/* Suitability Reasons */}
                    <Card>
                      <CardHeader>
                        <CardTitle>Why This University Matches You</CardTitle>
                      </CardHeader>
                      <CardContent>
                        <ul className="list-disc list-inside space-y-2">
                          {selectedUniversity.suitability_reasons.map((reason, index) => (
                            <li key={index}>{reason}</li>
                          ))}
                        </ul>
                      </CardContent>
                    </Card>

                    {/* Detailed Information */}
                    {selectedUniversity.details && (
                      <div className="space-y-6">
                        <Card>
                          <CardHeader>
                            <CardTitle>About</CardTitle>
                            <CardDescription>{selectedUniversity.details.description}</CardDescription>
                          </CardHeader>
                        </Card>

                        <Card>
                          <CardHeader>
                            <CardTitle>Programs</CardTitle>
                          </CardHeader>
                          <CardContent>
                            <ul className="list-disc list-inside space-y-2">
                              {selectedUniversity.details.programs.map((program, index) => (
                                <li key={index}>{program}</li>
                              ))}
                            </ul>
                          </CardContent>
                        </Card>

                        <Card>
                          <CardHeader>
                            <CardTitle>Admission Requirements</CardTitle>
                          </CardHeader>
                          <CardContent>
                            <ul className="list-disc list-inside space-y-2">
                              {selectedUniversity.details.admission_requirements.map((req, index) => (
                                <li key={index}>{req}</li>
                              ))}
                            </ul>
                          </CardContent>
                        </Card>

                        <Card>
                          <CardHeader>
                            <CardTitle>Tuition & Fees</CardTitle>
                          </CardHeader>
                          <CardContent>
                            <p>{selectedUniversity.details.tuition_fees}</p>
                          </CardContent>
                        </Card>

                        <Card>
                          <CardHeader>
                            <CardTitle>Campus Life</CardTitle>
                          </CardHeader>
                          <CardContent>
                            <p>{selectedUniversity.details.campus_life}</p>
                          </CardContent>
                        </Card>
                      </div>
                    )}

                    {/* Justification */}
                    {selectedUniversity.justification && (
                      <div className="space-y-6">
                        <Card>
                          <CardHeader>
                            <CardTitle>Match Analysis</CardTitle>
                          </CardHeader>
                          <CardContent className="space-y-4">
                            <div>
                              <h3 className="font-semibold mb-2">Academic Match</h3>
                              <p>{selectedUniversity.justification.academic_match}</p>
                            </div>
                            <div>
                              <h3 className="font-semibold mb-2">Cultural Fit</h3>
                              <p>{selectedUniversity.justification.cultural_fit}</p>
                            </div>
                            <div>
                              <h3 className="font-semibold mb-2">Financial Fit</h3>
                              <p>{selectedUniversity.justification.financial_fit}</p>
                            </div>
                            <div>
                              <h3 className="font-semibold mb-2">Overall Assessment</h3>
                              <p>{selectedUniversity.justification.overall_assessment}</p>
                            </div>
                          </CardContent>
                        </Card>
                      </div>
                    )}
                  </>
                )}
              </div>
            )}
          </div>
        </div>
      </main>
    </div>
  )
}

