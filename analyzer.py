import re
import io
from typing import Dict, List, Set, Any, Tuple
from pypdf import PdfReader

# Comprehensive list of stop words to filter out noise
STOP_WORDS = {
    "a", "about", "above", "after", "again", "against", "all", "am", "an", "and",
    "any", "are", "aren't", "as", "at", "be", "because", "been", "before", "being",
    "below", "between", "both", "but", "by", "can", "can't", "cannot", "could",
    "couldn't", "did", "didn't", "do", "does", "doesn't", "doing", "don't", "down",
    "during", "each", "few", "for", "from", "further", "had", "hadn't", "has",
    "hasn't", "have", "haven't", "having", "he", "he'd", "he'll", "he's", "her",
    "here", "here's", "hers", "herself", "him", "himself", "his", "how", "how's",
    "i", "i'd", "i'll", "i'm", "i've", "if", "in", "into", "is", "isn't", "it",
    "it's", "its", "itself", "let's", "me", "more", "most", "mustn't", "my",
    "myself", "no", "nor", "not", "of", "off", "on", "once", "only", "or", "other",
    "ought", "our", "ours", "ourselves", "out", "over", "own", "same", "shan't",
    "she", "she'd", "she'll", "she's", "should", "shouldn't", "so", "some", "such",
    "than", "that", "that's", "the", "their", "theirs", "them", "themselves",
    "then", "there", "there's", "these", "they", "they'd", "they'll", "they're",
    "they've", "this", "those", "through", "to", "too", "under", "until", "up",
    "very", "was", "wasn't", "we", "we'd", "we'll", "we're", "we've", "were",
    "weren't", "what", "what's", "when", "when's", "where", "where's", "which",
    "while", "who", "who's", "whom", "why", "why's", "with", "won't", "would",
    "wouldn't", "you", "you'd", "you'll", "you're", "you've", "your", "yours",
    "yourself", "yourselves", "etc", "eg", "ie", "role", "candidate", "job",
    "work", "position", "company", "looking", "required", "requirements",
    "responsibilities", "qualification", "qualifications", "preferred", "plus",
    "opportunity", "applicant", "applicants", "ability", "experience", "years",
    "knowledge", "skills", "understanding", "good", "strong", "must", "able"
}

# Standard Hard / Technical skills dictionary (normalized lowercase)
TECH_SKILLS = {
    # Languages
    "python", "javascript", "typescript", "java", "c++", "c#", "golang", "go",
    "rust", "ruby", "php", "swift", "kotlin", "scala", "r", "dart", "html",
    "css", "html5", "css3", "sass", "sql", "bash", "shell", "powershell",
    
    # Frameworks & Libraries
    "react", "react.js", "reactjs", "angular", "vue", "vue.js", "vuejs", "next.js",
    "nextjs", "node", "node.js", "nodejs", "express", "express.js", "django",
    "flask", "fastapi", "spring", "spring boot", "asp.net", ".net", ".net core",
    "laravel", "rails", "ruby on rails", "tailwind", "bootstrap", "jquery",
    "redux", "graphql", "rest api", "restful", "rest apis", "grpc",
    
    # Databases & Caching
    "postgresql", "postgres", "mysql", "mongodb", "sqlite", "redis", "elasticsearch",
    "cassandra", "dynamodb", "oracle", "mariadb", "firebase", "supabase",
    
    # Cloud, DevOps & Infrastructure
    "aws", "amazon web services", "azure", "gcp", "google cloud", "docker",
    "kubernetes", "k8s", "ci/cd", "cicd", "jenkins", "github actions", "gitlab",
    "terraform", "ansible", "linux", "nginx", "apache", "serverless", "microservices",
    "kafka", "rabbitmq", "cloudformation",
    
    # Data Science / AI / ML
    "machine learning", "deep learning", "nlp", "computer vision", "artificial intelligence",
    "tensorflow", "pytorch", "keras", "pandas", "numpy", "scikit-learn", "scipy",
    "data analysis", "data visualization", "tableau", "power bi", "spark", "hadoop",
    "llm", "large language models", "prompt engineering",
    
    # Testing & Tooling
    "git", "github", "bitbucket", "jira", "confluence", "postman", "jest",
    "cypress", "selenium", "pytest", "unit testing", "integration testing",
    "tdd", "agile", "scrum", "kanban", "devops", "system design", "oop",
    "object-oriented", "data structures", "algorithms"
}

