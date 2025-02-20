// functions/embed/index.ts

import "jsr:@supabase/functions-js/edge-runtime.d.ts"
const session = new Supabase.ai.Session('gte-small');

// Helper function to sanitize embeddings for JSON compatibility
function sanitizeEmbedding(embedding: number[]): number[] {
  if (!Array.isArray(embedding)) {
    return [];
  }

  return embedding.map(value => {
    // Check for NaN or Infinity
    if (typeof value !== 'number' || !Number.isFinite(value)) {
      return 0.0;
    }
    // Ensure values are within safe JSON range
    return Math.max(Math.min(value, 1e38), -1e38);
  });
}

Deno.serve(async (req) => {
  try {
    const { texts, batchMode = false } = await req.json();

    // Validate inputs
    if (!Array.isArray(texts)) {
      throw new Error("Invalid input: 'texts' must be an array of strings.");
    }

    let embeddings;

    if (batchMode) {
      // BATCH MODE: texts is an array of strings
      if (!texts.every(item => typeof item === 'string')) {
        throw new Error("Batch mode requires an array of strings.");
      }

      try {
        // Generate all embeddings in one call with error handling for each item
        const flatEmbeddings = await Promise.all(
          texts.map(async (text) => {
            try {
              return await session.run(text, {
                mean_pool: true,
                normalize: true,
              });
            } catch (err) {
              console.error(`Error generating embedding: ${err.message}`);
              // Return zero vector of appropriate size (384 for gte-small)
              return new Array(384).fill(0);
            }
          })
        );

        // Sanitize embeddings
        embeddings = flatEmbeddings.map(sanitizeEmbedding);
      } catch (batchError) {
        console.error(`Batch embedding error: ${batchError.message}`);
        // Create empty embeddings as fallback
        embeddings = texts.map(() => new Array(384).fill(0));
      }
    } else {
      // SINGLE MODE: Just one text
      if (texts.length !== 1) {
        throw new Error("Single mode requires exactly one text.");
      }

      try {
        // Normalize text to prevent null/undefined errors
        const normalizedText = String(texts[0] || "").trim() || "empty";

        // Generate the embedding with proper error handling
        const singleEmbedding = await session.run(normalizedText, {
          mean_pool: true,
          normalize: true,
        });

        // Sanitize embedding
        embeddings = [sanitizeEmbedding(singleEmbedding)];
      } catch (singleError) {
        console.error(`Single embedding error: ${singleError.message}`);
        embeddings = [new Array(384).fill(0)];
      }
    }

    return new Response(
      JSON.stringify({ embeddings }),
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