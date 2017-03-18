from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa, ec
from cryptography import x509
from cryptography.x509.oid import NameOID, ExtensionOID
import cryptography.x509.oid as oid
import os
import pickle
from cryptography.hazmat.primitives import hashes
import caTree
from enum import Enum
from pprint import pprint
from random import randint
import datetime
import binascii

OID_IN_USE = {'common_name': {'default': True, 'mandatory': True},
              'country_name': {'default': False, 'mandatory': False},
              'domain_component': {'default': False, 'mandatory': False},
              'email_address': {'default': False, 'mandatory': False},
              'locality_name': {'default': False, 'mandatory': False},
              'organization_name': {'default': False, 'mandatory': False},
              'organizational_unit_name': {'default': False, 'mandatory': False},
              'serial_number': {'default': False, 'mandatory': False},
              'state_or_province_name': {'default': False, 'mandatory': False}}


class Certificate(object):
    def __init__(self, cert=None):
        self._certificate_string = cert

    @property
    def certificate(self):
        return x509.load_pem_x509_certificate(self._certificate_string, backend=default_backend())

    @certificate.setter
    def certificate(self, value):
        self._certificate_string = value.public_bytes(serialization.Encoding.PEM)

    def __str__(self):
        return str(self._certificate_string, 'utf-8')


