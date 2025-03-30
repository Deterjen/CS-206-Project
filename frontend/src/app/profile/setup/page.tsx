"use client";

import { useState, useEffect } from "react";
import { useRouter } from "next/navigation";
import { useAuthContext } from "@/providers/AuthProvider";

import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";

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
      // Check for user-specific profile data
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
          
          console.log("Loaded profile data for:", user.username);
        } catch (error) {
          console.error("Error loading profile data:", error);
        }
      }
      setIsLoading(false);
    }
  }, [user?.username, authLoading]);

  // Once final step is done, combine everything and submit
  function handleFinalSubmit() {
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

    // Save user-specific data
    localStorage.setItem(`profileData_${user.username}`, JSON.stringify({
      step1: step1Data,
      step2: step2Data,
      step3: step3Data,
      step4: step4Data,
      step5: step5Data,
      step6: step6Data,
      step7: step7Data,
      step8: step8Data,
    }));

    // Save formatted data for recommendations
    localStorage.setItem("profileData", JSON.stringify(combinedProfile));

    // Set a flag to prevent redirect loops 
    localStorage.setItem("profileSubmitted", "true");

    // Navigate away to dashboard
    router.push("/profile/dashboard");
  }

  // Save a step's data and advance to next step
  function handleStepSubmit(step: number, data: Step1Data | Step2Data | Step3Data | Step4Data | Step5Data | Step6Data | Step7Data | Step8Data) {
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
      
      localStorage.setItem(`profileData_${user.username}`, JSON.stringify(currentProgress));
    }
  }

  // Function to go back to previous step
  function handleBack() {
    if (currentStep > 1) {
      setCurrentStep(currentStep - 1);
    }
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
    <div className="container py-8">
      <Card className="w-full max-w-4xl mx-auto">
        <CardHeader>
          <CardTitle>Profile Setup</CardTitle>
          <CardDescription>Step {currentStep} of 8</CardDescription>
        </CardHeader>
        <CardContent>
          {renderStep()}
        </CardContent>
      </Card>
    </div>
  );
}
