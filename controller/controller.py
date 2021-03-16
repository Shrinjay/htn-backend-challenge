import flask as fk
import sys
from loader.loader import load_from_json
from validators import validate_user_update_request, validate_user_request, validate_request_parameters,\
    check_validators, validate_skill_request
from controller.controller_helpers import get_user_data_from_ids, generate_update_from_req, generate_skills_freq_query
import sqlite3 as db

FILE_PATH = 'loader/hacker-data-2021.json'
DB_FILE_PATH = 'user_db.db'

controller = fk.Blueprint('controller', __name__)


@controller.route('/run_loader')
def run_loader():
    conn = db.connect(DB_FILE_PATH)

    loader_status = fk.jsonify(load_from_json(FILE_PATH, conn))

    conn.close()
    return loader_status


@controller.route('/users', methods=['GET'])
def get_users():
    conn = db.connect(DB_FILE_PATH)
    cur = conn.cursor()
    validator_responses = check_validators(
        [validate_user_request(fk.request, cur), validate_request_parameters(fk.request, ['user'])]
    )

    if len(validator_responses) > 0:
        return fk.jsonify(validator_responses)

    if fk.request.args.get('user') is None:
        cur.execute('SELECT id FROM users')
        target_ids = list(map(lambda row: row[0], cur.fetchall()))

    else:
        target_ids = [int(user_id) for user_id in fk.request.args.getlist('user')]

    user_data = get_user_data_from_ids(target_ids, cur)

    cur.close()
    return fk.jsonify(user_data)


@controller.route('/users', methods=['PUT'])
def update_users():
    conn = db.connect(DB_FILE_PATH)
    cur = conn.cursor()

    validator_responses = check_validators([
        validate_request_parameters(fk.request, ['user']),
        validate_user_request(fk.request, cur),
        *validate_user_update_request(fk.request)
    ])

    if len(validator_responses) > 0:
        return fk.jsonify(validator_responses)

    user_update = fk.request.get_json() if isinstance(fk.request.get_json(), list) else [fk.request.get_json()]
    target_ids = fk.request.args.getlist('user')

    for user_id, user_update in [(target_ids[i], user_update[i]) for i in range(len(target_ids))]:
        for sql in generate_update_from_req(int(user_id), cur, user_update):
            cur.execute(sql)

    conn.commit()
    updated_user_data = get_user_data_from_ids(target_ids, cur)

    cur.close()
    return fk.jsonify(updated_user_data)


@controller.route('/skills')
def get_skills():
    conn = db.connect(DB_FILE_PATH)
    cur = conn.cursor()

    validator_responses = check_validators([
        validate_request_parameters(fk.request, ['min_frequency', 'max_frequency']),
        validate_skill_request(fk.request)
    ])

    if len(validator_responses) > 0:
        return fk.jsonify(validator_responses)

    min_frequency = int(fk.request.args.get('min_frequency')) if fk.request.args.get('min_frequency') is not None else 0
    max_frequency = int(fk.request.args.get('max_frequency')) \
        if fk.request.args.get('max_frequency') is not None else sys.maxsize

    query = generate_skills_freq_query(min_frequency, max_frequency)
    cur.execute(query)
    frequency_table = cur.fetchall()

    cur.close()
    return fk.jsonify([{'name': entry[0], 'frequency': entry[1]} for entry in frequency_table])