import dataclasses
import datetime
import pathlib
import sqlite3
import sys
import typing

import jinja2
import pandas

INDEX_TEMPLATE = "index.html"


@dataclasses.dataclass
class Day:
    number: int
    name: str


@dataclasses.dataclass
class Record:
    hour: int
    pool: int
    aqua: int
    wellness: int


@dataclasses.dataclass
class Chart:
    day: Day
    days: int
    labels: str
    serie_pool: str
    serie_aqua: str
    serie_wellness: str


def main() -> None:
    with sqlite3.connect(":memory:") as conn:
        load_files(conn)
        publish_page(get_charts(conn.cursor()))


def load_files(conn: sqlite3.Connection) -> None:
    paths = list(pathlib.Path("data").rglob("**/*.csv"))

    for path in paths:
        load_csv(conn, path)

    print(f"Files were loaded: {len(paths)}")


def load_csv(conn: sqlite3.Connection, path: pathlib.Path) -> None:
    df = pandas.read_csv(path, sep=",")
    df.to_sql("data", conn, if_exists="append")


def get_charts(cursor: sqlite3.Cursor) -> typing.List[Chart]:
    charts = []
    days = [Day(1, "Pondělí"),
            Day(2, "Úterý"),
            Day(3, "Středa"),
            Day(4, "Čtvrtek"),
            Day(5, "Pátek"),
            Day(6, "Sobota"),
            Day(0, "Neděle")]

    date_from = get_date_from()

    if date_from:
        print(f"Date filter from: {date_from:%Y-%m-%d}")

    for day in days:
        records = get_records(cursor, day, date_from)
        charts.append(get_chart(cursor, records, day, date_from))

    print("Data were selected.")
    return charts


def get_date_from() -> typing.Optional[datetime.datetime]:
    if len(sys.argv) == 1:
        return None

    return datetime.datetime.strptime(sys.argv[1], "%Y-%m-%d")


def get_records(cursor: sqlite3.Cursor, day: Day, date_from: datetime.datetime) -> typing.List[Record]:
    cursor.execute("SELECT strftime('%H', dt), round(avg(pool), 0), round(avg(aqua), 0), round(avg(wellness), 0) "
                   "FROM data "
                   f"WHERE strftime('%w', dt) = '{day.number}'{get_date_filter(date_from)}"
                   "GROUP BY strftime('%H', dt) "
                   "ORDER BY strftime('%H', dt)")
    return [Record(int(r[0]), int(r[1]), int(r[2]), int(r[3])) for r in cursor.fetchall()]


def get_date_filter(date_from: datetime.datetime) -> str:
    return f" AND strftime('%Y-%m-%d', dt) >= '{date_from:%Y-%m-%d}'" if date_from else ""


def get_chart(cursor: sqlite3.Cursor, records: typing.List[Record], day: Day, date_from: datetime.datetime) -> Chart:
    return Chart(day=day,
                 days=get_days_count(cursor, day, date_from),
                 labels=str([r.hour for r in records]),
                 serie_pool=str([r.pool for r in records]),
                 serie_aqua=str([r.aqua for r in records]),
                 serie_wellness=str([r.wellness for r in records]))


def get_days_count(cursor: sqlite3.Cursor, day: Day, date_from: datetime.datetime) -> int:
    cursor.execute(f"SELECT DISTINCT date(dt) FROM data "
                   f"WHERE strftime('%w', dt) = '{day.number}'{get_date_filter(date_from)}")
    return len(cursor.fetchall())


def publish_page(charts: typing.List[Chart]) -> None:
    page = pathlib.Path(get_file_name())
    page.write_text(get_template().render(charts=charts, dt=datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")),
                    "UTF-8")
    print(f"Page was published: {page}")


def get_file_name() -> str:
    if len(sys.argv) == 1:
        return "index.html"

    return sys.argv[2]


def get_template() -> jinja2.Template:
    env = jinja2.Environment(
        loader=jinja2.FileSystemLoader("templates"),
        autoescape=jinja2.select_autoescape(["html", "xml"])
    )
    return env.get_template(INDEX_TEMPLATE)


if __name__ == "__main__":
    main()
