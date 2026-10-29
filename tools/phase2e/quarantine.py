"""E0 integrity/unpacking primitives, not an approved model downloader or loader."""

import bz2
import hashlib
import re
import time


class IntegrityError(ValueError):
    pass


def verify_bytes(data, *, size, sha256=None, git_blob=None):
    if type(size) is not int or not 0 < size <= 128 * 1024 * 1024 or len(data) != size:
        raise IntegrityError("Artifact size mismatch")
    if sha256 is None and git_blob is None:
        raise IntegrityError("Artifact identity required")
    digest = hashlib.sha256(data).hexdigest()
    if sha256 is not None and (not re.fullmatch(r"[a-f0-9]{64}", sha256) or digest != sha256):
        raise IntegrityError("Artifact SHA-256 mismatch")
    if git_blob is not None:
        actual = hashlib.sha1(b"blob " + str(size).encode() + b"\0" + data).hexdigest()
        if not re.fullmatch(r"[a-f0-9]{40}", git_blob) or actual != git_blob:
            raise IntegrityError("Artifact Git blob mismatch")
    return digest


def unpack_bzip2(data, *, output_limit, ratio_limit, time_limit, clock=time.monotonic):
    """One bounded stream, no filenames, paths, archives, trailing bytes or loaders.

    Wall checks bound progress between small native decompressor calls. A caller
    MUST also use an OS-limited disposable process for hard CPU/RSS/time limits;
    this helper alone is not that process or evidence of A4/A5 approval.
    """
    if not isinstance(data, bytes) or not 4 <= len(data) <= 32 * 1024 * 1024 or data[:3] != b"BZh":
        raise IntegrityError("Not an allowed bzip2 input")
    if type(output_limit) is not int or not 1 <= output_limit <= 128 * 1024 * 1024:
        raise IntegrityError("Output limit required")
    if type(ratio_limit) is not int or not 1 <= ratio_limit <= 512:
        raise IntegrityError("Ratio limit required")
    if type(time_limit) not in {int, float} or not 0 < time_limit <= 30:
        raise IntegrityError("Time limit required")
    ceiling = min(output_limit, len(data) * ratio_limit)
    started, decoder, output = clock(), bz2.BZ2Decompressor(), bytearray()
    position = 0
    try:
        while True:
            if clock() - started >= time_limit:
                raise IntegrityError("Unpack deadline exceeded")
            if decoder.needs_input:
                if position >= len(data):
                    raise IntegrityError("Truncated stream")
                chunk = data[position:position + 65536]
                position += len(chunk)
            else:
                chunk = b""
            output.extend(decoder.decompress(chunk, max_length=min(65536, ceiling - len(output) + 1)))
            if len(output) > ceiling:
                raise IntegrityError("Unpack limit exceeded")
            if decoder.eof:
                if decoder.unused_data or position != len(data) or not output:
                    raise IntegrityError("Trailing/concatenated/empty stream")
                return bytes(output)
    except (OSError, EOFError):
        raise IntegrityError("Malformed stream") from None