class Key(object):
    def __init__(self, node, length=256, passphrase=''):
        if length == 256:
            curve = ec.SECP256R1
        elif length == 384:
            curve = ec.SECP384R1
        else:
            raise ValueError
        self._node = node
        self._key_length = length
        key = ec.generate_private_key(curve=curve, backend=default_backend())
        self._str_key = key.private_bytes(encoding=serialization.Encoding.PEM,
                                          format=serialization.PrivateFormat.TraditionalOpenSSL,
                                          encryption_algorithm=serialization.BestAvailableEncryption(passphrase.encode()
                                                                                                     ))
        self._str_csr = None
        self._str_certificate = None

    def __str__(self):
        output = str(self._str_key, 'utf-8')
        output += str(self._str_csr, 'utf-8')
        output += str(self._str_certificate, 'utf-8')
        return output

    @property
    def certificate(self):
        return x509.load_pem_x509_certificate(self._str_certificate, backend=default_backend())

    @certificate.setter
    def certificate(self, value):
        self._str_certificate = value.public_bytes(serialization.Encoding.PEM)

    def private_key(self, passphrase=''):
        try:
            return serialization.load_pem_private_key(self._str_key,
                                                      passphrase.encode(),
                                                      default_backend())
        except ValueError as e:
            print('ERROR: Incorrect Password')

    @property
    def csr(self):
        return x509.load_pem_x509_csr(self._str_csr, default_backend())

    def create_root_certificate(self, passphrase):
        node = self._node
        key = self.private_key(passphrase)
        subject = issuer = x509.Name(subject_string(node))
        builder = x509.CertificateBuilder()
        builder = builder.subject_name(subject)
        builder = builder.issuer_name(issuer)
        builder = builder.public_key(key.public_key())
        builder = builder.serial_number(x509.random_serial_number())
        builder = builder.not_valid_before(datetime.datetime.utcnow())
        builder = builder.not_valid_after(datetime.datetime.utcnow() + datetime.timedelta(days=randint(7000, 15000)))
        builder = builder.add_extension(x509.SubjectAlternativeName(subject_alt_name_string(node)), critical=False, )
        builder = builder.add_extension(x509.SubjectKeyIdentifier.from_public_key(key.public_key()), critical=False)
        builder = builder.add_extension(x509.KeyUsage(digital_signature=node.key_usage['digital_signature'],
                                                      content_commitment=node.key_usage['content_commitment'],
                                                      key_encipherment=node.key_usage['key_encipherment'],
                                                      data_encipherment=node.key_usage['data_encipherment'],
                                                      key_agreement=node.key_usage['key_agreement'],
                                                      key_cert_sign=node.key_usage['key_cert_sign'],
                                                      crl_sign=node.key_usage['crl_sign'],
                                                      encipher_only=node.key_usage['encipher_only'],
                                                      decipher_only=node.key_usage['decipher_only']), critical=True)
        builder = builder.add_extension(x509.BasicConstraints(ca=True, path_length=None), critical=True, )
        if self._key_length == 256:
            self.certificate = builder.sign(key, hashes.SHA256(), default_backend())
        elif self._key_length == 384:
            self.certificate = builder.sign(key, hashes.SHA384(), default_backend())
        else:
            raise ValueError

    def create_cert_sign_req(self, passphrase):
        node = self._node
        builder = x509.CertificateSigningRequestBuilder().subject_name(x509.Name(subject_string(node)))
        builder = builder.add_extension(x509.SubjectAlternativeName(subject_alt_name_string(node)), critical=False,)
        if self._key_length == 256:
            csr = builder.sign(self.private_key(passphrase), hashes.SHA256(), default_backend())
        elif self._key_length == 384:
            csr = builder.sign(self.private_key(passphrase), hashes.SHA384(), default_backend())
        else:
            raise ValueError
        self._str_csr = csr.public_bytes(serialization.Encoding.PEM)

    def sign_csr(self, csr, passphrase):
    # def sign_csr(csr, ca_key: ec.EllipticCurvePrivateKey, ca_cert: x509.Certificate, ca=False):
        ski = self.certificate.extensions.get_extension_for_class(x509.SubjectKeyIdentifier)
        one_day = datetime.timedelta(1, 0, 0)
        builder = x509.CertificateBuilder()
        builder = builder.subject_name(x509.Name(csr.subject))
        builder = builder.issuer_name(x509.Name(self.certificate.subject))
        builder = builder.not_valid_before(datetime.datetime.today() - one_day)
        builder = builder.not_valid_after(datetime.datetime.utcnow() + datetime.timedelta(days=3600))
        # builder = builder.serial_number(x509.random_serial_number())
        builder = builder.serial_number(random_serial_number())
        builder = builder.public_key(csr.public_key())
        builder = builder.add_extension(x509.AuthorityKeyIdentifier(key_identifier=ski.value.digest,
                                                                    authority_cert_issuer=None,
                                                                    authority_cert_serial_number=None),
                                        critical=False)
        # TODO: Fix the Key Usage so it inherits from the CSR
        builder = builder.add_extension(x509.KeyUsage(digital_signature=True,
                                                      content_commitment=True,
                                                      key_encipherment=False,
                                                      data_encipherment=False,
                                                      key_agreement=False,
                                                      key_cert_sign=True,
                                                      crl_sign=True,
                                                      encipher_only=False,
                                                      decipher_only=False), critical=True)
        for i in csr.extensions:
            builder = builder.add_extension(i.value, critical=False)
        # TODO Make sure CA flag is appropriatly set
        builder = builder.add_extension(x509.BasicConstraints(ca=True, path_length=None), critical=True, )
        if self._key_length == 256:
            certificate = builder.sign(private_key=self.private_key(passphrase),
                                       algorithm=hashes.SHA256(),
                                       backend=default_backend())
        elif self._key_length == 384:
            certificate = builder.sign(private_key=self.private_key(passphrase),
                                       algorithm=hashes.SHA256(),
                                       backend=default_backend())
        else:
            raise ValueError
        return certificate


    # if isinstance(certificate, x509.Certificate):
    #         return certificate


def subject_string(node):
    subject_list = []
    if node.common_name:
        subject_list.append(x509.NameAttribute(NameOID.COMMON_NAME, node.common_name))
    if node.organizational_unit_name:
        subject_list.append(x509.NameAttribute(NameOID.ORGANIZATIONAL_UNIT_NAME, node.organizational_unit_name))
    if node.organization_name:
        subject_list.append(x509.NameAttribute(NameOID.ORGANIZATION_NAME, node.organization_name))
    if node.locality_name:
        subject_list.append(x509.NameAttribute(NameOID.LOCALITY_NAME, node.locality_name))
    if node.state_or_province_name:
        subject_list.append(x509.NameAttribute(NameOID.STATE_OR_PROVINCE_NAME, node.state_or_province_name))
    if node.country_name:
        subject_list.append(x509.NameAttribute(NameOID.COUNTRY_NAME, node.country_name))
    if node.email_address:
        subject_list.append(x509.NameAttribute(NameOID.EMAIL_ADDRESS, node.email_address))
    if node.domain_component:
        subject_list.append(x509.NameAttribute(NameOID.DOMAIN_COMPONENT, node.domain_component))
    return subject_list


