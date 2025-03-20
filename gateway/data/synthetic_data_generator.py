import datetime
import json
import logging
import os
import random

import numpy as np
from faker import Faker

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger("SyntheticDataGenerator")

# Initialize faker for generating realistic names and text
fake = Faker()

# Set seed for reproducibility
random.seed(42)
np.random.seed(42)
fake.seed_instance(42)

# Define university characteristics with popularity weights
UNIVERSITIES = [
    {
        "id": 1,
        "name": "National University of Singapore",
        "short_name": "NUS",
        "location": "Singapore",
        "size": "Large",  # >20K students
        "setting": "Urban",
        "popularity_weight": 0.30,  # Highest weight - most popular
        "profile": {
            "description": "Singapore's flagship university with a comprehensive education system",
            "strengths": ["Research excellence", "Comprehensive education", "Strong international reputation"],
            "teaching_style": "Mix of theoretical and hands-on",
            "campus_culture": ["Diverse", "Competitive", "Traditional", "Collaborative"],
            "facilities_quality": (8, 10),  # Range for random generation
            "affordability": (5, 7),
            "career_services": (8, 10),
            "alumni_network": (8, 10),
            "student_diversity": "High",
            "research_focus": "High"
        }
    },
    {
        "id": 2,
        "name": "Nanyang Technological University",
        "short_name": "NTU",
        "location": "Singapore",
        "size": "Large",  # >20K students
        "setting": "Urban",
        "popularity_weight": 0.25,  # Second most popular
        "profile": {
            "description": "Research-intensive university with beautiful campus and strong engineering focus",
            "strengths": ["Engineering excellence", "Modern facilities", "Research innovation"],
            "teaching_style": "Project-based and collaborative",
            "campus_culture": ["Innovative", "Collaborative", "Diverse"],
            "facilities_quality": (8, 10),  # Range for random generation
            "affordability": (5, 7),
            "career_services": (8, 9),
            "alumni_network": (7, 9),
            "student_diversity": "High",
            "research_focus": "High"
        }
    },
    {
        "id": 3,
        "name": "Singapore Management University",
        "short_name": "SMU",
        "location": "Singapore",
        "size": "Medium",  # ~10K students
        "setting": "Urban",
        "popularity_weight": 0.20,  # Third most popular
        "profile": {
            "description": "City campus with interactive teaching and business focus",
            "strengths": ["Business education", "Interactive learning", "City campus location"],
            "teaching_style": "Interactive, seminar-style",
            "campus_culture": ["Professional", "Extroverted", "Collaborative"],
            "facilities_quality": (8, 9),  # Range for random generation
            "affordability": (4, 6),
            "career_services": (8, 10),
            "alumni_network": (7, 9),
            "student_diversity": "Medium",
            "research_focus": "Medium"
        }
    },
    {
        "id": 4,
        "name": "Singapore University of Technology and Design",
        "short_name": "SUTD",
        "location": "Singapore",
        "size": "Small",  # <5K students
        "setting": "Urban",
        "popularity_weight": 0.10,  # Smaller university
        "profile": {
            "description": "Design-centric education with interdisciplinary approach",
            "strengths": ["Design thinking", "Innovation", "Interdisciplinary education"],
            "teaching_style": "Hands-on, project-based",
            "campus_culture": ["Innovative", "Creative", "Collaborative"],
            "facilities_quality": (8, 10),  # Range for random generation
            "affordability": (5, 7),
            "career_services": (7, 9),
            "alumni_network": (6, 8),  # Newer university
            "student_diversity": "Medium",
            "research_focus": "High"
        }
    },
    {
        "id": 5,
        "name": "Singapore Institute of Technology",
        "short_name": "SIT",
        "location": "Singapore",
        "size": "Medium",  # ~10K students
        "setting": "Urban",
        "popularity_weight": 0.15,  # Newer but growing
        "profile": {
            "description": "Applied learning with strong industry connections",
            "strengths": ["Applied education", "Industry relevance", "Practical skills"],
            "teaching_style": "Applied, industry-focused",
            "campus_culture": ["Practical", "Industry-oriented", "Collaborative"],
            "facilities_quality": (7, 9),  # Range for random generation
            "affordability": (6, 8),  # More affordable
            "career_services": (8, 10),
            "alumni_network": (6, 8),  # Newer university
            "student_diversity": "Medium",
            "research_focus": "Low"
        }
    }
]

