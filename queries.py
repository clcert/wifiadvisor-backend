from sqlalchemy.orm import Session
from sqlalchemy.sql import exists
from sqlalchemy import and_, or_, desc
import models
import schemas
from bisect import bisect_left


def get_asn_by_ip(db: Session, ip: str):
    asn = db.query(models.Asn).join(models.LatestSubnetAsns, models.Asn.id == models.LatestSubnetAsns.asn_id).\
        filter(models.LatestSubnetAsns.subnet.op(">>")(ip)).\
        first()
    return asn


def add_to_database(db: Session, schema_test: schemas.BaseModel):
    db.add(schema_test)
    db.commit()
    db.refresh(schema_test)


def check_mac_mask_exists(db, schema_test: schemas.BaseModel):
    return db.query(exists().where(and_(models.MacManuf.mac == schema_test.mac, models.MacManuf.mask == schema_test.mask))).scalar()


def create_test_base(db: Session, test_base: schemas.TestBase, ip):
    asn = get_asn_by_ip(db, ip)
    asn_id = asn.id if asn else None
    db_test = models.Test(**test_base.dict(), public_ip=ip, asn_id=asn_id)
    add_to_database(db, db_test)
    return db_test


def create_specific_test(db: Session, result_test: schemas.BaseModel, model_test: models.Base, id_fk=None):
    db_test = model_test(
        **result_test.dict(), test_id=id_fk) if id_fk else model_test(**result_test.dict())
    add_to_database(db, db_test)
    return db_test


def get_manuf(db: Session, devices_test: models.DevicesTest):
    if check_mac_mask_exists(db, devices_test):
        manuf_device = db.query(models.MacManuf).filter(and_(
            models.MacManuf.mac == devices_test.mac, models.MacManuf.mask == devices_test.mask)).first()
    else:
        manuf_device = schemas.MacManufOut(
            mac=devices_test.mac, mask=devices_test.mask)
    return manuf_device


def get_only_manuf(db: Session, devices_test: models.DevicesTest):
    if check_mac_mask_exists(db, devices_test):
        mac_manuf = db.query(models.MacManuf).filter(and_(
            models.MacManuf.mac == devices_test.mac, models.MacManuf.mask == devices_test.mask)).first()
        manuf_device = mac_manuf.comment if mac_manuf.comment != "" else mac_manuf.manuf
    else:
        manuf_device = None
    return manuf_device

def get_tests_with_list(db: Session, ip, model_test: models.Base):
    tests_id_timestamp = db.query(model_test.test_id, models.Test.timestamp).distinct().join(
        models.Test).filter(models.Test.public_ip == ip).order_by(models.Test.timestamp.desc())[:5]
    results = []
    for test_id_timestamp in tests_id_timestamp:
        results.append({
            "test": db.query(model_test).filter(model_test.test_id == test_id_timestamp[0]).all(),
            "timestamp": test_id_timestamp[1]
        })
    return results


def get_devices_tests(db: Session, ip):
    tests_id_timestamp = db.query(models.DevicesTest.test_id, models.Test.timestamp).distinct().join(
        models.Test).filter(models.Test.public_ip == ip).order_by(models.Test.timestamp.desc())[:5]
    results = []
    for test_id_timestamp in tests_id_timestamp:
        results.append({
            "test": [schemas.DevicesOut(**devices_test.__dict__, manuf=get_only_manuf(db, devices_test)) for devices_test in db.query(models.DevicesTest).filter(models.DevicesTest.test_id == test_id_timestamp[0]).all()],
            "timestamp": test_id_timestamp[1]
        })
    return results


def get_tests(db: Session, ip, model_test: models.Base):
    tests = db.query(model_test, models.Test.timestamp).join(models.Test).filter(
        models.Test.public_ip == ip).order_by(models.Test.timestamp.desc())[:5]
    return [{"test": test[0], "timestamp":test[1]} for test in tests]


def get_ooni_web_tests(db: Session, ip):
    tests_ooni = db.query(models.WebTestOoni, models.Test.timestamp).join(models.Test).filter(
        models.Test.public_ip == ip).order_by(models.Test.timestamp.desc())[:5]
    results = []
    for test in tests_ooni:
        tpc_connect = db.query(models.TcpConnectWebTestOoni).filter(
            models.TcpConnectWebTestOoni.test_id == test[0].id).all()
        results.append({
            "test": test[0],
            "tcp_connect": tpc_connect,
            "timestamp": test[1]
        })
    return results


def get_ndt_test(db: Session, ip, model_test: models.NdtTestOoni):
    tests = db.query(model_test, models.Test.timestamp).join(models.Test).filter(
        models.Test.public_ip == ip).order_by(models.Test.timestamp.desc())[:5]
    return [{"test": test[0], "mlab": get_mlab(test[0]), "timestamp":test[1]} for test in tests]


def get_mlab(ndt: models.NdtTestOoni):
    download = [0.23243849257549207, 0.6875543587708922, 1.4410504358198128, 2.5799351721570947,
                4.2181690863027095, 8.773812503971508, 15.482419418393432, 26.208500361301887, 48.865976128894346,
                182.20702077771392]
    min_download = 0.0
    max_download = 695.5644904984871
    mean_download = 16.960839419237896
    download_rtt = [76.0, 149.0, 171.0, 226.0,
                    249.0, 262.0, 270.0, 282.0, 306.0, 839.0]

    upload = [0.2606367586170152, 0.6115126968261643, 1.4246995691135311, 2.4488057786169932, 3.859683497799003,
              5.912398780958386, 8.91031485283244, 15.44939531147001, 31.775679487886162, 89.76927089572779]
    min_upload = 0.0
    max_upload = 528.015639162466
    mean_upload = 10.976625369387257
    upload_rtt = [90.148, 158.957, 196.166, 248.975,
                  262.096, 278.547, 298.721, 324.653, 401.559, 1363.0]
    return {
        "p_upload": (bisect_left(upload, ndt.upload) + 1) * 10 if (bisect_left(upload, ndt.upload) < 10) else 100 ,
        "p_download": (bisect_left(download, ndt.download) + 1) * 10 if (bisect_left(upload, ndt.upload) < 10) else 100 ,
        "p_rtt": (bisect_left(download_rtt, ndt.avg_rtt) + 1) * 10 if (bisect_left(upload, ndt.upload) < 10) else 100 ,
    }
