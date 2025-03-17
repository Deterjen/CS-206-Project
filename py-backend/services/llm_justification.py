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
                    "University Recommendation": recommended_university,
                    "Similar Students": similar_students
                }],
                stream=False
            )
        )

        justification = response.rows[0].columns["Justification"].text
        return justification
