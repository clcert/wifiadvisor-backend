"""
 * the regex code for the mac address was obtained from stackoverflow (https://stackoverflow.com/questions/4260467/what-is-a-regular-expression-for-a-mac-address)
 * the regex code for the private ip address was obtained from stackoverflow (https://stackoverflow.com/questions/2814002/private-ip-address-identifier-in-regular-expression)
"""
from pydantic import BaseModel, PositiveInt, IPvAnyAddress, constr, conint, confloat, root_validator
from typing import Optional, List
from datetime import datetime 

import models
class MacManufOut(BaseModel):
    mac: constr(regex = r'^([0-9A-Fa-f]{2}[:]){5}([0-9A-Fa-f]{2})')
    mask: PositiveInt
    manuf: Optional[str]
    class Config:
        orm_mode = True

class TestBase(BaseModel):
    device_android: Optional[str]
    mac: Optional[constr(regex = r'^([0-9A-Fa-f]{2}[:]){5}([0-9A-Fa-f]{2})')]
    mask: Optional[PositiveInt]
    place: Optional[str]
    username: Optional[str]

    @classmethod    
    @root_validator(pre=True)
    def check_mac_mask(cls, values):
        mac, mask = values.get('mac'), values.get('mask')
        if (mac is None and mask is not None) or (mac is not None and mask is None):
            raise ValueError('missing mask or mac values')
        return values
    class Config:
        orm_mode = True
        
class ProtocolTest(BaseModel):
    protocol_name: str
    key_management: Optional[str]
    cipher: Optional[str] 
    class Config:
        orm_mode = True

class DevicesTest(BaseModel):
    mac: constr(regex = r'^([0-9A-Fa-f]{2}[:]){5}([0-9A-Fa-f]{2})')
    mask: PositiveInt = 24
    router: bool=False
    private_ip: constr(regex = r'(10|127|169\.254|172\.1[6-9]|172\.2[0-9]|172\.3[0-1]|192\.168)\.[0-9]{1,3}\.[0-9]{1,3}')
    class Config:
        orm_mode = True

class DevicesOut(BaseModel):
    mac: constr(regex = r'^([0-9A-Fa-f]{2}[:]){5}([0-9A-Fa-f]{2})')
    mask: PositiveInt = 24
    router: bool=False
    private_ip: constr(regex = r'(10|127|169\.254|172\.1[6-9]|172\.2[0-9]|172\.3[0-1]|192\.168)\.[0-9]{1,3}\.[0-9]{1,3}')
    manuf: Optional[str]
    class Config:
        orm_mode = True

class DnsTest(BaseModel):
    dns1_android: Optional[IPvAnyAddress]
    dns2_android: Optional[IPvAnyAddress]
    ns_akamai: Optional[IPvAnyAddress]
    ecs_akamai: Optional[IPvAnyAddress]
    ip_akamai: Optional[IPvAnyAddress]
    do_flag: Optional[bool]
    ad_flag: Optional[bool]
    rrsig: Optional[bool]
    resolver_ip_oarc: Optional[IPvAnyAddress]
    rating_source_port: Optional[models.RatingOarcEnum]
    rating_transaction_id: Optional[models.RatingOarcEnum]
    std_source_port: Optional[conint(ge=0)]
    std_transaction_id:  Optional[conint(ge=0)]
    bits_of_entropy_source_port: Optional[confloat(ge=0)]
    bits_of_entropy_transaction_id: Optional[confloat(ge=0)]
    
    @classmethod
    @root_validator(pre=True)
    def check_resolver_ip(cls, values):
        dns_android, dns_akami = values.get('dns1_android'), values.get('ns')
        if dns_android is None and dns_akami is None:
            raise ValueError('at least one resolver ip')
        return values
    
    @classmethod
    @root_validator
    def check_dnssec(cls, values):
        do_flag, ad_flag, rrsig = values.get('do_flag'), values.get('ad_flag'), values.get('rrsig')
        if (do_flag is not None and (ad_flag is None or rrsig is None)) or (do_flag is None and (ad_flag is not None or rrsig is not None)):
            raise ValueError('some dnssec values are missing')
        return values
    
    @classmethod
    @root_validator
    def check_oarc(cls, values):
        resolver_ip_oarc = values.get('resolver_ip_oarc')
        rating_source_port = values.get('rating_source_port')
        rating_transaction_id = values.get('rating_transaction_id')
        std_source_port = values.get('std_source_port')
        std_transaction_id = values.get('std_transaction_id')

        if (resolver_ip_oarc is not None):
            if((rating_transaction_id is not None and std_transaction_id is None) or (rating_transaction_id is None and std_transaction_id is not None)):
                raise ValueError('some oarc values of transaction_id are missing')
            elif((rating_source_port is not None and std_source_port is None) or (rating_source_port is None and std_source_port is not None)):
                raise ValueError('some oarc values of source_port are missing')
            elif(rating_source_port is None and std_source_port is None and rating_transaction_id is None and std_transaction_id is None):
                raise ValueError('some oarc values are missing')
        elif (rating_source_port is not None or std_source_port is not None or rating_transaction_id is not None or std_transaction_id is not None):
            raise ValueError('resolver_ip_oarc is missing')
        return values

    class Config:
        orm_mode = True

class NdtTestOoni(BaseModel):
    report_id: str
    avg_rtt: Optional[float]
    download: float
    mss: Optional[int]
    max_rtt: Optional[float]
    min_rtt: Optional[float]
    ping: Optional[float]
    retransmit_rate: Optional[float]
    upload: float
    class Config:
        orm_mode = True

class WebTestOoni(BaseModel):
    report_id: str
    url: str
    resolver_asn: str
    resolver_ip: IPvAnyAddress
    resolver_network_name: str
    client_resolver: IPvAnyAddress
    dns_experiment_failure: Optional[str]
    control_failure: Optional[str]
    http_experiment_failure: Optional[str]
    dns_consistency: Optional[models.DnsConsistencyEnum]
    body_length_match: Optional[bool]
    headers_match: Optional[bool]
    status_code_match: Optional[bool]
    title_match: Optional[bool]
    accessible: Optional[bool]
    blocking: Optional[models.BlockingEnum]
    class Config:
        orm_mode = True

class TcpConnectWebTestOoni(BaseModel):
    ip: Optional[IPvAnyAddress]
    port: Optional[PositiveInt]
    status_blocked: Optional[bool]
    status_failure_string: Optional[str]
    status_success: bool
    class Config:
        orm_mode = True