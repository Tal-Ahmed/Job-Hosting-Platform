import os
import flask
import mongoengine

from bson import json_util

import analytics.statistics as stats

import shared.secrets as secrets


component = 'API'

app = flask.Flask(__name__, template_folder="./templates")


def render_template(*args, **kwargs):
    kwargs.update({
        'env': os.environ.get('ENV') or ''
    })
    return flask.render_template(*args, **kwargs)


@app.route("/")
def index():
    return render_template('index.html', page_script='index.js')


@app.route("/csdashboard")
def cs_dashboard():
    return render_template('index.html', page_script='cs.js')


@app.route('/api/jobs-vs-programs-stat', methods=['POST'])
def jobs_vs_programs_stat():
    programs_vs_jobs = stats.get_jobs_vs_programs()

    response = {
        'data': [{'name': program, 'jobs': programs_vs_jobs[program]} for program in programs_vs_jobs]
    }

    return flask.Response(response=json_util.dumps(response), status=200, mimetype="application/json")


@app.route('/api/jobs-vs-levels-stat', methods=['POST'])
def jobs_vs_levels_stat():
    jobs_vs_levels = stats.get_jobs_vs_levels()

    response = {
        'data': [{'name': level, 'jobs': jobs_vs_levels[level]} for level in jobs_vs_levels]
    }

    return flask.Response(response=json_util.dumps(response), status=200, mimetype="application/json")


@app.route('/api/jobs-vs-terms-stat', methods=['POST'])
def jobs_vs_terms_stat():
    jobs_vs_terms = stats.get_jobs_vs_terms()

    response = {
        'data': [{'year': term['_id']['year'], 'term': term['_id']['term'], 'jobs': term['count']}
                 for term in jobs_vs_terms]
    }

    return flask.Response(response=json_util.dumps(response), status=200, mimetype="application/json")


@app.route('/api/jobs-vs-locations-stat', methods=['POST'])
def jobs_vs_locations_stat():
    jobs_vs_locations = stats.get_jobs_vs_locations()

    response = {
        'data': [{'name': location['name'], 'longitude': location['longitude'], 'latitude': location['latitude']}
                 for location in jobs_vs_locations]
    }

    return flask.Response(response=json_util.dumps(response), status=200, mimetype="application/json")


@app.route('/api/jobs-vs-programming-languages-stat', methods=['POST'])
def jobs_vs_programming_languages_stat():
    jobs_vs_programming_languages = stats.get_jobs_vs_programming_languages()

    response = {
        'data': [{'name': language['_id']['keyword'], 'jobs': language['count']}
                 for language in jobs_vs_programming_languages]
    }

    return flask.Response(response=json_util.dumps(response), status=200, mimetype="application/json")


@app.route('/api/jobs-vs-databases-stat', methods=['POST'])
def jobs_vs_databases_stat():
    jobs_vs_databases = stats.get_jobs_vs_databases()

    response = {
        'data': [{'name': language['_id']['keyword'], 'jobs': language['count']}
                 for language in jobs_vs_databases]
    }

    return flask.Response(response=json_util.dumps(response), status=200, mimetype="application/json")


@app.route('/api/jobs-vs-operating-systems-stat', methods=['POST'])
def jobs_vs_os_stat():
    jobs_vs_os = stats.get_jobs_vs_operating_systems()

    response = {
        'data': [{'name': language['_id']['keyword'], 'jobs': language['count']}
                 for language in jobs_vs_os]
    }

    return flask.Response(response=json_util.dumps(response), status=200, mimetype="application/json")


@app.route('/api/jobs-vs-web-frameworks-stat', methods=['POST'])
def jobs_vs_web_frameworks_stat():
    jobs_vs_web_frameworks = stats.get_jobs_vs_web_frameworks()

    response = {
        'data': [{'name': language['_id']['keyword'], 'jobs': language['count']}
                 for language in jobs_vs_web_frameworks]
    }

    return flask.Response(response=json_util.dumps(response), status=200, mimetype="application/json")


@app.route('/api/jobs-vs-apache-frameworks-stat', methods=['POST'])
def jobs_vs_apache_frameworks_stat():
    jobs_vs_apache_frameworks = stats.get_jobs_vs_apache_frameworks()

    response = {
        'data': [{'name': language['_id']['keyword'], 'jobs': language['count']}
                 for language in jobs_vs_apache_frameworks]
    }

    return flask.Response(response=json_util.dumps(response), status=200, mimetype="application/json")


@app.route('/api/jobs-vs-js-libraries-stat', methods=['POST'])
def jobs_vs_js_libraries_stat():
    jobs_vs_js_libraries = stats.get_jobs_vs_javascript_libraries()

    response = {
        'data': [{'name': language['_id']['keyword'], 'jobs': language['count']}
                 for language in jobs_vs_js_libraries]
    }

    return flask.Response(response=json_util.dumps(response), status=200, mimetype="application/json")


@app.route('/api/jobs-vs-css-frameworks-stat', methods=['POST'])
def jobs_vs_css_frameworks_stat():
    jobs_vs_css_frameworks = stats.get_jobs_vs_css_frameworks()

    response = {
        'data': [{'name': language['_id']['keyword'], 'jobs': language['count']}
                 for language in jobs_vs_css_frameworks]
    }

    return flask.Response(response=json_util.dumps(response), status=200, mimetype="application/json")


if __name__ == "__main__":
    mongoengine.connect(secrets.MONGO_DATABASE, host=secrets.MONGO_HOST, port=secrets.MONGO_PORT)
    app.run(host='0.0.0.0', debug=True)
