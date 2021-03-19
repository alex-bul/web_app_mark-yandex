import flask

from data import db_session
from data.jobs import Jobs

blueprint = flask.Blueprint(
    'jobs_api',
    __name__,
    template_folder='templates'
)


@blueprint.route('/api/jobs')
def get_news():
    db_sess = db_session.create_session()
    jobs = db_sess.query(Jobs).all()
    return flask.jsonify({'jobs': [item.to_dict(
        only=(
            'id', 'job', 'team_leader', 'work_size', 'collaborators',
            'start_date', 'end_date', 'is_finished', 'category')
    ) for item in jobs]})


@blueprint.route('/api/jobs/<int:job_id>')
def get_one_job(job_id):
    db_sess = db_session.create_session()
    jobs = db_sess.query(Jobs).get(job_id)
    if not jobs:
        return flask.jsonify({'error': 'Not found'})
    return flask.jsonify({'jobs': jobs.to_dict(
        only=(
            'id', 'job', 'team_leader', 'work_size', 'collaborators',
            'start_date', 'end_date', 'is_finished', 'category')
    )})