# Soft Skills
SOFT_SKILLS = {
    "communication", "verbal communication", "written communication", "leadership",
    "teamwork", "collaboration", "cross-functional", "problem solving",
    "analytical thinking", "critical thinking", "time management", "organization",
    "adaptability", "flexibility", "mentorship", "coaching", "ownership",
    "attention to detail", "creativity", "negotiation", "presentation",
    "stakeholder management", "project management", "client facing"
}

# Strong Action Verbs for ATS impact analysis
ACTION_VERBS = {
    "accelerated", "accomplished", "achieved", "acquired", "adapted", "administered",
    "advised", "analyzed", "appraised", "approved", "architected", "arranged",
    "assembled", "assessed", "audited", "automated", "authored", "balanced",
    "boosted", "briefed", "budgeted", "built", "calculated", "centralized",
    "championed", "clarified", "coached", "collaborated", "combined", "communicated",
    "composed", "computed", "conceptualized", "conducted", "consolidated",
    "constructed", "consulted", "controlled", "coordinated", "corrected", "counseled",
    "created", "cultivated", "customized", "debugged", "decreased", "defined",
    "delegated", "delivered", "demonstrated", "deployed", "designed", "detailed",
    "detected", "determined", "developed", "devised", "diagnosed", "directed",
    "discovered", "dispatched", "diversified", "documented", "drafted", "earned",
    "edited", "educated", "eliminated", "enabled", "enforced", "engineered",
    "enhanced", "enlarged", "established", "estimated", "evaluated", "examined",
    "executed", "expanded", "expedited", "experimented", "explored", "facilitated",
    "finalized", "forecasted", "formulated", "founded", "fostered", "generated",
    "guided", "handled", "headed", "identified", "illustrated", "implemented",
    "improved", "improvised", "increased", "indexed", "influenced", "initiated",
    "innovated", "inspected", "installed", "instituted", "instructed", "integrated",
    "intensified", "interpreted", "introduced", "invented", "investigated",
    "launched", "lead", "led", "leveraged", "maintained", "managed", "maximized",
    "measured", "mediated", "mentored", "minimized", "modeled", "moderated",
    "modernized", "monitored", "motivated", "negotiated", "obtained", "operated",
    "optimized", "orchestrated", "organized", "originated", "overhauled", "oversaw",
    "performed", "pioneered", "planned", "prepared", "presented", "produced",
    "programmed", "promoted", "proposed", "provided", "published", "purchased",
    "quantified", "raised", "rebuilt", "recommended", "reconciled", "recruited",
    "redesigned", "reduced", "refined", "reformed", "regulated", "remodeled",
    "reorganized", "replaced", "reported", "researched", "resolved", "restructured",
    "revamped", "reviewed", "revised", "revitalized", "saved", "scheduled",
    "screened", "secured", "selected", "separated", "shaped", "simplified",
    "solved", "spearheaded", "standardized", "streamlined", "strengthened",
    "structured", "supervised", "supported", "surpassed", "synthesized", "systematized",
    "tabulated", "targeted", "tested", "tracked", "trained", "transformed",
    "transitioned", "translated", "triumphed", "troubleshot", "unified", "upgraded",
    "utilized", "validated", "verified", "yielded"
}

# Standard ATS Section Headers
ATS_SECTIONS = {
    "contact": ["email", "phone", "linkedin", "github", "address", "contact"],
    "experience": ["experience", "work experience", "employment history", "professional experience", "work history"],
    "education": ["education", "academic background", "degrees", "certifications", "qualifications", "university", "college"],
    "skills": ["skills", "technical skills", "core competencies", "technologies", "tech stack", "tools"],
    "projects": ["projects", "personal projects", "key projects", "portfolio"],
    "summary": ["summary", "professional summary", "about me", "objective", "profile"]
}


def extract_text_from_pdf(pdf_file_bytes: bytes) -> str:
    """
    Extracts plain text from PDF file bytes using pypdf.
    """
    try:
        pdf_stream = io.BytesIO(pdf_file_bytes)
        reader = PdfReader(pdf_stream)
        text_content = []
        for i, page in enumerate(reader.pages):
            page_text = page.extract_text() or ""
            text_content.append(page_text)
        full_text = "\n".join(text_content).strip()
        return full_text
    except Exception as e:
        raise ValueError(f"Failed to parse PDF: {str(e)}")


def clean_and_tokenize(text: str) -> List[str]:
    """
    Tokenizes text into cleaned lowercase alphanumeric tokens.
    """
    clean_str = re.sub(r'[^a-zA-Z0-9\+\#\.\-]', ' ', text.lower())
    tokens = [t.strip('.-') for t in clean_str.split() if t.strip('.-')]
    return tokens


