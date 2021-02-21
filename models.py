from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, DateTime, Enum, Float
from sqlalchemy.orm import relationship
from sqlalchemy_utils import IPAddressType
from sqlalchemy.dialects.postgresql import INET, CIDR , MACADDR
from sqlalchemy.sql import func
from sqlalchemy.schema import ForeignKeyConstraint
import enum

from database import Base

class DnsConsistencyEnum(enum.Enum):
    consistent = "consistent"
    reverse_match = "reverse_match"
    inconsistent = "inconsistent"

class BlockingEnum(enum.Enum):
    tcp_ip = "tcp_ip"
    dns = "dns"
    http_diff = "http-diff"
    http_failure = "http-failure"
    not_blocking = "not_blocking" ##false

class RatingOarcEnum(enum.Enum):
    GREAT = "GREAT"
    GOOD = "GOOD"
    POOR = "POOR"

class Asn(Base):

    __tablename__ = "asns"
    
    id = Column(Integer, primary_key = True, autoincrement = False )
    asn_organization = Column(String)
    
class AsnNetwork(Base):

    __tablename__  = "asn_networks"

    id = Column(Integer, primary_key=True, index=True)
    asn = Column(ForeignKey('asns.id'))
    network = Column(CIDR)

class MacManuf(Base):

    __tablename__ = 'macs_manuf'

    mac = Column(MACADDR, primary_key = True)
    mask = Column(Integer, primary_key = True)
    manuf = Column(String)
    comment = Column(String)

class Test(Base):
    __tablename__ = 'tests'
    
    id = Column(Integer, primary_key=True, index=True)
    public_ip = Column(INET)
    timestamp = Column(DateTime(timezone=True), server_default=func.now())
    asn_id = Column(ForeignKey('asns.id')) 
    device_android = Column(String)
    mac = Column(MACADDR)
    mask = Column(Integer)
    place = Column(String)
    username = Column(String)

class ProtocolTest(Base):
    __tablename__ = 'protocol_tests'

    id = Column(Integer, primary_key=True, index=True)
    test_id = Column(ForeignKey('tests.id'), nullable = False)
    protocol_name = Column(String, nullable = False) 
    key_management = Column(String)
    cipher = Column(String)

class DevicesTest(Base):
    
    __tablename__ = 'devices_tests'

    id = Column(Integer, primary_key=True, index=True)
    test_id = Column(ForeignKey('tests.id'))
    mac = Column(MACADDR,  nullable=False)
    mask = Column(Integer,  nullable=False)
    router = Column(Boolean)

class DnsTest(Base):
    
    __tablename__ = 'dns_tests'

    id = Column(Integer, primary_key=True, index=True)
    test_id = Column(ForeignKey('tests.id'))
    dns1_android = Column(IPAddressType)
    dns2_android = Column(IPAddressType)
    ns_akamai = Column(IPAddressType)
    ecs_akamai = Column(IPAddressType)
    ip_akamai = Column(IPAddressType)
    do_flag = Column(Boolean)
    ad_flag = Column(Boolean)
    rrsig = Column(Boolean)
    resolver_ip_oarc = Column(IPAddressType)
    rating_source_port = Column(Enum(RatingOarcEnum))
    rating_transaction_id = Column(Enum(RatingOarcEnum))
    std_source_port = Column(Integer)
    std_transaction_id =  Column(Integer)
    bits_of_entropy_source_port = Column(Float)
    bits_of_entropy_transaction_id = Column(Float)

class NdtTestOoni(Base):

    __tablename__ = "ndt_tests_ooni"

    id = Column(Integer, primary_key=True, index=True)
    test_id = Column(ForeignKey('tests.id'), nullable= False)
    report_id = Column(String, nullable= False)
    avg_rtt = Column(Float)
    download = Column(Float, nullable= False)
    mss = Column(Integer)
    max_rtt = Column(Float)
    min_rtt = Column(Float)
    ping = Column(Float)
    retransmit_rate = Column(Float)
    upload = Column(Float, nullable= False)

class WebTestOoni(Base):

    __tablename__ = 'web_tests_ooni'

    id = Column(Integer, primary_key=True, index=True)
    test_id = Column(ForeignKey('tests.id'), nullable= False)
    report_id =  Column(String, nullable= False)
    url = Column(String, nullable= False)
    resolver_asn = Column(String)
    resolver_ip = Column(INET)
    resolver_network_name = Column(String)
    client_resolver = Column(INET, nullable= False)
    dns_experiment_failure = Column(String)
    control_failure = Column(String)
    http_experiment_failure = Column(String)
    dns_consistency = Column(Enum(DnsConsistencyEnum), nullable= False)
    body_length_match = Column(Boolean)
    headers_match = Column(Boolean)
    status_code_match = Column(Boolean)
    title_match = Column(Boolean)
    accessible = Column(Boolean)
    blocking = Column(Enum(BlockingEnum))

class TcpConnectWebTestOoni(Base):
    __tablename__ = 'tcp_connect_web_tests_ooni'

    id = Column(Integer, primary_key=True, index=True)
    ip = Column(INET, nullable= False)
    port = Column(Integer, nullable= False)
    status_blocked = Column(Boolean)
    status_failure_string = Column(String)
    status_success = Column(Boolean, nullable= False)
    test_id = Column(ForeignKey('web_tests_ooni.id'), nullable= False)

