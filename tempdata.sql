-- Start a transaction
BEGIN;

-- Insert sample universities with diverse characteristics
INSERT INTO universities (name, location, size, setting) VALUES
    ('Stanford University', 'California, USA', 'Large', 'Urban'),
    ('Massachusetts Institute of Technology', 'Massachusetts, USA', 'Medium', 'Urban'),
    ('University of Michigan', 'Michigan, USA', 'Large', 'Urban'),
    ('Cornell University', 'New York, USA', 'Medium', 'Rural'),
    ('Rice University', 'Texas, USA', 'Small', 'Urban'),
    ('Williams College', 'Massachusetts, USA', 'Small', 'Rural'),
    ('University of California, Berkeley', 'California, USA', 'Large', 'Urban'),
    ('University of Washington', 'Washington, USA', 'Large', 'Urban'),
    ('Harvard University', 'Massachusetts, USA', 'Medium', 'Urban'),
    ('University of North Carolina', 'North Carolina, USA', 'Large', 'Urban');

-- Insert programs for each university
-- Stanford programs
INSERT INTO programs (university_id, name, department, degree_level) VALUES
    (1, 'Computer Science', 'Engineering', 'Undergraduate'),
    (1, 'Business Administration', 'Business', 'Undergraduate'),
    (1, 'Mechanical Engineering', 'Engineering', 'Undergraduate');

-- MIT programs
INSERT INTO programs (university_id, name, department, degree_level) VALUES
    (2, 'Electrical Engineering', 'Engineering', 'Undergraduate'),
    (2, 'Physics', 'Science', 'Undergraduate'),
    (2, 'Computer Science', 'Engineering', 'Undergraduate');

-- University of Michigan programs
INSERT INTO programs (university_id, name, department, degree_level) VALUES
    (3, 'Psychology', 'Social Sciences', 'Undergraduate'),
    (3, 'Business Administration', 'Business', 'Undergraduate'),
    (3, 'Chemical Engineering', 'Engineering', 'Undergraduate');

-- Cornell programs
INSERT INTO programs (university_id, name, department, degree_level) VALUES
    (4, 'Agriculture', 'Agriculture & Life Sciences', 'Undergraduate'),
    (4, 'Biology', 'Biological Sciences', 'Undergraduate'),
    (4, 'Hotel Administration', 'Business', 'Undergraduate');

-- Rice programs
INSERT INTO programs (university_id, name, department, degree_level) VALUES
    (5, 'Architecture', 'Architecture', 'Undergraduate'),
    (5, 'Bioengineering', 'Engineering', 'Undergraduate'),
    (5, 'English', 'Humanities', 'Undergraduate');

-- Williams College programs
INSERT INTO programs (university_id, name, department, degree_level) VALUES
    (6, 'Mathematics', 'Mathematics and Statistics', 'Undergraduate'),
    (6, 'Art History', 'Arts', 'Undergraduate'),
    (6, 'Economics', 'Social Sciences', 'Undergraduate');

-- UC Berkeley programs
INSERT INTO programs (university_id, name, department, degree_level) VALUES
    (7, 'Computer Science', 'Engineering', 'Undergraduate'),
    (7, 'Environmental Science', 'Sciences', 'Undergraduate'),
    (7, 'Political Science', 'Social Sciences', 'Undergraduate');

-- University of Washington programs
INSERT INTO programs (university_id, name, department, degree_level) VALUES
    (8, 'Information Science', 'Information School', 'Undergraduate'),
    (8, 'Nursing', 'Medicine', 'Undergraduate'),
    (8, 'Business Administration', 'Business', 'Undergraduate');

-- Harvard programs
INSERT INTO programs (university_id, name, department, degree_level) VALUES
    (9, 'Economics', 'Social Sciences', 'Undergraduate'),
    (9, 'History', 'Humanities', 'Undergraduate'),
    (9, 'Computer Science', 'Engineering', 'Undergraduate');

-- UNC programs
INSERT INTO programs (university_id, name, department, degree_level) VALUES
    (10, 'Biology', 'Science', 'Undergraduate'),
    (10, 'Media and Journalism', 'Communications', 'Undergraduate'),
    (10, 'Psychology', 'Social Sciences', 'Undergraduate');

