"""
Candidate Matcher Module
Intelligently matches candidate resumes to job descriptions using:
  1. AI-powered evaluation (GPT-3.5) - PRIMARY METHOD
  2. TF-IDF similarity matching - FALLBACK

AI EVALUATION SYSTEM:
- Evaluates skill usage with weighted scoring
- Prioritizes demonstrated skills over keyword lists
- Assesses work experience, projects, internships, and certifications
- Returns detailed analysis including strengths and gaps
- Provides clear ACCEPT/HOLD/REJECT recommendations

REQUIREMENTS FOR AI MODE:
- OpenAI API key must be set in .env file (OPENAI_API_KEY)
- If not available, automatically falls back to TF-IDF matching

SKILL WEIGHTING RULES (AI):
- HIGHEST: Skill listed AND demonstrated in projects/work
- HIGH: Skill demonstrated in work/projects (not in Skills section)
- MEDIUM: Skill listed in Skills section only
- LOW: Weakly implied or tangential skills

SCORING GUIDELINES:
- 0.85-1.0: Excellent - Strong demonstrated skills align with all requirements
- 0.70-0.84: Good - Most key skills demonstrated, minor gaps acceptable
- 0.50-0.69: Moderate - Some demonstrable skills but significant gaps
- 0.30-0.49: Weak - Few relevant demonstrated skills
- 0.0-0.29: Poor - Little to no relevant skills demonstrated
"""

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import re
import json
from config import OPENAI_API_KEY

# Try to import OpenAI
try:
    from openai import OpenAI
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False

# ============================================================================
# AI-BASED RESUME EVALUATION SYSTEM PROMPT
# ============================================================================
# AI_EVALUATION_PROMPT = """
# You are an expert AI hiring assistant evaluating how well a candidate's resume matches a job description.

# TASK: Analyze the resume and return ONLY valid JSON with this exact structure (no extra text):

# {
#   "match_score": 0.85,
#   "reasoning": "Brief explanation of the score",
#   "strengths": ["Strength 1", "Strength 2", "Strength 3"],
#   "gaps": ["Gap 1", "Gap 2"],
#   "demonstrated_skills": ["Skill with evidence from projects/work"],
#   "listed_skills_only": ["Skill listed but without proof of use"],
#   "recommendation": "ACCEPT/HOLD/REJECT"
# }

# EVALUATION RULES

# 1. SKILL WEIGHTING (Most Important)

# - HIGHEST → Skill listed in Skills section AND demonstrated in projects, internships, jobs, or certifications  
# - HIGH → Skill demonstrated in projects/work even if not listed in Skills  
# - MEDIUM → Skill listed in Skills but no clear proof of use  
# - LOW → Weakly implied or loosely related skills

# Prefer **demonstrated skills over keyword lists**. Skills with proof of use should increase the score more than skills that are only listed.

# 2. EVALUATION FACTORS (priority order)

# 1. Relevant skills with proven usage
# 2. Relevant work experience
# 3. Technical projects showing capability
# 4. Internships with practical work
# 5. Certifications and education
# 6. Overall alignment with the job requirements

# 3. SCORING GUIDELINES

# 0.85–1.00 → Excellent match  
# 0.70–0.84 → Good match  
# 0.50–0.69 → Moderate match  
# 0.30–0.49 → Weak match  
# 0.00–0.29 → Poor match  

# 4. ASSESSMENT PRINCIPLES

# - Prioritize **evidence of skill usage**
# - Evaluate depth of work, not just years
# - Consider transferable skills from similar domains
# - Penalize resumes listing many skills without proof

# 5. FAIR EVALUATION

# - Judge only professional competencies
# - Ignore name, location, gender, or personal details

# RESUME:
# {resume}

# JOB DESCRIPTION:
# {job_description}

# Return ONLY valid JSON.
# """

AI_EVALUATION_PROMPT = """
You are an AI hiring assistant.

Evaluate how well the resume matches the job description.

Return ONLY valid JSON:

{{
  "match_score": 0.0,
  "reasoning": "",
  "strengths": [],
  "gaps": [],
  "demonstrated_skills": [],
  "listed_skills_only": [],
  "recommendation": ""
}}

RULES:
- Focus on skills used in projects/work more than listed skills
- Consider partial matches
- Do NOT expect perfect match

SCORING:
- 0.8+ strong
- 0.6–0.79 good
- 0.4–0.59 moderate
- <0.4 weak

RECOMMENDATION:
- >=0.65 ACCEPT
- 0.5–0.64 HOLD
- <0.5 REJECT

RESUME:
{resume}

JOB:
{job_description}
"""

