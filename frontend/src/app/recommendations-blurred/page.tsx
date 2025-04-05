"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { useToast } from "@/components/ui/use-toast";
import {
  getRecommendations,
  getRecommendationDetails,
  getRecommendationJustification,
  getSimilarStudents,
} from "@/api/apiClient";
import { useAuthContext } from "@/providers/AuthProvider";
import { Button } from "@/components/ui/button";
import { Radar } from "react-chartjs-2";
import {
  Chart as ChartJS,
  RadialLinearScale,
  PointElement,
  LineElement,
  Filler,
  Tooltip,
  Legend,
} from "chart.js";
import dynamic from "next/dynamic";

// Register Chart.js components
ChartJS.register(
  RadialLinearScale,
  PointElement,
  LineElement,
  Filler,
  Tooltip,
  Legend
);

// Dynamically import the payment popup component
const PaymentPopup = dynamic(() => import("@/components/payment"), {
  ssr: false,
});

// Function to map university names to their image paths
const getUniversityImage = (universityName: string): string => {
  const nameToImageMap: { [key: string]: string } = {
    "National University of Singapore": "/images/NUS.png",
    "Nanyang Technological University": "/images/NTU.png",
    "Singapore Management University": "/images/SMU.png",
    "Singapore University of Technology and Design": "/images/SUTD.png",
    "Singapore Institute of Technology": "/images/SIT.png",
  };

  return nameToImageMap[universityName] || "/images/school.svg";
};

interface SimilarStudent {
  id: number;
  recommendation_id: number;
  existing_student_id: string;
  similarity_score: number;
  academic_similarity: number;
  social_similarity: number;
  financial_similarity: number;
  career_similarity: number;
  geographic_similarity: number;
  facilities_similarity: number;
  reputation_similarity: number;
  personal_fit_similarity: number;
  created_at: string;
}

interface University {
  id: string;
  name: string;
  location: string;
  logo: string;
  matchScore: number;
  images: string[];
  benefits: string[];
  drawbacks: string[];
  suitabilityReasons: string[];
  similarStudents?: SimilarStudent[];
  hasLogoFallback?: boolean;
  hasImageFallback?: boolean;
  academic_score?: number;
  personal_fit_score?: number;
  social_score?: number;
  financial_score?: number;
  career_score?: number;
  geographic_score?: number;
  facilities_score?: number;
  reputation_score?: number;
}

