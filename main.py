from helpers import _kill_chrome, _generate_resume, _generate_cover_letter, _get_information
from classes.Providers.Indeed import Indeed
from classes.Database import Database



def main() -> None:
    _kill_chrome()
    db = Database()
    db.create_table()

    me = _get_information()

    indeed = Indeed(db=db, \
                    job_query="Software Engineer", \
                        place_query="New York, USA")
    indeed.search(advanced=True)

    jobs = db.get_jobs()
    print(jobs)

    resume_path = _generate_resume(info=me)

    for job in jobs:
        cover_letter_path = _generate_cover_letter(job["job_description_markdown"], me)
        indeed.apply(job["id"], cover_letter_path, resume_path)

if __name__ == "__main__":
    main()
