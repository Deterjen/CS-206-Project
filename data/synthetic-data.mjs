const universities = ['NUS', 'NTU', 'SMU', 'SUTD', 'SUSS'];
const genders = ['Male', 'Female', 'Other', 'Prefer not to say'];
const nationalities = ['Singaporean', 'Malaysian', 'Indonesian', 'Chinese', 'Indian', 'Vietnamese', 'Other Asian'];
const qualifications = ['A-Levels', 'IB', 'Polytechnic Diploma', 'High School Diploma'];
const learningStyles = ['Lecture-Based', 'Hands-On', 'Research-Driven', 'Online/Hybrid'];
const populationPreference = ['Small', 'Medium', 'Large'];
const campusSettings = ['Urban', 'Suburban'];
const livingArrangement = ['On Campus', 'Commute'];
const majors = {
    'NUS': ['Computer Science', 'Business Analytics', 'Medicine', 'Law', 'Engineering', 'Arts and Social Sciences'],
    'NTU': ['Computer Science', 'Engineering', 'Business', 'Communications', 'Science', 'Art, Design & Media'],
    'SMU': ['Business Management', 'Information Systems', 'Economics', 'Law', 'Accountancy', 'Computing & Law'],
    'SUTD': ['Engineering Systems & Design', 'Information Systems Technology & Design', 'Architecture & Sustainable Design'],
    'SUSS': ['Business Analytics', 'Early Childhood Education', 'Social Work', 'Supply Chain Management']
};
const careerGoals = ['Industry Professional', 'Researcher', 'Entrepreneur', 'Government', 'NGO/Non-profit'];
const universityTags = {
    'NUS': ['Research Oriented', 'Global Recognition', 'Comprehensive Programs', 'Strong Alumni Network'],
    'NTU': ['Smart Campus', 'Research Excellence', 'Industry Connections', 'Sustainable Focus'],
    'SMU': ['City Campus', 'Interactive Learning', 'Professional Network', 'Business Focus'],
    'SUTD': ['Design Innovation', 'Technology Focus', 'Small Class Size', 'Industry Collaboration'],
    'SUSS': ['Flexible Learning', 'Work-Study Integration', 'Lifelong Learning', 'Practice-Oriented']
};

function generateRandomResponse(university) {
    const response = {
        age: Math.floor(Math.random() * (25 - 19) + 19),
        gender: genders[Math.floor(Math.random() * genders.length)],
        nationality: nationalities[Math.floor(Math.random() * nationalities.length)],
        qualification: qualifications[Math.floor(Math.random() * qualifications.length)],
        highSchoolGPA: (Math.random() * (4.0 - 3.0) + 3.0).toFixed(2),
        university: university,
        selectionCriteria: (() => {
            const criteria = ['Ranking', 'Tuition Fees', 'Scholarships', 'Reputation', 'Campus Facilities',
                'Location', 'Job Placement Rate', 'Specific Course Offerings', 'Faculty Quality'];
            const shuffled = criteria.sort(() => 0.5 - Math.random());
            return shuffled.slice(0, 3);
        })(),
        consideredOthers: Math.random() < 0.8 ? 'Yes' : 'No',
        secondChoice: (() => {
            let others = universities.filter(u => u !== university);
            return others[Math.floor(Math.random() * others.length)];
        })(),
        satisfaction: Math.floor(Math.random() * (10 - 6) + 6),
        universityTags: (() => {
            const tags = universityTags[university];
            const shuffled = tags.sort(() => 0.5 - Math.random());
            return shuffled.slice(0, 2);
        })(),
        learningStyle: learningStyles[Math.floor(Math.random() * learningStyles.length)],
        populationPreference: populationPreference[Math.floor(Math.random() * populationPreference.length)],
        campusSetting: campusSettings[Math.floor(Math.random() * campusSettings.length)],
        costImportance: Math.floor(Math.random() * 10) + 1,
        scholarship: Math.random() < 0.3 ? 'Yes' : 'No',
        living: livingArrangement[Math.floor(Math.random() * livingArrangement.length)],
        major: majors[university][Math.floor(Math.random() * majors[university].length)],
        careerGoal: careerGoals[Math.floor(Math.random() * careerGoals.length)],
        internshipImportance: Math.floor(Math.random() * (10 - 7) + 7),
        universityInternship: Math.random() < 0.6 ? 'Yes' : 'No',
        familyInfluence: Math.floor(Math.random() * 10) + 1,
        friendInfluence: Math.floor(Math.random() * 10) + 1,
        socialMediaInfluence: Math.floor(Math.random() * 10) + 1,
        rankingInfluence: Math.floor(Math.random() * (10 - 5) + 5)
    };
    return response;
}

// Generate 20 responses for each university
const responsesPerUniveristy = 50
const allResponses = [];
universities.forEach(uni => {
    for (let i = 0; i < responsesPerUniveristy; i++) {
        allResponses.push(generateRandomResponse(uni));
    }
});

// Convert to CSV
import Papa from 'papaparse';
import fs from 'fs';

// Convert to CSV
const csv = Papa.unparse(allResponses);

// Write CSV to file
fs.writeFileSync('output.csv', csv);

console.log("CSV file has been written to output.csv");

// Basic statistics
console.log("\nTotal number of responses:", allResponses.length);
console.log("\nResponses per university:", universities.map(uni => ({
    university: uni,
    count: allResponses.filter(r => r.university === uni).length
})));

// Average satisfaction by university
const avgSatisfaction = universities.map(uni => ({
    university: uni,
    avgSatisfaction: (allResponses
        .filter(r => r.university === uni)
        .reduce((acc, curr) => acc + curr.satisfaction, 0) / responsesPerUniveristy
    ).toFixed(2)
}));
console.log("\nAverage satisfaction by university:", avgSatisfaction);