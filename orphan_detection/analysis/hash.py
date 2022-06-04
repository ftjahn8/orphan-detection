


def fnv_1a(data: bytes) -> int:
    hash = 0xcbf29ce484222325
    for byte in data:
        hash = hash ^ byte
        hash = (hash * 0x100000001b3) % 2**64
    return hash

# print(bin(fnv_1a("FELIX ETZKORN".encode("utf-8"))))
