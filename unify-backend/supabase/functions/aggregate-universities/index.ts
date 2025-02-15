// functions/aggregate-universities/index.ts

import { createClient } from 'https://esm.sh/@supabase/supabase-js@2'
import { groupBy, meanBy, flatten, countBy, take } from 'https://esm.sh/lodash-es@4.17.21'
import { University } from "../shared/types.ts"

const format_university = (data: University): string => {
  return `
    University profile: ${data.university_name}
    Student satisfaction: ${data.average_satisfaction}/10
    Key attributes: ${data.selection_criteria.join(', ')}
    Known for: ${data.university_tags.join(', ')}
  `.trim();
}

Deno.serve(async (req) => {
  try {
    console.log('Starting university aggregation');

    // Initialize Supabase client
    const supabaseClient = createClient(
      Deno.env.get('SUPABASE_URL') ?? '',
      Deno.env.get('SUPABASE_SERVICE_ROLE_KEY') ?? ''
    );

    // Get all user profiles
    const { data: profiles, error: profilesError } = await supabaseClient
      .from('user_profiles')
      .select('*');

    if (profilesError) {
      console.error('Error fetching profiles:', profilesError);
      throw profilesError;
    }

    if (!profiles || profiles.length === 0) {
      console.error('No profiles found in database');
      throw new Error('No profiles found in database');
    }

    console.log(`Found ${profiles.length} profiles to process`);

    // Group profiles by university
    const universitiesData = groupBy(profiles, 'university');
    console.log('Universities to process:', Object.keys(universitiesData));

    const processedUniversities = [];
    const errors = [];

    // Process each university
    for (const [universityName, universityProfiles] of Object.entries(universitiesData)) {
      try {
        console.log(`\nProcessing ${universityName} with ${universityProfiles.length} profiles`);

        // Calculate aggregated data
        const average_satisfaction = Math.round(meanBy(universityProfiles, 'satisfaction') * 10) / 10;
        console.log(`Average satisfaction: ${average_satisfaction}`);

        // Aggregate selection criteria and tags
        const allSelectionCriteria = flatten(universityProfiles.map(p => 
          Array.isArray(p.selection_criteria) ? p.selection_criteria : []
        )).filter(Boolean);

        const allTags = flatten(universityProfiles.map(p => 
          Array.isArray(p.university_tags) ? p.university_tags : []
        )).filter(Boolean);

        console.log(`Found ${allSelectionCriteria.length} criteria and ${allTags.length} tags`);

        // Get most common criteria and tags (top 5)
        const selection_criteria = take(
          Object.entries(countBy(allSelectionCriteria))
            .sort((a, b) => b[1] - a[1])
            .map(([criteria]) => criteria),
          5
        );

        const university_tags = take(
          Object.entries(countBy(allTags))
            .sort((a, b) => b[1] - a[1])
            .map(([tag]) => tag),
          5
        );

        const universityData: University = {
          university_name: universityName,
          selection_criteria,
          average_satisfaction,
          university_tags
        };

        // Generate university embedding
        const { data: embedData, error: embedError } = await supabaseClient.functions.invoke('embed', {
          body: { 
            text: format_university(universityData)
          }
        });

        if (embedError) {
          console.error('Embedding error:', embedError);
          throw embedError;
        }

        // Check if embedding exists in response
        if (!embedData?.embedding) {
          console.error('Invalid embedding data:', embedData);
          throw new Error('No valid embedding received');
        }

        // Upsert university data
        const { data: insertedData, error: upsertError } = await supabaseClient
          .from('universities')
          .upsert({
            university_name: universityName,
            selection_criteria,
            average_satisfaction,
            university_tags,
            university_embedding: embedData.embedding
          })
          .select();

        if (upsertError) {
          console.error('Upsert error:', upsertError);
          throw upsertError;
        }

        processedUniversities.push(insertedData?.[0] || universityData);
        console.log(`Successfully processed ${universityName}`);

      } catch (error) {
        console.error(`Error processing ${universityName}:`, error);
        errors.push({
          university: universityName,
          error: error instanceof Error ? error.message : 'Unknown error'
        });
      }
    }

    // Final status check
    if (processedUniversities.length === 0) {
      throw new Error('No universities were successfully processed');
    }

    return new Response(
      JSON.stringify({
        success: true,
        processed: processedUniversities.length,
        errors: errors.length,
        errorDetails: errors
      }),
      { 
        status: 200,
        headers: { 
          'Content-Type': 'application/json'
        }
      }
    );

  } catch (error) {
    console.error('Aggregation failed:', error);
    return new Response(
      JSON.stringify({
        success: false,
        error: error instanceof Error ? error.message : 'Unknown error',
        errorDetails: error
      }),
      {
        status: 500,
        headers: { 
          'Content-Type': 'application/json'
        }
      }
    );
  }
});