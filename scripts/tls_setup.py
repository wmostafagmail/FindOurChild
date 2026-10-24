"""Two-day, loopback-only test certificate. Trust installation is a separate explicit local step."""

from datetime import UTC, datetime, timedelta
from ipaddress import ip_address, ip_network
from pathlib import Path

from cryptography import x509
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.x509.oid import NameOID


def main():
    directory = Path(".runtime/tls")
    directory.mkdir(parents=True, mode=0o700, exist_ok=True)
    if (directory / "cert.pem").exists():
        return
    key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
    name = x509.Name([x509.NameAttribute(NameOID.COMMON_NAME, "Find Our Child synthetic loopback")])
    cert = (
        x509.CertificateBuilder()
        .subject_name(name)
        .issuer_name(name)
        .public_key(key.public_key())
        .serial_number(x509.random_serial_number())
        .not_valid_before(datetime.now(UTC) - timedelta(minutes=1))
        .not_valid_after(datetime.now(UTC) + timedelta(days=2))
        .add_extension(
            x509.SubjectAlternativeName([x509.IPAddress(ip_address("127.0.0.1")), x509.DNSName("localhost")]),
            critical=False,
        )
        .add_extension(x509.BasicConstraints(ca=True, path_length=0), critical=True)
        .add_extension(
            x509.NameConstraints(
                permitted_subtrees=[x509.DNSName("localhost"), x509.IPAddress(ip_network("127.0.0.0/8"))],
                excluded_subtrees=None,
            ),
            critical=True,
        )
        .sign(key, hashes.SHA256())
    )
    (directory / "key.pem").write_bytes(
        key.private_bytes(
            serialization.Encoding.PEM, serialization.PrivateFormat.PKCS8, serialization.NoEncryption()
        )
    )
    (directory / "key.pem").chmod(0o600)
    (directory / "cert.pem").write_bytes(cert.public_bytes(serialization.Encoding.PEM))


if __name__ == "__main__":
    main()
