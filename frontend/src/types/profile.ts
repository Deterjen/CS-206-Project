export interface ProfileFormData {
  // Section 1: Academic Interest Similarity
  preferredFields: string[];
  learningStyle: string;
  careerGoals: string;
  furtherEducation: string;

  // Section 2: Social and Cultural Compatibility
  campusCultureImportance: number;
  extracurricularActivities: string[];
  extracurricularHours: string;
  specificActivities: string;

  // Section 3: Career Prospects
  internshipImportance: number;
  leadershipInterest: string;
  alumniNetworkValue: number;

  // Section 4: Financial Feasibility
  affordabilityImportance: number;
  budget: string;
  scholarshipInterest: string;

  // Section 5: Geographic Preferences
  preferredRegion: string;
  campusSetting: string;
  livingArrangement: string;

  // Section 6: Campus Facilities
  importantFacilities: string[];
  modernAmenitiesImportance: number;

  // Section 7: Reputation and Brand Value
  rankingImportance: number;
  testimonialInfluence: number;
  importantFactors: string[];

  // Section 8: Personal Fit
  personalityTraits: string[];
  preferredStudentSize: string;
  lifestylePreferences: string;
}

export const formOptions = {
  preferredFields: [
    "Business",
    "Computing/IT",
    "Engineering",
    "Sciences",
    "Social Sciences",
    "Arts & Humanities",
    "Medicine & Health",
    "Law",
    "Education",
    "Other",
  ],
  learningStyles: [
    "Hands-on/Practical",
    "Visual",
    "Auditory",
    "Theoretical",
    "Group-based",
    "Self-paced/Individual",
  ],
  furtherEducation: ["Yes", "No", "Undecided"],
  extracurricularActivities: [
    "Sports",
    "Arts & Culture",
    "Academic Clubs",
    "Community Service",
    "Professional/Career Clubs",
    "Social Clubs",
    "Other",
  ],
  extracurricularHours: [
    "0 (None)",
    "1–5 hours",
    "6–10 hours",
    "11–15 hours",
    "16–20 hours",
    "20+ hours",
  ],
  yesNo: ["Yes", "No"],
  campusSettings: ["Urban", "Rural"],
  livingArrangements: ["On Campus", "Off Campus", "Commute from Home"],
  facilities: [
    "Sports Facilities",
    "Libraries and Study Spaces",
    "On-Campus Housing",
    "Religious or Minority Support Centers",
    "Modern Amenities",
    "Other",
  ],
  importantFactors: [
    "Academic Reputation",
    "Location",
    "Campus Culture",
    "Affordability",
    "Scholarship Opportunities",
    "Internship Opportunities",
    "Modern Facilities",
    "Alumni Network Strength",
    "Other",
  ],
  personalityTraits: [
    "Extroverted",
    "Introverted",
    "Ambivert",
    "Analytical",
    "Creative",
    "Ambitious",
    "Practical Thinker",
  ],
  studentSizes: [
    "Small (<5K students)",
    "Medium (~10K students)",
    "Large (>20K students)",
  ],
};
