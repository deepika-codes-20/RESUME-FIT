import unittest
import io
from pypdf import PdfWriter
from analyzer import (
    clean_and_tokenize,
    extract_keywords_from_text,
    check_resume_sections,
    count_quantifiable_metrics,
    analyze_resume_ats,
    extract_text_from_pdf
)
from app import app


class TestResumeFitAnalyzer(unittest.TestCase):

    def setUp(self):
        self.app = app.test_client()
        self.app.testing = True

        self.sample_resume = (
            "Jane Doe\n"
            "Email: jane.doe@example.com | Phone: (123) 456-7890 | LinkedIn: linkedin.com/in/janedoe\n\n"
            "Summary:\n"
            "Passionate Senior Python Engineer with 5+ years of experience designing scalable microservices.\n\n"
            "Skills:\n"
            "Python, Django, FastAPI, PostgreSQL, Docker, AWS, Git, Redis, Agile\n\n"
            "Experience:\n"
            "Lead Backend Engineer | CloudScale Inc (2021 - Present)\n"
            "- Architected and deployed microservices on AWS using Docker and FastAPI.\n"
            "- Optimized database queries on PostgreSQL, reducing response time by 45%.\n"
            "- Managed a team of 4 software engineers and spearheaded CI/CD pipeline automation.\n\n"
            "Education:\n"
            "Bachelor of Science in Computer Science, University of Technology\n"
        )

        self.sample_jd = (
            "We are seeking a Senior Python Developer with deep experience in FastAPI, Docker, and AWS.\n"
            "Responsibilities:\n"
            "- Develop and scale REST APIs using Python and FastAPI or Django.\n"
            "- Maintain PostgreSQL databases and Redis caching.\n"
            "- Deploy applications to AWS with Docker.\n"
            "Requirements:\n"
            "- Proficiency in Python, PostgreSQL, Docker, AWS, Git, Kubernetes, and GraphQL."
        )

    def test_tokenization_and_cleaning(self):
        tokens = clean_and_tokenize("Python, FastAPI & PostgreSQL (REST APIs)!")
        self.assertIn("python", tokens)
        self.assertIn("fastapi", tokens)
        self.assertIn("postgresql", tokens)

    def test_keyword_extraction(self):
        analysis = extract_keywords_from_text(self.sample_resume)
        self.assertIn("python", analysis["tech_skills"])
        self.assertIn("fastapi", analysis["tech_skills"])
        self.assertIn("docker", analysis["tech_skills"])
        self.assertIn("architected", analysis["action_verbs"])
        self.assertIn("optimized", analysis["action_verbs"])

    def test_section_detection(self):
        sections = check_resume_sections(self.sample_resume)
        self.assertTrue(sections["contact"])
        self.assertTrue(sections["email"])
        self.assertTrue(sections["phone"])
        self.assertTrue(sections["experience"])
        self.assertTrue(sections["skills"])
        self.assertTrue(sections["education"])
        self.assertTrue(sections["summary"])

    def test_quantifiable_metrics(self):
        metrics = count_quantifiable_metrics(self.sample_resume)
        self.assertGreaterEqual(metrics, 1)

    def test_ats_analysis_scoring_and_improvements(self):
        result = analyze_resume_ats(self.sample_resume, self.sample_jd)
        self.assertIn("score", result)
        self.assertGreaterEqual(result["score"], 60)
        self.assertIn("matched_keywords", result)
        self.assertIn("missing_keywords", result)
        self.assertIn("improvements", result)

        # Kubernetes and GraphQL were in JD but not in sample resume
        missing_lower = [k.lower() for k in result["missing_keywords"]]
        self.assertTrue("kubernetes" in missing_lower or "graphql" in missing_lower)

        # Python and Docker were in both
        matched_lower = [k.lower() for k in result["matched_keywords"]]
        self.assertIn("python", matched_lower)
        self.assertIn("docker", matched_lower)

    def test_empty_inputs_raise_error(self):
        with self.assertRaises(ValueError):
            analyze_resume_ats("", self.sample_jd)
        with self.assertRaises(ValueError):
            analyze_resume_ats(self.sample_resume, "")

    def test_flask_index_route(self):
        response = self.app.get('/')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'ResumeFit', response.data)

    def test_flask_sample_route(self):
        response = self.app.get('/api/sample')
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertIn("sample_jd", data)
        self.assertIn("sample_resume", data)

    def test_flask_analyze_api_valid(self):
        response = self.app.post('/api/analyze', data={
            'resume_text': self.sample_resume,
            'job_description': self.sample_jd
        })
        self.assertEqual(response.status_code, 200)
        json_data = response.get_json()
        self.assertTrue(json_data["success"])
        self.assertIn("data", json_data)
        self.assertIn("score", json_data["data"])
        self.assertIn("improvements", json_data["data"])

    def test_flask_analyze_api_missing_jd(self):
        response = self.app.post('/api/analyze', data={
            'resume_text': self.sample_resume
        })
        self.assertEqual(response.status_code, 400)
        json_data = response.get_json()
        self.assertFalse(json_data["success"])

    def test_pdf_extraction_with_real_pdf(self):
        # Create a small valid in-memory PDF with pypdf
        writer = PdfWriter()
        page = writer.add_blank_page(width=200, height=200)
        pdf_bytes = io.BytesIO()
        writer.write(pdf_bytes)
        pdf_bytes.seek(0)

        # Ensure extract_text_from_pdf runs without throwing
        extracted = extract_text_from_pdf(pdf_bytes.getvalue())
        self.assertIsInstance(extracted, str)


if __name__ == '__main__':
    unittest.main()
