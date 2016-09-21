from mongoengine import *

from datetime import datetime

from models.employer import Employer
from models.job import Job
from models.applicant import Applicant

import engine


def import_job(**kwargs):
    """Import job from Jobmine.

    Keyword arguments:
    employer_name -- Employer name
    job_title -- Title of job
    year -- Year the job was advertised
    term -- Term job was advertised [Fall -> 1, Winter -> 2, Spring -> 3]
    location -- Location job was advertised
    openings -- Number of job openings
    remaining -- Number of job openings remaining
    summary -- Job summary
    """

    # Convert to ASCII (ignore Unicode)
    employer_name = kwargs['employer_name'].encode('ascii', 'ignore').lower()
    job_title = kwargs['job_title'].encode('ascii', 'ignore').lower()
    term = int(kwargs['term'])
    location = kwargs['location'].encode('ascii', 'ignore').lower()
    openings = int(kwargs['openings'])
    summary = kwargs['summary']
    date = kwargs['date']
    year = date.year

    applicants = 0

    if not kwargs['applicants'].encode('ascii', 'ignore'):
        applicants = int(kwargs['applicants'])

    # If employer does not exist, create it
    if not Employer.employer_exists(employer_name):
        employer = Employer(name=employer_name)

        applicant = Applicant(applicants=applicants, date=date)

        # Assume new job so number of remaining positions is same as openings
        job = Job(title=job_title, summary=engine.filter_summary(summary), year=year, term=term,
                  location=[location], openings=openings, remaining=openings, applicants=[applicant])

        job.save()

        employer.jobs.append(job)
        employer.save()

    # Employer already exists
    else:
        employer = Employer.objects(name=employer_name).no_dereference().first()

        # If job does not exist, create it
        if not Job.job_exists(job_title):
            applicant = Applicant(applicants=applicants, date=date)

            # Assume new job so number of remaining positions is same as openings
            job = Job(title=job_title, summary=engine.filter_summary(summary), year=year, term=term,
                      location=[location], openings=openings, remaining=openings, applicants=[applicant])

            job.save()

            employer.update_one(push__jobs=job)

        # Job already exists
        else:
            job = Job.objects(id__in=[job.id for job in employer.jobs], title=job_title).first()
    
            filtered_summary = engine.filter_summary(summary)

            if not year >= job.year:
                raise ValueError('Job: {} by {} cannot be advertised before {}'
                                 .format(job_title, employer_name, job.year))

            # Job summary is not the same. In this case the employer most likely changed the job
            if not filtered_summary == job.summary:
                job.update_one(set__deprecated=True)
                
                applicant = Applicant(applicants=applicants, date=date)
    
                # Assume new job so number of remaining positions is same as openings
                new_job = Job(title=job_title, summary=filtered_summary, year=year, term=term,
                              location=[location], openings=openings, remaining=openings, applicants=[applicant])
    
                new_job.save()
    
                employer.update_one(push__jobs=new_job)
            
            # Job is the same (same title and description)
            else:
                # If job is being advertised in new term
                if year != job.year and term != job.term:
                    # Add hire ratio for previous term
                    hire_ratio = float(job.openings - remaining) / job.openings
                    
                    job.hire_rate.add_rating(hire_ratio)
                    
                    job.update(set__year=year, set__term=term, add_to_set__location=location, set__openings=openings,
                               set__remaining=openings, push__applicants=Applicant(applicants=applicants, date=date))

                # Job is being updated. We need to update location, openings, remaining, hire_rate, applicants
                else:
                    remaining = job.openings

                    # Job posting has decreased, some positions filled up
                    if openings < job.openings:
                        remaining = openings

                    if openings > job.openings:
                        raise ValueError('Job: {} by {} has more openings than in DB'.format(job_title, employer_name))

                    job.update(add_to_set__location=location, remaining=remaining,
                               push__applicants=Applicant(applicants=applicants, date=date))