def subject_alt_name_string(node):
    subject_alt_name_list = []
    for name in node.subject_alt_names:
        subject_alt_name_list.append(x509.DNSName(name))
    return subject_alt_name_list


OID_NAMES = {
    NameOID.COMMON_NAME: "commonName",
    NameOID.COUNTRY_NAME: "countryName",
    NameOID.LOCALITY_NAME: "localityName",
    NameOID.STATE_OR_PROVINCE_NAME: "stateOrProvinceName",
    NameOID.STREET_ADDRESS: "streetAddress",
    NameOID.ORGANIZATION_NAME: "organizationName",
    NameOID.ORGANIZATIONAL_UNIT_NAME: "organizationalUnitName",
    NameOID.SERIAL_NUMBER: "serialNumber",
    NameOID.SURNAME: "surname",
    NameOID.GIVEN_NAME: "givenName",
    NameOID.TITLE: "title",
    NameOID.GENERATION_QUALIFIER: "generationQualifier",
    NameOID.X500_UNIQUE_IDENTIFIER: "x500UniqueIdentifier",
    NameOID.DN_QUALIFIER: "dnQualifier",
    NameOID.PSEUDONYM: "pseudonym",
    NameOID.USER_ID: "userID",
    NameOID.DOMAIN_COMPONENT: "domainComponent",
    NameOID.EMAIL_ADDRESS: "emailAddress",
    NameOID.JURISDICTION_COUNTRY_NAME: "jurisdictionCountryName",
    NameOID.JURISDICTION_LOCALITY_NAME: "jurisdictionLocalityName",
    NameOID.JURISDICTION_STATE_OR_PROVINCE_NAME: (
        "jurisdictionStateOrProvinceName"
    ),
    NameOID.BUSINESS_CATEGORY: "businessCategory",
    NameOID.POSTAL_ADDRESS: "postalAddress",
    NameOID.POSTAL_CODE: "postalCode"}


class CertFunctions():
    def __init__(self):
        self._oids = {'business_category': {'default': False, 'mandatory': False},
                      'common_name': {'default': True, 'mandatory': True},
                      'country_name': {'default': False, 'mandatory': False},
                      'dn_qualifier': {'default': False, 'mandatory': False},
                      'domain_component': {'default': False, 'mandatory': False},
                      'email_address': {'default': False, 'mandatory': False},
                      'generation_qualifier': {'default': False, 'mandatory': False},
                      'given_name': {'default': False, 'mandatory': False},
                      'jurisdiction_country_name': {'default': False, 'mandatory': False},
                      'jurisdiction_locality_name': {'default': False, 'mandatory': False},
                      'jurisdiction_state_or_province_name': {'default': False, 'mandatory': False},
                      'locality_name': {'default': False, 'mandatory': False},
                      'organization_name': {'default': False, 'mandatory': False},
                      'organizational_unit_name': {'default': False, 'mandatory': False},
                      'postal_address': {'default': False, 'mandatory': False},
                      'postal_code': {'default': False, 'mandatory': False},
                      'pseudonym': {'default': False, 'mandatory': False},
                      'serial_number': {'default': False, 'mandatory': False},
                      'state_or_province_name': {'default': False, 'mandatory': False},
                      'street_address': {'default': False, 'mandatory': False},
                      'surname': {'default': False, 'mandatory': False},
                      'title': {'default': False, 'mandatory': False},
                      'user_id': {'default': False, 'mandatory': False},
                      'x500_unique_identifier': {'default': False, 'mandatory': False}}


