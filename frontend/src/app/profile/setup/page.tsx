"use client";

import { useState, useEffect } from "react";
import { useRouter } from "next/navigation";

import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { saveQuestionnaire, type RecommendationRequest } from "@/api/apiClient";

// Import each step's form and types
import Step1Form, { Step1Data } from "./Step1Form";
import Step2Form, { Step2Data } from "./Step2Form";
import Step3Form, { Step3Data } from "./Step3Form";
import Step4Form, { Step4Data } from "./Step4Form";
import Step5Form, { Step5Data } from "./Step5Form";
import Step6Form, { Step6Data } from "./Step6Form";
import Step7Form, { Step7Data } from "./Step7Form";
import Step8Form, { Step8Data } from "./Step8Form";

export default function ProfileSetupPage() {
  const router = useRouter();

  // Track which step user is on
  const [currentStep, setCurrentStep] = useState(1);

  // Store partial data from each step
  const [step1Data, setStep1Data] = useState<Step1Data | null>(null);
  const [step2Data, setStep2Data] = useState<Step2Data | null>(null);
  const [step3Data, setStep3Data] = useState<Step3Data | null>(null);
  const [step4Data, setStep4Data] = useState<Step4Data | null>(null);
  const [step5Data, setStep5Data] = useState<Step5Data | null>(null);
  const [step6Data, setStep6Data] = useState<Step6Data | null>(null);
  const [step7Data, setStep7Data] = useState<Step7Data | null>(null);
  const [step8Data, setStep8Data] = useState<Step8Data | null>(null);

  // Load saved data when component mounts
  useEffect(() => {
    const savedData = localStorage.getItem("profileData");
    if (savedData) {
      const data = JSON.parse(savedData) as RecommendationRequest;
      
      // Distribute data to appropriate step states
      setStep1Data({
        preferredFields: data.preferred_fields,
        learningStyle: data.learning_style,
        careerGoals: data.career_goals[0] || "", // Take first item since form expects string
        furtherEducation: data.further_education,
      });

      setStep2Data({
        cultureImportance: data.culture_importance,
        extracurriculars: data.interested_activities,
        weeklyHours: data.weekly_extracurricular_hours.toString(),
        passionateActivities: data.passionate_activities.join(", "), // Join array to string for form
      });

      setStep3Data({
        internshipImportance: data.internship_importance,
        leadershipInterest: data.leadership_interest ? "yes" : "no",
        alumniNetworkValue: data.alumni_network_value,
      });

      setStep4Data({
        affordabilityImportance: data.affordability_importance,
        yearlyBudget: data.yearly_budget.toString(),
        financialAidInterest: data.financial_aid_interest ? "yes" : "no",
      });

      setStep5Data({
        preferredRegion: data.preferred_region,
        preferredSetting: data.preferred_setting,
        preferredLivingArrangement: data.preferred_living_arrangement,
      });

      setStep6Data({
        importantFacilities: data.important_facilities,
        modernAmenitiesImportance: data.modern_amenities_importance,
      });

      setStep7Data({
        rankingImportance: data.ranking_importance,
        alumniTestimonialInfluence: data.alumni_testimonial_influence,
        selectionFactors: data.important_selection_factors,
      });

      setStep8Data({
        personalityTraits: data.personality_traits,
        studentPopulationSize: data.preferred_student_population,
        lifestylePreferences: data.lifestyle_preferences,
      });
    }
  }, []);

  // Once final step is done, combine everything and submit
  async function handleFinalSubmit() {
    try {
      // Get the username from localStorage or your auth context
      const username = localStorage.getItem("username");
      if (!username) {
        throw new Error("User not authenticated");
      }

      // Combine all step data into the format expected by the API
      const finalData: RecommendationRequest = {
        algorithm: "hybrid", // Optional, defaults to "hybrid"
        num_results: 5, // Optional, defaults to 5
        preferred_fields: step1Data?.preferredFields || [],
        learning_style: step1Data?.learningStyle || "",
        career_goals: step1Data?.careerGoals ? [step1Data.careerGoals] : [],
        further_education: step1Data?.furtherEducation || "",
        culture_importance: step2Data?.cultureImportance || 5,
        interested_activities: step2Data?.extracurriculars || [],
        weekly_extracurricular_hours: parseInt(step2Data?.weeklyHours || "0"),
        passionate_activities: step2Data?.passionateActivities ? step2Data.passionateActivities.split(',').map(item => item.trim()) : [],
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
        lifestyle_preferences: step8Data?.lifestylePreferences || ""
      };

      // Save to localStorage for the dashboard to display it
      localStorage.setItem("profileData", JSON.stringify(finalData));

      // Send to backend using the API client
      await saveQuestionnaire(username, finalData);

      // Navigate to dashboard on success
      router.push("/profile/dashboard");
    } catch (error) {
      console.error("Error saving questionnaire:", error);
      // You might want to show an error message to the user here
      alert("Failed to save your profile. Please try again.");
    }
  }

  function renderStep() {
    switch (currentStep) {
      case 1:
        return (
          <Step1Form
            initialData={step1Data}
            onNext={(data) => {
              setStep1Data(data);
              setCurrentStep(2);
            }}
          />
        );
      case 2:
        return (
          <Step2Form
            initialData={step2Data}
            onNext={(data) => {
              setStep2Data(data);
              setCurrentStep(3);
            }}
            onBack={() => setCurrentStep(1)}
          />
        );
      case 3:
        return (
          <Step3Form
            initialData={step3Data}
            onNext={(data) => {
              setStep3Data(data);
              setCurrentStep(4);
            }}
            onBack={() => setCurrentStep(2)}
          />
        );
      case 4:
        return (
          <Step4Form
            initialData={step4Data}
            onNext={(data) => {
              setStep4Data(data);
              setCurrentStep(5);
            }}
            onBack={() => setCurrentStep(3)}
          />
        );
      case 5:
        return (
          <Step5Form
            initialData={step5Data}
            onNext={(data) => {
              setStep5Data(data);
              setCurrentStep(6);
            }}
            onBack={() => setCurrentStep(4)}
          />
        );
      case 6:
        return (
          <Step6Form
            initialData={step6Data}
            onNext={(data) => {
              setStep6Data(data);
              setCurrentStep(7);
            }}
            onBack={() => setCurrentStep(5)}
          />
        );
      case 7:
        return (
          <Step7Form
            initialData={step7Data}
            onNext={(data) => {
              setStep7Data(data);
              setCurrentStep(8);
            }}
            onBack={() => setCurrentStep(6)}
          />
        );
      case 8:
        return (
          <Step8Form
            initialData={step8Data}
            onNext={(data) => {
              setStep8Data(data);
              // We're done – handle final submission
              handleFinalSubmit();
            }}
            onBack={() => setCurrentStep(7)}
          />
        );
      default:
        return <div>Unknown step</div>;
    }
  }

  return (
    <div className="container flex h-screen flex-col">
      <div className="flex items-center justify-center mt-6">
        <Card className="w-[650px]">
          <CardHeader>
            <CardTitle>Profile Setup (Step {currentStep} of 8)</CardTitle>
            <CardDescription>Fill out each section to get recommendations.</CardDescription>
          </CardHeader>
          <CardContent>{renderStep()}</CardContent>
        </Card>
      </div>
    </div>
  );
}