-- Insert existing students
-- Student 1: Stanford Computer Science student
INSERT INTO existing_students (university_id, program_id, year_of_study)
VALUES (1, 1, '3rd year');

-- Add university info
INSERT INTO existing_students_university_info (student_id, overall_satisfaction, university_match)
VALUES (1, 9, 9);

-- Add academic info
INSERT INTO existing_students_academic (student_id, teaching_quality, learning_styles, professor_accessibility, academic_resources, academic_credentials)
VALUES (1, 8, ARRAY['Lecture-based', 'Project-based', 'Research-oriented'], 7, 9, '{"GPA": "3.8", "SAT": "1480"}');

-- Add social info
INSERT INTO existing_students_social (student_id, campus_culture, extracurricular_activities, weekly_extracurricular_hours, social_groups_ease)
VALUES (1, ARRAY['Diverse', 'Inclusive', 'Innovative'], ARRAY['Academic Clubs', 'Professional/Career Clubs'], '6–10 hours', 8);

-- Add career info
INSERT INTO existing_students_career (student_id, job_placement_support, internship_experience, career_services_helpfulness, alumni_network_strength)
VALUES (1, 9, TRUE, 8, 9);

-- Add financial info
INSERT INTO existing_students_financial (student_id, affordability, received_financial_aid, financial_aid_percentage, campus_employment_availability)
VALUES (1, 6, TRUE, '51-75%', 7);

-- Add facilities info
INSERT INTO existing_students_facilities (student_id, facilities_quality, regularly_used_facilities, housing_quality)
VALUES (1, 9, ARRAY['Libraries', 'Study Spaces', 'Student Centers'], 8);

-- Add reputation info
INSERT INTO existing_students_reputation (student_id, ranking_importance, employer_value_perception, important_reputation_aspects)
VALUES (1, 8, 9, ARRAY['Academic Excellence', 'Industry Connections', 'Innovation']);

-- Add personal fit info
INSERT INTO existing_students_personal_fit (student_id, personality_match, typical_student_traits, would_choose_again, thriving_student_type)
VALUES (1, 9, ARRAY['Ambitious', 'Analytical', 'Innovative'], 'Definitely Yes', 'Someone who is self-motivated, intellectually curious, and comfortable in a competitive yet collaborative environment. Stanford works well for students who are ambitious and want to be surrounded by innovation.');

-- Add selection criteria
INSERT INTO existing_students_selection_criteria (student_id, important_decision_factors, retrospective_important_factors)
VALUES (1, ARRAY['Academic Reputation', 'Career Opportunities', 'Research Opportunities'], 'Looking back, I should have put more weight on work-life balance and mental health support. The academic pressure can be intense.');

-- Add additional insights
INSERT INTO existing_students_additional_insights (student_id, university_strengths, university_weaknesses, prospective_student_advice)
VALUES (1, 'Amazing opportunities in tech and entrepreneurship. World-class faculty and research facilities. Strong industry connections.', 'Cost of living is extremely high. Academic pressure can be overwhelming at times. Competitive atmosphere might not be for everyone.', 'Take advantage of networking opportunities early. Don''t be afraid to reach out to professors and alumni. Balance your coursework with extracurriculars that genuinely interest you.');

-- Student 2: MIT Electrical Engineering student
INSERT INTO existing_students (university_id, program_id, year_of_study)
VALUES (2, 4, '4th year');

-- Add university info
INSERT INTO existing_students_university_info (student_id, overall_satisfaction, university_match)
VALUES (2, 8, 9);

-- Add academic info
INSERT INTO existing_students_academic (student_id, teaching_quality, learning_styles, professor_accessibility, academic_resources, academic_credentials)
VALUES (2, 9, ARRAY['Hands-on/Practical', 'Research-oriented', 'Lecture-based'], 6, 10, '{"GPA": "3.9", "SAT": "1550"}');