def extract_ngrams(tokens: List[str], n: int = 2) -> List[str]:
    """
    Extracts n-gram phrases (e.g., bigrams, trigrams) from token list.
    """
    return [" ".join(tokens[i:i+n]) for i in range(len(tokens) - n + 1)]


def extract_keywords_from_text(text: str) -> Dict[str, Any]:
    """
    Extracts relevant keywords, technical skills, soft skills, and n-grams from text.
    """
    lower_text = text.lower()
    tokens = clean_and_tokenize(text)
    
    # Filter stopwords and short tokens
    meaningful_tokens = [t for t in tokens if t not in STOP_WORDS and len(t) > 1 and not t.isnumeric()]
    
    # Extract 2-grams and 3-grams
    bigrams = extract_ngrams(meaningful_tokens, 2)
    trigrams = extract_ngrams(meaningful_tokens, 3)
    
    # Detect hard technical skills
    matched_tech = set()
    for skill in TECH_SKILLS:
        # Check boundary match or substring for compound words
        pattern = r'(?<![a-zA-Z0-9])' + re.escape(skill) + r'(?![a-zA-Z0-9])'
        if re.search(pattern, lower_text):
            matched_tech.add(skill)
            
    # Detect soft skills
    matched_soft = set()
    for soft in SOFT_SKILLS:
        pattern = r'(?<![a-zA-Z0-9])' + re.escape(soft) + r'(?![a-zA-Z0-9])'
        if re.search(pattern, lower_text):
            matched_soft.add(soft)
            
    # Detect action verbs
    found_action_verbs = set()
    for verb in ACTION_VERBS:
        pattern = r'(?<![a-zA-Z0-9])' + re.escape(verb) + r'(?![a-zA-Z0-9])'
        if re.search(pattern, lower_text):
            found_action_verbs.add(verb)

    # General domain keywords (frequent meaningful terms)
    freq: Dict[str, int] = {}
    for t in meaningful_tokens:
        freq[t] = freq.get(t, 0) + 1

    # Add frequent bigrams
    for bg in bigrams:
        if bg in TECH_SKILLS or bg in SOFT_SKILLS:
            freq[bg] = freq.get(bg, 0) + 2

    return {
        "tokens": meaningful_tokens,
        "tech_skills": matched_tech,
        "soft_skills": matched_soft,
        "action_verbs": found_action_verbs,
        "freq": freq,
        "raw_text": text
    }


def check_resume_sections(resume_text: str) -> Dict[str, bool]:
    """
    Checks if standard ATS resume sections are present.
    """
    lower_text = resume_text.lower()
    sections_found = {}
    
    for section_name, keywords in ATS_SECTIONS.items():
        found = False
        for kw in keywords:
            pattern = r'(?<![a-zA-Z0-9])' + re.escape(kw) + r'(?![a-zA-Z0-9])'
            if re.search(pattern, lower_text):
                found = True
                break
        sections_found[section_name] = found

    # Additional contact info check: email & phone regex
    has_email = bool(re.search(r'[\w\.-]+@[\w\.-]+\.\w+', resume_text))
    has_phone = bool(re.search(r'(\+?\d{1,3}[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}', resume_text))
    
    sections_found["email"] = has_email
    sections_found["phone"] = has_phone
    sections_found["contact"] = sections_found.get("contact", False) or (has_email and has_phone)
    
    return sections_found


def count_quantifiable_metrics(resume_text: str) -> int:
    """
    Detects metrics like percentages (25%), dollar amounts ($10k), numbers with impact.
    """
    patterns = [
        r'\d+%',                          # 50%
        r'\$\s?\d+([.,]\d+)?(\s?[kKmMbB])?', # $100k
        r'\b\d{1,3}(,\d{3})+(\+)?\b',     # 100,000+
        r'\b\d+\+\s+(users|clients|projects|features|team members|engineers|customers)\b',
        r'\bincreased by \d+\b',
        r'\breduced by \d+\b',
        r'\bgrew by \d+\b'
    ]
    total_metrics = 0
    for p in patterns:
        matches = re.findall(p, resume_text, flags=re.IGNORECASE)
        total_metrics += len(matches)
    return total_metrics


