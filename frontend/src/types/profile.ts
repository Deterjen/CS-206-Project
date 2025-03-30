export interface ProfileFormData {
  // Section 1: Academic Preferences
  preferred_fields: string[];
  learning_style: string;
  career_goals: string;
  further_education: string;

  // Section 2: Extracurricular Activities
  culture_importance: number;
  interested_activities: string[];
  weekly_extracurricular_hours: string;
  passionate_activities: string;

  // Section 3: Career & Network
  internship_importance: number;
  leadership_interest: boolean;
  alumni_network_value: number;

  // Section 4: Financial & Location
  affordability_importance: number;
  yearly_budget: number;
  financial_aid_interest: boolean;
  preferred_region: string;
  preferred_setting: string;
  preferred_living_arrangement: string;

  // Section 5: Personal Preferences
  important_facilities: string[];
  modern_amenities_importance: number;
  ranking_importance: number;
  alumni_testimonial_influence: number;
  important_selection_factors: string[];
  personality_traits: string[];
  preferred_student_population: string;
  lifestyle_preferences: string;
}
