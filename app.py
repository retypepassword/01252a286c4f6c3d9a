from flask import Flask, request
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from sqlalchemy import func, literal_column, select
from sqlalchemy.orm import Mapped, mapped_column
from geoalchemy2 import Geometry
from typing import TYPE_CHECKING, Final, Optional

app = Flask(__name__)
app.config[
    "SQLALCHEMY_DATABASE_URI"
] = "postgresql://postgres:password@db:5432/postgres"

db = SQLAlchemy(app)
migrate = Migrate(
    app,
    db,
    include_schemas=True,
    include_name=lambda name, type_, parent_names: name == "proposal"
    if type_ == "schema"
    else True,
)

METERS_TO_MILES: Final[float] = 0.0006213712

if TYPE_CHECKING:
    from sqlalchemy.orm import DeclarativeBase
    from flask_sqlalchemy.model import Model as FlaskModel

    class Model(DeclarativeBase, FlaskModel):
        pass

else:
    Model = db.Model


@app.get("/<zipcode>")
def zipcode_nearest(zipcode: str) -> str:
    zip: ZipCode | None = ZipCode.query.get(zipcode)
    if zip is None:
        return f"Zip {zipcode} was not found"

    rows = db.session.execute(
        select(
            Physician.name,
            Physician.city,
            func.ST_DistanceSphere(Physician.geom, zip.geom).label("distance"),
        )
        .limit(2)
        .order_by(func.ST_DistanceSphere(Physician.geom, zip.geom))
    ).all()
    return (
        (
            f"Your nearest physicians are: <ol>"
            f"<li>{rows[0].name} from {rows[0].city}, {round(rows[0].distance * METERS_TO_MILES, 1)} mi away</li>"
            f"<li>{rows[1].name} from {rows[1].city}, {round(rows[1].distance * METERS_TO_MILES, 1)} mi away</li>"
            f"</ol>"
        )
        if len(rows) >= 2 and rows[0] is not None and rows[1] is not None
        else "No physician found"
    )


@app.post("/physician")
def add_physician():
    if not request.is_json:
        return "Bad request", 400
    data = request.get_json()
    if "name" not in data or "address" not in data:
        return "Bad request; missing name or address", 400

    db.session.add(
        Physician(
            name=data["name"],
            address=data["address"],
            city=select(literal_column("(addy).location")).select_from(
                func.geocode(data["address"], 1)
            ),
            geom=select(func.st_transform(literal_column("geomout"), 4326)).select_from(
                func.geocode(data["address"], 1)
            ),
        )
    )
    db.session.commit()
    return f"Added {data['name']}"


class DefaultSchema:
    __table_args__ = {"schema": "proposal"}


class Physician(Model, DefaultSchema):
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str]
    address: Mapped[str]
    city: Mapped[Optional[str]]
    geom = mapped_column(Geometry(geometry_type="POINT", srid=4326))

    def __repr__(self) -> str:
        return f"{self.name}: {self.address}"


class ZipCode(Model, DefaultSchema):
    zip: Mapped[str] = mapped_column(primary_key=True)
    latitude: Mapped[float]
    longitude: Mapped[float]
    geom = mapped_column(Geometry(geometry_type="POINT", srid=4326))

    def __repr__(self) -> str:
        return f"{self.zip}: {self.latitude}, {self.longitude}"
