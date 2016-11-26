from datetime import datetime
import mongoengine

import elasticsearch
from elasticsearch import helpers

from models.employer import Employer
import models.term as Term

import shared.secrets as secrets
import shared.logger as logger


COMPONENT = 'Search'

elastic_instance = elasticsearch.Elasticsearch()


def index_jobmine():
    logger.info(COMPONENT, 'Indexing jobmine data')

    elastic_instance.indices.delete(index='jobmine', ignore=[404])

    elastic_instance.indices.create('jobmine', body={
        "mappings": {
            "employers": {
                "properties": {
                    "employer_name": {"type": "string"},
                    "employer_jobs": {"type": "string"}
                }
            },
            "jobs": {
                "_parent": {
                    "type": "employers"
                },
                "properties": {
                    "job_title": {"type": "string"},
                    "job_year": {"type": "integer"},
                    "job_term": {"type": "string"},
                    "job_summary": {"type": "string"},
                    "job_locations": {"type": "string"},
                    "job_programs": {"type": "string"},
                    "job_levels": {"type": "string"}
                }
            }
        }
    })

    logger.info(COMPONENT, 'Indexing jobmine employers and jobs')

    employers = []
    jobs = []

    for employer in Employer.objects.only('name', 'jobs'):
        logger.info(COMPONENT, 'Indexing employer: {}'.format(employer.name))

        employer_document = {
            "_index": "jobmine",
            "_type": "employers",
            "_id": employer.name,
            "_source": {
                "employer_name": employer.name,
                "employer_jobs": [str(job.id) for job in employer.jobs]
            }
        }

        employers.append(employer_document)

        for job in employer.jobs:
            if not job.deprecated:
                logger.info(COMPONENT, 'Indexing job: {} for employer: {}'.format(job.title, employer.name))

                job_document = {
                    "_index": "jobmine",
                    "_type": "jobs",
                    "_parent": employer.name,
                    "_id": str(job.id),
                    "_source": {
                        "employer_name": employer.name,
                        "job_title": job.title,
                        "job_year": job.year,
                        "job_term": job.term,
                        "job_summary": job.summary,
                        "job_keywords": [k.keyword for k in job.keywords],
                        "job_locations": [location.name for location in job.location],
                        "job_programs": job.programs,
                        "job_levels": job.levels
                    }
                }

                jobs.append(job_document)

            if len(jobs) == 1000:
                helpers.bulk(elastic_instance, jobs)
                jobs = []

        if len(employers) == 1000:
            helpers.bulk(elastic_instance, employers)
            employers = []

    if len(employers) > 0:
        helpers.bulk(elastic_instance, employers)

    if len(jobs) > 0:
        helpers.bulk(elastic_instance, jobs)


def query_jobs_and_employers(query, page):
    start_page = 10 * (int(page) - 1)

    now = datetime.now()

    response = elastic_instance.search(index='jobmine', doc_type=['jobs'], body={
        "from": start_page, "size": 10,
        "sort": [
            {"job_year": "desc"},
            "_score"
        ],
        "query": {
            "bool": {
                "should": [
                    {
                        "match": {
                            "job_term": Term.get_term(now.month)
                        }
                    }
                ],
                "must": {
                    "multi_match": {
                        "query": query,
                        "type": "cross_fields",
                        "fields": ["employer_name^4", "job_title^4", "job_term"]
                    }
                }
            }
        }
    })

    return response


def query_jobs(query, page):
    start_page = 10 * (int(page) - 1)

    now = datetime.now()

    body = {
        "from": start_page, "size": 10,
        "sort": [
            {"job_year": "desc"},
            "_score"
        ],
        "query": {
            "bool": {
                "should": [
                    {
                        "match": {
                            "job_term": Term.get_term(now.month)
                        }
                    }
                ]
            }
        }
    }

    if query:
        body['query']['bool']['must'] = {
            "multi_match": {
                "query": query,
                "type": "cross_fields",
                "fields": ["job_title^4", "job_keywords^4", "job_summary^3", "job_term"]
            }
        }

    response = elastic_instance.search(index='jobmine', doc_type=['jobs'], body=body)

    return response


if __name__ == "__main__":
    mongoengine.connect(secrets.MONGO_DATABASE, host=secrets.MONGO_HOST, port=secrets.MONGO_PORT)
    index_jobmine()