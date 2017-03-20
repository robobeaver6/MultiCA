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
import logging


class Key(object):
    def __init__(self, node):
        # if length == 256:
        #     curve = ec.SECP256R1
        # elif length == 384:
        #     curve = ec.SECP384R1
        # else:
        #     raise ValueError
        self._node = node
        self._key_length = 256
        # key = ec.generate_private_key(curve=curve, backend=default_backend())
        # self._str_key = key.private_bytes(encoding=serialization.Encoding.PEM,
        #                                   format=serialization.PrivateFormat.TraditionalOpenSSL,
        #                                   encryption_algorithm=serialization.BestAvailableEncryption(passphrase.encode()
        #                                   ))
        self._str_key = None
        self._str_csr = None
        self._str_certificate = None

    def __str__(self):
        output = ''
        if self._str_key:
            output += str(self._str_key, 'utf-8')
        if self._str_csr:
            output += str(self._str_csr, 'utf-8')
        if self._str_certificate:
            output += str(self._str_certificate, 'utf-8')
        return output

    def create_private_key(self, length: int=256, pass_phrase: str=''):
        if length == 256:
            self._key_length = length
            curve = ec.SECP256R1
        elif length == 384:
            self._key_length = length
            curve = ec.SECP384R1
        else:
            raise ValueError
        if not self._str_key:
            key = ec.generate_private_key(curve=curve, backend=default_backend())
            self._str_key = key.private_bytes(encoding=serialization.Encoding.PEM,
                                              format=serialization.PrivateFormat.TraditionalOpenSSL,
                                              encryption_algorithm=serialization.BestAvailableEncryption(
                                                  pass_phrase.encode()))

    @property
    def private_key_exists(self):
        if self._str_key:
            return True
        else:
            return False

    def private_key(self, passphrase=''):
        try:
            return serialization.load_pem_private_key(self._str_key,
                                                      passphrase.encode(),
                                                      default_backend())
        except ValueError as e:
            print('ERROR: Incorrect Password')

    @property
    def certificate(self):
        if self._str_certificate is None or self._str_certificate == b'':
            return None
        else:
            try:
                cert = x509.load_pem_x509_certificate(self._str_certificate, backend=default_backend())
                return cert
            except:
                logging.critical('certificate error: ')

    @certificate.setter
    def certificate(self, value):
        self._str_certificate = value.public_bytes(serialization.Encoding.PEM)



    @property
    def csr(self):
        if self._str_csr:
            return x509.load_pem_x509_csr(self._str_csr, default_backend())
        else:
            return None

    @property
    def ready(self):
        if self.private_key is not None and self.certificate is not None:
            return True
        else:
            return False

    def create_root_certificate(self, passphrase):
        """
        Create self signed Root CA Certificate
        :param passphrase: Private key pass phrase
        :return:
        """
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
        """
        Generate a Certificate Signing Request (CSR) for the current object's private key
        :param passphrase: Private key Password
        :return:
        """
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
        """
        Signs a Certificate Signing Request with the key and cert of this object
        :param csr: Certificate Signing Request passed to function for signing
        :param passphrase: Private key passphrase
        :return: Signed x509 Certificate object
        """
        ski = self.certificate.extensions.get_extension_for_class(x509.SubjectKeyIdentifier)
        key = self.private_key(passphrase)
        one_day = datetime.timedelta(1, 0, 0)
        builder = x509.CertificateBuilder()
        builder = builder.subject_name(x509.Name(csr.subject))
        builder = builder.issuer_name(x509.Name(self.certificate.subject))
        builder = builder.not_valid_before(datetime.datetime.today() - one_day)
        builder = builder.not_valid_after(datetime.datetime.utcnow() + datetime.timedelta(days=3600))
        builder = builder.serial_number(random_serial_number())
        builder = builder.public_key(csr.public_key())
        builder = builder.add_extension(x509.AuthorityKeyIdentifier(key_identifier=ski.value.digest,
                                                                    authority_cert_issuer=None,
                                                                    authority_cert_serial_number=None),
                                        critical=False)
        builder = builder.add_extension(x509.SubjectKeyIdentifier.from_public_key(key.public_key()), critical=False)
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
            certificate = builder.sign(private_key=key,
                                       algorithm=hashes.SHA256(),
                                       backend=default_backend())
        elif self._key_length == 384:
            certificate = builder.sign(private_key=key,
                                       algorithm=hashes.SHA256(),
                                       backend=default_backend())
        else:
            raise ValueError
        return certificate


    # if isinstance(certificate, x509.Certificate):
    #         return certificate


def subject_string(node):
    """
    Iterate through caTree.Node() object to build list of Subject Key Identifiers
    :param node: caTree Node to base Subject Name on
    :return: List of x509.NameAttributes
    """
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
    """
    Build list of x509.DNSName objects for cert builder's Subject Alternate Names
    :param node: caTree.Node() Object to base names on
    :return:
    """
    subject_alt_name_list = []
    for name in node.subject_alt_names:
        subject_alt_name_list.append(x509.DNSName(name))
    return subject_alt_name_list


class CertFunctions:
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

        self.OID_IN_USE = {'common_name': {'default': True, 'mandatory': True},
                           'country_name': {'default': False, 'mandatory': False},
                           'domain_component': {'default': False, 'mandatory': False},
                           'email_address': {'default': False, 'mandatory': False},
                           'locality_name': {'default': False, 'mandatory': False},
                           'organization_name': {'default': False, 'mandatory': False},
                           'organizational_unit_name': {'default': False, 'mandatory': False},
                           'serial_number': {'default': False, 'mandatory': False},
                           'state_or_province_name': {'default': False, 'mandatory': False}}


def list_oids():
    oid_list = []
    for key in dir(x509.NameOID):
        if key[0] != '_' or '':
            oid_list.append(key)

    print(oid_list)

def random_serial_number():
    #return utils.int_from_bytes(os.urandom(20), "big") >> 1
    return int.from_bytes(os.urandom(16), byteorder='big')


def main():

    node = caTree.Node('Root Node')
    node.common_name = 'ca.test.com'
    node.organizational_unit_name = '(c) Billy big bollox'
    node.organization_name = 'Test123'
    node.country_name = 'US'
    node.domain = 'test.com'
    node.subject_alt_names_add('www.bbc.com')
    node.subject_alt_names_add('www.widgets.com')
    child_node = caTree.Node('subCA', node)

    node.key = Key(node, 256, 'PassPhrase')
    node.key.create_root_certificate('PassPhrase')

    child_node.key = Key(child_node, 256, 'PassPhrase')
    child_node.key.create_cert_sign_req('PassPhrase')

    child_node.key.certificate = node.key.sign_csr(child_node.key.csr, 'PassPhrase')

    print(node.key)
    print(child_node.key)
    print(node)
    print(child_node)

def debug_cert(certificate):
    with open("test_cert.pem", "wb") as f:
        f.write(certificate.public_bytes(serialization.Encoding.PEM))

    os.system('openssl x509 -in test_cert.pem -noout -text')

if __name__ == '__main__':
    main()
