from config import get_smtp_settings
from termcolor import colored
from g4f.client import Client

import subprocess
import smtplib
import yaml
import ssl
import os

ALLOWED_IMAGE_EXTENSIONS = [
    ".png",
    ".jpg",
    ".jpeg",
]

def _kill_chrome() -> None:
    # Helper function to kill chrome
    response = None
    if os.name == "posix":
        response = subprocess.run(["pkill", "chrome"])
    else:
        response = subprocess.run(["taskkill", "/IM", "chrome.exe", "/F"])
    if response.returncode == 0:
        print(colored("Chrome Killed Successfully!", "green"))
    else:
        print(colored("Error Killing Chrome!", "red"))

def _check_image(path: str) -> bool:
    if os.path.exists(path):
        # Check if it's an image
        if path.endswith(tuple(ALLOWED_IMAGE_EXTENSIONS)):
            return True
        else:
            return False
    else:
        return False

def _check_email(email: str) -> bool:
    # Helper function to check if email is valid
    return "@" in email and "." in email

def _extract_username(url: str, provider: str) -> str:
    # Helper function to extract username from URL
    if provider == "LinkedIn":
        return url.split("/")[-1]
    elif provider == "GitHub":
        return url.split("/")[-1]
    elif provider == "Portfolio":
        return url.split("/")[-1]
    else:
        return url.split("/")[-1]

def _get_information() -> dict:
    # Helper function to get basic user information
    def get_input(prompt):
        return input(colored(prompt, "blue"))

    def get_valid_input(prompt, validation_func, error_message):
        while True:
            value = get_input(prompt)
            if validation_func(value):
                return value
            print(colored(error_message, "red"))

    def add_items(prompt, items, split_chars=False):
        add_new_item = True
        while add_new_item:
            item = {}
            for field, field_prompt in prompt.items():
                item[field] = get_input(field_prompt)
                if split_chars:
                    item[field] = item[field].split(",")
            items.append(item)
            add_new_item = get_input(colored("> Do you want to add another? (Y/N) ", "blue")).lower() == "y"

    full_name = get_input("> What is your full name? ")

    email = get_valid_input("> What is your email? ", _check_email, "> Invalid Email. Please try again.")
    city = get_input("> What is your city? ")
    country = get_input("> What is your country? ")
    phone_number = get_input("> What is your phone number? ")

    profiles = []
    for provider in ["LinkedIn", "GitHub", "Portfolio", "Other"]:
        profile_url = get_input(f"> What is your {provider} URL? ")
        if profile_url:
            username = _extract_username(profile_url, provider)
            profiles.append({
                "network": provider,
                "username": username,
                "url": profile_url
            })

    user_image = get_valid_input("> What is the URL or path to your Image/Avatar? ", _check_image, "> Invalid Image. Please try again.")

    skills_prompt = {"name": "> What is your skill category? ", "keywords": "> What are the keywords? (Separate by comma) "}
    skills = []
    add_items(skills_prompt, skills, split_chars=True)

    educations_prompt = {"area": "> What area did you work in? ", "institution": "> At what institution did you work? ", "start_date": "> What is the start date? "}
    educations = []
    add_items(educations_prompt, educations)

    projects_prompt = {"description": "> What is the project description? ", "keywords": "> What are the keywords? (Separate by comma) ", "name": "> What is the project name? ", "project_url": "> What is the project URL? "}
    
    projects = []
    add_items(projects_prompt, projects)

    work_experience_prompt = {"area": "> What area did you work in? ", "company": "> What company did you work at? ", "description": "> What is the job description? ", "end_date": "> What is the end date? ", "start_date": "> What is the start date? "}
    work_experience = []
    add_items(work_experience_prompt, work_experience)

    return {
        "full_name": full_name,
        "email": email,
        "city": city,
        "country": country,
        "phone_number": phone_number,
        "profiles": profiles,
        "user_image": user_image,
        "skills": skills,
        "educations": educations,
        "projects": projects,
        "work_experience": work_experience
    }

def _populate_configuration(info) -> None:
    print(info)
    basics = {
        "email": info["email"],
        "location": {
            "city": info["city"],
            "countryCode": info["country"]
        },
        "name": info["full_name"],
        "phone": info["phone_number"],
        "profiles": info["profiles"],
        "url": "https://youtube.com/@fuji_codes"
    }

    education = []

    for edu in info["educations"]:
        education.append({
            "area": edu["area"],
            "institution": edu["institution"],
            "startDate": edu["start_date"]
        })

    projects = []

    for project in info["projects"]:
        projects.append({
            "description": project["description"],
            "keywords": project["keywords"],
            "name": project["name"],
            "url": project["project_url"]
        })

    skills = info["skills"]

    work = []

    for exp in info["work_experience"]:
        work.append({
            "highlights": [
                exp["description"]
            ],
            "name": exp["company"],
            "position": exp["area"],
            "startDate": exp["start_date"],
            "endDate": exp["end_date"]
        })

    configuration = {
        "basics": basics,
        "education": education,
        "projects": projects,
        "skills": skills,
        "work": work
    }

    with open("resume_config.yaml", "w") as file:
        yaml.dump(configuration, file)

