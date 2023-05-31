from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives import serialization
import os, random, datetime

#Self-signed certificate creation
from cryptography import x509
from cryptography.x509.oid import NameOID

#Symmetric key generation
from cryptography.hazmat.primitives.serialization import load_pem_public_key, load_pem_private_key
from cryptography.hazmat.primitives.asymmetric import padding

from services.key_handling_module import KeyHandlerUI
hashingAlgorithm = hashes.SHA512()
passwd_hashingAlgorithm = hashes.SHA256()
passwd_attempts = 4
BufferSize = 1024


#Generate key pair
def makeKey():
    private_key = rsa.generate_private_key(
        public_exponent=65537,
        key_size=2048,
        backend=default_backend()
    )
    public_key = private_key.public_key()
    writeKey(private_key)
    return {'private':private_key,'public':public_key}



#Encrypt a message with assymetric public key
def encrypt(pub,message):
    encrypted = pub.encrypt(
        message,
        padding.OAEP(
            mgf=padding.MGF1(algorithm=hashingAlgorithm),
            algorithm=hashingAlgorithm,
            label=None
        )
    )
    return encrypted

#Decrypt a message with assymetric private key
def decrypt(priv,message):
    decrypted = priv.decrypt(
        message,
        padding.OAEP(
            mgf=padding.MGF1(algorithm=hashingAlgorithm),
            algorithm=hashingAlgorithm,
            label=None
        )
    )
    return decrypted

#Encoding public key as bytestring
def pubString(pub):
    pem = pub.public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo
    )
    return pem

#Unpacking a bytestring public key into a key object
def readPub(pubString):
    public_key = serialization.load_pem_public_key(
        pubString,
        backend=default_backend()
    )
    return public_key

#Writing encrypted private key to file (for use with the certificate)
def writeKey(priv):
    keyHandler = KeyHandlerUI()
    passwd = keyHandler.key
    priv = priv.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.TraditionalOpenSSL,
        encryption_algorithm=serialization.BestAvailableEncryption(passwd)
    )
    with open('Identity/private_key.pem', 'wb') as f:
        f.write(priv)

def retrieveKey():
    keyHandler = KeyHandlerUI() 
    passwd = keyHandler.key
    with open("Identity/private_key.pem", "rb") as key_file:
        private_key = serialization.load_pem_private_key(
            data=key_file.read(),
            password=passwd, #bytes(passwd, encoding='utf-8'),
            backend=default_backend()
        )
        public_key = private_key.public_key()
        return {'private':private_key,'public':public_key}
    private_key = load_pem_private_key(pemlines, None, default_backend())
    return private_key


#Generating a self-signed certificate with an existing private key
def makeCert():
    if not os.path.isfile('Identity/certificate.pem'):
        #Generate private key
        key = makeKey()['private']

        #Generate ranom alias
        aliasID = f"{random.randint(1,10000000)}".zfill(8)
        alias = f"Anon{aliasID}"

        #The only data we're adding on are an organization name, and the computer's hostname
        subject = issuer = x509.Name([x509.NameAttribute(NameOID.COMMON_NAME, alias)])

        cert = x509.CertificateBuilder().subject_name(
            subject
        ).issuer_name(
            issuer
        ).public_key(
            key.public_key()
        ).serial_number(
            x509.random_serial_number()
        ).not_valid_before(
            datetime.datetime.utcnow()
        ).not_valid_after(
            #Valid for one year
            datetime.datetime.utcnow() + datetime.timedelta(days=365)
        ).add_extension(
            x509.SubjectAlternativeName([x509.DNSName(u'localhost')]),
            critical=False,
        # Sign the certificate with the private key
        ).sign(key, hashes.SHA256(), default_backend())

        #Write certificate to file        
        with open('Identity/certificate.pem','wb') as fp:
            fp.write(cert.public_bytes(serialization.Encoding.PEM))

        #Write private key to file
        # writeKey(key)


def verifyCert(remPubKey, remCert):
    issuer_public_key = load_pem_public_key(remPubKey)
    cert_to_check = x509.load_der_x509_certificate(remCert)
    try:
        issuer_public_key.verify(
            cert_to_check.signature,
            cert_to_check.tbs_certificate_bytes,
            # Depends on the algorithm used to create the certificate
            padding.PKCS1v15(),
            cert_to_check.signature_hash_algorithm,
        )
        return True
    except Exception as e:
        print("exception ", e)
        return False