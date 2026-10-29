"""Package the fixed minimal ABI module and upstream notices into a locked wheel."""

import base64
import csv
import hashlib
import io
import sysconfig
import zipfile
from pathlib import Path


def main():
    if not __debug__:
        raise SystemExit("Packaging assertions cannot be disabled")
    assert sysconfig.get_config_var("SOABI") == "cpython-313-x86_64-linux-gnu"
    module, = Path("/build/native-build").glob("_foc_dlib_native*.so")
    root = Path("/build")
    distribution = "foc_dlib_native-0.1.0.dist-info"
    files = {module.name: module.read_bytes(),
             distribution + "/METADATA": b"Metadata-Version: 2.4\nName: foc-dlib-native\nVersion: 0.1.0\nRequires-Python: ==3.13.13\nSummary: Data-free source probe; no model execution API\n",
             distribution + "/WHEEL": b"Wheel-Version: 1.0\nGenerator: foc-source-probe-v1\nRoot-Is-Purelib: false\nTag: cp313-cp313-linux_x86_64\n",
             distribution + "/licenses/LICENSE.dlib.txt": (root / "source/dlib/LICENSE.txt").read_bytes(),
             distribution + "/licenses/LICENSE.pybind11": (root / "source/dlib/external/pybind11/LICENSE").read_bytes()}
    record = io.StringIO()
    writer = csv.writer(record, lineterminator="\n")
    for name, data in sorted(files.items()):
        encoded = base64.urlsafe_b64encode(hashlib.sha256(data).digest()).decode().rstrip("=")
        writer.writerow([name, "sha256=" + encoded, len(data)])
    writer.writerow([distribution + "/RECORD", "", ""])
    files[distribution + "/RECORD"] = record.getvalue().encode()
    output = root / "dist"
    output.mkdir()
    with zipfile.ZipFile(output / "foc_dlib_native-0.1.0-cp313-cp313-linux_x86_64.whl", "w", zipfile.ZIP_DEFLATED) as archive:
        for name, data in sorted(files.items()):
            info = zipfile.ZipInfo(name, (2025, 5, 15, 0, 0, 0))
            info.external_attr = 0o100644 << 16
            info.compress_type = zipfile.ZIP_DEFLATED
            archive.writestr(info, data)


if __name__ == "__main__":
    main()
