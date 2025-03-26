from typing import Dict, Any

from jamaibase import JamAI, protocol as p


class JustificationGenerator:
    def __init__(self, project_id: str, pat: str):
        self.client = JamAI(
            project_id=project_id,
            token=pat
        )

    def generate_justification(self, student_profile: Dict[str, Any], recommended_university: Dict[str, Any],
                               similar_students: Dict[str, Any]) -> str:
        # Add a row to the 'Recommender' table with all three inputs
        response = self.client.add_table_rows(
            table_type=p.TableType.action,
            request=p.RowAddRequest(
                table_id="Recommender",
                data=[{
                    "Student Profile": student_profile,
                    "Recommendation": recommended_university,
                    "Similar Students": similar_students
                }],
                stream=False
            )
        )

        # Extract raw text from the response
        raw_pros = response.rows[0].columns["Pros"].text
        raw_cons = response.rows[0].columns["Cons"].text
        raw_conclusion = response.rows[0].columns["Conclusion"].text

        # Process bullet points into a list
        def extract_bullets(text):
            bullets = text.split("* ")  # Split on '* ' to separate bullet points
            bullets = [bullet.strip() for bullet in bullets if bullet.strip()]  # Remove empty strings and trim spaces
            return bullets

        pros_list = extract_bullets(raw_pros)
        cons_list = extract_bullets(raw_cons)

        return {
            "Pros": pros_list,
            "Cons": cons_list,
            "Conclusion": [raw_conclusion.strip()]  # Wrap conclusion in a list for consistency
        }
