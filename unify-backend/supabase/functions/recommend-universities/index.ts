// functions/recommend-universities/index.ts

import { createClient } from 'https://esm.sh/@supabase/supabase-js@2'
import { groupBy, meanBy } from 'https://esm.sh/lodash-es@4.17.21'

interface ProspectiveStudentProfile {
  age: number;
  gender: string;
  nationality: string;
  qualification: string;
  high_school_gpa: number;
  selection_criteria: string[];
  university_tags: string[];
  learning_style: string;
  population_preference: string;
  campus_setting: string;
  cost_importance: number;
  scholarship: boolean;
  living: string;
  career_goal: string;
  internship_importance: number;
  university_internship: boolean;
  family_influence: number;
  friend_influence: number;
  social_media_influence: number;
  ranking_influence: number;
}

interface RecommendationRequest {
  userProfile: ProspectiveStudentProfile;
  limit?: number;
  minSatisfaction?: number;
  similarProfilesCount?: number;
}

const format_profile = (profile: ProspectiveStudentProfile): string => {
  return `
    Prospective student profile: ${profile.age} year old ${profile.gender} from ${profile.nationality}.
    Academic background: ${profile.qualification} with GPA ${profile.high_school_gpa}.
    Career goal: Aims to be a ${profile.career_goal}.
    Learning preferences: Prefers ${profile.learning_style} learning in a ${profile.campus_setting} setting with ${profile.population_preference} student population.
    Values: Prioritizes ${profile.selection_criteria.join(', ')}.
    Interests: ${profile.university_tags.join(', ')}.
    Living arrangement: ${profile.living}.
    Financial aspects: Cost importance ${profile.cost_importance}/10, Scholarship status: ${profile.scholarship ? 'Yes' : 'No'}.
    Internships: Importance ${profile.internship_importance}/10, University internship program: ${profile.university_internship ? 'Yes' : 'No'}.
    Decision influences: Family (${profile.family_influence}/10), Friends (${profile.friend_influence}/10), Social Media (${profile.social_media_influence}/10), Rankings (${profile.ranking_influence}/10).
  `.trim();
}

Deno.serve(async (req) => {
  try {
    console.log('Starting recommendation process');

    const { 
      userProfile, 
      limit = 3, 
      minSatisfaction = 7,
      similarProfilesCount = 10 
    } = await req.json() as RecommendationRequest;

    console.log('Received request:', { limit, minSatisfaction, similarProfilesCount });
    console.log('User profile:', userProfile);

    // Validate required fields
    const requiredFields = [
      'age', 'gender', 'nationality', 'qualification', 'high_school_gpa',
      'selection_criteria', 'university_tags', 'learning_style',
      'population_preference', 'campus_setting', 'cost_importance',
      'scholarship', 'living', 'career_goal', 'internship_importance',
      'university_internship', 'family_influence', 'friend_influence',
      'social_media_influence', 'ranking_influence'
    ];

    const missingFields = requiredFields.filter(field => !(field in userProfile));
    if (missingFields.length > 0) {
      throw new Error(`Missing required fields: ${missingFields.join(', ')}`);
    }

    // Initialize Supabase client
    console.log('Initializing Supabase client');
    const supabaseClient = createClient(
      Deno.env.get('SUPABASE_URL') ?? '',
      Deno.env.get('SUPABASE_SERVICE_ROLE_KEY') ?? ''
    );

    // Generate embedding for the prospective student's profile
    console.log('Generating embedding for profile');
    const { data: embedData, error: embedError } = await supabaseClient.functions.invoke('embed', {
      body: { text: format_profile(userProfile) }
    });

    if (embedError) {
      console.error('Embedding error:', embedError);
      throw new Error(`Failed to generate embedding: ${embedError.message}`);
    }

    if (!embedData?.embedding) {
      console.error('Invalid embedding data:', embedData);
      throw new Error('No valid embedding received from embedding function');
    }

    console.log('Embedding generated successfully');

    // Find similar profiles
    console.log('Finding similar profiles');
    const { data: similarProfiles, error: searchError } = await supabaseClient
      .rpc('match_user_profiles', {
        query_embedding: embedData.embedding,
        match_threshold: 0.7,
        match_count: similarProfilesCount
      });

    if (searchError) {
      console.error('Search error:', searchError);
      throw searchError;
    }

    console.log(`Found ${similarProfiles?.length || 0} similar profiles`);

    if (!similarProfiles || similarProfiles.length === 0) {
      return new Response(
        JSON.stringify({
          success: true,
          recommendations: [],
          metadata: {
            message: 'No similar profiles found'
          }
        }),
        { headers: { 'Content-Type': 'application/json' } }
      );
    }

    // Group similar profiles by university
    const profilesByUniversity = groupBy(similarProfiles, 'university');
    console.log('Universities found:', Object.keys(profilesByUniversity));

    // Calculate scores for each university
    const universityScores = Object.entries(profilesByUniversity).map(([university, profiles]) => {
      const avgSatisfaction = meanBy(profiles, 'satisfaction');
      const avgSimilarity = meanBy(profiles, 'similarity');
      
      // Calculate criteria and tag matches
      const criteriaMatch = profiles.filter(p => 
        p.selection_criteria.some(c => userProfile.selection_criteria.includes(c))
      ).length / profiles.length;
      
      const tagsMatch = profiles.filter(p =>
        p.university_tags.some(t => userProfile.university_tags.includes(t))
      ).length / profiles.length;

      // Normalize satisfaction score to 0-1 range (from 0-10 range)
      const normalizedSatisfaction = avgSatisfaction / 10;
      
      // Calculate composite score (all components are now in 0-1 range)
      const compositeScore = (
        avgSimilarity * 0.4 +          // Already in 0-1 range from vector similarity
        normalizedSatisfaction * 0.3 +  // Normalized from 0-10 to 0-1 range
        criteriaMatch * 0.2 +           // Already in 0-1 range (ratio)
        tagsMatch * 0.1                 // Already in 0-1 range (ratio)
      );

      return {
        university_name: university,
        similarity_score: compositeScore,
        average_satisfaction: avgSatisfaction,
        num_similar_profiles: profiles.length,
        matching_criteria_ratio: criteriaMatch,
        matching_tags_ratio: tagsMatch
      };
    });

    // Filter and sort recommendations
    console.log('Filtering and sorting recommendations');
    const recommendations = universityScores
      .filter(uni => uni.average_satisfaction >= minSatisfaction)
      .sort((a, b) => b.similarity_score - a.similarity_score)
      .slice(0, limit);

    // Final response
    return new Response(
      JSON.stringify({
        success: true,
        recommendations,
        metadata: {
          similar_profiles_found: similarProfiles.length,
          universities_considered: universityScores.length
        }
      }),
      { headers: { 'Content-Type': 'application/json' } }
    );

  } catch (error) {
    console.error('Recommendation error:', error);
    return new Response(
      JSON.stringify({
        success: false,
        error: error instanceof Error ? error.message : 'Unknown error'
      }),
      {
        status: 500,
        headers: { 'Content-Type': 'application/json' }
      }
    );
  }
});