export default function RecommendationsPage() {
  const router = useRouter();
  const { user, isLoading: isAuthLoading } = useAuthContext();
  const { toast } = useToast();
  const [universities, setUniversities] = useState<University[]>([]);
  const [selectedUniversity, setSelectedUniversity] = useState<University | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [hasAttemptedLoad, setHasAttemptedLoad] = useState(false);
  const [isPaymentOpen, setIsPaymentOpen] = useState(false);
  const [loadingStage, setLoadingStage] = useState<string>("");

  const loadingMessages = [
    "Analyzing your academic preferences...",
    "Evaluating your extracurricular interests...",
    "Processing your career aspirations...",
    "Examining financial parameters...",
    "Identifying universities with matching programs...",
    "Finding similar student profiles...",
    "Calculating cultural fit scores...",
    "Running geographic preference analysis...",
    "Evaluating campus facilities that match your needs...",
    "Ranking universities by overall compatibility...",
    "Generating personalized match scores...",
    "Preparing your customized university insights...",
    "Finalizing top recommendations for you...",
    "Gathering insights from similar students...",
  ];

  const loadRecommendations = async () => {
    if (!user?.username) {
      if (!isAuthLoading && hasAttemptedLoad) {
        toast({
          title: "Error",
          description: "Please log in to view recommendations",
          variant: "destructive",
        });
        router.push("/auth");
      }
      return;
    }

    // Check for cached recommendations first
    try {
      const cachedRecommendations = localStorage.getItem(
        "cachedRecommendations"
      );
      if (cachedRecommendations) {
        console.log("Using cached recommendations");
        const parsedRecommendations = JSON.parse(cachedRecommendations);
        setUniversities(parsedRecommendations);
        if (parsedRecommendations.length > 0) {
          setSelectedUniversity(parsedRecommendations[0]);
        }
        setTimeout(
          () => localStorage.removeItem("cachedRecommendations"),
          2000
        );
        setHasAttemptedLoad(true);
        return;
      }
    } catch (error) {
      console.error("Error reading cached recommendations:", error);
    }

    setIsLoading(true);
    setLoadingStage(loadingMessages[0]);

    try {
      setLoadingStage(loadingMessages[1]);
      const response = await getRecommendations(user.username, 5);
      if (!response.data) {
        throw new Error("No recommendations data received");
      }

      const recommendations = response.data;
      const universitiesWithDetails: University[] = [];

      const batchSize = 2;
      for (let i = 0; i < recommendations.length; i += batchSize) {
        const batch = recommendations.slice(i, i + batchSize);

        const messageIndex = Math.min(
          3 +
            Math.floor(
              (i / recommendations.length) * (loadingMessages.length - 3)
            ),
          loadingMessages.length - 1
        );
        setLoadingStage(loadingMessages[messageIndex]);

        const batchResults = await Promise.all(
          batch.map(async (rec) => {
            try {
              const [
                detailsResponse,
                justificationResponse,
                similarStudentsResponse,
              ] = await Promise.all([
                getRecommendationDetails(user.username, rec.id),
                getRecommendationJustification(user.username, rec.id).catch(
                  (err) => {
                    console.error(
                      `Failed to get justification for ${rec.university_id}:`,
                      err
                    );
                    return { data: {} };
                  }
                ),
                getSimilarStudents(user.username, rec.id).catch((err) => {
                  console.error(
                    `Failed to get similar students for ${rec.university_id}:`,
                    err
                  );
                  return { data: [] };
                }),
              ]);

              const details = detailsResponse.data || {};
              const recommendation = details.recommendation || {};
              const justification = justificationResponse.data || {};
              const similarStudents = similarStudentsResponse.data || [];

              const universityDetails = details.university || {};
              const justData = justification.data || justification;

              const extractArray = (data: any, keys: string[]): string[] => {
                for (const key of keys) {
                  if (Array.isArray(data[key])) return data[key];
                  if (data[key] && typeof data[key] === "string")
                    return [data[key]];
                }
                return [];
              };

              const benefits = extractArray(justData, ["Pros", "pros"]);
              const drawbacks = extractArray(justData, ["Cons", "cons"]);
              const suitabilityReasons = extractArray(justData, [
                "Conclusion",
                "conclusion",
              ]);

              return {
                id: rec.id.toString(),
                name: universityDetails.name || "Unknown University",
                location:
                  universityDetails.location || "Location not specified",
                logo: universityDetails.logo_url || "/placeholder-logo.svg",
                matchScore: rec.overall_score * 100,
                images: Array.isArray(universityDetails.images)
                  ? universityDetails.images
                  : [],
                benefits,
                drawbacks,
                suitabilityReasons,
                similarStudents: Array.isArray(similarStudents)
                  ? similarStudents
                  : [],
                hasLogoFallback: false,
                hasImageFallback: false,
                academic_score: recommendation.academic_score || 0,
                personal_fit_score: recommendation.personal_fit_score || 0,
                social_score: recommendation.social_score || 0,
                financial_score: recommendation.financial_score || 0,
                career_score: recommendation.career_score || 0,
                geographic_score: recommendation.geographic_score || 0,
                facilities_score: recommendation.overall_fit_score || 0,
                reputation_score: recommendation.reputation_score || 0,
              };
            } catch (error) {
              console.error(
                `Error fetching details for university ${rec.university_id}:`,
                error
              );
              return {
                id: rec.id.toString(),
                name: "Unknown University",
                location: "Location not specified",
                logo: "/placeholder-logo.svg",
                matchScore: rec.overall_score * 100,
                images: [],
                benefits: [],
                drawbacks: [],
                suitabilityReasons: [],
                similarStudents: [],
                hasLogoFallback: true,
                hasImageFallback: true,
                academic_score: 0,
                personal_fit_score: 0,
                social_score: 0,
                financial_score: 0,
                career_score: 0,
                geographic_score: 0,
                facilities_score: 0,
                reputation_score: 0,
              };
            }
          })
        );

        universitiesWithDetails.push(...batchResults);

        if (universitiesWithDetails.length > 0 && universities.length === 0) {
          setUniversities([...universitiesWithDetails]);
          setSelectedUniversity(universitiesWithDetails[0]);
        }
      }

      setLoadingStage("Preparing your personalized recommendations...");
      setUniversities(universitiesWithDetails);

      try {
        localStorage.setItem(
          "cachedRecommendations",
          JSON.stringify(universitiesWithDetails)
        );
      } catch (error) {
        console.error("Error storing recommendations in localStorage:", error);
      }
    } catch (err) {
      console.error("Error loading recommendations:", err);
      toast({
        title: "Error",
        description: "Failed to load recommendations. Please try again.",
        variant: "destructive",
      });
    } finally {
      setIsLoading(false);
      setLoadingStage("");
      setHasAttemptedLoad(true);
    }
  };

  useEffect(() => {
    if (!isAuthLoading) {
      if (user?.username) {
        loadRecommendations();
      } else if (hasAttemptedLoad) {
        router.push("/auth");
      }
    }
  }, [user?.username, isAuthLoading]);

  useEffect(() => {
    if (selectedUniversity) {
      console.log("SELECTED UNIVERSITY:", {
        name: selectedUniversity.name,
        benefits: selectedUniversity.benefits,
        drawbacks: selectedUniversity.drawbacks,
        suitabilityReasons: selectedUniversity.suitabilityReasons,
        similarStudents: selectedUniversity.similarStudents,
        academic_score: selectedUniversity.academic_score,
        personal_fit_score: selectedUniversity.personal_fit_score,
        social_score: selectedUniversity.social_score,
        financial_score: selectedUniversity.financial_score,
        career_score: selectedUniversity.career_score,
        geographic_score: selectedUniversity.geographic_score,
        facilities_score: selectedUniversity.facilities_score,
        reputation_score: selectedUniversity.reputation_score,
      });
    }
  }, [selectedUniversity]);

  const handleFindRecommendations = async () => {
    await loadRecommendations();
  };

  const handleSelectPlan = (
    plan: "monthly" | "quarterly" | "annual" | "lifetime" | null
  ) => {
    setIsPaymentOpen(false);
    if (plan) {
      localStorage.setItem("subscriptionPlan", plan);
      router.push("/recommendations");
    }
  };

  const handleUniversityClick = (university: University, index: number) => {
    if (index < 3) {
      setIsPaymentOpen(true);
    } else {
      setSelectedUniversity(university);
    }
  };

  const getRadarChartData = (
    university: University,
    student?: SimilarStudent,
    studentNumber?: number
  ) => {
    const labels = [
      "Academic",
      "Personal Fit",
      "Social",
      "Financial",
      "Career",
      "Geographic",
      "Facilities",
      "Reputation",
    ];

    const universityDataset = {
      label: "Your Scores",
      data: [
        (university.academic_score ?? 0) * 10,
        (university.personal_fit_score ?? 0) * 10,
        (university.social_score ?? 0) * 10,
        (university.financial_score ?? 0) * 10,
        (university.career_score ?? 0) * 10,
        (university.geographic_score ?? 0) * 10,
        (university.facilities_score ?? 0) * 10,
        (university.reputation_score ?? 0) * 10,
      ],
      backgroundColor: "rgba(255, 99, 132, 0.2)",
      borderColor: "rgba(255, 99, 132, 1)",
      borderWidth: 1,
    };

    if (!student) {
      return {
        labels,
        datasets: [universityDataset],
      };
    }

    return {
      labels,
      datasets: [
        universityDataset,
        {
          label: `Student ${studentNumber} Similarity`,
          data: [
            student.academic_similarity * 10,
            student.personal_fit_similarity * 10,
            student.social_similarity * 10,
            student.financial_similarity * 10,
            student.career_similarity * 10,
            student.geographic_similarity * 10,
            student.facilities_similarity * 10,
            student.reputation_similarity * 10,
          ],
          backgroundColor: "rgba(0, 255, 0, 0.2)",
          borderColor: "rgba(0, 255, 0, 1)",
          borderWidth: 1,
        },
      ],
    };
  };

  const radarOptions = {
    scales: {
      r: {
        angleLines: {
          color: "rgba(0, 0, 0, 0.1)",
        },
        grid: {
          color: "rgba(0, 0, 0, 0.1)",
        },
        ticks: {
          beginAtZero: true,
          max: 10,
          stepSize: 2,
        },
        pointLabels: {
          font: {
            size: 12,
          },
        },
      },
    },
    plugins: {
      legend: {
        position: "top" as const,
      },
      title: {
        display: true,
        text: "Dimension Matching Analysis",
      },
    },
  };

  if (isAuthLoading || (!hasAttemptedLoad && !user)) {
    return (
      <div className="flex flex-col items-center justify-center min-h-screen">
        <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-primary mb-4"></div>
        <p className="text-gray-500">Initializing...</p>
      </div>
    );
  }

  if (!user && hasAttemptedLoad) {
    return (
      <div className="container flex h-screen items-center justify-center">
        <div className="text-center">
          <h1 className="text-2xl font-bold mb-4">
            Please log in to view recommendations
          </h1>
          <Button asChild>
            <a href="/auth">Log In</a>
          </Button>
        </div>
      </div>
    );
  }

  if (isLoading) {
    return (
      <div className="flex flex-col items-center justify-center min-h-screen">
        <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-primary mb-4"></div>
        <p className="text-gray-600 font-medium">
          {loadingStage || "Preparing recommendations..."}
        </p>
        <p className="text-sm text-gray-400 mt-2">This may take a moment</p>
      </div>
    );
  }

  return (
    <div className="flex min-h-screen bg-gray-100">
      {/* Sidebar */}
      <div className="w-1/4 bg-white shadow-lg overflow-y-auto">
        <div className="p-4">
          <h2 className="text-xl font-semibold mb-4">
            Recommended Universities
          </h2>
          <div className="space-y-2">
            {universities.map((university, index) => (
              <div key={university.id} className="relative">
                <button
                  onClick={() => handleUniversityClick(university, index)}
                  className={`w-full text-left p-3 rounded-lg transition-colors cursor-pointer ${
                    selectedUniversity?.id === university.id
                      ? "bg-primary text-white"
                      : "hover:bg-gray-100"
                  }`}
                >
                  <div className="flex items-center space-x-3">
                    <img
                      src={
                        getUniversityImage(university.name) ||
                        (university.images && university.images.length > 0
                          ? university.images[0]
                          : "/placeholder-university.svg")
                      }
                      alt={university.name}
                      className={index < 3 ? "blur-sm w-8" : "w-8"}
                      onError={(e) => {
                        const target = e.target as HTMLImageElement;
                        if (!university.hasImageFallback) {
                          university.hasImageFallback = true;
                          target.src = "/placeholder-university.svg";
                        }
                      }}
                    />
                    <div className={index < 3 ? "blur-sm" : ""}>
                      <div className="font-medium">{university.name}</div>
                      <div className="text-sm opacity-75">
                        Match Score: {Math.round(university.matchScore)}%
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
                  <h1 className="text-3xl font-bold">
                    {selectedUniversity.name}
                  </h1>
                  <p className="text-gray-600">{selectedUniversity.location}</p>
                </div>
                <div className="text-right">
                  <div className="text-2xl font-bold text-primary">
                    {Math.round(selectedUniversity.matchScore)}%
                  </div>
                  <div className="text-sm text-gray-600">Match Score</div>
                </div>
              </div>

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

                    <div className="mb-6">
                      <h2 className="text-xl font-semibold mb-3">
                        Why This University?
                      </h2>
                      <ul className="space-y-2">
                        {selectedUniversity.suitabilityReasons.map(
                          (reason, index) => (
                            <li key={index} className="flex items-start">
                              <span className="text-blue-500 mr-2">•</span>
                              {reason}
                            </li>
                          )
                        )}
                      </ul>
                    </div>

                    {/* Radar Charts - also blurred */}
                    {selectedUniversity.similarStudents &&
                      selectedUniversity.similarStudents.length > 0 && (
                        <div className="mb-6">
                          <h2 className="text-xl font-semibold mb-3">
                            Similarity Analysis
                          </h2>
                          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                            {selectedUniversity.similarStudents.map(
                              (student, index) => (
                                <div
                                  key={index}
                                  className="bg-gray-50 p-4 rounded-lg"
                                >
                                  <h3 className="text-lg font-medium mb-2">
                                    You vs. Student {index + 1}
                                  </h3>
                                  <div className="w-full max-w-xs mx-auto">
                                    <Radar
                                      data={getRadarChartData(
                                        selectedUniversity,
                                        student,
                                        index + 1
                                      )}
                                      options={radarOptions}
                                    />
                                  </div>
                                </div>
                              )
                            )}
                          </div>
                        </div>
                      )}
                  </div>

                  {/* Premium CTA overlay */}
                  <div className="absolute inset-0 flex flex-col items-center justify-center bg-white/70 rounded-lg">
                    <h3 className="text-xl font-bold mb-4">Premium Content</h3>
                    <p className="text-center max-w-md mb-6">
                      Unlock full access to view detailed insights and
                      similarity analysis for this premium university match.
                    </p>
                    <div className="flex gap-4">
                      <Button
                        onClick={() => setIsPaymentOpen(true)}
                        className="px-6 cursor-pointer"
                      >
                        Get Full Access
                      </Button>
                    </div>
                  </div>
                </div>
              ) : (
                // Regular university content (fully visible)
                <>
                  <div className="mb-6">
                    <h2 className="text-xl font-semibold mb-3">Benefits</h2>
                    {selectedUniversity.benefits &&
                    selectedUniversity.benefits.length > 0 ? (
                      <ul className="space-y-2">
                        {selectedUniversity.benefits.map((benefit, index) => (
                          <li key={index} className="flex items-start">
                            <span className="text-green-500 mr-2">✓</span>
                            {benefit}
                          </li>
                        ))}
                      </ul>
                    ) : (
                      <p className="text-gray-500">
                        No specific benefits listed for this university.
                      </p>
                    )}
                  </div>

                  <div className="mb-6">
                    <h2 className="text-xl font-semibold mb-3">Drawbacks</h2>
                    {selectedUniversity.drawbacks &&
                    selectedUniversity.drawbacks.length > 0 ? (
                      <ul className="space-y-2">
                        {selectedUniversity.drawbacks.map((drawback, index) => (
                          <li key={index} className="flex items-start">
                            <span className="text-red-500 text-lg mr-2">✗</span>
                            {drawback}
                          </li>
                        ))}
                      </ul>
                    ) : (
                      <p className="text-gray-500">
                        No specific drawbacks listed for this university.
                      </p>
                    )}
                  </div>

                  <div className="mb-6">
                    <h2 className="text-xl font-semibold mb-3">
                      Why This University?
                    </h2>
                    {selectedUniversity.suitabilityReasons &&
                    selectedUniversity.suitabilityReasons.length > 0 ? (
                      <ul className="space-y-2">
                        {selectedUniversity.suitabilityReasons.map(
                          (reason, index) => (
                            <li key={index} className="flex items-start">
                              <span className="text-blue-500 mr-2">•</span>
                              {reason}
                            </li>
                          )
                        )}
                      </ul>
                    ) : (
                      <p className="text-gray-500">
                        No specific suitability reasons listed for this
                        university.
                      </p>
                    )}
                  </div>

                  <div className="mb-6">
                    <h2 className="text-xl font-semibold mb-3">
                      Similar Students
                    </h2>
                    {selectedUniversity.similarStudents &&
                    selectedUniversity.similarStudents.length > 0 ? (
                      <ul className="space-y-2">
                        {selectedUniversity.similarStudents.map(
                          (student, index) => (
                            <li key={index} className="flex items-start">
                              <span className="text-purple-500 mr-2">→</span>
                              Student {index + 1} - Similarity:{" "}
                              {Math.round(student.similarity_score * 100)}%
                            </li>
                          )
                        )}
                      </ul>
                    ) : (
                      <p className="text-gray-500">
                        No similar student information available.
                      </p>
                    )}
                  </div>

                  {/* University Scores Radar Chart */}
                  {selectedUniversity && (
                    <div className="mb-6">
                      <h2 className="text-xl font-semibold mb-3">
                        Univeristy Similarity Score
                      </h2>
                      <div className="bg-gray-50 p-4 rounded-lg">
                        <div className="w-full max-w-xs mx-auto">
                          <Radar
                            data={getRadarChartData(selectedUniversity)}
                            options={radarOptions}
                          />
                        </div>
                      </div>
                    </div>
                  )}

                  {/* Comparison Radar Charts */}
                  {selectedUniversity.similarStudents &&
                    selectedUniversity.similarStudents.length > 0 && (
                      <div className="mb-6">
                        <h2 className="text-xl font-semibold mb-3">
                          Similarity Analysis (You vs. Similar Students)
                        </h2>
                        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                          {selectedUniversity.similarStudents.map(
                            (student, index) => (
                              <div
                                key={index}
                                className="bg-gray-50 p-4 rounded-lg"
                              >
                                <h3 className="text-lg font-medium mb-2">
                                  You vs. Student {index + 1}
                                </h3>
                                <div className="w-full max-w-xs mx-auto">
                                  <Radar
                                    data={getRadarChartData(
                                      selectedUniversity,
                                      student,
                                      index + 1
                                    )}
                                    options={radarOptions}
                                  />
                                </div>
                              </div>
                            )
                          )}
                        </div>
                      </div>
                    )}
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
  );
}