def evaluate_resume_with_ai(resume_text, job_description):
    """
    Evaluate resume using OpenAI's GPT model with detailed criteria
    
    Args:
        resume_text: Full text from candidate resume
        job_description: Full text from job description
    
    Returns:
        Tuple of (score, recommendation, analysis_dict)
    """
    if not OPENAI_AVAILABLE or not OPENAI_API_KEY:
        print("⚠️  OpenAI not available, falling back to TF-IDF matching...")
        return None, None, None

def evaluate_resume_with_ai(resume_text, job_description):
    """
    Evaluate resume using OpenAI's GPT model with detailed criteria
    
    Args:
        resume_text: Full text from candidate resume
        job_description: Full text from job description
    
    Returns:
        Tuple of (score, recommendation, analysis_dict)
    """
    if not OPENAI_AVAILABLE or not OPENAI_API_KEY:
        print("⚠️  OpenAI not available, falling back to TF-IDF matching...")
        return None, None, None
    
    try:
        client = OpenAI(api_key=OPENAI_API_KEY)
        
        # Format the prompt with resume and job description
        prompt = AI_EVALUATION_PROMPT.format(
            resume=resume_text,  # Limit to first 3000 chars
            job_description=job_description  # Limit to first 2000 chars
        )
        
        print("🤖 Evaluating resume with AI...")
        
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                # {
                #     "role": "system",
                #     "content": "You are an expert HR hiring assistant. Return ONLY valid JSON, no other text."
                # },
                {
                    "role": "system",
                    "content": "Return ONLY JSON. Be lenient with partial matches. Do not reject unless clearly unqualified."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            temperature=0.3,
            max_tokens=500
        )
        
        # Parse the response
        response_text = response.choices[0].message.content.strip()
        
        # Try to extract JSON if there's extra text
        try:
            # Find JSON object in response
            start_idx = response_text.find('{')
            end_idx = response_text.rfind('}') + 1
            if start_idx >= 0 and end_idx > start_idx:
                json_str = response_text[start_idx:end_idx]
                analysis = json.loads(json_str)
            else:
                analysis = json.loads(response_text)
        except json.JSONDecodeError:
            print("⚠️  Could not parse AI response, using defaults...")
            return None, None, None
        
        return (
            analysis.get('match_score', 0.5),
            analysis.get('recommendation', 'HOLD'),
            analysis
        )
    
    except Exception as e:
        print(f"⚠️  AI evaluation error: {e}. Falling back to TF-IDF...")
        return None, None, None


# ============================================================================
# LEGACY TF-IDF MATCHING (Used as fallback)
# ============================================================================
def match_resume_to_job_tfidf(resume_text, job_text):
    """
    Legacy TF-IDF based matching - used as fallback when AI is not available
    Calculate match score between resume and job description
    
    Args:
        resume_text: Full text from candidate resume
        job_text: Full text from job description
    
    Returns:
        Match score between 0 and 1 (0-100%)
    """
    try:
        if not resume_text or not job_text:
            print("❌ Resume or job text is empty")
            return 0.0
        
        # Create documents array
        documents = [resume_text, job_text]
        
        # Vectorize using TF-IDF
        vectorizer = TfidfVectorizer(
            lowercase=True,
            stop_words='english',
            min_df=1,
            max_features=1000
        )
        
        vectors = vectorizer.fit_transform(documents)
        
        # Calculate cosine similarity
        similarity = cosine_similarity(vectors[0:1], vectors[1:2])
        
        # Handle empty similarity matrix
        if similarity is None or similarity.size == 0:
            print("⚠️  Could not calculate similarity score")
            return 0.0
        
        score = similarity[0][0] if similarity.shape[0] > 0 and similarity.shape[1] > 0 else 0.0
        
        # Ensure score is between 0 and 1
        score = max(0.0, min(1.0, score))
        
        return score
    
    except Exception as e:
        print(f"❌ Error in TF-IDF matching: {e}")
        return 0.0


def match_resume_to_job(resume_text, job_text):
    """
    Main matching function - tries AI evaluation first, falls back to TF-IDF
    
    Args:
        resume_text: Full text from candidate resume
        job_text: Full text from job description
    
    Returns:
        Match score between 0 and 1 (0-100%)
    """
    # TRY AI EVALUATION FIRST
    ai_score, ai_recommendation, ai_analysis = evaluate_resume_with_ai(resume_text, job_text)
    
    if ai_score is not None:
        print(f"✅ AI Evaluation - Score: {ai_score}, Recommendation: {ai_recommendation}")
        # Store AI analysis for later use
        global LAST_AI_ANALYSIS
        LAST_AI_ANALYSIS = ai_analysis
        return ai_score
    
    # FALLBACK TO TF-IDF IF AI NOT AVAILABLE
    print("📊 Using TF-IDF matching (AI not available)...")
    return match_resume_to_job_tfidf(resume_text, job_text)


