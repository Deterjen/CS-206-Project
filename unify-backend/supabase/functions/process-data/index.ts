// functions/process-data/index.ts

import "jsr:@supabase/functions-js/edge-runtime.d.ts"
import { createClient } from 'https://esm.sh/@supabase/supabase-js@2'
import Papa from 'https://esm.sh/papaparse@5.4.1'
import { UserProfile } from '../shared/types.ts'

const format_userprofile = (data: UserProfile): string => {
  return `
    Student profile: ${data.age} year old ${data.gender} from ${data.nationality}.
    Academic background: ${data.qualification} with GPA ${data.high_school_gpa}, studying ${data.major}.
    Career goal: Aims to be a ${data.career_goal}.
    Learning preferences: Prefers ${data.learning_style} learning in a ${data.campus_setting} setting with ${data.population_preference} student population.
    Values: Prioritizes ${data.selection_criteria.join(', ')}.
    University interests: ${data.university_tags.join(', ')}.
    Living arrangement: ${data.living}.
    Financial aspects: Cost importance ${data.cost_importance}/10, Scholarship status: ${data.scholarship ? 'Yes' : 'No'}.
    Internships: Importance ${data.internship_importance}/10, University internship program: ${data.university_internship ? 'Yes' : 'No'}.
    Decision influences: Family (${data.family_influence}/10), Friends (${data.friend_influence}/10), Social Media (${data.social_media_influence}/10), Rankings (${data.ranking_influence}/10).
    University choices: ${data.considered_others ? `Considered others, second choice: ${data.second_choice}` : 'Did not consider others'}.
  `.trim();
}

Deno.serve(async (req) => {
  try {
    const csvContent = await req.text();

    // Parse CSV data
    const { data: surveyResponses, errors: parseErrors } = Papa.parse(csvContent, {
      header: true,
      dynamicTyping: true,
      skipEmptyLines: true
    });

    if (parseErrors.length > 0) {
      throw new Error(`CSV parsing errors: ${JSON.stringify(parseErrors)}`);
    }

    // Initialize Supabase client
    const supabaseClient = createClient(
      Deno.env.get('SUPABASE_URL') ?? '',
      Deno.env.get('SUPABASE_SERVICE_ROLE_KEY') ?? ''
    );

    const processedProfiles = [];
    const errors = [];

    // Process each survey response
    for (const response of surveyResponses) {
      try {
        // Convert survey response to UserProfile format
        const userProfile: UserProfile = {
          age: response.age,
          gender: response.gender,
          nationality: response.nationality,
          qualification: response.qualification,
          high_school_gpa: response.high_school_gpa,
          university: response.university,
          major: response.major,
          selection_criteria: Array.isArray(response.selection_criteria) 
            ? response.selection_criteria 
            : response.selection_criteria.split(',').map(s => s.trim()),
          considered_others: Boolean(response.considered_others),
          second_choice: response.second_choice,
          satisfaction: parseInt(response.satisfaction),
          university_tags: Array.isArray(response.university_tags)
            ? response.university_tags
            : response.university_tags.split(',').map(s => s.trim()),
          learning_style: response.learning_style,
          population_preference: response.population_preference,
          campus_setting: response.campus_setting,
          cost_importance: parseInt(response.cost_importance),
          scholarship: Boolean(response.scholarship),
          living: response.living,
          career_goal: response.career_goal,
          internship_importance: response.internship_importance,
          university_internship: Boolean(response.university_internship),
          family_influence: response.family_influence,
          friend_influence: response.friend_influence,
          social_media_influence: response.social_media_influence,
          ranking_influence: response.ranking_influence
        };

        // Generate embedding
        const { data: embedData, error: embedError } = await supabaseClient.functions.invoke('embed', {
          body: { text: format_userprofile(userProfile) }
        });

        if (embedError) {
          throw new Error(`Failed to generate embedding: ${embedError.message}`);
        }

        const { embedding } = embedData;

        // Insert into database
        const { data, error: insertError } = await supabaseClient
          .from('user_profiles')
          .insert([{
            ...userProfile,
            user_embedding: embedding
          }])
          .select();

        if (insertError) throw insertError;
        processedProfiles.push(data[0]);

      } catch (error) {
        errors.push({
          profile: response,
          error: error instanceof Error ? error.message : 'Unknown error'
        });
      }
    }

    return new Response(
      JSON.stringify({
        success: true,
        processed: processedProfiles.length,
        errors: errors.length,
        errorDetails: errors
      }),
      { headers: { 'Content-Type': 'application/json' } }
    );

  } catch (error) {

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