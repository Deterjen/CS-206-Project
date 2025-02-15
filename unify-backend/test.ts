import { createClient } from '@supabase/supabase-js'
import fs from 'fs'
import path from 'path'
import { fileURLToPath } from 'url'
import { TestResult } from './src/types'

// Load environment variables
import dotenv from 'dotenv'
dotenv.config({ path: '.env.local' })

const __filename = fileURLToPath(import.meta.url)
const __dirname = path.dirname(__filename)

// Initialize Supabase client
const supabaseUrl = process.env.SUPABASE_URL
const supabaseServiceKey = process.env.SUPABASE_SERVICE_ROLE_KEY

if (!supabaseUrl || !supabaseServiceKey) {
    throw new Error('Missing required environment variables')
}

const supabase = createClient(supabaseUrl, supabaseServiceKey)

async function runTest(testName: string, testFn: () => Promise<void>): Promise<TestResult> {
    try {
        await testFn()
        return { name: testName, success: true }
    } catch (error) {
        return {
            name: testName,
            success: false,
            error: error instanceof Error ? error.message : 'Unknown error',
            details: error
        }
    }
}

async function clearTestData() {
    console.log('Clearing test data...')
    await supabase.from('user_profiles').delete().neq('id', 0)
    await supabase.from('universities').delete().neq('id', 0)
    console.log('Test data cleared')
}

async function testEmbeddingGeneration() {
    console.log('\nTesting embedding generation...')

    const testProfile = {
        age: 18,
        gender: "Male",
        nationality: "Singapore",
        qualification: "A Levels",
        high_school_gpa: 4.0,
        university: "NUS",
        major: "Computer Science",
        selection_criteria: ["Academic reputation", "Research opportunities"],
        considered_others: true,
        second_choice: "NTU",
        satisfaction: 8,
        university_tags: ["Research", "Technology"],
        learning_style: "Visual",
        population_preference: "Large",
        campus_setting: "Urban",
        cost_importance: 7,
        scholarship: true,
        living: "On campus",
        career_goal: "Software Engineer",
        internship_importance: 9,
        university_internship: true,
        family_influence: 6,
        friend_influence: 5,
        social_media_influence: 4,
        ranking_influence: 8
    }

    const { data: embedData, error: embedError } = await supabase.functions.invoke('embed', {
        body: { text: JSON.stringify(testProfile) }
    })

    if (embedError) {
        throw new Error(`Embedding generation failed: ${embedError.message}`)
    }

    if (!embedData.embedding || !Array.isArray(embedData.embedding) || embedData.embedding.length !== 384) {
        throw new Error('Invalid embedding generated')
    }

    console.log('Embedding generation successful')
}

async function testDataProcessing() {
    console.log('\nTesting data processing...')

    // Read sample data from CSV
    const csvPath = path.join(__dirname, '/data/output.csv')
    const csvContent = fs.readFileSync(csvPath, 'utf-8')

    // Process data using the process-data function
    const { data, error } = await supabase.functions.invoke('process-data', {
        body: csvContent
    })

    if (error) {
        throw new Error(`Data processing failed: ${error.message}`)
    }

    if (!data.success) {
        throw new Error(`Data processing failed: ${data.error || 'Unknown error'}`)
    }

    console.log(`Processed ${data.processed} profiles`)
    if (data.errors.length > 0) {
        console.warn(`Encountered ${data.errors.length} errors during processing`)
        console.warn('Error details:', data.errorDetails)
    }

    // Verify data was stored in the database
    const { data: storedProfiles, error: queryError } = await supabase
        .from('user_profiles')
        .select('*')

    if (queryError) throw queryError

    if (!storedProfiles || storedProfiles.length === 0) {
        throw new Error('No profiles were stored in the database')
    }

    console.log(`Successfully stored ${storedProfiles.length} profiles in the database`)
}

async function testUniversityAggregation() {
    console.log('\nTesting university aggregation...')

    // First verify we have user profiles in the database
    const { data: userProfiles, error: profileError } = await supabase
        .from('user_profiles')
        .select('*')

    if (profileError) {
        throw new Error(`Failed to fetch user profiles: ${profileError.message}`)
    }

    if (!userProfiles || userProfiles.length === 0) {
        throw new Error('No user profiles found in database. Please run data processing first.')
    }

    console.log(`Found ${userProfiles.length} user profiles to aggregate`)

    // Log unique universities in profiles
    const uniqueUniversities = [...new Set(userProfiles.map(p => p.university))]
    console.log('Universities found in profiles:', uniqueUniversities)

    // Run university aggregation
    const { data: aggregationResult, error: aggregationError } = await supabase.functions.invoke('aggregate-universities')

    if (aggregationError) {
        throw new Error(`University aggregation failed: ${aggregationError.message}`)
    }

    if (!aggregationResult.success) {
        console.error('Aggregation response:', aggregationResult)
        throw new Error(`University aggregation failed: ${aggregationResult.error || 'Unknown error'}`)
    }

    // Give a small delay to ensure database writes are complete
    await new Promise(resolve => setTimeout(resolve, 2000))

    // Verify universities were created
    const { data: universities, error: queryError } = await supabase
        .from('universities')
        .select('*')

    if (queryError) {
        console.error('Error querying universities:', queryError)
        throw queryError
    }

    console.log('Universities after aggregation:', universities ? universities.length : 0)

    if (!universities || universities.length === 0) {
        const { data: errorLog, error: logError } = await supabase
            .from('error_logs')
            .select('*')
            .order('created_at', { ascending: false })
            .limit(5)

        if (!logError && errorLog) {
            console.error('Recent error logs:', errorLog)
        }

        throw new Error('No universities were created during aggregation')
    }

    console.log(`Successfully aggregated data for ${universities.length} universities:`)
    universities.forEach(uni => {
        console.log(`- ${uni.university_name}:`)
        console.log(`  Satisfaction: ${uni.average_satisfaction}`)
        console.log(`  Tags: ${uni.university_tags.join(', ')}`)
    })

    if (aggregationResult.errors && aggregationResult.errors.length > 0) {
        console.warn(`Encountered ${aggregationResult.errors.length} errors during aggregation`)
        console.warn('Error details:', aggregationResult.errorDetails)
    }
}