# Define programs by university with popularity weights
PROGRAMS = {
    "NUS": [
        {"id": 1, "name": "Computer Science", "department": "Computing", "degree_level": "Undergraduate",
         "popularity_weight": 0.30,  # Very popular
         "profile": {"teaching_style": "Research-intensive, theoretical foundation", "career_prospects": "Excellent",
                     "difficulty": "High"}},
        {"id": 2, "name": "Medicine", "department": "Medicine", "degree_level": "Undergraduate",
         "popularity_weight": 0.25,  # Very popular but limited intake
         "profile": {"teaching_style": "Comprehensive, clinical-based", "career_prospects": "Excellent",
                     "difficulty": "Very High"}},
        {"id": 3, "name": "Law", "department": "Law", "degree_level": "Undergraduate",
         "popularity_weight": 0.15,  # Competitive
         "profile": {"teaching_style": "Case-based method", "career_prospects": "Excellent", "difficulty": "High"}},
        {"id": 4, "name": "Business Administration", "department": "Business", "degree_level": "Undergraduate",
         "popularity_weight": 0.20,  # Popular
         "profile": {"teaching_style": "Global focus, research-oriented", "career_prospects": "Very Good",
                     "difficulty": "Medium"}},
        {"id": 5, "name": "Mechanical Engineering", "department": "Engineering", "degree_level": "Undergraduate",
         "popularity_weight": 0.10,  # Less popular but solid
         "profile": {"teaching_style": "Mix of theory and application", "career_prospects": "Very Good",
                     "difficulty": "High"}}
    ],
    "NTU": [
        {"id": 6, "name": "Mechanical Engineering", "department": "Engineering", "degree_level": "Undergraduate",
         "popularity_weight": 0.15,  # Good reputation
         "profile": {"teaching_style": "Strong industry projects", "career_prospects": "Excellent",
                     "difficulty": "High"}},
        {"id": 7, "name": "Computer Science", "department": "Computing", "degree_level": "Undergraduate",
         "popularity_weight": 0.35,  # Very popular
         "profile": {"teaching_style": "AI focus, project-based", "career_prospects": "Excellent",
                     "difficulty": "High"}},
        {"id": 8, "name": "Business", "department": "Business", "degree_level": "Undergraduate",
         "popularity_weight": 0.20,  # Popular
         "profile": {"teaching_style": "Strong in accounting and finance", "career_prospects": "Very Good",
                     "difficulty": "Medium"}},
        {"id": 9, "name": "Art, Design & Media", "department": "Art", "degree_level": "Undergraduate",
         "popularity_weight": 0.15,  # Unique program
         "profile": {"teaching_style": "Creative, portfolio-based", "career_prospects": "Good",
                     "difficulty": "Medium"}},
        {"id": 10, "name": "Environmental Science", "department": "Science", "degree_level": "Undergraduate",
         "popularity_weight": 0.15,  # Growing interest
         "profile": {"teaching_style": "Sustainability focus", "career_prospects": "Good", "difficulty": "Medium"}}
    ],
    "SMU": [
        {"id": 11, "name": "Business Management", "department": "Business", "degree_level": "Undergraduate",
         "popularity_weight": 0.35,  # SMU's flagship
         "profile": {"teaching_style": "Interactive, case studies", "career_prospects": "Excellent",
                     "difficulty": "Medium"}},
        {"id": 12, "name": "Accountancy", "department": "Accountancy", "degree_level": "Undergraduate",
         "popularity_weight": 0.20,  # Strong program
         "profile": {"teaching_style": "Professional preparation", "career_prospects": "Excellent",
                     "difficulty": "High"}},
        {"id": 13, "name": "Information Systems", "department": "Computing", "degree_level": "Undergraduate",
         "popularity_weight": 0.20,  # Growing in popularity
         "profile": {"teaching_style": "Business technology focus", "career_prospects": "Very Good",
                     "difficulty": "Medium"}},
        {"id": 14, "name": "Economics", "department": "Economics", "degree_level": "Undergraduate",
         "popularity_weight": 0.15,  # Solid program
         "profile": {"teaching_style": "Policy oriented", "career_prospects": "Very Good", "difficulty": "High"}},
        {"id": 15, "name": "Law", "department": "Law", "degree_level": "Undergraduate",
         "popularity_weight": 0.10,  # Newer program
         "profile": {"teaching_style": "Practice-oriented", "career_prospects": "Excellent", "difficulty": "Very High"}}
    ],
    "SUTD": [
        {"id": 16, "name": "Architecture and Sustainable Design", "department": "Architecture",
         "degree_level": "Undergraduate",
         "popularity_weight": 0.30,  # Signature program
         "profile": {"teaching_style": "Design thinking", "career_prospects": "Very Good", "difficulty": "High"}},
        {"id": 17, "name": "Engineering Product Development", "department": "Engineering",
         "degree_level": "Undergraduate",
         "popularity_weight": 0.25,  # Popular
         "profile": {"teaching_style": "Interdisciplinary approach", "career_prospects": "Very Good",
                     "difficulty": "High"}},
        {"id": 18, "name": "Information Systems Technology and Design", "department": "Computing",
         "degree_level": "Undergraduate",
         "popularity_weight": 0.25,  # Growing with tech demand
         "profile": {"teaching_style": "User experience focus", "career_prospects": "Excellent", "difficulty": "High"}},
        {"id": 19, "name": "Engineering Systems and Design", "department": "Engineering",
         "degree_level": "Undergraduate",
         "popularity_weight": 0.20,  # Solid program
         "profile": {"teaching_style": "Systems thinking", "career_prospects": "Very Good", "difficulty": "High"}}
    ],
    "SIT": [
        {"id": 20, "name": "Accountancy", "department": "Accountancy", "degree_level": "Undergraduate",
         "popularity_weight": 0.20,  # Practical focus
         "profile": {"teaching_style": "Work-study program", "career_prospects": "Very Good", "difficulty": "Medium"}},
        {"id": 21, "name": "Information Security", "department": "Computing", "degree_level": "Undergraduate",
         "popularity_weight": 0.30,  # High demand field
         "profile": {"teaching_style": "Practical cybersecurity", "career_prospects": "Excellent",
                     "difficulty": "High"}},
        {"id": 22, "name": "Hospitality Business", "department": "Business", "degree_level": "Undergraduate",
         "popularity_weight": 0.15,  # Niche program
         "profile": {"teaching_style": "Industry partnership", "career_prospects": "Good", "difficulty": "Medium"}},
        {"id": 23, "name": "Allied Health", "department": "Health", "degree_level": "Undergraduate",
         "popularity_weight": 0.20,  # Growing healthcare demand
         "profile": {"teaching_style": "Practical clinical focus", "career_prospects": "Very Good",
                     "difficulty": "High"}},
        {"id": 24, "name": "Mechanical Engineering", "department": "Engineering", "degree_level": "Undergraduate",
         "popularity_weight": 0.15,  # Standard offering
         "profile": {"teaching_style": "Industry-relevant skills", "career_prospects": "Very Good",
                     "difficulty": "Medium"}}
    ]
}

