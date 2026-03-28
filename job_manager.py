import os
from datetime import datetime

BASE_RESUME_DIR = "resumes"


def ensure_base_dir():
    """Ensure base resumes directory exists"""
    if not os.path.exists(BASE_RESUME_DIR):
        os.makedirs(BASE_RESUME_DIR)


def create_job(job_id: str, jd_text: str):
    """
    Create a new job folder with jd.txt
    
    Structure:
    resumes/
        └── job_id/
              ├── jd.txt
    """
    ensure_base_dir()

    job_path = os.path.join(BASE_RESUME_DIR, job_id)

    if os.path.exists(job_path):
        raise Exception(f"Job {job_id} already exists")

    os.makedirs(job_path)

    jd_path = os.path.join(job_path, "jd.txt")

    with open(jd_path, "w", encoding="utf-8") as f:
        f.write(jd_text)

    return {
        "job_id": job_id,
        "path": job_path,
        "jd_path": jd_path,
        "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }


def get_all_jobs():
    """
    Discover all jobs from filesystem
    
    Returns:
        [
            {
                "job_id": "01",
                "path": "resumes/01",
                "jd_path": ".../jd.txt"
            }
        ]
    """
    ensure_base_dir()

    jobs = []

    for folder in os.listdir(BASE_RESUME_DIR):
        job_path = os.path.join(BASE_RESUME_DIR, folder)

        if not os.path.isdir(job_path):
            continue

        jd_path = os.path.join(job_path, "jd.txt")

        # Only treat as job if jd.txt exists
        if os.path.exists(jd_path):
            jobs.append({
                "job_id": folder,
                "path": job_path,
                "jd_path": jd_path
            })

    return sorted(jobs, key=lambda x: x["job_id"])


def get_job(job_id: str):
    """Get single job details"""
    job_path = os.path.join(BASE_RESUME_DIR, job_id)
    jd_path = os.path.join(job_path, "jd.txt")

    if not os.path.exists(job_path) or not os.path.exists(jd_path):
        return None

    return {
        "job_id": job_id,
        "path": job_path,
        "jd_path": jd_path
    }


def save_uploaded_file(file, job_id: str):
    """Save uploaded file into job folder"""
    job = get_job(job_id)

    if not job:
        raise Exception("Invalid job")

    save_path = os.path.join(job["path"], file.name)

    with open(save_path, "wb") as f:
        f.write(file.getbuffer())

    return save_path


def download_resume_from_url(url: str, job_id: str):
    """Download resume from URL into job folder"""
    import requests

    job = get_job(job_id)
    if not job:
        raise Exception("Invalid job")

    filename = url.split("/")[-1]
    save_path = os.path.join(job["path"], filename)

    response = requests.get(url)

    if response.status_code != 200:
        raise Exception("Failed to download file")

    with open(save_path, "wb") as f:
        f.write(response.content)

    return save_path