-- Add social info
INSERT INTO existing_students_social (student_id, campus_culture, extracurricular_activities, weekly_extracurricular_hours, social_groups_ease)
VALUES (2, ARRAY['Innovative', 'Competitive', 'Collaborative'], ARRAY['Academic Clubs', 'Professional/Career Clubs', 'Arts & Culture'], '11–15 hours', 7);

-- Add career info
INSERT INTO existing_students_career (student_id, job_placement_support, internship_experience, career_services_helpfulness, alumni_network_strength)
VALUES (2, 10, TRUE, 9, 10);

-- Add financial info
INSERT INTO existing_students_financial (student_id, affordability, received_financial_aid, financial_aid_percentage, campus_employment_availability)
VALUES (2, 7, TRUE, '76-100%', 8);

-- Add facilities info
INSERT INTO existing_students_facilities (student_id, facilities_quality, regularly_used_facilities, housing_quality)
VALUES (2, 8, ARRAY['Laboratories', 'Libraries', 'Study Spaces'], 7);

-- Add reputation info
INSERT INTO existing_students_reputation (student_id, ranking_importance, employer_value_perception, important_reputation_aspects)
VALUES (2, 9, 10, ARRAY['Research Output', 'Innovation', 'Academic Excellence']);

-- Add personal fit info
INSERT INTO existing_students_personal_fit (student_id, personality_match, typical_student_traits, would_choose_again, thriving_student_type)
VALUES (2, 9, ARRAY['Analytical', 'Ambitious', 'Creative'], 'Definitely Yes', 'Students who thrive at MIT are problem solvers who enjoy tackling complex challenges. Those with strong quantitative skills who are willing to work extremely hard will do well here.');

-- Add selection criteria
INSERT INTO existing_students_selection_criteria (student_id, important_decision_factors, retrospective_important_factors)
VALUES (2, ARRAY['Academic Reputation', 'Research Opportunities', 'Program Offerings'], 'I wish I had considered geographic location more. Boston winters are tough, and being far from home was harder than I thought.');

-- Add additional insights
INSERT INTO existing_students_additional_insights (student_id, university_strengths, university_weaknesses, prospective_student_advice)
VALUES (2, 'Unparalleled research opportunities. Brilliant faculty and peers. Strong focus on innovation and pushing boundaries. Excellent career outcomes.', 'Workload can be overwhelming and stressful. Social scene is limited compared to other schools. Weather is challenging.', 'Prepare for intense academic rigor. Build a support network early. Don''t be afraid to ask for help when needed. Take advantage of the amazing research opportunities from day one.');

-- Student 3: University of Michigan Psychology student
INSERT INTO existing_students (university_id, program_id, year_of_study)
VALUES (3, 7, '2nd year');

-- Add university info
INSERT INTO existing_students_university_info (student_id, overall_satisfaction, university_match)
VALUES (3, 10, 9);

-- Add academic info
INSERT INTO existing_students_academic (student_id, teaching_quality, learning_styles, professor_accessibility, academic_resources, academic_credentials)
VALUES (3, 8, ARRAY['Lecture-based', 'Seminar-based'], 9, 8, '{"GPA": "3.7", "ACT": "32"}');

-- Add social info
INSERT INTO existing_students_social (student_id, campus_culture, extracurricular_activities, weekly_extracurricular_hours, social_groups_ease)
VALUES (3, ARRAY['Diverse', 'Collaborative', 'Progressive'], ARRAY['Sports', 'Community Service', 'Academic Clubs'], '11–15 hours', 10);

-- Add career info
INSERT INTO existing_students_career (student_id, job_placement_support, internship_experience, career_services_helpfulness, alumni_network_strength)
VALUES (3, 8, FALSE, 7, 9);

-- Add financial info
INSERT INTO existing_students_financial (student_id, affordability, received_financial_aid, financial_aid_percentage, campus_employment_availability)
VALUES (3, 8, TRUE, '26-50%', 9);

-- Add facilities info
INSERT INTO existing_students_facilities (student_id, facilities_quality, regularly_used_facilities, housing_quality)
VALUES (3, 9, ARRAY['Libraries', 'Student Centers', 'Sports Facilities'], 8);