# Define possible values for various fields
YEAR_OF_STUDY = ["1st year", "2nd year", "3rd year", "4th year", "5+ years", "Postgraduate"]
LEARNING_STYLES = ["Lecture-based", "Hands-on/Practical", "Project-based", "Research-oriented", "Seminar-based",
                   "Online/Remote"]
CAMPUS_CULTURE = ["Diverse", "Inclusive", "Competitive", "Collaborative", "Conservative", "Progressive", "Traditional",
                  "Innovative"]
EXTRACURRICULAR_ACTIVITIES = ["Sports", "Arts & Culture", "Academic Clubs", "Community Service",
                              "Professional/Career Clubs", "Student Government", "Greek Life"]
WEEKLY_HOURS = ["0 (None)", "1–5 hours", "6–10 hours", "11–15 hours", "16–20 hours", "20+ hours"]
FINANCIAL_AID_PERCENTAGE = ["0-25%", "26-50%", "51-75%", "76-100%"]
FACILITIES = ["Libraries", "Sports Facilities", "Laboratories", "Study Spaces", "Student Centers", "Dining Halls",
              "Health Services"]
REPUTATION_ASPECTS = ["Academic Excellence", "Research Output", "Industry Connections", "Global Recognition",
                      "Innovation", "Alumni Success"]
PERSONALITY_TRAITS = ["Ambitious", "Creative", "Analytical", "Collaborative", "Competitive", "Introverted",
                      "Extroverted", "Independent"]
WOULD_CHOOSE_AGAIN = ["Definitely Yes", "Probably Yes", "Unsure", "Probably Not", "Definitely Not"]
DECISION_FACTORS = ["Academic Reputation", "Program Offerings", "Location", "Cost/Financial Aid", "Campus Culture",
                    "Career Opportunities", "Research Opportunities", "Facilities", "Family Influence"]


def get_univ_by_short_name(short_name):
    """Find university by short name"""
    for univ in UNIVERSITIES:
        if univ["short_name"] == short_name:
            return univ
    return None


def generate_universities():
    """Generate university records"""
    timestamp = datetime.datetime.now().isoformat()
    universities = []

    for univ in UNIVERSITIES:
        universities.append({
            "id": univ["id"],
            "name": univ["name"],
            "location": univ["location"],
            "size": univ["size"],
            "setting": univ["setting"],
            "created_at": timestamp
        })

    return universities


def generate_programs():
    """Generate program records"""
    timestamp = datetime.datetime.now().isoformat()
    programs = []

    for univ_short_name, univ_programs in PROGRAMS.items():
        univ = get_univ_by_short_name(univ_short_name)
        univ_id = univ["id"]

        for program in univ_programs:
            programs.append({
                "id": program["id"],
                "university_id": univ_id,
                "name": program["name"],
                "department": program["department"],
                "degree_level": program["degree_level"],
                "created_at": timestamp
            })

    return programs


def generate_student_core(student_id, univ_id, program_id):
    """Generate core student record"""
    timestamp = datetime.datetime.now().isoformat()
    return {
        "id": student_id,
        "university_id": univ_id,
        "program_id": program_id,
        "year_of_study": random.choice(YEAR_OF_STUDY),
        "created_at": timestamp
    }


def generate_university_info(student_id, univ_profile):
    """Generate university information section"""
    timestamp = datetime.datetime.now().isoformat()
    univ_match_base = 7  # Base value

    # Adjust based on university profile
    if "prestigious" in univ_profile.get("description", "").lower():
        overall_satisfaction_min, overall_satisfaction_max = 7, 10
    else:
        overall_satisfaction_min, overall_satisfaction_max = 6, 9

    return {
        "id": student_id,
        "student_id": student_id,
        "overall_satisfaction": random.randint(overall_satisfaction_min, overall_satisfaction_max),
        "university_match": random.randint(univ_match_base, 10),
        "created_at": timestamp
    }


