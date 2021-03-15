import flask as fk
from loader import load_from_json
from controller_helpers import get_all_user_data_from_ids, generate_update_from_req
import sqlite3 as db

FILE_PATH = 'hacker-data-2021.json'
DB_FILE_PATH = 'user_db.db'

controller = fk.Blueprint('controller', __name__)


@controller.route('/run_loader')
def run_loader():
    conn = db.connect(DB_FILE_PATH)
    return fk.jsonify(load_from_json(FILE_PATH, conn))


@controller.route('/users', methods=['GET'])
def get_users():
    conn = db.connect(DB_FILE_PATH)
    cur = conn.cursor()

    if fk.request.args.get('user') is None:
        cur.execute('SELECT id FROM users')
        all_ids = list(map(lambda row: row[0], cur.fetchall()))
        all_user_data = get_all_user_data_from_ids(all_ids, cur)

    else:
        target_ids = [int(user_id) for user_id in fk.request.args.getlist('user')]
        all_user_data = get_all_user_data_from_ids(target_ids, cur)

    return fk.jsonify(all_user_data)


@controller.route('/users', methods=['PUT'])
def update_users():
    conn = db.connect(DB_FILE_PATH)
    cur = conn.cursor()
    req = [fk.request.json] if len(fk.request.json) == 0 else fk.request.json
    target_ids = fk.request.args.getlist('user')

    for user_id, skill_req in [(target_ids[i], req[i]) for i in range(len(target_ids))]:
        for sql in generate_update_from_req(int(user_id), cur, skill_req):
            cur.execute(sql)

    conn.commit()

    return fk.jsonify(get_all_user_data_from_ids(target_ids, cur))




