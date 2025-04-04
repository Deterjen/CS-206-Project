import { ProfileFormData } from "@/types/profile";
import { recommendationService } from "@/api/services";

export async function submitProfileForm(data: ProfileFormData, username: string) {
  try {
    // Convert the form data to match the API request format
    const requestData = {
      ...data,
      // Ensure career_goals is an array
      career_goals: typeof data.career_goals === 'string' 
        ? [data.career_goals] 
        : data.career_goals,
      // Convert passionate_activities to array if it's a string
      passionate_activities: typeof data.passionate_activities === 'string' 
        ? [data.passionate_activities] 
        : data.passionate_activities,
    };

    await recommendationService.saveQuestionnaire(username, requestData);
    return { success: true };
  } catch (error) {
    console.error("Error saving questionnaire:", error);
    return { 
      success: false, 
      error: error instanceof Error ? error.message : "Failed to save your profile" 
    };
  }
}