def generate_academic(student_id, univ_profile, program_profile):
    """Generate academic section"""
    timestamp = datetime.datetime.now().isoformat()

    # Select learning styles based on university and program teaching style
    university_teaching = univ_profile.get("teaching_style", "").lower()
    program_teaching = program_profile.get("teaching_style", "").lower()

    likely_styles = []
    if "theoretical" in university_teaching or "theoretical" in program_teaching:
        likely_styles.append("Lecture-based")
        likely_styles.append("Research-oriented")

    if "hands-on" in university_teaching or "practical" in program_teaching:
        likely_styles.append("Hands-on/Practical")

    if "project" in university_teaching or "project" in program_teaching:
        likely_styles.append("Project-based")

    if "interactive" in university_teaching or "seminar" in program_teaching:
        likely_styles.append("Seminar-based")

    # If no specific styles matched, add some defaults
    if not likely_styles:
        likely_styles = ["Lecture-based", "Project-based"]

    # Randomly select 2-3 learning styles, with bias toward the likely ones
    num_styles = random.randint(2, 3)
    learning_styles = []

    # First add likely styles (up to the desired number)
    for style in likely_styles[:num_styles]:
        learning_styles.append(style)

    # If we need more, randomly add from the full list
    while len(learning_styles) < num_styles:
        style = random.choice(LEARNING_STYLES)
        if style not in learning_styles:
            learning_styles.append(style)

    # Generate teaching quality based on university profile
    if program_profile.get("difficulty") == "Very High":
        teaching_quality_min, teaching_quality_max = 7, 10
    elif program_profile.get("difficulty") == "High":
        teaching_quality_min, teaching_quality_max = 6, 9
    else:
        teaching_quality_min, teaching_quality_max = 5, 8

    # Generate professor accessibility
    if "small" in univ_profile.get("size", "").lower():
        prof_access_min, prof_access_max = 7, 10
    else:
        prof_access_min, prof_access_max = 5, 9

    # Generate academic credentials
    credentials = {}
    credentials["GPA"] = str(round(random.uniform(3.0, 4.0), 1))
    test_type = random.choice(["SAT", "ACT", "IB", "A-Levels"])

    if test_type == "SAT":
        credentials[test_type] = str(random.randint(1200, 1600))
    elif test_type == "ACT":
        credentials[test_type] = str(random.randint(24, 36))
    elif test_type == "IB":
        credentials[test_type] = str(random.randint(30, 45))
    else:  # A-Levels
        credentials[test_type] = random.choice(["AAA", "AAB", "ABB", "BBB"])

    return {
        "id": student_id,
        "student_id": student_id,
        "teaching_quality": random.randint(teaching_quality_min, teaching_quality_max),
        "learning_styles": learning_styles,
        "professor_accessibility": random.randint(prof_access_min, prof_access_max),
        "academic_resources": random.randint(7, 10),  # Singapore universities tend to have good resources
        "academic_credentials": credentials,
        "created_at": timestamp
    }


def generate_social(student_id, univ_profile):
    """Generate social and cultural section"""
    timestamp = datetime.datetime.now().isoformat()

    # Select campus culture based on university profile
    uni_culture = univ_profile.get("campus_culture", [])
    num_cultures = random.randint(2, 3)

    # If university has defined culture options, bias selection toward those
    campus_culture = []
    for i in range(min(num_cultures, len(uni_culture))):
        campus_culture.append(uni_culture[i])

    # Add random cultures if needed
    while len(campus_culture) < num_cultures:
        culture = random.choice(CAMPUS_CULTURE)
        if culture not in campus_culture:
            campus_culture.append(culture)

    # Select extracurricular activities
    num_activities = random.randint(1, 3)
    extracurricular_activities = random.sample(EXTRACURRICULAR_ACTIVITIES, num_activities)

    # Determine social groups ease based on university size and culture
    if "inclusive" in univ_profile.get("campus_culture", []):
        social_min, social_max = 7, 10
    elif univ_profile.get("size") == "Small":
        social_min, social_max = 6, 9
    else:
        social_min, social_max = 5, 8

    return {
        "id": student_id,
        "student_id": student_id,
        "campus_culture": campus_culture,
        "extracurricular_activities": extracurricular_activities,
        "weekly_extracurricular_hours": random.choice(WEEKLY_HOURS),
        "social_groups_ease": random.randint(social_min, social_max),
        "created_at": timestamp
    }


def generate_career(student_id, univ_profile, program_profile):
    """Generate career development section"""
    timestamp = datetime.datetime.now().isoformat()

    # Job placement based on university and program profile
    program_prospects = program_profile.get("career_prospects", "")
    career_services_range = univ_profile.get("career_services", (6, 8))

    if program_prospects == "Excellent":
        job_placement_min, job_placement_max = 8, 10
    elif program_prospects == "Very Good":
        job_placement_min, job_placement_max = 7, 9
    else:
        job_placement_min, job_placement_max = 6, 8

    # Determine internship experience probability
    if "industry" in univ_profile.get("description", "").lower():
        internship_prob = 0.85
    else:
        internship_prob = 0.65

    internship_experience = random.random() < internship_prob

    # Determine alumni network strength
    alumni_range = univ_profile.get("alumni_network", (6, 8))

    return {
        "id": student_id,
        "student_id": student_id,
        "job_placement_support": random.randint(job_placement_min, job_placement_max),
        "internship_experience": internship_experience,
        "career_services_helpfulness": random.randint(int(career_services_range[0]), int(career_services_range[1])),
        "alumni_network_strength": random.randint(int(alumni_range[0]), int(alumni_range[1])),
        "created_at": timestamp
    }