LAST_AI_ANALYSIS = None

def get_matching_keywords(resume_text, job_text):
    """
    Find keywords that match between resume and job description
    
    Args:
        resume_text: Resume text
        job_text: Job description text
    
    Returns:
        List of matching keywords
    """
    try:
        # Extract keywords from both
        resume_words = set(re.findall(r'\b\w{4,}\b', resume_text.lower()))
        job_words = set(re.findall(r'\b\w{4,}\b', job_text.lower()))
        
        # Find common words
        matching = resume_words.intersection(job_words)
        
        return sorted(list(matching))
    
    except Exception as e:
        print(f"❌ Error finding matching keywords: {e}")
        return []

def get_missing_keywords(resume_text, job_text):
    """
    Find keywords in job description that are missing in resume
    
    Args:
        resume_text: Resume text
        job_text: Job description text
    
    Returns:
        List of important missing keywords
    """
    try:
        resume_words = set(re.findall(r'\b\w{4,}\b', resume_text.lower()))
        
        # Extract likely important words from job description
        job_sentences = job_text.split('.')
        
        missing = []
        for sentence in job_sentences:
            words = set(re.findall(r'\b\w{4,}\b', sentence.lower()))
            # Words in job but not in resume
            difference = words - resume_words
            
            # Only consider substantial words
            if difference:
                missing.extend(list(difference)[:3])
        
        return list(set(missing))[:10]
    
    except Exception as e:
        print(f"❌ Error finding missing keywords: {e}")
        return []

def generate_match_report(resume_text, job_text, score):
    """
    Generate a detailed matching report
    Uses AI analysis if available, otherwise generates from keywords
    
    Args:
        resume_text: Resume text
        job_text: Job description text
        score: Match score
    
    Returns:
        Detailed report dictionary
    """
    try:
        report = {
            'score': score,
            'score_percentage': f"{score * 100:.1f}%",
        }
        
        # Use AI analysis if available
        if LAST_AI_ANALYSIS is not None:
            ai = LAST_AI_ANALYSIS
            report['matching_keywords'] = ai.get('demonstrated_skills', [])
            report['missing_keywords'] = ai.get('gaps', [])
            report['strengths'] = ai.get('strengths', [])
            report['gaps'] = ai.get('gaps', [])
            report['demonstrated_skills'] = ai.get('demonstrated_skills', [])
            report['listed_skills_only'] = ai.get('listed_skills_only', [])
            
            recommendation = ai.get('recommendation', 'HOLD')
            if recommendation == 'ACCEPT':
                report['status'] = 'ACCEPT'
                report['reason'] = ai.get('reasoning', 'Strong match with job requirements')
            elif recommendation == 'REJECT':
                report['status'] = 'REJECT'
                report['reason'] = ai.get('reasoning', 'Insufficient match with job requirements')
            else:
                report['status'] = 'HOLD'
                report['reason'] = ai.get('reasoning', 'Moderate match - requires manual review')
        else:
            # Fallback to keyword analysis
            report['matching_keywords'] = get_matching_keywords(resume_text, job_text)
            report['missing_keywords'] = get_missing_keywords(resume_text, job_text)
            
            # Determine status based on score
            if score >= 0.70:
                report['status'] = 'ACCEPT'
                report['reason'] = 'Strong match with job requirements'
            elif score >= 0.50:
                report['status'] = 'HOLD'
                report['reason'] = 'Moderate match - requires manual review'
            else:
                report['status'] = 'REJECT'
                report['reason'] = 'Insufficient match with job requirements'
        
        return report
    
    except Exception as e:
        print(f"❌ Error generating report: {e}")
        return {'score': score, 'status': 'ERROR', 'reason': str(e)}

if __name__ == "__main__":
    # Test the matcher
    print("Candidate Matcher Test\n")
    
    sample_resume = "Python developer with 5 years of experience in Django and React"
    sample_job = "We are looking for a Python developer with Django experience and React skills"
    
    score = match_resume_to_job(sample_resume, sample_job)
    print(f"Match Score: {score:.2f} ({score*100:.1f}%)")
    
    report = generate_match_report(sample_resume, sample_job, score)
    print(f"\nReport:")
    print(f"  Status: {report['status']}")
    print(f"  Score: {report['score_percentage']}")
    print(f"  Reason: {report['reason']}")
    print(f"  Matching Keywords: {report['matching_keywords'][:5]}")