from pytest import *
from crypto import Key
from caTree import Node
from cryptography.hazmat.primitives.asymmetric import ec
from cryptography import x509

root_node = Node('Root')

test_node1 = Node('Populated', root_node)
test_node1.common_name = 'Common Name'
test_node1.organizational_unit_name = 'Organisational Unit'
test_node1.organization_name = 'Organisation Name'
test_node1.locality_name = 'Locality'
test_node1.state_or_province_name = 'State or Province'
test_node1.country_name = 'UK'
test_node1.email_address = 'email@address.com'
test_node1.domain_component = 'www.domain.com'
test_node1.subject_alt_names = ['alt1.domain.com', 'alt2.domain.com']
test_node2 = Node('Empty', root_node)
test_sub1 = Node('Sub-1', test_node1)
test_sub2 = Node('Sub-2', test_node2)


def test_key_object_creation():
    for child in root_node.children:
        assert isinstance(child.key, Key)
        assert child.key.private_key_exists is False
        assert child.key.csr_exists is False
        assert child.key.certificate_exists is False
        assert child.key.ready is False


def test_key_private_key():
    for length in (256, 384):
        for child in root_node.children:
            # test Unencrypted
            child.key.private_key_delete()
            child.key.create_private_key(length=length)
            assert isinstance(child.key.private_key(), ec.EllipticCurvePrivateKey)
            # test Encrypted
            child.key.private_key_delete()
            child.key.create_private_key(length=length, pass_phrase='fred')
            assert isinstance(child.key.private_key(pass_phrase='fred'), ec.EllipticCurvePrivateKey)


def test_key_csr():
    for pass_phrase in (None, 'fred'):
        for child in root_node.children:
            child.key.private_key_delete()
            child.key.create_private_key(pass_phrase=pass_phrase)
            child.key.csr_delete()
            child.key.create_cert_sign_req(pass_phrase=pass_phrase)
            assert isinstance(child.key.csr, x509.CertificateSigningRequest)

def test_key_root_certificate():
    """
    Test that certificate returned from .certificate property is a valid x509 cert type
    Test that the root CA has appropriate Basic Constraints and key usage set
    Basic Constraint CA must be True.
    Key usage key_cert_sign and CRL sign must be True. digital_signature and content_commitment are optional
        All other key usage flags must be false.
        Encipher and Decipher only can only be quiried if key_agreement is true
    :return:
    """
    for pass_phrase in (None, 'fred'):
        for length in (256, 384):
            for child in root_node.children:
                child.key.private_key_delete()
                child.key.create_private_key(length=length, pass_phrase=pass_phrase)
                child.key.csr_delete()
                # child.key.create_cert_sign_req(pass_phrase=pass_phrase)
                child.key.create_root_certificate(passphrase=pass_phrase)
                assert isinstance(child.key.certificate, x509.Certificate)
                assert child.key.certificate.extensions.get_extension_for_class(x509.BasicConstraints).value.ca
                assert child.key.certificate.extensions.get_extension_for_class(x509.KeyUsage).value.key_cert_sign
                assert child.key.certificate.extensions.get_extension_for_class(x509.KeyUsage).value.crl_sign
                assert not child.key.certificate.extensions.get_extension_for_class(x509.KeyUsage).value.key_encipherment
                assert not child.key.certificate.extensions.get_extension_for_class(x509.KeyUsage).value.data_encipherment
                assert not child.key.certificate.extensions.get_extension_for_class(x509.KeyUsage).value.key_agreement


def test_key_sub_ca_certificate():
    """
    Test that certificate returned from .certificate property is a valid x509 cert type
    Test that the sub CA has appropriate Basic Constraints and key usage set
    Basic Constraint CA must be True.
    Key usage key_cert_sign and CRL sign must be True. digital_signature and content_commitment are optional
        All other key usage flags must be false.
        Encipher and Decipher only can only be quiried if key_agreement is true
    :return:
    """
    for pass_phrase in (None, 'fred'):
        for length in (256, 384):
            for root_ca in root_node.children:
                root_ca.key.private_key_delete()
                root_ca.key.create_private_key(length=length, pass_phrase=pass_phrase)
                root_ca.key.csr_delete()
                root_ca.key.create_root_certificate(passphrase=pass_phrase)
                sub_ca = Node('Sub-CA-()-()'.format(root_ca.name, length), root_ca)
                sub_ca.key.private_key_delete()
                sub_ca.key.create_private_key(length=length, pass_phrase=pass_phrase)
                sub_ca.key.csr_delete()
                sub_ca.key.create_cert_sign_req(pass_phrase=pass_phrase)
                del sub_ca.key.certificate
                sub_ca.key.certificate = sub_ca.parent.key.sign_csr(sub_ca.key.csr, pass_phrase=pass_phrase)
                assert isinstance(sub_ca.key.certificate, x509.Certificate)
                assert sub_ca.key.certificate.extensions.get_extension_for_class(x509.BasicConstraints).value.ca
                assert sub_ca.key.certificate.extensions.get_extension_for_class(x509.KeyUsage).value.key_cert_sign
                assert sub_ca.key.certificate.extensions.get_extension_for_class(x509.KeyUsage).value.crl_sign
                assert not sub_ca.key.certificate.extensions.get_extension_for_class(
                    x509.KeyUsage).value.key_encipherment
                assert not sub_ca.key.certificate.extensions.get_extension_for_class(
                    x509.KeyUsage).value.data_encipherment
                assert not sub_ca.key.certificate.extensions.get_extension_for_class(x509.KeyUsage).value.key_agreement
                sub_ca_auth_key_id = sub_ca.key.certificate.extensions.get_extension_for_class(
                    x509.AuthorityKeyIdentifier).value.key_identifier
                ca_auth_key_id = root_ca.key.certificate.extensions.get_extension_for_class(
                    x509.SubjectKeyIdentifier).value.digest
                assert sub_ca_auth_key_id == ca_auth_key_id