def generate_financial(student_id, univ_profile):
    """Generate financial aspects section"""
    timestamp = datetime.datetime.now().isoformat()

    # Determine affordability range from university profile
    affordability_range = univ_profile.get("affordability", (5, 7))

    # Financial aid probability varies by university
    if "affordable" in univ_profile.get("description", "").lower():
        financial_aid_prob = 0.5
    else:
        financial_aid_prob = 0.65

    received_financial_aid = random.random() < financial_aid_prob

    # Financial aid percentage
    if received_financial_aid:
        financial_aid_percentage = random.choice(FINANCIAL_AID_PERCENTAGE)
    else:
        financial_aid_percentage = None

    return {
        "id": student_id,
        "student_id": student_id,
        "affordability": random.randint(int(affordability_range[0]), int(affordability_range[1])),
        "received_financial_aid": received_financial_aid,
        "financial_aid_percentage": financial_aid_percentage,
        "campus_employment_availability": random.randint(5, 8),
        "created_at": timestamp
    }


def generate_facilities(student_id, univ_profile):
    """Generate campus facilities section"""
    timestamp = datetime.datetime.now().isoformat()

    # Determine facilities quality from university profile
    facilities_range = univ_profile.get("facilities_quality", (6, 8))

    # Randomly select facilities used
    num_facilities = random.randint(2, 4)
    regularly_used_facilities = random.sample(FACILITIES, num_facilities)

    # On-campus housing quality
    if "beautiful campus" in univ_profile.get("description", "").lower():
        housing_min, housing_max = 7, 9
    else:
        housing_min, housing_max = 6, 8

    # Some students might not live on campus
    housing_quality = random.choice([random.randint(housing_min, housing_max), None])

    return {
        "id": student_id,
        "student_id": student_id,
        "facilities_quality": random.randint(int(facilities_range[0]), int(facilities_range[1])),
        "regularly_used_facilities": regularly_used_facilities,
        "housing_quality": housing_quality,
        "created_at": timestamp
    }


def generate_reputation(student_id, univ_profile):
    """Generate reputation and value section"""
    timestamp = datetime.datetime.now().isoformat()

    # Generate ranking importance
    if "prestigious" in univ_profile.get("description", "").lower():
        ranking_min, ranking_max = 7, 10
    else:
        ranking_min, ranking_max = 5, 8

    # Generate employer value perception based on university's reputation
    if "prestigious" in univ_profile.get("description", "").lower():
        employer_min, employer_max = 8, 10
    else:
        employer_min, employer_max = 6, 9

    # Select reputation aspects
    num_aspects = random.randint(2, 4)
    important_reputation_aspects = random.sample(REPUTATION_ASPECTS, num_aspects)

    return {
        "id": student_id,
        "student_id": student_id,
        "ranking_importance": random.randint(ranking_min, ranking_max),
        "employer_value_perception": random.randint(employer_min, employer_max),
        "important_reputation_aspects": important_reputation_aspects,
        "created_at": timestamp
    }


def generate_personal_fit(student_id, univ_profile, program_profile):
    """Generate personal fit and reflection section"""
    timestamp = datetime.datetime.now().isoformat()

    # Personality match based on difficulty of program and university culture
    if program_profile.get("difficulty") in ["High", "Very High"]:
        personality_match_scale = (6, 10)  # More variable - depends on student fit
    else:
        personality_match_scale = (7, 10)  # Generally better fit for medium difficulty

    # Student traits based on university and program
    program_traits = []
    if program_profile.get("difficulty") in ["High", "Very High"]:
        program_traits.extend(["Ambitious", "Analytical"])
    if "creative" in program_profile.get("teaching_style", "").lower():
        program_traits.append("Creative")
    if "collaborative" in univ_profile.get("teaching_style", "").lower():
        program_traits.append("Collaborative")

    # Ensure we have a good set of traits
    while len(program_traits) < 2:
        trait = random.choice(PERSONALITY_TRAITS)
        if trait not in program_traits:
            program_traits.append(trait)

    # Final traits - pick 2-3 from the likely ones
    typical_student_traits = random.sample(program_traits, min(len(program_traits), random.randint(2, 3)))

    # Would choose again - influenced by personality match and program satisfaction
    personality_match = random.randint(personality_match_scale[0], personality_match_scale[1])
    if personality_match >= 8:
        would_choose_options = ["Definitely Yes", "Probably Yes"]
        would_choose_weights = [0.7, 0.3]
    elif personality_match >= 6:
        would_choose_options = ["Probably Yes", "Unsure", "Probably Not"]
        would_choose_weights = [0.5, 0.3, 0.2]
    else:
        would_choose_options = ["Unsure", "Probably Not", "Definitely Not"]
        would_choose_weights = [0.4, 0.4, 0.2]

    would_choose_again = random.choices(would_choose_options, weights=would_choose_weights)[0]

    # Thriving student type
    univ_name = univ_profile.get("name", "this university")
    program_name = program_profile.get("name", "this program")

    # Create description of thriving student based on university and program
    student_descriptions = [
        f"A student who is {typical_student_traits[0].lower()} and enjoys {program_profile.get('teaching_style', 'various teaching styles')}.",
        f"Someone who thrives in a {univ_profile.get('campus_culture', ['diverse'])[0].lower()} environment and wants to pursue {program_name}.",
        f"{univ_name} works well for students who are self-motivated and interested in {program_profile.get('teaching_style', 'learning')}."
    ]

    thriving_student_type = random.choice(student_descriptions)

    return {
        "id": student_id,
        "student_id": student_id,
        "personality_match": personality_match,
        "typical_student_traits": typical_student_traits,
        "would_choose_again": would_choose_again,
        "thriving_student_type": thriving_student_type,
        "created_at": timestamp
    }