-- Add reputation info
INSERT INTO existing_students_reputation (student_id, ranking_importance, employer_value_perception, important_reputation_aspects)
VALUES (3, 7, 8, ARRAY['Academic Excellence', 'Global Recognition', 'Alumni Success']);

-- Add personal fit info
INSERT INTO existing_students_personal_fit (student_id, personality_match, typical_student_traits, would_choose_again, thriving_student_type)
VALUES (3, 10, ARRAY['Extroverted', 'Collaborative', 'Ambitious'], 'Definitely Yes', 'Michigan is perfect for students who want balance between strong academics and vibrant social life. It''s great for those who enjoy school spirit, sports, and being part of a large, diverse community.');

-- Add selection criteria
INSERT INTO existing_students_selection_criteria (student_id, important_decision_factors, retrospective_important_factors)
VALUES (3, ARRAY['Campus Culture', 'Academic Reputation', 'Location'], 'I think I made the right choices. Maybe I should have considered specific program strengths more than overall university reputation.');

-- Add additional insights
INSERT INTO existing_students_additional_insights (student_id, university_strengths, university_weaknesses, prospective_student_advice)
VALUES (3, 'Amazing school spirit and sense of community. Excellent balance of academics and social life. Great alumni network. Beautiful campus.', 'Large class sizes in introductory courses. Weather can be harsh in winter. Campus is very spread out and can be difficult to navigate at first.', 'Get involved early in student organizations. Try to find smaller communities within the larger university. Don''t be intimidated by the size - it offers tremendous opportunities if you seek them out.');

-- Student 4: Cornell Agriculture student
INSERT INTO existing_students (university_id, program_id, year_of_study)
VALUES (4, 10, '4th year');

-- Add university info
INSERT INTO existing_students_university_info (student_id, overall_satisfaction, university_match)
VALUES (4, 7, 8);

-- Add academic info
INSERT INTO existing_students_academic (student_id, teaching_quality, learning_styles, professor_accessibility, academic_resources, academic_credentials)
VALUES (4, 9, ARRAY['Hands-on/Practical', 'Research-oriented', 'Project-based'], 9, 8, '{"GPA": "3.5", "SAT": "1380"}');

-- Add social info
INSERT INTO existing_students_social (student_id, campus_culture, extracurricular_activities, weekly_extracurricular_hours, social_groups_ease)
VALUES (4, ARRAY['Traditional', 'Competitive', 'Collaborative'], ARRAY['Community Service', 'Academic Clubs', 'Greek Life'], '6–10 hours', 7);

-- Add career info
INSERT INTO existing_students_career (student_id, job_placement_support, internship_experience, career_services_helpfulness, alumni_network_strength)
VALUES (4, 8, TRUE, 7, 9);

-- Add financial info
INSERT INTO existing_students_financial (student_id, affordability, received_financial_aid, financial_aid_percentage, campus_employment_availability)
VALUES (4, 6, TRUE, '26-50%', 7);

-- Add facilities info
INSERT INTO existing_students_facilities (student_id, facilities_quality, regularly_used_facilities, housing_quality)
VALUES (4, 7, ARRAY['Laboratories', 'Libraries', 'Student Centers'], 6);

-- Add reputation info
INSERT INTO existing_students_reputation (student_id, ranking_importance, employer_value_perception, important_reputation_aspects)
VALUES (4, 8, 9, ARRAY['Academic Excellence', 'Research Output', 'Global Recognition']);

-- Add personal fit info
INSERT INTO existing_students_personal_fit (student_id, personality_match, typical_student_traits, would_choose_again, thriving_student_type)
VALUES (4, 7, ARRAY['Ambitious', 'Analytical', 'Independent'], 'Probably Yes', 'Cornell works well for self-motivated students who can handle academic pressure and don''t mind a somewhat isolated location. It''s good for those who appreciate nature and don''t need constant urban stimulation.');

-- Add selection criteria
INSERT INTO existing_students_selection_criteria (student_id, important_decision_factors, retrospective_important_factors)
VALUES (4, ARRAY['Program Offerings', 'Academic Reputation', 'Research Opportunities'], 'I should have considered the remote location more carefully. Winters are rough and there''s not much around Ithaca.');

