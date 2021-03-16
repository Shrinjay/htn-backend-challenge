from typing import List
import sys

USER_FIELDS = ['name', 'picture', 'company', 'email', 'phone']
SKILL_FIELDS = ['skill_name', 'skill_value']


def get_user_data_from_ids(id_list: List[int], cur):
    return list(map(lambda user_id: get_user_json_by_id(user_id, cur), id_list))


def get_user_json_by_id(user_id: int, cur):

    cur.execute(f"SELECT {','.join(USER_FIELDS)} FROM users WHERE id={user_id};")
    user_row = cur.fetchall()[0]
    cur.execute(f"SELECT {','.join(SKILL_FIELDS)} FROM skills WHERE user_id={user_id};")
    skill_rows = cur.fetchall()

    user_json = dict(zip(USER_FIELDS, list(user_row)))
    user_json['skills'] = list(map(lambda skill_row: {'name': skill_row[0], 'rating': skill_row[1]}, skill_rows))
    return user_json


def generate_update_from_req(target_id, cur, req):
    update_entries = req.items()
    update_no_skills = list(filter(lambda entry: entry[0] != 'skills', update_entries))
    update_skills = list(filter(lambda entry: entry[0] == 'skills', update_entries))
    queries = []

    if len(update_no_skills) != 0:
        sql = "UPDATE users SET "
        for i in range(len(update_no_skills)):
            sql += f"{update_no_skills[i][0]}='{update_no_skills[i][1]}'"
            sql += ", " if i < len(update_no_skills) - 1 else " "
        sql += f"WHERE id={target_id};"
        queries.append(sql)

    if len(update_skills) != 0:
        try:
            cur.execute(f"SELECT skill_name FROM skills WHERE user_id={target_id};")
            existing_skills = list(map(lambda row: row[0], cur.fetchall()))
            requested_skills = update_skills[0][1]
            skills_to_update = list(
                filter(lambda update_skill: update_skill['name'] in existing_skills, requested_skills))
            skills_to_insert = list(
                filter(lambda insert_skill: insert_skill['name'] not in existing_skills, requested_skills))

            for skill in skills_to_update:
                update_query = f"UPDATE skills SET skill_value={skill['rating']} " \
                               f"WHERE user_id={target_id} AND skill_name='{skill['name']}';"
                queries.append(update_query)

            for skill in skills_to_insert:
                insert_query = f"INSERT INTO skills (user_id, skill_name, skill_value) " \
                               f"VALUES ({target_id}, '{skill['name']}', {skill['rating']});"
                queries.append(insert_query)

        except KeyError:
            return []

    return queries


def generate_skills_freq_query(min_frequency: int, max_frequency: int):

    sql = f"""
        WITH skill_data AS (
            SELECT skill_name, COUNT(*) AS frequency FROM skills GROUP BY skill_name ORDER BY frequency DESC
        )
        SELECT * FROM skill_data 
        """
    if min_frequency > 0:
        sql += f"WHERE frequency > {min_frequency} "

    if max_frequency < sys.maxsize:
        sql += f"{'WHERE' if min_frequency == 0 else 'AND'} frequency < {max_frequency}"

    return sql


