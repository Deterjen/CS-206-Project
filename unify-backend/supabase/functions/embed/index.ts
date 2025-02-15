// functions/embed/index.ts

import "jsr:@supabase/functions-js/edge-runtime.d.ts"
const session = new Supabase.ai.Session('gte-small');

Deno.serve(async (req) => {
  try {
    const { text } = await req.json();

    // Generate the embedding
    const embedding = await session.run(text, {
      mean_pool: true,
      normalize: true,
    });

    return new Response(
      JSON.stringify({ embedding }),
      { headers: { 'Content-Type': 'application/json' } }
    );
  } catch (error) {
    return new Response(
      JSON.stringify({ error: error.message }),
      {
        status: 400,
        headers: { 'Content-Type': 'application/json' }
      }
    );
  }
});