-- Add additional insights
INSERT INTO existing_students_additional_insights (student_id, university_strengths, university_weaknesses, prospective_student_advice)
VALUES (4, 'World-class faculty and research facilities. Beautiful campus and natural surroundings. Strong reputation and name recognition. Excellent agriculture and life sciences programs.', 'Isolated location can feel limiting. Harsh winters and challenging topography ("Ithaca is gorges" but also "Ithaca is cold"). High-stress academic environment. Limited dining and entertainment options in town.', 'Be prepared for academic rigor and weather challenges. Build a strong support network. Take advantage of the natural beauty and outdoor activities. Don''t underestimate the importance of good winter clothing.');

-- Continue with more students for other universities...

-- Student 5: Rice Architecture student
INSERT INTO existing_students (university_id, program_id, year_of_study)
VALUES (5, 13, '3rd year');

-- Add university info
INSERT INTO existing_students_university_info (student_id, overall_satisfaction, university_match)
VALUES (5, 9, 9);

-- Add academic info
INSERT INTO existing_students_academic (student_id, teaching_quality, learning_styles, professor_accessibility, academic_resources, academic_credentials)
VALUES (5, 9, ARRAY['Hands-on/Practical', 'Project-based', 'Studio-based'], 10, 8, '{"GPA": "3.7", "SAT": "1420"}');

-- Add social info
INSERT INTO existing_students_social (student_id, campus_culture, extracurricular_activities, weekly_extracurricular_hours, social_groups_ease)
VALUES (5, ARRAY['Collaborative', 'Inclusive', 'Innovative'], ARRAY['Arts & Culture', 'Academic Clubs', 'Community Service'], '11–15 hours', 9);

-- Add career info
INSERT INTO existing_students_career (student_id, job_placement_support, internship_experience, career_services_helpfulness, alumni_network_strength)
VALUES (5, 8, TRUE, 8, 8);

-- Add financial info
INSERT INTO existing_students_financial (student_id, affordability, received_financial_aid, financial_aid_percentage, campus_employment_availability)
VALUES (5, 7, TRUE, '51-75%', 7);

-- Add facilities info
INSERT INTO existing_students_facilities (student_id, facilities_quality, regularly_used_facilities, housing_quality)
VALUES (5, 9, ARRAY['Study Spaces', 'Libraries', 'Student Centers'], 9);

-- Add reputation info
INSERT INTO existing_students_reputation (student_id, ranking_importance, employer_value_perception, important_reputation_aspects)
VALUES (5, 7, 8, ARRAY['Academic Excellence', 'Innovation', 'Global Recognition']);

-- Add personal fit info
INSERT INTO existing_students_personal_fit (student_id, personality_match, typical_student_traits, would_choose_again, thriving_student_type)
VALUES (5, 9, ARRAY['Creative', 'Collaborative', 'Analytical'], 'Definitely Yes', 'Rice is ideal for students who appreciate a tight-knit community with strong academics. It works well for creative, intellectual students who prefer quality interactions over massive social scenes.');

-- Add selection criteria
INSERT INTO existing_students_selection_criteria (student_id, important_decision_factors, retrospective_important_factors)
VALUES (5, ARRAY['Academic Reputation', 'Campus Culture', 'Facilities'], 'I''m happy with my choice. The residential college system really creates a supportive community that I didn''t fully appreciate during the selection process.');

-- Add additional insights
INSERT INTO existing_students_additional_insights (student_id, university_strengths, university_weaknesses, prospective_student_advice)
VALUES (5, 'Exceptional architecture program with great facilities. Small class sizes with personalized attention. The residential college system creates a strong sense of community. Beautiful campus.', 'Limited options for off-campus activities. Houston weather can be challenging (hot and humid). Small size means fewer course offerings in some areas.', 'Embrace the residential college system - it''s the heart of the Rice experience. Take advantage of the intimate learning environment and build relationships with faculty. Budget for transportation to explore Houston, as the immediate area has limited options.');

-- Add many more students for a good dataset size

-- Commit the transaction
COMMIT;