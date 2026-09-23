import os
import sys
from flask import Flask, render_template, request, jsonify
from werkzeug.utils import secure_filename
from analyzer import extract_text_from_pdf, analyze_resume_ats

app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16 MB limit
ALLOWED_EXTENSIONS = {'pdf'}

def allowed_file(filename: str) -> bool:
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/api/analyze', methods=['POST'])
def analyze():
    try:
        # Validate Job Description
        job_description = request.form.get('job_description', '').strip()
        if not job_description:
            return jsonify({
                "success": False,
                "error": "Please enter or paste a Job Description."
            }), 400

        # Handle PDF File upload or direct resume text
        resume_text = ""
        if 'resume_file' in request.files:
            file = request.files['resume_file']
            if file and file.filename != '':
                if not allowed_file(file.filename):
                    return jsonify({
                        "success": False,
                        "error": "Invalid file format. Please upload a PDF file (.pdf)."
                    }), 400
                
                file_bytes = file.read()
                if len(file_bytes) == 0:
                    return jsonify({
                        "success": False,
                        "error": "The uploaded PDF file is empty."
                    }), 400
                
                try:
                    resume_text = extract_text_from_pdf(file_bytes)
                except Exception as e:
                    return jsonify({
                        "success": False,
                        "error": f"Could not extract text from PDF: {str(e)}"
                    }), 400

        # Fallback if text was passed directly (e.g. testing / sample)
        if not resume_text and request.form.get('resume_text'):
            resume_text = request.form.get('resume_text', '').strip()

        if not resume_text:
            return jsonify({
                "success": False,
                "error": "No resume provided. Please upload a PDF resume file."
            }), 400

        # Run ATS Analysis
        analysis_result = analyze_resume_ats(resume_text, job_description)
        
        return jsonify({
            "success": True,
            "data": analysis_result
        }), 200

    except ValueError as ve:
        return jsonify({
            "success": False,
            "error": str(ve)
        }), 400
    except Exception as e:
        return jsonify({
            "success": False,
            "error": f"An unexpected error occurred during analysis: {str(e)}"
        }), 500


@app.route('/api/sample', methods=['GET'])
def sample_data():
    """
    Returns sample job description and resume text for instant demo & testing.
    """
    sample_jd = (
        "Senior Full Stack Software Engineer\n\n"
        "About the Role:\n"
        "We are looking for a Senior Full Stack Engineer with expertise in Python, React, and AWS.\n\n"
        "Responsibilities:\n"
        "- Architect, design, and develop scalable REST APIs and microservices using Python and Flask/FastAPI.\n"
        "- Build interactive, responsive frontend web interfaces using React, TypeScript, and modern CSS.\n"
        "- Deploy, manage, and monitor containerized applications with Docker and Kubernetes on AWS.\n"
        "- Work closely with product managers and cross-functional teams in an Agile Scrum environment.\n"
        "- Implement automated CI/CD pipelines, write unit tests with PyTest, and perform code reviews.\n\n"
        "Requirements:\n"
        "- 4+ years of professional software development experience.\n"
        "- Strong proficiency in Python, JavaScript, TypeScript, React, and SQL (PostgreSQL).\n"
        "- Hands-on experience with Docker, CI/CD, Git, and cloud services (AWS or GCP).\n"
        "- Solid understanding of data structures, system design, and database optimization.\n"
        "- Excellent problem-solving, communication, and teamwork skills."
    )
    
    sample_resume = (
        "Alex Morgan\n"
        "Email: alex.morgan.dev@example.com | Phone: (555) 019-2834 | LinkedIn: linkedin.com/in/alexmorgan-dev\n\n"
        "Professional Summary:\n"
        "Results-driven Full Stack Software Engineer with 4 years of experience building scalable web applications. "
        "Proficient in Python, React, JavaScript, and PostgreSQL with a strong track record of optimizing system performance.\n\n"
        "Skills:\n"
        "- Languages & Frameworks: Python, JavaScript, React, Flask, HTML5, CSS3, SQL, PostgreSQL\n"
        "- Tools & DevOps: Git, Docker, GitHub, Linux, REST APIs, Agile, JIRA\n\n"
        "Professional Experience:\n"
        "Software Engineer | TechNova Solutions (2022 – Present)\n"
        "- Developed and maintained high-throughput REST APIs using Python and Flask, reducing response times by 32%.\n"
        "- Built interactive dashboard components in React and JavaScript used by over 50,000 active monthly users.\n"
        "- Automated database query indexing on PostgreSQL, improving system query efficiency by 25%.\n"
        "- Collaborated with cross-functional engineering teams in daily Agile Scrum sprints.\n\n"
        "Junior Developer | Horizon Labs (2020 – 2022)\n"
        "- Implemented front-end user interfaces and responsive layouts using HTML5, CSS3, and JavaScript.\n"
        "- Conducted unit testing and fixed bugs, improving test coverage by 20%.\n\n"
        "Education:\n"
        "B.S. in Computer Science | State University (2016 – 2020)"
    )

    return jsonify({
        "sample_jd": sample_jd,
        "sample_resume": sample_resume
    })


if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    print(f"==================================================")
    print(f" ResumeFit - ATS Resume Analyzer")
    print(f" Running locally at: http://127.0.0.1:{port}")
    print(f" Press Ctrl+C to stop the server")
    print(f"==================================================")
    app.run(host='0.0.0.0', port=port, debug=False)
