import sqlite3 as db
import json
import itertools


class LoaderQuery:
    def __init__(self, user_query, skills_queries):
        self.user_query = user_query
        self.skills_queries = list(itertools.chain(skills_queries))


def find(predicate, list):
    for e in list:
        if predicate(e):
            return e
    return None


def generate_skill_insert_query(index: int, skills_object):
    sql = f"INSERT into skills (user_id, skill_name, skill_value) " \
          f"VALUES ({index}, '{skills_object['name']}', {skills_object['rating']});"
    return sql


def clean_skills_list(skills_list):

    cleaned_skills = []
    for skill in skills_list:
        duplicate_skill = find(lambda saved_skill: saved_skill['name'] == skill['name'], cleaned_skills)

        if duplicate_skill is None:
            cleaned_skills.append(skill)
        else:
            duplicate_skill['rating'] = max(duplicate_skill['rating'], skill['rating'])

    return cleaned_skills


def generate_insert_query(index: int, entry) -> LoaderQuery:
    user_sql = f"INSERT into users (id, name, picture, company, email, phone) " \
               f"VALUES ({index}, '{entry['name']}', '{entry['picture']}', '{entry['company']}', '{entry['email']}'," \
               f" '{entry['phone']}');"

    cleaned_skills = clean_skills_list(entry['skills'])
    skill_queries = list(map(lambda skill: generate_skill_insert_query(index, skill), cleaned_skills))
    return LoaderQuery(user_sql, skill_queries)


def insert_from_loader(cur, query_object: LoaderQuery):
    cur.execute(query_object.user_query)
    for skill_query in query_object.skills_queries:
        cur.execute(skill_query)


def clear_db(cur):
    try:
        cur.execute("DELETE FROM skills;")
        cur.execute("DELETE FROM users;")
    except db.OperationalError:
        cur.execute("""CREATE TABLE "users" (
                    "id"	INTEGER,
                    "name"	TEXT,
                    "picture"	TEXT,
                    "company"	TEXT,
                    "email"	TEXT,
                    "phone"	TEXT,
                    PRIMARY KEY("id")
                );"""
                    )
        cur.execute("""CREATE TABLE "skills" (
                                    "user_id"	INTEGER NOT NULL,
                                    "entry_id"	INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
                                    "skill_name"	TEXT,
                                    "skill_value"	INTEGER
                                )"""
                    )
    try:
        cur.execute("DELETE FROM sqlite_sequence;")
    except db.OperationalError:
        print("sequence doesn't exist")


def load_from_json(file_path: str, conn):
    with open(file_path) as file_data:
        raw_data = json.load(file_data)

    query_list = list(map(generate_insert_query, [i for i in range(len(raw_data))], raw_data))

    cur = conn.cursor()
    clear_db(cur)
    conn.commit()

    for query_object in query_list:
        insert_from_loader(cur, query_object)
    conn.commit()
    cur.close()

    return True