def generate_selection_criteria(student_id, univ_profile, program_profile):
    """Generate selection criteria section"""
    timestamp = datetime.datetime.now().isoformat()

    # Determine important decision factors based on university strengths
    potential_factors = []
    for strength in univ_profile.get("strengths", []):
        if "research" in strength.lower():
            potential_factors.append("Research Opportunities")
        if "reputation" in strength.lower() or "excellence" in strength.lower():
            potential_factors.append("Academic Reputation")
        if "facilities" in strength.lower():
            potential_factors.append("Facilities")
        if "industry" in strength.lower():
            potential_factors.append("Career Opportunities")
        if "location" in strength.lower() or "campus" in strength.lower():
            potential_factors.append("Location")

    # If we don't have enough factors, add some defaults
    while len(potential_factors) < 3:
        factor = random.choice(DECISION_FACTORS)
        if factor not in potential_factors:
            potential_factors.append(factor)

    # Select a random subset of these factors
    num_factors = random.randint(2, 4)
    important_decision_factors = random.sample(potential_factors, min(len(potential_factors), num_factors))

    # Generate retrospective important factors
    retrospective_factors = [
        f"Looking back, I should have considered work-life balance more seriously.",
        f"I wish I had put more emphasis on internship opportunities.",
        f"The location and cost of living should have been more important factors in my decision.",
        f"I think I made the right choice focusing on {important_decision_factors[0].lower()}.",
        f"I should have considered the teaching style more carefully before choosing."
    ]

    retrospective_important_factors = random.choice(retrospective_factors)

    return {
        "id": student_id,
        "student_id": student_id,
        "important_decision_factors": important_decision_factors,
        "retrospective_important_factors": retrospective_important_factors,
        "created_at": timestamp
    }


def generate_additional_insights(student_id, univ_profile, program_profile):
    """Generate additional insights section"""
    timestamp = datetime.datetime.now().isoformat()

    # Generate university strengths based on university profile
    strength_templates = [
        f"Strong {program_profile.get('name')} program with excellent faculty.",
        f"Great {univ_profile.get('strengths', ['education'])[0]} and learning environment.",
        f"Amazing campus facilities and resources for students.",
        f"Strong industry connections leading to good job opportunities.",
        f"Excellent research opportunities and mentorship.",
        f"Diverse student body and inclusive campus culture."
    ]
    university_strengths = random.choice(strength_templates)

    # Generate weaknesses
    weakness_templates = [
        f"High cost of living and tuition fees.",
        f"Competitive environment can be stressful at times.",
        f"Some courses could benefit from more practical, hands-on components.",
        f"Administrative processes can be bureaucratic and time-consuming.",
        f"Limited parking and transportation options.",
        f"Work-life balance can be challenging with heavy course loads."
    ]
    university_weaknesses = random.choice(weakness_templates)

    # Generate advice
    advice_templates = [
        f"Take advantage of networking opportunities with industry professionals.",
        f"Get involved in extracurricular activities to build a well-rounded profile.",
        f"Don''t hesitate to approach professors for guidance and mentorship.",
        f"Start internship hunting early to secure the best opportunities.",
        f"Balance your academic commitments with self-care and social activities.",
        f"Utilize all the resources available on campus - they''re there for you."
    ]
    prospective_student_advice = random.choice(advice_templates)

    return {
        "id": student_id,
        "student_id": student_id,
        "university_strengths": university_strengths,
        "university_weaknesses": university_weaknesses,
        "prospective_student_advice": prospective_student_advice,
        "created_at": timestamp
    }


def calculate_student_distribution(total_students=None, num_students_per_program=None):
    """
    Calculate the distribution of students across universities and programs.

    Args:
        total_students: Total number of students to generate (takes precedence if specified)
        num_students_per_program: Number of students per program (used if total_students not specified)

    Returns:
        Dictionary mapping (university_short_name, program_id) to number of students
    """
    distribution = {}

    if total_students is None and num_students_per_program is None:
        # Default to 5 students per program if neither is specified
        num_students_per_program = 5

    if total_students is None:
        # Fixed number per program
        for univ_short_name, programs in PROGRAMS.items():
            for program in programs:
                distribution[(univ_short_name, program["id"])] = num_students_per_program

        # Calculate and log the total
        total = sum(distribution.values())
        logger.info(f"Generating {total} students ({num_students_per_program} per program)")

    else:
        # Calculate weighted distribution based on popularity
        logger.info(f"Generating {total_students} students distributed across universities and programs")

        # Calculate university weights
        univ_weights = {univ["short_name"]: univ["popularity_weight"] for univ in UNIVERSITIES}

        # Normalize university weights
        univ_weight_sum = sum(univ_weights.values())
        univ_weights = {k: v / univ_weight_sum for k, v in univ_weights.items()}

        # Allocate students to universities
        univ_allocation = {}
        remaining = total_students

        for univ_short_name, weight in univ_weights.items():
            if univ_short_name == list(univ_weights.keys())[-1]:
                # Last university gets remaining students to ensure exact total
                univ_allocation[univ_short_name] = remaining
            else:
                # Allocate students based on university popularity weight
                allocation = max(1, int(round(total_students * weight)))
                univ_allocation[univ_short_name] = allocation
                remaining -= allocation

        # For each university, distribute students among its programs
        for univ_short_name, programs in PROGRAMS.items():
            univ_total = univ_allocation[univ_short_name]

            # Calculate program weights for this university
            program_weights = {p["id"]: p["popularity_weight"] for p in programs}

            # Normalize weights
            weight_sum = sum(program_weights.values())
            program_weights = {k: v / weight_sum for k, v in program_weights.items()}

            # Allocate to programs
            remaining = univ_total
            for i, (program_id, weight) in enumerate(program_weights.items()):
                if i == len(program_weights) - 1:
                    # Last program gets remaining students
                    distribution[(univ_short_name, program_id)] = remaining
                else:
                    allocation = max(1, int(round(univ_total * weight)))
                    distribution[(univ_short_name, program_id)] = allocation
                    remaining -= allocation

    return distribution