async function testRecommendations() {
    console.log('\nTesting recommendation system...')

    const testProfile = {
        age: 19,
        gender: 'Female',
        nationality: 'Singapore',
        qualification: 'A Levels',
        high_school_gpa: 3.8,
        selection_criteria: ['Job prospects', 'Campus life'],
        university_tags: ['Business', 'Urban'],
        learning_style: 'Hands-on',
        population_preference: 'Medium',
        campus_setting: 'Urban',
        cost_importance: 8,
        scholarship: false,
        living: 'Off campus',
        career_goal: 'Management Consultant',
        internship_importance: 9,
        university_internship: true,
        family_influence: 7,
        friend_influence: 6,
        social_media_influence: 5,
        ranking_influence: 8
    }

    const { data, error } = await supabase.functions.invoke('recommend-universities', {
        body: {
            userProfile: testProfile,
            limit: 3,
            minSatisfaction: 7
        }
    })

    if (error) {
        throw new Error(`Recommendation generation failed: ${error.message}`)
    }

    if (!data.success || !data.recommendations) {
        throw new Error('Failed to generate recommendations')
    }

    if (data.recommendations.length === 0) {
        throw new Error('No recommendations generated')
    }

    console.log('Recommendation system test successful')
    console.log('Sample recommendations:');
    data.recommendations.forEach((r: { university_name: any; similarity_score: number; average_satisfaction: any; num_similar_profiles: any; matching_criteria_ratio: number; matching_tags_ratio: number }) => {
        console.log(`${r.university_name}:
        - Similarity Score: ${(r.similarity_score * 100).toFixed(1)}%
        - Average Satisfaction: ${(r.average_satisfaction).toFixed(1)}/10
        - Similar Profiles: ${r.num_similar_profiles}
        - Matching Criteria: ${(r.matching_criteria_ratio * 100).toFixed(1)}%
        - Matching Tags: ${(r.matching_tags_ratio * 100).toFixed(1)}%`
        );
    });
}

async function runAllTests() {
    console.log('Starting test suite...\n')

    const tests = [
        {
            name: 'Embedding Generation',
            fn: testEmbeddingGeneration,
            description: 'Testing the embedding generation functionality'
        },
        {
            name: 'Data Processing',
            fn: testDataProcessing,
            description: 'Processing survey data and storing user profiles'
        },
        {
            name: 'University Aggregation',
            fn: testUniversityAggregation,
            description: 'Aggregating university data from user profiles'
        },
        {
            name: 'Recommendation System',
            fn: testRecommendations,
            description: 'Testing university recommendations based on user profile'
        }
    ] as const

    const results: TestResult[] = []
    let allPassed = true

    for (const test of tests) {
        console.log(`\n🔄 Running: ${test.name}`)
        console.log(`Description: ${test.description}`)
        
        const result = await runTest(test.name, test.fn)
        results.push(result)

        if (!result.success) {
            console.log(`\n❌ ${test.name} failed:`)
            console.log(`   Error: ${result.error}`)
            if (result.details) {
                console.log('   Details:', result.details)
            }
            allPassed = false
            break // Stop testing if any test fails
        } else {
            console.log(`\n✅ ${test.name} completed successfully`)
        }

        // Add a small delay between tests to ensure proper sequencing
        await new Promise(resolve => setTimeout(resolve, 1000))
    }

    console.log('\n📊 Test Summary:')
    const successful = results.filter(r => r.success).length
    const failed = results.length - successful
    const skipped = tests.length - results.length

    console.log(`✅ Passed: ${successful}`)
    console.log(`❌ Failed: ${failed}`)
    if (skipped > 0) {
        console.log(`⏭️  Skipped: ${skipped} (due to previous failure)`)
    }

    if (!allPassed) {
        console.log('\n❌ Test suite failed - stopping here')
        process.exit(1)
    } else {
        console.log('\n✅ All tests passed successfully')
    }
}

// Main execution
const main = async () => {
    try {
        await clearTestData()
        await runAllTests()
    } catch (error) {
        console.error('Test suite failed:', error)
        process.exit(1)
    }
}

main()