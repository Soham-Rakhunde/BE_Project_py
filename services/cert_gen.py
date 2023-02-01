from cryptography import x509
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.x509.oid import NameOID
import datetime
import uuid

private_key = rsa.generate_private_key(
    public_exponent=65537,
    key_size=2048,
    backend=default_backend()
)

with open("ca.pem", "wb") as f:
    f.write(private_key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.TraditionalOpenSSL,
        encryption_algorithm=serialization.BestAvailableEncryption(b"password"),
    ))

one_day = datetime.timedelta(1, 0, 0)
public_key = private_key.public_key()

subject = issuer = x509.Name([
    x509.NameAttribute(NameOID.COUNTRY_NAME, u"India"),
    x509.NameAttribute(NameOID.STATE_OR_PROVINCE_NAME, u"Maharashtra"),
    x509.NameAttribute(NameOID.LOCALITY_NAME, u"Pune"),
    x509.NameAttribute(NameOID.ORGANIZATION_NAME, u"localhost"),
    x509.NameAttribute(NameOID.COMMON_NAME, u"localhost"),
])

builder = x509.CertificateBuilder()
builder = builder.subject_name(subject)
builder = builder.issuer_name(issuer)
builder = builder.not_valid_before(datetime.datetime.today() - one_day)
builder = builder.not_valid_after(datetime.datetime(2025, 8, 2))
builder = builder.serial_number(x509.random_serial_number())
builder = builder.public_key(public_key)
builder = builder.add_extension(
    x509.SubjectAlternativeName([x509.DNSName(u"localhost")]),
    x509.BasicConstraints(ca=True, path_length=None), 
    critical=False,
)
certificate = builder.sign(
    private_key=private_key, algorithm=hashes.SHA256(),
    backend=default_backend()
)
print(isinstance(certificate, x509.Certificate))

with open("ca.crt", "wb") as f:
    f.write(certificate.public_bytes(
        encoding=serialization.Encoding.PEM,
    ))