def sign_csr(csr, ca_key: ec.EllipticCurvePrivateKey, ca_cert: x509.Certificate, ca=False):
    ski = ca_cert.extensions.get_extension_for_class(x509.SubjectKeyIdentifier)
    one_day = datetime.timedelta(1, 0, 0)
    builder = x509.CertificateBuilder()
    builder = builder.subject_name(x509.Name(csr.subject))
    builder = builder.issuer_name(x509.Name(ca_cert.subject))
    builder = builder.not_valid_before(datetime.datetime.today() - one_day)
    builder = builder.not_valid_after(datetime.datetime.utcnow() + datetime.timedelta(days=3600))
    # builder = builder.serial_number(x509.random_serial_number())
    builder = builder.serial_number(random_serial_number())
    builder = builder.public_key(csr.public_key())
    builder = builder.add_extension(x509.AuthorityKeyIdentifier(key_identifier=ski.value.digest,
                                                                authority_cert_issuer=None,
                                                                authority_cert_serial_number=None),
                                    critical=False)
    builder = builder.add_extension(x509.KeyUsage(digital_signature=True,
                                                  content_commitment=True,
                                                  key_encipherment=False,
                                                  data_encipherment=False,
                                                  key_agreement=False,
                                                  key_cert_sign=True,
                                                  crl_sign=True,
                                                  encipher_only=False,
                                                  decipher_only=False), critical=True)
    for i in csr.extensions:
        builder = builder.add_extension(i.value, critical=False)
    builder = builder.add_extension(x509.BasicConstraints(ca=ca, path_length=None), critical=True,)
    certificate = builder.sign(private_key=ca_key,
                               algorithm=hashes.SHA256(),
                               backend=default_backend())
    if isinstance(certificate, x509.Certificate):
        return certificate


def list_oids():
    oid_list = []
    for key in dir(x509.NameOID):
        if key[0] != '_' or '':
            oid_list.append(key)

    print(oid_list)

def random_serial_number():
    #return utils.int_from_bytes(os.urandom(20), "big") >> 1
    return int.from_bytes(os.urandom(16), byteorder='big') >> 1


def main():

    node = caTree.Node('Root Node')
    node.common_name = 'ca.test.com'
    node.organizational_unit_name = '(c) Billy big bollox'
    node.organization_name = 'Test123'
    node.country_name = 'US'
    node.domain = 'test.com'
    node.subject_alt_names_add('www.bbc.com')
    node.subject_alt_names_add('www.widgets.com')

    root_key = Key(node, 256, 'PassPhrase')
    root_key.create_root_certificate('PassPhrase')
    root_key.create_cert_sign_req('PassPhrase')
    root_key.sign_csr(root_key.csr, 'PassPhrase')

    print(root_key)
    # root_cert = create_root_certificate(node, root_key)
    #
    # sub_key = create_private_key(ec.SECP256R1, 'PassPhrase')
    # csr = create_cert_sign_req(node, sub_key)

    # pprint(subject_string(node))
    # pprint(subject_alt_name_string(node))

    # pprint(root_key)
    # pprint(str(root_cert))
    # pprint(sub_key)
    # pprint(csr.decode('utf-8'))
    # print('Subject      =' + str(csr.subject))
    # print('extension    =' + str(csr.extensions))
    # print('Public Key   =' + str(csr.public_key()))
    # print('Hash Alg     =' + str(csr.signature_hash_algorithm))
    # print('Sig Alg      =' + str(csr.signature_algorithm_oid))
    # print('Public Bytes =' + str(csr.public_bytes(serialization.Encoding.PEM)))
    # print('TBS          =' + str(csr.tbs_certrequest_bytes))

    # print(csr)
    # sub_cert = certificate()
    # sub_cert.certificate = (sign_csr(csr, root_key, root_cert, ca=True))
    # print(sub_cert)

def debug_cert(certificate):
    with open("test_cert.pem", "wb") as f:
        f.write(certificate.public_bytes(serialization.Encoding.PEM))

    os.system('openssl x509 -in test_cert.pem -noout -text')

if __name__ == '__main__':
    main()