def analyze_resume_ats(resume_text: str, job_description: str) -> Dict[str, Any]:
    """
    Main ATS evaluation pipeline comparing resume text with job description.
    Returns comprehensive score, subscores, matched/missing keywords, and actionable improvements.
    """
    if not resume_text.strip():
        raise ValueError("Resume text is empty or could not be extracted.")
    if not job_description.strip():
        raise ValueError("Job description cannot be empty.")

    resume_analysis = extract_keywords_from_text(resume_text)
    jd_analysis = extract_keywords_from_text(job_description)

    # 1. Target Keywords from Job Description
    # We combine tech skills, soft skills, and top frequent domain tokens
    jd_target_keywords: Set[str] = set()
    jd_target_keywords.update(jd_analysis["tech_skills"])
    jd_target_keywords.update(jd_analysis["soft_skills"])

    # Add top frequent meaningful terms from JD if tech/soft skills are sparse
    sorted_jd_terms = sorted(jd_analysis["freq"].items(), key=lambda x: x[1], reverse=True)
    for term, count in sorted_jd_terms[:15]:
        if len(term) > 3 and term not in STOP_WORDS:
            jd_target_keywords.add(term)

    # If JD is very short or generic, add all extracted tokens
    if len(jd_target_keywords) < 5:
        for t in jd_analysis["tokens"][:10]:
            jd_target_keywords.add(t)

    # 2. Match Keywords
    resume_lower = resume_text.lower()
    matched_keywords: List[str] = []
    missing_keywords: List[str] = []

    for kw in sorted(jd_target_keywords):
        pattern = r'(?<![a-zA-Z0-9])' + re.escape(kw) + r'(?![a-zA-Z0-9])'
        if re.search(pattern, resume_lower):
            matched_keywords.append(kw)
        else:
            missing_keywords.append(kw)

    total_target = max(len(jd_target_keywords), 1)
    keyword_match_pct = round((len(matched_keywords) / total_target) * 100, 1)

    # 3. Technical Skills Alignment
    jd_tech = jd_analysis["tech_skills"]
    matched_tech = [s for s in jd_tech if s in resume_analysis["tech_skills"]]
    missing_tech = [s for s in jd_tech if s not in resume_analysis["tech_skills"]]
    tech_match_pct = round((len(matched_tech) / max(len(jd_tech), 1)) * 100, 1) if jd_tech else keyword_match_pct

    # 4. Resume Structure & Formatting
    sections = check_resume_sections(resume_text)
    word_count = len(resume_text.split())
    
    # Section presence scoring (out of 100)
    section_score = 0
    if sections.get("contact"): section_score += 25
    if sections.get("experience"): section_score += 25
    if sections.get("skills"): section_score += 25
    if sections.get("education"): section_score += 15
    if sections.get("summary") or sections.get("projects"): section_score += 10

    # Word count evaluation (250 to 900 words is optimal for 1-2 pages ATS)
    word_count_status = "Optimal"
    if word_count < 150:
        word_count_status = "Too short (under 150 words)"
        section_score = max(0, section_score - 20)
    elif word_count < 250:
        word_count_status = "Slightly short"
    elif word_count > 1200:
        word_count_status = "Too long (over 1200 words)"
        section_score = max(0, section_score - 10)

    # 5. Impact & Action Verbs
    action_verbs_found = resume_analysis["action_verbs"]
    metrics_count = count_quantifiable_metrics(resume_text)
    
    # Impact score based on action verb variety and measurable results
    impact_score = min(100, (len(action_verbs_found) * 10) + (metrics_count * 15))

    # 6. Overall Weighted ATS Score (0 - 100)
    # Weights:
    # 50% Keyword Match
    # 25% Technical Skills Match
    # 15% Structure & Formatting
    # 10% Impact & Action Verbs
    overall_score = round(
        (keyword_match_pct * 0.50) +
        (tech_match_pct * 0.25) +
        (section_score * 0.15) +
        (impact_score * 0.10)
    )
    overall_score = max(0, min(100, overall_score))

    # Determine Grade & Verdict
    if overall_score >= 85:
        match_level = "Excellent Match"
        match_color = "success" # Green
        summary_verdict = "Your resume strongly aligns with this job description. You have a high probability of passing initial ATS keyword filters."
    elif overall_score >= 70:
        match_level = "Good Match"
        match_color = "primary" # Blue/Indigo
        summary_verdict = "Your resume covers most core competencies, but adding a few missing target keywords will significantly improve your ranking."
    elif overall_score >= 50:
        match_level = "Moderate Match"
        match_color = "warning" # Amber/Orange
        summary_verdict = "Your resume has moderate alignment. Several key technologies and domain skills mentioned in the job description are missing."
    else:
        match_level = "Low Match"
        match_color = "danger" # Red
        summary_verdict = "Your resume is missing critical job keywords and requirements. High risk of being filtered out by automated ATS scanners."

    # 7. Generate Actionable Improvement Areas
    improvements: List[Dict[str, str]] = []

    # Improvement Area: Missing Technical Skills
    if missing_tech:
        top_missing_tech = ", ".join(f"'{s.title()}'" for s in missing_tech[:6])
        improvements.append({
            "category": "Missing Hard Skills",
            "priority": "High",
            "title": f"Add missing core technical skills: {top_missing_tech}",
            "description": f"The job description explicitly mentions {top_missing_tech}. If you have experience with these tools or concepts, ensure they are explicitly listed in your Skills or Experience section."
        })

    # Improvement Area: General Missing Keywords
    other_missing = [kw for kw in missing_keywords if kw not in missing_tech]
    if other_missing:
        sample_missing = ", ".join(f"'{kw}'" for kw in other_missing[:5])
        improvements.append({
            "category": "Keyword Optimization",
            "priority": "High" if overall_score < 70 else "Medium",
            "title": f"Incorporate target domain terms: {sample_missing}",
            "description": "ATS algorithms scan for direct keyword density. Weave these phrases naturally into your past achievement bullet points."
        })

    # Improvement Area: Missing Standard Sections
    missing_sections = []
    if not sections.get("experience"): missing_sections.append("Work Experience")
    if not sections.get("skills"): missing_sections.append("Skills / Technologies")
    if not sections.get("education"): missing_sections.append("Education")
    if not sections.get("contact"): missing_sections.append("Direct Contact Info (Email & Phone)")
    if not sections.get("summary"): missing_sections.append("Professional Summary")

    if missing_sections:
        improvements.append({
            "category": "Resume Structure",
            "priority": "High",
            "title": f"Add standard section headers: {', '.join(missing_sections)}",
            "description": "ATS parsers look for standard headings to categorize your background. Use clear, un-nested headers like 'Experience', 'Education', and 'Skills'."
        })

    # Improvement Area: Quantifiable Metrics
    if metrics_count < 2:
        improvements.append({
            "category": "Measurable Impact",
            "priority": "Medium",
            "title": "Quantify your achievements with numbers and percentages",
            "description": "Only a few measurable outcomes (%, $, metric improvements) were found. High-ranking resumes quantify results (e.g., 'Reduced API latency by 35%', 'Managed a team of 6 engineers')."
        })

    # Improvement Area: Action Verbs
    if len(action_verbs_found) < 5:
        improvements.append({
            "category": "Content & Phrasing",
            "priority": "Medium",
            "title": "Start bullet points with strong action verbs",
            "description": "Use impactful action verbs such as 'Architected', 'Spearheaded', 'Streamlined', 'Optimized', and 'Delivered' rather than passive phrases like 'Responsible for'."
        })

    # Improvement Area: Resume Length
    if word_count < 250:
        improvements.append({
            "category": "Resume Length",
            "priority": "Medium",
            "title": "Expand on your project and work experience details",
            "description": f"Your resume contains only {word_count} words. A standard 1-page ATS resume typically contains 350–700 words detailing your responsibilities and tools."
        })
    elif word_count > 1000:
        improvements.append({
            "category": "Resume Length",
            "priority": "Low",
            "title": "Consider condensing content for concise scanning",
            "description": f"Your resume is {word_count} words. Ensuring your resume is focused and under 2 pages (500–900 words) helps both ATS scanners and human recruiters."
        })

    # If everything is already great
    if not improvements:
        improvements.append({
            "category": "Optimization",
            "priority": "Low",
            "title": "Resume is well-optimized for ATS",
            "description": "Your resume has high keyword density, standard structural headers, and strong action verbs. Keep your formatting simple and avoid multi-column tables."
        })

    return {
        "score": overall_score,
        "match_level": match_level,
        "match_color": match_color,
        "summary_verdict": summary_verdict,
        "sub_scores": {
            "keyword_match": keyword_match_pct,
            "tech_skills_match": tech_match_pct,
            "structure_score": section_score,
            "impact_score": impact_score
        },
        "statistics": {
            "word_count": word_count,
            "word_count_status": word_count_status,
            "total_jd_keywords": len(jd_target_keywords),
            "matched_keywords_count": len(matched_keywords),
            "missing_keywords_count": len(missing_keywords),
            "action_verbs_count": len(action_verbs_found),
            "metrics_count": metrics_count
        },
        "matched_keywords": matched_keywords,
        "missing_keywords": missing_keywords,
        "sections_detected": sections,
        "improvements": improvements
    }