def get_default_theme_location() -> str:
    venv_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    site_packages_dir = os.path.join(venv_dir, "lib", "site-packages") if os.name == "posix" else os.path.join(venv_dir, "Lib", "site-packages")

    resumy_dir = os.path.join(site_packages_dir, "resumy")

    if not resumy_dir:
        raise FileNotFoundError("Resumy not found. Please install resumy.")

    themes_dir = os.path.join(resumy_dir, "themes")
    default_theme = os.path.join(themes_dir, "prairie")

    return default_theme

def _generate_resume(info: dict) -> None:
    # Helper function to generate resume
    _populate_configuration(info)

    theme = input(colored("> What theme would you like to use? (Default: prairie) ", "blue") \
                    or get_default_theme_location())

    response = subprocess.run([
        "resumy",
        "build",
        "-o",
        "resume.pdf",
        "--theme",
        theme,
        "resume_config.yaml",
    ])

    if response.returncode == 0:
        print(colored("Resume Generated Successfully!", "green"))
    else:
        print(colored("Error Generating Resume!", "red"))

def _turn_markdown_to_pdf(markdown_path: str, pdf_path: str) -> None:
    # Helper function to turn markdown to pdf
    response = subprocess.run([
        "md2pdf",
        markdown_path,
        pdf_path,
        "--css",
        "css/md2pdf.css"
    ])

    if response.returncode == 0:
        print(colored("=> Markdown to PDF Conversion Successful!", "green"))
    else:
        print(colored("=> Error Converting Markdown to PDF!", "red"))

def _send_email(email: str, subject: str, cover_letter_path: str, resume_path: str) -> None:
    # Helper function to send email
    # Combine cover letter and resume
    attachment = "application.zip"
    response = subprocess.run([
        "zip",
        attachment,
        cover_letter_path,
        resume_path
    ])

    if response.returncode != 0:
        print(colored("Error Creating Attachment!", "red"))
        return

    smtp_settings = get_smtp_settings()

    message = f"""Dear Hiring Manager,
I am writing to apply for the position of a Software Engineer at your company. I am confident that my skills and experience are a perfect match for this position. I am excited about the opportunity to work with your team and contribute to the company's success.

Please find my resume and cover letter attached. I look forward to the opportunity to discuss my application in further detail.

Thank you for considering my application.

Best Regards,
{smtp_settings['sender_name']}
"""
    
    context = ssl.create_default_context()

    with smtplib.SMTP_SSL(smtp_settings["host"], smtp_settings["port"], context=context) as server:
        server.login(smtp_settings["auth"]["user"], smtp_settings["auth"]["pass"])

        message = f"Subject: {subject}\n\n{message}"
        server.sendmail(smtp_settings["auth"]["user"], email, message)

        with open(attachment, "rb") as file:
            server.sendmail(smtp_settings["auth"]["user"], email, file.read())

    print(colored("Email Sent Successfully!", "green"))

def _generate_cover_letter(job_description: str, info: dict) -> str:
    """
    Generates a cover letter in Markdown format, then converts it to PDF.

    :param job_description: The job description to generate the cover letter for.
    :param info: The user information to use in the cover letter.

    :return: The cover letter's path in PDF format.    
    """
    client = Client()

    # Generate using ChatGPT
    prompt = f"""Hello, ChatGPT!
Please generate a cover letter for a job application. The cover letter should be
returned in Markdown format. Only return the cover letter text, no need for the
front matter. DO NOT reference this prompt or explain what you are doing.

---

Job Description:

{job_description}

---

User Information:

Full Name: {info["full_name"]}
Email: {info["email"]}
City: {info["city"]}
Country: {info["country"]}
Phone Number: {info["phone_number"]}
Profiles: {info["profiles"]}
Skills: {info["skills"]}
Educations: {info["educations"]}
Projects: {info["projects"]}

---

Thank you!
"""
    is_ok = False

    while not is_ok:
        cover_letter = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "user", "content": prompt}
            ]
        ).choices[0].message.content

        print(colored("=> Cover Letter Generated Successfully!", "green"))
        print(cover_letter)

        is_ok_unparsed = input(colored("> Is the cover letter okay? (Y/N) ", "blue"))

        if is_ok_unparsed.lower() == "y":
            is_ok = True

    cover_letter_path = "cover_letter.md"
    with open(cover_letter_path, "w") as file:
        file.write(cover_letter)

    # Convert to PDF
    pdf_path = "cover_letter.pdf"
    _turn_markdown_to_pdf(cover_letter_path, pdf_path)

    #os.remove(cover_letter_path)

    return pdf_path
