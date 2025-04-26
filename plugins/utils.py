'''
Utils for mas.
'''


def crypt_anon_id(id: int) -> str:
    return str(id*7)[:-1]


def decrypt_anon_id(id: int) -> int:
    return int(str(id/7)[:-1])


if __name__ == "__main__":
    print(crypt_anon_id(428192863))
    print(crypt_anon_id(299735004))