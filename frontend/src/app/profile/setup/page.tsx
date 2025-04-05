"use client";

import { useState, useEffect } from "react";
import { useRouter } from "next/navigation";
import { useAuthContext } from "@/providers/AuthProvider";

import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";

// Import each step's form and types
import Step1Form, { Step1Data } from "./Step1Form";
import Step2Form, { Step2Data } from "./Step2Form";
import Step3Form, { Step3Data } from "./Step3Form";
import Step4Form, { Step4Data } from "./Step4Form";
import Step5Form, { Step5Data } from "./Step5Form";
import Step6Form, { Step6Data } from "./Step6Form";
import Step7Form, { Step7Data } from "./Step7Form";
import Step8Form, { Step8Data } from "./Step8Form";
import { submitProfileForm } from "./submitForm";
import { toast } from "@/components/ui/use-toast";
import { Loader2 } from "lucide-react";
import { profileService } from "@/api/services";

export default function ProfileSetupPage() {
  const router = useRouter();
  const { user, isLoading: authLoading } = useAuthContext();

  // Redirect if not logged in
  useEffect(() => {
    if (!authLoading && !user) {
      router.push("/auth");
    }
  }, [user, authLoading, router]);

  // Track which step user is on
  const [currentStep, setCurrentStep] = useState(1);
  const [isLoading, setIsLoading] = useState(true);
  const [isSubmitting, setIsSubmitting] = useState(false);

  // Store partial data from each step
  const [step1Data, setStep1Data] = useState<Step1Data | null>(null);
  const [step2Data, setStep2Data] = useState<Step2Data | null>(null);
  const [step3Data, setStep3Data] = useState<Step3Data | null>(null);
  const [step4Data, setStep4Data] = useState<Step4Data | null>(null);
  const [step5Data, setStep5Data] = useState<Step5Data | null>(null);
  const [step6Data, setStep6Data] = useState<Step6Data | null>(null);
  const [step7Data, setStep7Data] = useState<Step7Data | null>(null);
  const [step8Data, setStep8Data] = useState<Step8Data | null>(null);

  // Load existing profile data if available
  useEffect(() => {
    if (!authLoading && user?.username) {
      setIsLoading(true);

      // First try to get profile data from API
      const fetchProfileDataFromAPI = async () => {
        try {
          const response = await profileService.getProfile(user.username);
          if (response.data && response.data.profile) {
            const profileData = response.data.profile;

            // Map learning style from API format to select option values
            const mapLearningStyle = (apiStyle: string) => {
              const mapping: { [key: string]: string } = {
                "Hands-on/Practical": "hands_on",
                Visual: "visual",
                Auditory: "auditory",
                Theoretical: "theoretical",
                "Group-based": "group_based",
                "Self-paced/Individual": "self_paced",
                "Research-oriented": "research_oriented",
              };
              return mapping[apiStyle] || "";
            };

            const standardFields = [
              "business",
              "computing_it",
              "engineering",
              "sciences",
              "social_sciences",
              "arts_humanities",
              "medicine_health",
              "law",
              "education",
            ];

            function mapPreferredFields(fields: string[] = []) {
              const mapping: { [key: string]: string } = {
                Business: "business",
                "Computing/IT": "computing_it",
                Engineering: "engineering",
                Sciences: "sciences",
                "Social Sciences": "social_sciences",
                "Arts & Humanities": "arts_humanities",
                "Medicine & Health": "medicine_health",
                Law: "law",
                Education: "education",
              };

              // Convert each field using the mapping
              return fields.map(
                (field) =>
                  mapping[field] ||
                  // If no mapping exists, check if it's a custom field
                  (standardFields.includes(field) ? field : "other")
              );
            }

            // Map extracurricular activities to match form values
            function mapExtracurriculars(activities: string[] = []) {
              const mapping: { [key: string]: string } = {
                Sports: "sports",
                "Arts & Culture": "arts_culture",
                "Academic Clubs": "academic_clubs",
                "Community Service": "community_service",
                "Professional/Career Clubs": "professional_clubs",
                "Social Clubs": "social_clubs",
                "Research-oriented Activities": "research_activities",
              };

              // Convert each activity using the mapping
              return activities.map(
                (activity) =>
                  mapping[activity] ||
                  // If no mapping exists, check if it's a custom activity
                  (standardActivities.includes(activity) ? activity : "other")
              );
            }

            // Define standard activities array
            const standardActivities = [
              "sports",
              "arts_culture",
              "academic_clubs",
              "community_service",
              "professional_clubs",
              "social_clubs",
              "research_activities",
            ];

            // Get custom fields/activities for "other" fields
            function getCustomFields(
              fields: string[] = [],
              standardList: string[]
            ) {
              const customFields = fields.filter(
                (f) =>
                  !Object.keys(standardList).includes(f) &&
                  !standardList.includes(f)
              );
              return customFields.join(", ");
            }

            // Convert API response to step data format expected by the setup forms
            const stepData = {
              step1: {
                preferredFields: mapPreferredFields(
                  profileData.preferred_fields
                ),
                preferredFieldsOther: getCustomFields(
                  profileData.preferred_fields,
                  standardFields
                ),
                learningStyle: mapLearningStyle(profileData.learning_style),
                careerGoals: profileData.career_goals || "",
                furtherEducation:
                  profileData.further_education?.toLowerCase() || "",
              },
              step2: {
                cultureImportance: profileData.culture_importance || 5,
                extracurriculars: mapExtracurriculars(
                  profileData.interested_activities
                ),
                extracurricularsOther: getCustomFields(
                  profileData.interested_activities,
                  standardActivities
                ),
                weeklyHours: profileData.weekly_extracurricular_hours || "",
                passionateActivities: profileData.passionate_activities || "",
              },
              step3: {
                internshipImportance: profileData.internship_importance || 5,
                leadershipInterest: profileData.leadership_interest
                  ? "yes"
                  : "no",
                alumniNetworkValue: profileData.alumni_network_value || 5,
              },
              step4: {
                affordabilityImportance:
                  profileData.affordability_importance || 5,
                yearlyBudget: profileData.yearly_budget
                  ? profileData.yearly_budget.toString()
                  : "",
                financialAidInterest: profileData.financial_aid_interest
                  ? "yes"
                  : "no",
              },
              step5: {
                preferredRegion: profileData.preferred_region || "",
                // Convert to lowercase to match select options
                preferredSetting:
                  profileData.preferred_setting?.toLowerCase() || "",
                // Map living arrangement to match select options
                preferredLivingArrangement: mapLivingArrangement(
                  profileData.preferred_living_arrangement
                ),
              },
              step6: {
                importantFacilities: profileData.important_facilities || [],
                // Check if there are custom facilities
                importantFacilitiesOther: getCustomFacilities(
                  profileData.important_facilities
                ),
                modernAmenitiesImportance:
                  profileData.modern_amenities_importance || 5,
              },
              step7: {
                rankingImportance: profileData.ranking_importance || 5,
                alumniTestimonialInfluence:
                  profileData.alumni_testimonial_influence || 5,
                selectionFactors: profileData.important_selection_factors || [],
                // Check if there are custom selection factors
                selectionFactorsOther: getCustomSelectionFactors(
                  profileData.important_selection_factors
                ),
              },
              step8: {
                personalityTraits: profileData.personality_traits || [],
                // Check if there are custom personality traits
                personalityTraitsOther: getCustomPersonalityTraits(
                  profileData.personality_traits
                ),
                // Map student population size to match select options
                studentPopulationSize: mapStudentPopulation(
                  profileData.preferred_student_population
                ),
                lifestylePreferences: profileData.lifestyle_preferences || "",
              },
            };

            // Helper function to map living arrangement values
            function mapLivingArrangement(arrangement: string) {
              const mapping: { [key: string]: string } = {
                "On Campus": "on_campus",
                "Off Campus": "off_campus",
                "Commute from Home": "commute",
              };
              return mapping[arrangement] || "";
            }

            // Helper function to map student population size
            function mapStudentPopulation(size: string) {
              const mapping: { [key: string]: string } = {
                Small: "small",
                Medium: "medium",
                Large: "large",
              };
              return mapping[size] || "";
            }

            // Helper functions to extract custom options
            function getCustomFacilities(facilities: string[] = []) {
              const standardFacilities = [
                "sports_facilities",
                "libraries",
                "on_campus_housing",
                "support_centers",
                "modern_amenities",
              ];
              const customFacilities = facilities.filter(
                (f) => !standardFacilities.includes(f)
              );
              return customFacilities.join(", ");
            }

            function getCustomSelectionFactors(factors: string[] = []) {
              const standardFactors = [
                "academic_reputation",
                "location",
                "campus_culture",
                "affordability",
                "scholarship_opportunities",
                "internship_opportunities",
                "modern_facilities",
                "alumni_network_strength",
              ];
              const customFactors = factors.filter(
                (f) => !standardFactors.includes(f)
              );
              return customFactors.join(", ");
            }

            function getCustomPersonalityTraits(traits: string[] = []) {
              const standardTraits = [
                "extroverted",
                "introverted",
                "ambivert",
                "analytical",
                "creative",
                "ambitious",
                "practical_thinker",
              ];
              const customTraits = traits.filter(
                (t) => !standardTraits.includes(t)
              );
              return customTraits.join(", ");
            }

            // Check and add "other" to arrays if we have custom options
            if (
              stepData.step6.importantFacilitiesOther &&
              !stepData.step6.importantFacilities.includes("other")
            ) {
              stepData.step6.importantFacilities.push("other");
            }

            if (
              stepData.step7.selectionFactorsOther &&
              !stepData.step7.selectionFactors.includes("other")
            ) {
              stepData.step7.selectionFactors.push("other");
            }

            if (
              stepData.step8.personalityTraitsOther &&
              !stepData.step8.personalityTraits.includes("other")
            ) {
              stepData.step8.personalityTraits.push("other");
            }

            // Set each step's data
            if (stepData.step1) setStep1Data(stepData.step1);
            if (stepData.step2) setStep2Data(stepData.step2);
            if (stepData.step3) setStep3Data(stepData.step3);
            if (stepData.step4) setStep4Data(stepData.step4);
            if (stepData.step5) setStep5Data(stepData.step5);
            if (stepData.step6) setStep6Data(stepData.step6);
            if (stepData.step7) setStep7Data(stepData.step7);
            if (stepData.step8) setStep8Data(stepData.step8);

            console.log("Loaded profile data from API for:", user.username);
            setIsLoading(false);
            return true; // API fetch successful
          }
        } catch (error) {
          console.error("Error fetching profile data from API:", error);
        }
        return false; // API fetch failed
      };

      // Try API first, fall back to localStorage
      fetchProfileDataFromAPI().then((apiSuccess) => {
        if (!apiSuccess) {
          // Check for user-specific profile data in localStorage
          const userProfileKey = `profileData_${user.username}`;
          const savedData = localStorage.getItem(userProfileKey);

          if (savedData) {
            try {
              const data = JSON.parse(savedData);
              // Carefully load each step data
              if (data.step1) setStep1Data(data.step1);
              if (data.step2) setStep2Data(data.step2);
              if (data.step3) setStep3Data(data.step3);
              if (data.step4) setStep4Data(data.step4);
              if (data.step5) setStep5Data(data.step5);
              if (data.step6) setStep6Data(data.step6);
              if (data.step7) setStep7Data(data.step7);
              if (data.step8) setStep8Data(data.step8);

              console.log(
                "Loaded profile data from localStorage for:",
                user.username
              );
            } catch (error) {
              console.error("Error loading profile data:", error);
            }
          }
          setIsLoading(false);
        }
      });
    }
  }, [user?.username, authLoading]);

  // Once final step is done, combine everything and submit
  async function handleFinalSubmit() {
    if (!user?.username) {
      console.error("No user logged in");
      router.push("/auth");
      return;
    }

    // Format the data for API compatibility
    const combinedProfile = {
      preferred_fields: step1Data?.preferredFields || [],
      learning_style: step1Data?.learningStyle || "",
      career_goals: step1Data?.careerGoals ? [step1Data.careerGoals] : [],
      further_education: step1Data?.furtherEducation || "",
      culture_importance: step2Data?.cultureImportance || 5,
      interested_activities: step2Data?.extracurriculars || [],
      weekly_extracurricular_hours: parseInt(step2Data?.weeklyHours || "0"),
      passionate_activities: step2Data?.passionateActivities
        ? step2Data.passionateActivities.split(",").map((item) => item.trim())
        : [],
      internship_importance: step3Data?.internshipImportance || 5,
      leadership_interest: step3Data?.leadershipInterest === "yes",
      alumni_network_value: step3Data?.alumniNetworkValue || 5,
      affordability_importance: step4Data?.affordabilityImportance || 5,
      yearly_budget: parseInt(step4Data?.yearlyBudget || "0"),
      financial_aid_interest: step4Data?.financialAidInterest === "yes",
      preferred_region: step5Data?.preferredRegion || "",
      preferred_setting: step5Data?.preferredSetting || "",
      preferred_living_arrangement: step5Data?.preferredLivingArrangement || "",
      important_facilities: step6Data?.importantFacilities || [],
      modern_amenities_importance: step6Data?.modernAmenitiesImportance || 5,
      ranking_importance: step7Data?.rankingImportance || 5,
      alumni_testimonial_influence: step7Data?.alumniTestimonialInfluence || 5,
      important_selection_factors: step7Data?.selectionFactors || [],
      personality_traits: step8Data?.personalityTraits || [],
      preferred_student_population: step8Data?.studentPopulationSize || "",
      lifestyle_preferences: step8Data?.lifestylePreferences || "",
    };

    // Save user-specific data
    localStorage.setItem(
      `profileData_${user.username}`,
      JSON.stringify({
        step1: step1Data,
        step2: step2Data,
        step3: step3Data,
        step4: step4Data,
        step5: step5Data,
        step6: step6Data,
        step7: step7Data,
        step8: step8Data,
      })
    );

    // Save formatted data for recommendations
    const stringData = JSON.stringify(combinedProfile);
    localStorage.setItem("profileData", stringData);

    try {
      setIsSubmitting(true);
      const parsedData = JSON.parse(stringData);
      const result = await submitProfileForm(parsedData, user.username);

      if (result.success) {
        toast({
          title: "Profile saved successfully",
          description:
            "Your preferences have been saved. Generating recommendations...",
        });
      } else {
        toast({
          title: "Error saving profile",
          description: result.error || "Please try again",
          variant: "destructive",
        });
      }
    } catch (error) {
      console.error("Error in profile completion:", error);
      toast({
        title: "Error saving profile",
        description: "An unexpected error occurred. Please try again.",
        variant: "destructive",
      });
    } finally {
      setIsSubmitting(false);

      // Set a flag to prevent redirect loops
      localStorage.setItem("profileSubmitted", "true");

      // Navigate away to dashboard
      router.push("/profile/dashboard");
    }
  }

  // Save a step's data and advance to next step
  function handleStepSubmit(
    step: number,
    data:
      | Step1Data
      | Step2Data
      | Step3Data
      | Step4Data
      | Step5Data
      | Step6Data
      | Step7Data
      | Step8Data
  ) {
    // Update the state based on which step was completed
    switch (step) {
      case 1:
        setStep1Data(data as Step1Data);
        break;
      case 2:
        setStep2Data(data as Step2Data);
        break;
      case 3:
        setStep3Data(data as Step3Data);
        break;
      case 4:
        setStep4Data(data as Step4Data);
        break;
      case 5:
        setStep5Data(data as Step5Data);
        break;
      case 6:
        setStep6Data(data as Step6Data);
        break;
      case 7:
        setStep7Data(data as Step7Data);
        break;
      case 8:
        setStep8Data(data as Step8Data);
        break;
    }

    // If this is the last step, call the final submit handler
    if (step === 8) {
      handleFinalSubmit();
    } else {
      // Otherwise, advance to the next step
      setCurrentStep(step + 1);
    }

    // Save progress after each step
    if (user?.username) {
      const currentProgress: {
        step1: Step1Data | null;
        step2: Step2Data | null;
        step3: Step3Data | null;
        step4: Step4Data | null;
        step5: Step5Data | null;
        step6: Step6Data | null;
        step7: Step7Data | null;
        step8: Step8Data | null;
      } = {
        step1: step1Data,
        step2: step2Data,
        step3: step3Data,
        step4: step4Data,
        step5: step5Data,
        step6: step6Data,
        step7: step7Data,
        step8: step8Data,
      };

      // Update with the current step's data
      switch (step) {
        case 1:
          currentProgress.step1 = data as Step1Data;
          break;
        case 2:
          currentProgress.step2 = data as Step2Data;
          break;
        case 3:
          currentProgress.step3 = data as Step3Data;
          break;
        case 4:
          currentProgress.step4 = data as Step4Data;
          break;
        case 5:
          currentProgress.step5 = data as Step5Data;
          break;
        case 6:
          currentProgress.step6 = data as Step6Data;
          break;
        case 7:
          currentProgress.step7 = data as Step7Data;
          break;
        case 8:
          currentProgress.step8 = data as Step8Data;
          break;
      }

      localStorage.setItem(
        `profileData_${user.username}`,
        JSON.stringify(currentProgress)
      );
    }
  }

  // Function to go back to previous step
  function handleBack() {
    if (currentStep > 1) {
      setCurrentStep(currentStep - 1);
    }
  }

  if (isSubmitting) {
    <div className="flex flex-col items-center">
      <Loader2 className="h-8 w-8 animate-spin text-primary mb-4" />
      <p className="text-gray-600 mb-4">
        Please wait while we save your profile and prepare recommendations...
      </p>
    </div>;
  }

  // Show loading state while checking auth
  if (authLoading || isLoading) {
    return (
      <div className="container flex h-screen items-center justify-center">
        <div className="text-center">
          <h1 className="text-2xl font-bold mb-4">Loading...</h1>
        </div>
      </div>
    );
  }

  // Show not logged in state
  if (!user) {
    return (
      <div className="container flex h-screen items-center justify-center">
        <div className="text-center">
          <h1 className="text-2xl font-bold mb-4">Please log in to continue</h1>
          <p className="text-muted-foreground">Redirecting to login page...</p>
        </div>
      </div>
    );
  }

  function renderStep() {
    switch (currentStep) {
      case 1:
        return (
          <Step1Form
            initialData={step1Data}
            onNext={(data) => handleStepSubmit(1, data)}
          />
        );
      case 2:
        return (
          <Step2Form
            initialData={step2Data}
            onNext={(data) => handleStepSubmit(2, data)}
            onBack={handleBack}
          />
        );
      case 3:
        return (
          <Step3Form
            initialData={step3Data}
            onNext={(data) => handleStepSubmit(3, data)}
            onBack={handleBack}
          />
        );
      case 4:
        return (
          <Step4Form
            initialData={step4Data}
            onNext={(data) => handleStepSubmit(4, data)}
            onBack={handleBack}
          />
        );
      case 5:
        return (
          <Step5Form
            initialData={step5Data}
            onNext={(data) => handleStepSubmit(5, data)}
            onBack={handleBack}
          />
        );
      case 6:
        return (
          <Step6Form
            initialData={step6Data}
            onNext={(data) => handleStepSubmit(6, data)}
            onBack={handleBack}
          />
        );
      case 7:
        return (
          <Step7Form
            initialData={step7Data}
            onNext={(data) => handleStepSubmit(7, data)}
            onBack={handleBack}
          />
        );
      case 8:
        return (
          <Step8Form
            initialData={step8Data}
            onNext={(data) => handleStepSubmit(8, data)}
            onBack={handleBack}
          />
        );
      default:
        return null;
    }
  }

  return (
    <div className="container py-8 min-w-full">
      <Card className="w-full max-w-4xl mx-auto">
        <CardHeader>
          <CardTitle>Profile Setup</CardTitle>
          <CardDescription>Step {currentStep} of 8</CardDescription>
        </CardHeader>
        <CardContent>{renderStep()}</CardContent>
      </Card>
    </div>
  );
}
