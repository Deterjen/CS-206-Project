# Unify Backend

This project consists of two main parts:

1. `/data`: Used to generate a synthetic dataset.
2. `/unify-backend`: Used to run the Supabase backend.

## Getting Started

### Prerequisites

- Node.js (v14 or higher)
- Supabase CLI
- Deno (for VSCode integration)

### Setup

1. **Clone the repository**:

   ```sh
   git clone git@github.com:Deterjen/CS-206-Project.git
   cd CS-206-Project
   ```

2. **Install dependencies**:

   ```sh
   cd unify-backend
   npm install
   ```

3. **Configure Supabase**:

   - Ensure you have the Supabase CLI installed. Follow the instructions [here](https://supabase.com/docs/guides/cli).
   - Initialize Supabase in the [unify-backend](http://_vscodecontentref_/0) directory:
     ```sh
     npx supabase init
     ```
   - Start Supabase:
     ```sh
     npx supabase start
     ```

4. **Set up PostgreSQL Database**:
   - Ensure PostgreSQL is installed and running on your machine.
   - Run the [postgres.sql](http://_vscodecontentref_/3) file to set up the database schema:
     ```sh
     psql -U your_username -d your_database -f postgres.sql
     ```

### Generating Synthetic Data

1. Navigate to the [data](http://_vscodecontentref_/1) folder:

   ```sh
   cd data
   ```

2. Run the script to generate synthetic data:

   ```sh
   ts-node ./synthetic-data.mjs
   ```

3. The generated data will be saved in [output.csv](http://_vscodecontentref_/2).

### Running the Backend

1. Navigate to the [unify-backend](http://_vscodecontentref_/3) folder:

   ```sh
   cd unify-backend
   ```

2. Ensure Supabase is running:

   ```sh
   supabase start
   ```

3. Run the data processing pipeline:
   ```sh
   node data-processing-pipeline/data-processor.js
   ```

### Environment Variables

Ensure you have the following environment variables set in your `.env.local` file in the [unify-backend](http://_vscodecontentref_/5) directory:

> Environment Variables will be provided after `npx supabase start` perform `npx supabase status` to view it again

- SUPABASE_URL
- SUPABASE_ANON_KEY
- SUPABASE_SERVICE_ROLE_KEY

## Current Implementation

### 1. Core Flow

1. **Profile Embedding Generation**

   - Takes prospective student profile
   - Formats profile into structured text
   - Generates embedding using gte-small model (384 dimensions)

2. **Similar Profile Search**

   - Uses pgvector's `match_user_profiles` function
   - Finds top N similar profiles using cosine similarity
   - Current threshold: 0.7
   - Default limit: 10 similar profiles

3. **University Scoring**

   - Groups similar profiles by university
   - Calculates composite score using weighted components:
     - Vector similarity (40%)
     - Student satisfaction (30%)
     - Selection criteria match (20%)
     - University tags match (10%)

4. **Recommendation Filtering**
   - Filters universities by minimum satisfaction score
   - Sorts by composite similarity score
   - Returns top K recommendations

### 2. Scoring Formula

```javascript
compositeScore =
  avgSimilarity * 0.4 + // Vector similarity
  normalizedSatisfaction * 0.3 + // Satisfaction score
  criteriaMatch * 0.2 + // Matching criteria ratio
  tagsMatch * 0.1; // Matching tags ratio
```

## Optimization Opportunities

1. **Dynamic Weighting System**

   ```typescript
   // 1. Dynamic Weighting System
   interface WeightConfig {
     similarity: number;
     satisfaction: number;
     criteria: number;
     tags: number;
     demographicMatch: number;
     careerAlignment: number;
   }

   class DynamicWeightCalculator {
     private baseWeights: WeightConfig = {
       similarity: 0.4,
       satisfaction: 0.3,
       criteria: 0.2,
       tags: 0.1,
       demographicMatch: 0.0,
       careerAlignment: 0.0,
     };

     calculateWeights(profile: ProspectiveStudentProfile): WeightConfig {
       const weights = { ...this.baseWeights };

       // Adjust weights based on profile completeness and preferences
       if (profile.selection_criteria?.length > 5) {
         weights.criteria += 0.1;
         weights.similarity -= 0.1;
       }

       // Increase career alignment weight if career goal is specified
       if (profile.career_goal) {
         weights.careerAlignment = 0.15;
         weights.similarity -= 0.15;
       }

       // Adjust demographic weight based on specified preferences
       if (profile.population_preference || profile.campus_setting) {
         weights.demographicMatch = 0.1;
         weights.tags -= 0.1;
       }

       return this.normalizeWeights(weights);
     }

     private normalizeWeights(weights: WeightConfig): WeightConfig {
       const sum = Object.values(weights).reduce((a, b) => a + b, 0);
       return Object.fromEntries(
         Object.entries(weights).map(([k, v]) => [k, v / sum])
       ) as WeightConfig;
     }
   }
   ```

   - Adapts recommendation weights based on user profile characteristics
   - Considers factors like:
   - Profile completeness
   - Strength of preferences
   - Career goals
   - Demographic preferences
   - Automatically normalizes weights to ensure they sum to 1.0

2. **Enhanced Similarity Calculation**

   ```typescript
   // 2. Enhanced Similarity Calculation
   class SimilarityCalculator {
     calculateOverallSimilarity(
       profile1: UserProfile,
       profile2: UserProfile,
       weights: WeightConfig
     ): number {
       const vectorSim = this.calculateVectorSimilarity(
         profile1.user_embedding,
         profile2.user_embedding
       );

       const demographicSim = this.calculateDemographicSimilarity(
         profile1,
         profile2
       );
       const preferenceSim = this.calculatePreferenceSimilarity(
         profile1,
         profile2
       );
       const careerSim = this.calculateCareerAlignment(profile1, profile2);

       return (
         vectorSim * weights.similarity +
         demographicSim * weights.demographicMatch +
         preferenceSim * weights.criteria +
         careerSim * weights.careerAlignment
       );
     }

     private calculateDemographicSimilarity(
       profile1: UserProfile,
       profile2: UserProfile
     ): number {
       const factors = [
         profile1.age === profile2.age
           ? 1
           : 1 - Math.abs(profile1.age - profile2.age) / 10,
         profile1.nationality === profile2.nationality ? 1 : 0,
         profile1.qualification === profile2.qualification ? 1 : 0,
         1 - Math.abs(profile1.high_school_gpa - profile2.high_school_gpa),
       ];

       return factors.reduce((sum, factor) => sum + factor, 0) / factors.length;
     }

     private calculatePreferenceSimilarity(
       profile1: UserProfile,
       profile2: UserProfile
     ): number {
       const criteriaMatch = this.calculateArraySimilarity(
         profile1.selection_criteria,
         profile2.selection_criteria
       );

       const tagsMatch = this.calculateArraySimilarity(
         profile1.university_tags,
         profile2.university_tags
       );

       const preferencesMatch = [
         profile1.learning_style === profile2.learning_style ? 1 : 0,
         profile1.population_preference === profile2.population_preference
           ? 1
           : 0,
         profile1.campus_setting === profile2.campus_setting ? 1 : 0,
         1 - Math.abs(profile1.cost_importance - profile2.cost_importance) / 10,
       ];

       return (
         criteriaMatch * 0.4 +
         tagsMatch * 0.3 +
         (preferencesMatch.reduce((sum, match) => sum + match, 0) /
           preferencesMatch.length) *
           0.3
       );
     }

     private calculateArraySimilarity(arr1: string[], arr2: string[]): number {
       const intersection = arr1.filter((item) => arr2.includes(item));
       const union = Array.from(new Set([...arr1, ...arr2]));
       return intersection.length / union.length;
     }
   }
   ```

   - Multi-dimensional similarity scoring that considers:
   - Vector similarity (from embeddings)
   - Demographic similarity
   - Preference similarity
   - Career alignment
   - Granular matching for arrays (criteria, tags) using Jaccard similarity
   - Weighted combination of different similarity aspects

3. **Diversity-Aware Recommendations**

   ```typescript
   // 3. Diversity-Aware Recommendations
   class DiversityManager {
     private readonly maxRecommendationsPerCluster: number = 2;

     diversifyRecommendations(
       recommendations: UniversityRecommendation[],
       userProfile: ProspectiveStudentProfile
     ): UniversityRecommendation[] {
       const clusters = this.clusterUniversities(recommendations);
       const diversified: UniversityRecommendation[] = [];
       const clusterCounts = new Map<string, number>();

       // Sort recommendations by score within each cluster
       clusters.forEach((cluster) => {
         cluster.sort((a, b) => b.similarity_score - a.similarity_score);
       });

       // Select top recommendations while maintaining diversity
       while (diversified.length < recommendations.length) {
         let added = false;

         for (const cluster of clusters) {
           const count = clusterCounts.get(cluster[0]?.cluster_id || "") || 0;

           if (
             count < this.maxRecommendationsPerCluster &&
             cluster.length > 0
           ) {
             diversified.push(cluster.shift()!);
             clusterCounts.set(cluster[0]?.cluster_id || "", count + 1);
             added = true;
           }
         }

         if (!added) break;
       }

       return diversified;
     }

     private clusterUniversities(
       recommendations: UniversityRecommendation[]
     ): UniversityRecommendation[][] {
       // Group universities by similar characteristics
       const clusters = new Map<string, UniversityRecommendation[]>();

       recommendations.forEach((rec) => {
         const clusterId = this.determineCluster(rec);
         if (!clusters.has(clusterId)) {
           clusters.set(clusterId, []);
         }
         clusters.get(clusterId)!.push({ ...rec, cluster_id: clusterId });
       });

       return Array.from(clusters.values());
     }

     private determineCluster(university: UniversityRecommendation): string {
       // Determine cluster based on university characteristics
       const features = [
         university.average_satisfaction > 8
           ? "high_satisfaction"
           : "normal_satisfaction",
         this.getCampusType(university),
         this.getSpecializationType(university),
       ];

       return features.join("_");
     }
   }
   ```

   - Clusters universities based on characteristics
   - Limits recommendations per cluster to ensure diversity
   - Maintains balance between similarity and diversity
   - Considers multiple dimensions:
   - Satisfaction levels
   - Campus type
   - Specialization areas

4. **Contextual Boosting**

   ```typescript
   // 4. Contextual Recommendation Boosting
   class ContextualBooster {
     applyContextualBoosts(
       recommendations: UniversityRecommendation[],
       userProfile: ProspectiveStudentProfile
     ): UniversityRecommendation[] {
       return recommendations
         .map((rec) => {
           let boostMultiplier = 1.0;

           // Career alignment boost
           if (this.hasCareerAlignment(rec, userProfile)) {
             boostMultiplier *= 1.2;
           }

           // Learning style match boost
           if (this.matchesLearningPreference(rec, userProfile)) {
             boostMultiplier *= 1.15;
           }

           // Cost sensitivity boost
           if (this.matchesCostPreference(rec, userProfile)) {
             boostMultiplier *= 1.1;
           }

           // Location preference boost
           if (this.matchesLocationPreference(rec, userProfile)) {
             boostMultiplier *= 1.1;
           }

           return {
             ...rec,
             similarity_score: rec.similarity_score * boostMultiplier,
             boost_factors: {
               career_alignment: this.hasCareerAlignment(rec, userProfile),
               learning_style: this.matchesLearningPreference(rec, userProfile),
               cost_match: this.matchesCostPreference(rec, userProfile),
               location_match: this.matchesLocationPreference(rec, userProfile),
             },
           };
         })
         .sort((a, b) => b.similarity_score - a.similarity_score);
     }

     private hasCareerAlignment(
       recommendation: UniversityRecommendation,
       profile: ProspectiveStudentProfile
     ): boolean {
       return recommendation.career_outcomes?.includes(profile.career_goal);
     }

     private matchesLearningPreference(
       recommendation: UniversityRecommendation,
       profile: ProspectiveStudentProfile
     ): boolean {
       return recommendation.learning_environment === profile.learning_style;
     }
   }
   ```

   - Applies intelligent boost factors based on:
   - Career alignment (20% boost)
   - Learning style match (15% boost)
   - Cost preferences (10% boost)
   - Location preferences (10% boost)
   - Maintains ordered scoring while incorporating contextual factors

5. **Enhanced Explanation Generation**

   ```typescript
   // 5. Explanation Generator
   class RecommendationExplainer {
     generateExplanation(
       recommendation: UniversityRecommendation,
       userProfile: ProspectiveStudentProfile
     ): RecommendationExplanation {
       const matchingCriteria = recommendation.selection_criteria.filter((c) =>
         userProfile.selection_criteria.includes(c)
       );

       const matchingTags = recommendation.university_tags.filter((t) =>
         userProfile.university_tags.includes(t)
       );

       const strengthFactors = this.identifyStrengthFactors(
         recommendation,
         userProfile
       );

       const uniqueSellingPoints = this.identifyUniqueSellingPoints(
         recommendation,
         userProfile
       );

       return {
         matching_points: {
           criteria: matchingCriteria,
           tags: matchingTags,
           strength_factors: strengthFactors,
           unique_points: uniqueSellingPoints,
         },
         satisfaction_metrics: {
           overall_score: recommendation.average_satisfaction,
           career_satisfaction: recommendation.career_outcome_satisfaction,
           learning_environment_satisfaction:
             recommendation.learning_satisfaction,
         },
         personalization_factors: this.getPersonalizationFactors(
           recommendation,
           userProfile
         ),
         detailed_explanation: this.generateDetailedExplanation(
           recommendation,
           userProfile,
           {
             matchingCriteria,
             matchingTags,
             strengthFactors,
             uniqueSellingPoints,
           }
         ),
       };
     }

     private generateDetailedExplanation(
       recommendation: UniversityRecommendation,
       userProfile: ProspectiveStudentProfile,
       factors: {
         matchingCriteria: string[];
         matchingTags: string[];
         strengthFactors: string[];
         uniqueSellingPoints: string[];
       }
     ): string {
       return `
       ${
         recommendation.university_name
       } appears to be a strong match for your profile for several reasons:
       
       ${this.formatCriteriaMatch(factors.matchingCriteria)}
       ${this.formatEnvironmentMatch(recommendation, userProfile)}
       ${this.formatCareerAlignment(recommendation, userProfile)}
       ${this.formatUniqueBenefits(factors.uniqueSellingPoints)}
       
       The university has an average satisfaction rating of ${
         recommendation.average_satisfaction
       }/10 
       from students with similar profiles to yours.
       `.trim();
     }
   }

   // 6. Usage Example
   class UniversityRecommender {
     private weightCalculator = new DynamicWeightCalculator();
     private similarityCalculator = new SimilarityCalculator();
     private diversityManager = new DiversityManager();
     private contextualBooster = new ContextualBooster();
     private explainer = new RecommendationExplainer();

     async generateRecommendations(
       userProfile: ProspectiveStudentProfile,
       options: RecommendationOptions
     ): Promise<EnhancedRecommendation[]> {
       // 1. Calculate weights based on profile
       const weights = this.weightCalculator.calculateWeights(userProfile);

       // 2. Get initial recommendations using vector similarity
       let recommendations = await this.getInitialRecommendations(
         userProfile,
         weights,
         options
       );

       // 3. Apply diversity considerations
       recommendations = this.diversityManager.diversifyRecommendations(
         recommendations,
         userProfile
       );

       // 4. Apply contextual boosts
       recommendations = this.contextualBooster.applyContextualBoosts(
         recommendations,
         userProfile
       );

       // 5. Generate explanations
       return recommendations.map((rec) => ({
         ...rec,
         explanation: this.explainer.generateExplanation(rec, userProfile),
       }));
     }
   }
   ```

   - Provides detailed, personalized explanations including:
   - Matching criteria and tags
   - Strength factors
   - Unique selling points
   - Satisfaction metrics
   - Personalization factors

## License

This project is licensed under the ISC License.
