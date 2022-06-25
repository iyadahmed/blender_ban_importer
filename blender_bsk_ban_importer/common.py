import struct

from mathutils import Matrix, Quaternion, Vector


def read_little_int_unsigned(file):
    return int.from_bytes(file.read(4), "little", signed=False)


def read_little_string(file, num_chars) -> bytes:
    return struct.unpack(f"<{num_chars}s", file.read(num_chars))[0]


def read_jmx_string(file):
    return read_little_string(file, read_little_int_unsigned(file)).decode()


def read_jmx_trasnform(file):
    qx, qy, qz, qw = struct.unpack("<4f", file.read(4 * 4))
    rotation = Quaternion((qw, qx, qy, qz))

    x, y, z = struct.unpack("<3f", file.read(4 * 3))
    translation = Vector((x, y, z))

    return translation, rotation
