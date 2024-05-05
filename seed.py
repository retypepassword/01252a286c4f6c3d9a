from typing import Dict, TypedDict
from app import app, db, Physician, ZipCode
from sqlalchemy import insert, text
import csv, itertools

with app.app_context():

    Physician.query.delete()
    ZipCode.query.delete()

    physicians = []
    physicians.append(Physician(name = "Dr. Francis", address = "123 Main St, San Francisco, CA"))
    physicians.append(Physician(name = "Dr. Oak", address = "123 Market St, Oakland, CA"))
    physicians.append(Physician(name = "Dr. Yi", address = "123 N Main St, Yreka, CA"))
    
    Zip = TypedDict('Zip', { 'zip': str, 'latitude': str, 'longitude': str })
    zipcodes: list[Zip] = []
    with open('US.txt') as csvfile:
        reader = csv.DictReader(csvfile, delimiter="\t", fieldnames=["country","zip","place name", "admin name 1", "admin code 1", "admin name 2", "admin code 2", "admin name 3", "admin code 3", "latitude", "longitude", "accuracy"])
        for row in reader:
            zipcodes.append({ "zip": row['zip'], "latitude": row['latitude'], "longitude": row['longitude'] })

    key = lambda x: x["zip"]
    deduped_zips: list[Zip] = [next(g) for _, g in itertools.groupby(sorted(zipcodes, key = key), key = key)]
    db.session.add_all(physicians)
    db.session.execute(insert(ZipCode), deduped_zips)
    db.session.execute(text("UPDATE proposal.zip_code z SET geom = geography('point(' || z.longitude || ' ' || z.latitude || ')')::geometry"))
    db.session.execute(text("UPDATE proposal.physician physician SET geom = ST_TRANSFORM(geoms.geomout, 4326), city = (geoms.addy).location FROM (select p.id, g.* FROM proposal.physician p CROSS JOIN geocode(p.address, 1) g) geoms WHERE geoms.id = physician.id"))
    db.session.commit()