def generate_existing_students(total_students=None, num_students_per_program=None):
    """
    Generate existing student records with all sections.

    Args:
        total_students: Total number of students to generate (takes precedence)
        num_students_per_program: Number of students per program (used if total_students not set)

    Returns:
        Dictionary with all generated student data
    """
    timestamp = datetime.datetime.now().isoformat()

    all_data = {
        "existing_students": [],
        "existing_students_university_info": [],
        "existing_students_academic": [],
        "existing_students_social": [],
        "existing_students_career": [],
        "existing_students_financial": [],
        "existing_students_facilities": [],
        "existing_students_reputation": [],
        "existing_students_personal_fit": [],
        "existing_students_selection_criteria": [],
        "existing_students_additional_insights": []
    }

    # Calculate distribution of students
    student_distribution = calculate_student_distribution(total_students, num_students_per_program)

    logger.info(
        f"Student distribution: {sum(student_distribution.values())} students across {len(student_distribution)} program-university combinations")

    student_id = 1

    # Track metrics for statistics
    stats = {
        "total_students": 0,
        "universities": {},
        "programs": {},
        "avg_satisfaction": [],
        "avg_teaching_quality": [],
        "internship_rate": 0,
        "financial_aid_rate": 0
    }

    for (univ_short_name, program_id), num_students in student_distribution.items():
        univ = get_univ_by_short_name(univ_short_name)
        univ_id = univ["id"]
        univ_profile = univ["profile"]

        # Find the program by ID
        program = None
        for p in PROGRAMS[univ_short_name]:
            if p["id"] == program_id:
                program = p
                break

        if not program:
            logger.warning(f"Program with ID {program_id} not found in {univ_short_name}")
            continue

        program_profile = program["profile"]

        logger.info(f"Generating {num_students} student(s) for {univ_short_name} - {program['name']}")

        # Update stats
        if univ_short_name not in stats["universities"]:
            stats["universities"][univ_short_name] = 0
        stats["universities"][univ_short_name] += num_students

        if program["name"] not in stats["programs"]:
            stats["programs"][program["name"]] = 0
        stats["programs"][program["name"]] += num_students

        for _ in range(num_students):
            # Generate core student record
            core = generate_student_core(student_id, univ_id, program_id)
            all_data["existing_students"].append(core)

            # Generate all sections
            university_info = generate_university_info(student_id, univ_profile)
            all_data["existing_students_university_info"].append(university_info)

            academic = generate_academic(student_id, univ_profile, program_profile)
            all_data["existing_students_academic"].append(academic)

            social = generate_social(student_id, univ_profile)
            all_data["existing_students_social"].append(social)

            career = generate_career(student_id, univ_profile, program_profile)
            all_data["existing_students_career"].append(career)

            financial = generate_financial(student_id, univ_profile)
            all_data["existing_students_financial"].append(financial)

            facilities = generate_facilities(student_id, univ_profile)
            all_data["existing_students_facilities"].append(facilities)

            reputation = generate_reputation(student_id, univ_profile)
            all_data["existing_students_reputation"].append(reputation)

            personal_fit = generate_personal_fit(student_id, univ_profile, program_profile)
            all_data["existing_students_personal_fit"].append(personal_fit)

            selection_criteria = generate_selection_criteria(student_id, univ_profile, program_profile)
            all_data["existing_students_selection_criteria"].append(selection_criteria)

            additional_insights = generate_additional_insights(student_id, univ_profile, program_profile)
            all_data["existing_students_additional_insights"].append(additional_insights)

            # Update stats
            stats["total_students"] += 1
            stats["avg_satisfaction"].append(university_info["overall_satisfaction"])
            stats["avg_teaching_quality"].append(academic["teaching_quality"])
            stats["internship_rate"] += 1 if career["internship_experience"] else 0
            stats["financial_aid_rate"] += 1 if financial["received_financial_aid"] else 0

            student_id += 1

    # Calculate and log statistics
    if stats["total_students"] > 0:
        logger.info(f"\n=== Generated Data Statistics ===")
        logger.info(f"Total students: {stats['total_students']}")
        logger.info(f"Universities distribution: {dict(sorted(stats['universities'].items()))}")
        logger.info(f"Programs distribution: {dict(sorted(stats['programs'].items()))}")
        logger.info(f"Average satisfaction: {sum(stats['avg_satisfaction']) / len(stats['avg_satisfaction']):.2f}/10")
        logger.info(
            f"Average teaching quality: {sum(stats['avg_teaching_quality']) / len(stats['avg_teaching_quality']):.2f}/10")
        logger.info(f"Internship rate: {stats['internship_rate'] / stats['total_students'] * 100:.1f}%")
        logger.info(f"Financial aid rate: {stats['financial_aid_rate'] / stats['total_students'] * 100:.1f}%")

    return all_data


