from django.db import connection


def get_zero_padded_integer_string(number, padding_size=6):
    return str(number).zfill(padding_size)


def get_db_sequence(sequence_name):
    with connection.cursor() as cursor:
        cursor.execute("SELECT nextval(%s);", (sequence_name,))
        return int(cursor.fetchone()[0])


def generate_referral_code_for_user():
    return "NCS%s" % get_zero_padded_integer_string(
        get_db_sequence("core_user_id_seq"), padding_size=4
    )