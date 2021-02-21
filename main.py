"""
the code for the following functions was obtained from the following sources.
get_db: FastApi tutorial (https://fastapi.tiangolo.com/tutorial/sql-databases/#main-fastapi-app)
adapt_pydantic_ip_address: Adapting types to fix SQLAlchemy's "can't adapt type" error "(https://gaganpreet.in/posts/sqlalchemy-cant-adapt-type/)
sudo uvicorn main:app --host 0.0.0.0 --port 80
"""
from fastapi import Depends, FastAPI, HTTPException, Request, status
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from sqlalchemy.sql import operators
from psycopg2.extensions import register_adapter, AsIs
from pydantic.networks import IPv4Address, IPv6Address
from typing import List
import logging
from fastapi.middleware.cors import CORSMiddleware
import models
import database
import queries
import schemas
from typing import Optional
def get_db():
    db = database.SessionLocal()
    try:
        yield db
    finally:
        db.close()

def adapt_pydantic_ip_address(ip):
    return AsIs(repr(ip.exploded))

models.Base.metadata.create_all(bind=database.engine)
app = FastAPI()
origins = [
    "http://0.0.0.0:8000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
register_adapter(IPv4Address, adapt_pydantic_ip_address)
register_adapter(IPv6Address, adapt_pydantic_ip_address)

responses = {
    404: {"description": "Error: Not Found"},
}

@app.get("/asn", responses ={**responses})
def get_asn(request: Request, db: Session=Depends(get_db)):
    try:
        client_host = request.client.host
        asn = queries.get_asn_by_ip(db, client_host)
        return {
                "client_host": client_host,
                "asn": asn
        }
    except Exception as e:
        message = "Error getting asn"
        logging.error(message, exc_info=e)
        return JSONResponse(status_code=404, content={"message": message})
        

@app.post("/tests/protocol", responses ={**responses}, status_code=status.HTTP_201_CREATED)
def add_protocol_test(request: Request, test:List[schemas.ProtocolTest], test_base: schemas.TestBase = schemas.TestBase() ,db: Session=Depends(get_db)):
    try:
        ip = request.client.host
        db_test_base = queries.create_test_base(db, test_base, ip)
        db_test_base_id = db_test_base.id
        for protocol_test in test:
            queries.create_specific_test(db, protocol_test, models.ProtocolTest, db_test_base_id)
    except Exception as e:
        message = "Error adding results to protocol tests table"
        logging.error(message, exc_info=e)
        return JSONResponse(status_code=404, content={"message": message})

"""
if no device has a known mac then do not add the test base. Also, add only if mac exists to devices tests. 
"""
@app.post("/tests/devices", responses ={**responses}, status_code=status.HTTP_201_CREATED, response_model=List[schemas.MacManufOut])
def add_devices_tests(request: Request, test:List[schemas.DevicesTest], test_base: schemas.TestBase = schemas.TestBase() ,db: Session=Depends(get_db)):
    try:
        ip = request.client.host
        db_test_base_id = None
        manuf_devices = []
        for devices_test in test:
            if db_test_base_id is None:
                db_test_base_id = queries.create_test_base(db, test_base, ip).id
            manuf_device = queries.get_manuf(db, devices_test)
            queries.create_specific_test(db, devices_test, models.DevicesTest, db_test_base_id)
            manuf_devices.append(manuf_device)
        return manuf_devices
    except Exception as e:
        message = "Error adding results to devices tests table"
        logging.error(message, exc_info=e)
        return JSONResponse(status_code=404, content={"message":message})

@app.post("/tests/dns", responses ={**responses}, status_code=status.HTTP_201_CREATED)
def add_dns_test(request: Request, dns_test:schemas.DnsTest, test_base: schemas.TestBase = schemas.TestBase(), db: Session=Depends(get_db)):
    try:
        ip = request.client.host
        db_test_base = queries.create_test_base(db, test_base, ip)
        queries.create_specific_test(db, dns_test, models.DnsTest, db_test_base.id)
    except Exception as e:
        message = "Error adding results to dns tests table"
        logging.error(message, exc_info=e)
        return JSONResponse(status_code=404, content={"message":message})

@app.post("/tests/ooni/ndt", responses ={**responses}, status_code=status.HTTP_201_CREATED)
def add_ndt_test(request: Request, test:schemas.NdtTestOoni, test_base: schemas.TestBase = schemas.TestBase() ,db: Session=Depends(get_db)):
    try:
        ip = request.client.host
        db_test_base = queries.create_test_base(db, test_base, ip)
        queries.create_specific_test(db, test, models.NdtTestOoni, db_test_base.id)
    except Exception as e:
        message = "Error adding results to ndt tests table"
        logging.error(message, exc_info=e)
        return JSONResponse(status_code=404, content={"message":message})

@app.post("/tests/ooni/web", responses ={**responses}, status_code=status.HTTP_201_CREATED)
def add_web_test_ooni(request: Request, web_test_ooni:schemas.WebTestOoni, tcp_connect_web_tests_ooni: List[schemas.TcpConnectWebTestOoni], test_base: schemas.TestBase = schemas.TestBase(), db: Session=Depends(get_db)):
    try:
        ip = request.client.host
        db_test_base = queries.create_test_base(db, test_base, ip)
        db_web_test_ooni_id = queries.create_specific_test(db, web_test_ooni, models.WebTestOoni, db_test_base.id).id
        for tcp_connect in tcp_connect_web_tests_ooni:
            queries.create_specific_test(db, tcp_connect, models.TcpConnectWebTestOoni, db_web_test_ooni_id)
    except Exception as e:
        message = "Error adding results to web tests"
        logging.error(message, exc_info=e)
        return JSONResponse(status_code=404, content={"message":message})

@app.get("/tests", responses ={**responses})
def get_tests(request: Request, db: Session = Depends(get_db)):
    ip = request.client.host
    protocols_tests = queries.get_tests_with_list(db, ip, models.ProtocolTest)
    devices_tests = queries.get_devices_tests(db, ip)
    dns_tests =  queries.get_tests(db, ip, models.DnsTest)
    ndt_tests_oonni = queries.get_tests(db, ip, models.NdtTestOoni)
    web_tests_ooni = queries.get_ooni_web_tests(db, ip)
    return {
        "protocols_test":protocols_tests,
        "devices_test":devices_tests,
        "dns_tests":dns_tests,
        "ndt_tests_ooni":ndt_tests_oonni,
        "web_tests_ooni":web_tests_ooni
    }

    