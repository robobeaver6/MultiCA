from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography import x509
from cryptography.x509.oid import NameOID
from cryptography.hazmat.primitives import hashes
from pprint import pprint

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


def main():
    list_oids()


def list_oids():
    oid_list = []
    for key in dir(x509.NameOID):
        if key[0] != '_' or '':
            oid_list.append(key.lower())
    # pprint(oid_list)
    # print(len(oid_list))
    oid_mand = [False] * 24
    oid_default = [False] * 24
    oids = dict()
    for z in zip(oid_list, oid_mand, oid_default):
        oids[z[0]] = {'mandatory': False,
                      'default': False}
    subject = issuer = x509.Name([
                         x509.NameAttribute(NameOID.COUNTRY_NAME, u"US"),
                         x509.NameAttribute(NameOID.STATE_OR_PROVINCE_NAME, u"CA"),
                         x509.NameAttribute(NameOID.LOCALITY_NAME, u"San Francisco"),
                         x509.NameAttribute(NameOID.ORGANIZATION_NAME, u"My Company"),
                         x509.NameAttribute(NameOID.COMMON_NAME, u"mysite.com"),
                         ])
    pprint(x509.NameAttribute(NameOID.COUNTRY_NAME, u"US"))


if __name__ == '__main__':
    main()
