from OpenSSL import crypto, SSL
import ssl
from socket import gethostname

from os.path import exists, join

from variables import *
from server_secret.server_variables import *
from client_secret.client_variables import *

def generate_cert():
    # create a key pair
    k = crypto.PKey()
    k.generate_key(crypto.TYPE_RSA, 1024)

    # create a self-signed cert
    cert = crypto.X509()
    cert.get_subject().OU = CERT_NAME
    cert.get_subject().CN = gethostname()
    cert.set_serial_number(1000)
    cert.gmtime_adj_notBefore(0)
    cert.gmtime_adj_notAfter(2**31-1)
    cert.set_issuer(cert.get_subject())
    cert.set_pubkey(k)
    cert.sign(k, 'sha1')

    open(join(CLI_SECRET, CERT_FILE), "wb").write(crypto.dump_certificate(crypto.FILETYPE_PEM, cert))
    open(join(SERV_SECRET, CERT_FILE), "wb").write(crypto.dump_certificate(crypto.FILETYPE_PEM, cert))
    open(join(SERV_SECRET, KEY_FILE), "wb").write(crypto.dump_privatekey(crypto.FILETYPE_PEM, k))

if __name__ == '__main__':
    generate_cert()