def generate_sql_insert_statements(data):
    """Generate SQL INSERT statements for all data tables"""
    sql_statements = []

    # Universities
    for univ in data["universities"]:
        cols = ", ".join(univ.keys())
        vals = ", ".join([f"'{str(v)}'" if isinstance(v, str) else str(v) for v in univ.values()])
        sql_statements.append(f"INSERT INTO universities ({cols}) VALUES ({vals});")

    # Programs
    for program in data["programs"]:
        cols = ", ".join(program.keys())
        vals = ", ".join([f"'{str(v)}'" if isinstance(v, str) else str(v) for v in program.values()])
        sql_statements.append(f"INSERT INTO programs ({cols}) VALUES ({vals});")

    # Existing Students and all sections
    for table_name, records in data.items():
        if table_name not in ["universities", "programs"]:
            for record in records:
                # Handle arrays and JSON fields
                processed_values = []
                for k, v in record.items():
                    if isinstance(v, list):
                        processed_values.append(f"ARRAY{str(v)}")
                    elif isinstance(v, dict):
                        processed_values.append(f"'{json.dumps(v)}'::jsonb")
                    elif v is None:
                        processed_values.append("NULL")
                    elif isinstance(v, str):
                        processed_values.append(f"'{v}'")
                    else:
                        processed_values.append(str(v))

                cols = ", ".join(record.keys())
                vals = ", ".join(processed_values)
                sql_statements.append(f"INSERT INTO {table_name} ({cols}) VALUES ({vals});")

    return sql_statements


def generate_data(total_students=None, num_students_per_program=None):
    """
    Generate a complete synthetic dataset.

    Args:
        total_students: Total number of students to generate (takes precedence)
        num_students_per_program: Number of students per program (used if total_students not specified)

    Returns:
        Dictionary with all generated data
    """
    # Generate universities and programs
    logger.info("Generating university and program data...")
    universities = generate_universities()
    programs = generate_programs()

    logger.info(f"Generated {len(universities)} universities and {len(programs)} programs")

    # Generate student data
    logger.info("Generating student data...")
    student_data = generate_existing_students(total_students, num_students_per_program)

    # Combine all data
    all_data = {
        "universities": universities,
        "programs": programs,
        **student_data
    }

    logger.info(f"Data generation complete")

    return all_data


def save_to_json(data, filename="synthetic_data.json"):
    """Save generated data to a JSON file"""

    path = f'{os.getcwd()}/data/out/{filename}'
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w") as f:
        json.dump(data, f, indent=2)
    logger.info(f"Data saved to {path}")


def save_sql_statements(data, filename="insert_statements.sql", batch_size=1000):
    """
    Save SQL INSERT statements to a file with proper transaction handling and batching.

    Args:
        data: Dictionary containing all generated data
        filename: Output SQL filename
        batch_size: Number of statements per batch for large datasets
    """
    sql_statements = generate_sql_insert_statements(data)
    total_statements = len(sql_statements)

    path = f'{os.getcwd()}/data/out/{filename}'
    logger.info(f"Writing {total_statements} SQL statements to {path}")

    try:
        with open(path, "w") as f:
            # Write transaction start ONCE at the beginning
            f.write("-- Start transaction\nBEGIN;\n\n")

            # Process statements in batches to prevent memory issues with large datasets
            for i in range(0, total_statements, batch_size):
                batch = sql_statements[i:i + batch_size]

                # Write this batch of statements
                for stmt in batch:
                    f.write(stmt + "\n")

                # Log progress
                logger.info(
                    f"  Wrote statements {i + 1}-{min(i + batch_size, total_statements)} of {total_statements}...")

            # Write transaction end ONCE at the end
            f.write("\n-- Commit transaction\nCOMMIT;\n")

        logger.info(f"SQL statements successfully saved to {path}")
    except Exception as e:
        logger.error(f"Error writing SQL file: {e}")
        raise


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description='Generate synthetic university student data')
    group = parser.add_mutually_exclusive_group()
    group.add_argument('--total', type=int, help='Total number of students to generate')
    group.add_argument('--per-program', type=int, default=5, help='Number of students per program (default: 5)')
    parser.add_argument('--json', type=str, default="synthetic_data.json", help='JSON output filename')
    parser.add_argument('--sql', type=str, default="insert_statements.sql", help='SQL output filename')
    args = parser.parse_args()

    # Generate data
    data = generate_data(args.total, args.per_program)

    # Save to files
    save_to_json(data, args.json)
    save_sql_statements(data, args.sql)
