# Singapore Universities Synthetic Dataset Generator

A comprehensive synthetic dataset generator for Singapore's five major universities (NUS, NTU, SMU, SUTD,
and SIT) that produces realistic student profiles with distinctive characteristics for each institution and program.

## Key Features

1. **Realistic University Profiles**
    - Each university has unique characteristics based on their real-world identities
    - Distinctive teaching styles, campus cultures, and strengths for each institution
    - Appropriate size classifications and facility ratings

2. **Program-Specific Characteristics**
    - 24 programs across 5 universities with distinctive teaching approaches
    - Difficulty levels and career prospects vary realistically by program
    - Program-specific personality traits and teaching methods

3. **Comprehensive Student Data**
    - Generates complete profiles covering all questionnaire sections
    - Data patterns align with university and program characteristics
    - Includes realistic free-text responses for additional insights

4. **Intelligent Data Variation**
    - Student satisfaction correlates with university-student fit
    - Learning experiences reflect the university's teaching philosophy
    - Career outcomes align with program reputation and industry connections

5. **Export Options**
    - Generates both JSON data and SQL insert statements
    - Ready to import directly into your Supabase PostgreSQL database
    - Well-structured for easy integration with your system


6. **Weighted Distribution**: When using `total_students`, students are distributed based on:

    - **University popularity**: Major universities like NUS get more students
    - **Program popularity**: In-demand programs like Computer Science get more students

## University Profiles

The generator creates distinct profiles for each university:

### NUS (National University of Singapore)

Singapore's oldest and most prestigious university with comprehensive education and strong research orientation.
Students tend to report high teaching quality but moderate professor accessibility due to its size.

### NTU (Nanyang Technological University)

Known for engineering excellence, beautiful campus, and project-based education. Students report strong industry
projects and a collaborative environment.

### SMU (Singapore Management University)

Business-focused education with interactive teaching in a central city location. Features smaller class sizes,
interactive teaching, and strong professional preparation.

### SUTD (Singapore University of Technology and Design)

Design-centric education with interdisciplinary approach and MIT partnership. Students experience hands-on,
project-based learning with innovation emphasis.

### SIT (Singapore Institute of Technology)

Applied learning focus with strong industry connections and practical skills development. Students report high industry
relevance and work-study opportunities.

Let me enhance the synthetic data generator with logging and an alternative way to specify the total number of students:

## Usage Examples

### Python API

```python
from synthetic_data_generator import generate_data, save_to_json, save_sql_statements

# Generate data with 3 students per program
data = generate_data(num_students_per_program=3)
save_to_json(data, "fixed_per_program.json")
save_sql_statements(data, "fixed_per_program.sql")

# Generate data with 100 total students distributed realistically 
data = generate_data(total_students=100)
save_to_json(data, "total_students.json")
save_sql_statements(data, "total_students.sql")
```

### Command Line

```bash
# Default (5 students per program)
python synthetic_data_generator.py

# 10 students per program with custom output files
python synthetic_data_generator.py --per-program 10 --json perprogram_data.json --sql perprogram_data.sql

# 200 total students distributed based on popularity
python synthetic_data_generator.py --total 200 --json total200_data.json --sql total200_data.sql
```

## University Characteristics

Each university has distinct properties that influence the generated data:

- **NUS**: Highest prestige, competitive, research-focused (30% of student distribution)
- **NTU**: Strong engineering focus, beautiful campus (25% of student distribution)
- **SMU**: Interactive teaching, business-oriented, city campus (20% of student distribution)
- **SUTD**: Design-centric, innovative, interdisciplinary (10% of student distribution)
- **SIT**: Applied learning, industry connections, practical skills (15% of student distribution)

## Program Characteristics

Each program also has unique attributes:

- **Computer Science at NUS**: Research-intensive, theoretical foundation (high difficulty)
- **Business Management at SMU**: Interactive, case studies (medium difficulty)
- **Architecture at SUTD**: Design thinking, portfolio-based (high difficulty)
- **Information Security at SIT**: Practical cybersecurity focus (high difficulty)

## Implementation Details

The synthetic data generator:

1. Initializes popularity weights for universities and programs
2. Calculates a distribution of students based on these weights
3. Generates realistic student profiles that reflect the characteristics of each institution
4. Produces both JSON data and SQL insert statements
5. Logs detailed statistics about the generated dataset