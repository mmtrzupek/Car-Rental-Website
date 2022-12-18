from app import db
import random
import string
current_user_id = None
current_user = None

def set_current_user_id(new_id):
    global current_user_id, current_user
    current_user_id = new_id
    if new_id is not None:
        with db.begin() as conn:
            current_user = conn.execute("""SELECT * FROM user WHERE user_id ='{}'""".format(new_id)).fetchone()
    else:
        current_user = None

def get_current_user_id():
    global current_user_id
    return current_user_id

def get_current_user():
    global current_user
    return current_user

def login(email, password):
    with db.begin() as conn:
        all_users = conn.execute("""SELECT * FROM user WHERE email LIKE '{}' AND password LIKE '{}'""".format(email,password))
    all_users = [u for u in all_users]
    if all_users is None:
        return None
    if len(all_users) != 1:
        return None
    user_ = all_users[0]
    set_current_user_id(user_.user_id)
    return user_

def logout():
    set_current_user_id(None)

def create_user(f_name, l_name, is_leasor, email, password):
    with db.begin() as conn:
        uids = list(conn.execute('SELECT user_id AS uid from user').fetchone().uid)
        is_leasor = int(float(is_leasor))
        flag = True
        while flag:
            id = str(''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(32)))
            if id not in uids:
                flag = False
        # age_str = f"'{age}'"
        # if not age:
        #     age_str = "NULL"
        q = f"INSERT INTO user VALUES ('{id}', '{email}', '{password}', '{is_leasor}', '{f_name}', '{l_name}')"
        conn.execute(q)

