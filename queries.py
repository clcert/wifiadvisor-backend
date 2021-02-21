from sqlalchemy.orm import Session
from sqlalchemy.sql import exists
from sqlalchemy import and_, or_, desc

import models
import schemas

def get_asn_by_ip(db: Session, ip: str):
    asn = db.query(models.Asn).join(models.AsnNetwork).\
        filter(models.AsnNetwork.network.op(">>")(ip)).\
        first()
    return asn

def add_to_database(db: Session, schema_test:schemas.BaseModel):
    db.add(schema_test)
    db.commit()
    db.refresh(schema_test)

def check_mac_mask_exists(db, schema_test:schemas.BaseModel):
    return db.query(exists().where(and_(models.MacManuf.mac == schema_test.mac, models.MacManuf.mask == schema_test.mask))).scalar()

def create_test_base(db: Session, test_base: schemas.TestBase, ip):
    asn = get_asn_by_ip(db, ip)
    asn_id = asn.id if asn else None
    db_test = models.Test(**test_base.dict(), public_ip=ip,asn_id= asn_id)
    add_to_database(db, db_test)
    return db_test

def create_specific_test(db: Session, result_test: schemas.BaseModel, model_test: models.Base, id_fk = None):
    db_test = model_test(**result_test.dict(), test_id= id_fk) if id_fk else  model_test(**result_test.dict())
    add_to_database(db, db_test)
    return db_test

def get_manuf(db: Session, devices_test:models.DevicesTest):
    if check_mac_mask_exists(db, devices_test):
        manuf_device = db.query(models.MacManuf).filter(and_(models.MacManuf.mac == devices_test.mac, models.MacManuf.mask == devices_test.mask)).first()
    else:
        manuf_device = schemas.MacManufOut(mac = devices_test.mac, mask = devices_test.mask)
    return manuf_device

def get_tests_with_list(db: Session, ip, model_test: models.Base):
    tests_id_timestamp = db.query(model_test.test_id, models.Test.timestamp).distinct().join(models.Test).filter(models.Test.public_ip==ip).order_by(models.Test.timestamp.desc())[:5]
    results = []
    for test_id_timestamp in tests_id_timestamp:
        results.append({
            "test":db.query(model_test).filter(model_test.test_id==test_id_timestamp[0]).all(),
            "timestamp":test_id_timestamp[1]
        })
    return results
    
def get_devices_tests(db:Session, ip):
    tests_id_timestamp = db.query(models.DevicesTest.test_id, models.Test.timestamp).distinct().join(models.Test).filter(models.Test.public_ip==ip).order_by(models.Test.timestamp.desc())[:5]
    results = []
    for test_id_timestamp in tests_id_timestamp:
        results.append({
            "test":[get_manuf(db, devices_test) for devices_test in db.query(models.DevicesTest).filter(models.DevicesTest.test_id==test_id_timestamp[0]).all()],
            "timestamp":test_id_timestamp[1]
        })
    return results

def get_tests(db: Session, ip, model_test: models.Base):
    tests = db.query(model_test, models.Test.timestamp).join(models.Test).filter(models.Test.public_ip==ip).order_by(models.Test.timestamp.desc())[:5]
    return [{"test":test[0], "timestamp":test[1]} for test in tests]

def get_ooni_web_tests(db: Session, ip):
    tests_ooni = db.query(models.WebTestOoni, models.Test.timestamp).join(models.Test).filter(models.Test.public_ip==ip).order_by(models.Test.timestamp.desc())[:5]
    results = []
    for test in tests_ooni:
        tpc_connect = db.query(models.TcpConnectWebTestOoni).filter(models.TcpConnectWebTestOoni.test_id==test[0].id).all()
        results.append({
            "test":test[0],
            "tcp_connect":tpc_connect,
            "timestamp":test[1]
        })
    return results