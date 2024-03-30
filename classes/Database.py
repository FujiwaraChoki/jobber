from typing import List

import json
import sqlite3

class Database:
    def __init__(self, db_file: str = "jobber.db") -> None:
        self.db_file = db_file
        self.connection = sqlite3.connect(self.db_file)
        self.cursor = self.connection.cursor()

    def create_table(self) -> None:
        """
        Creates the table if it doesn't exist.
        """
        self.cursor.execute("""
        CREATE TABLE IF NOT EXISTS jobs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT,
            location TEXT,
            salary TEXT,
            benefits TEXT,
            job_description_markdown TEXT,
            apply_button TEXT,
            url TEXT
        )
        """)

    def insert_job(self, job: dict) -> None:
        """
        Inserts a job into the database.

        :param job: Job dictionary.
        """
        self.cursor.execute("""
        INSERT INTO jobs (id, title, location, salary, benefits, job_description_markdown, apply_button, url)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            job["id"],
            job["title"],
            job["location"],
            job["salary"] if "salary" in job else None,
            json.dumps(job["benefits"]) if "benefits" in job else None,
            job["job_description_markdown"] if "job_description_markdown" in job else None,
            job["apply_button"] if "apply_button" in job else None,
            job["url"]
        ))

        self.connection.commit()

    def update_job(self, job: dict) -> None:
        """
        Updates a job in the database.

        :param job: Job dictionary.
        """
        previous_job = self.get_job(job["id"])

        self.cursor.execute("""
        UPDATE jobs
        SET title = ?,
            location = ?,
            salary = ?,
            benefits = ?,
            job_description_markdown = ?,
            apply_button = ?,
            url = ?
        WHERE id = ?
        """, (
            job["title"] if "title" in job else previous_job["title"],
            job["location"] if "location" in job else previous_job["location"],
            job["salary"] if "salary" in job else previous_job["salary"],
            json.dumps(job["benefits"]) if "benefits" in job else json.dumps(previous_job["benefits"]),
            job["job_description_markdown"] if "job_description_markdown" in job else previous_job["job_description_markdown"],
            job["apply_button"] if "apply_button" in job else previous_job["apply_button"],
            job["url"] if "url" in job else previous_job["url"],
            job["id"] if "id" in job else previous_job["id"]
        ))

        self.connection.commit()

    def delete_job(self, job_id: int) -> None:
        """
        Deletes a job from the database.

        :param job_id: Job ID.
        """
        self.cursor.execute("DELETE FROM jobs WHERE id = ?", (job_id,))
        self.connection.commit()

    def get_job(self, query: str, selector: str = "id") -> dict:
        """
        Returns a job from the database.

        :param query: Query string.
        :param selector: Selector.
        :return: Job dictionary.
        """
        print(self.get_jobs())
        self.cursor.execute(f"SELECT * FROM jobs WHERE {selector} = ?", (query,))
        job = self.cursor.fetchone()
        job_dict = {
            "id": job[0],
            "title": job[1],
            "location": job[2],
            "salary": job[3],
            "benefits": json.loads(job[4]),
            "job_description_markdown": job[5],
            "apply_button": job[6],
            "url": job[7]
        }

        return job_dict

    def get_jobs(self) -> List[dict]:
        """
        Returns all jobs from the database.

        :return: List of jobs.
        """
        self.cursor.execute("SELECT * FROM jobs")
        jobs = self.cursor.fetchall()

        jobs_list = []

        for job in jobs:
            job_dict = {
                "id": job[0],
                "title": job[1],
                "location": job[2],
                "salary": job[3],
                "benefits": json.loads(job[4]) if job[4] else None,
                "job_description_markdown": job[5],
                "apply_button": job[6],
                "url": job[7]
            }

            jobs_list.append(job_dict)

        return jobs_list

    def close(self) -> None:
        """
        Closes the connection.
        """
        self.connection.close()

    def __del__(self):
        self.close()
