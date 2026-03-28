import os
from datetime import datetime
import uuid

BASE_RESUME_DIR = "resumes"


def ensure_base_dir():
    """Ensure base resumes directory exists"""
    if not os.path.exists(BASE_RESUME_DIR):
        os.makedirs(BASE_RESUME_DIR)

def create_job(job_title, job_description, job_profile):
    ensure_base_dir()

    job_id = str(uuid.uuid4())[:8]  # short unique ID

    folder_path = os.path.join(BASE_RESUME_DIR, job_id)
    os.makedirs(folder_path, exist_ok=True)

    # Save JD
    jd_path = os.path.join(folder_path, "jd.txt")
    with open(jd_path, "w", encoding="utf-8") as f:
        f.write(job_description)

    # Save metadata
    meta = {
        "job_id": job_id,
        "title": job_title,
        "profile": job_profile,
        "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }

    import json
    with open(os.path.join(folder_path, "meta.json"), "w") as f:
        json.dump(meta, f)

    return meta


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


from resume_parser import extract_resume_text, extract_candidate_info

def save_uploaded_file(file, job_id):
    job = get_job(job_id)

    temp_path = os.path.join(job["path"], file.name)

    with open(temp_path, "wb") as f:
        f.write(file.getbuffer())

    # Extract info
    text = extract_resume_text(temp_path)
    info = extract_candidate_info(text)

    name = info.get("emails", ["candidate"])[0].split("@")[0]

    new_name = f"{name}_{int(datetime.now().timestamp())}.pdf"
    new_path = os.path.join(job["path"], new_name)

    os.rename(temp_path, new_path)

    return new_path


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