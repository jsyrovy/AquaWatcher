import calendar
import dataclasses
import datetime
import pathlib
import sqlite3
import typing

import jinja2
import pandas


@dataclasses.dataclass
class Day:
    number: int
    name: str
    is_day_of_week: bool


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
        publish_global(conn)
        publish_current_month(conn)


def load_files(conn: sqlite3.Connection) -> None:
    paths = list(pathlib.Path("data").rglob("**/*.csv"))

    for path in paths:
        load_csv(conn, path)

    print(f"Files were loaded: {len(paths)}")


def load_csv(conn: sqlite3.Connection, path: pathlib.Path) -> None:
    df = pandas.read_csv(path, sep=",")
    df.to_sql("data", conn, if_exists="append")


def publish_global(conn: sqlite3.Connection) -> None:
    days = [Day(1, "Pondělí", is_day_of_week=True),
            Day(2, "Úterý", is_day_of_week=True),
            Day(3, "Středa", is_day_of_week=True),
            Day(4, "Čtvrtek", is_day_of_week=True),
            Day(5, "Pátek", is_day_of_week=True),
            Day(6, "Sobota", is_day_of_week=True),
            Day(0, "Neděle", is_day_of_week=True)]
    publish_page("index.html", get_charts(conn.cursor(), days))


def get_charts(cursor: sqlite3.Cursor, days: typing.List[Day]) -> typing.List[Chart]:
    charts = []

    for day in days:
        records = get_records(cursor, day)
        charts.append(get_chart(cursor, records, day))

    print("Data were selected.")
    return charts


def get_records(cursor: sqlite3.Cursor, day: Day) -> typing.List[Record]:
    if day.is_day_of_week:
        cursor.execute("SELECT strftime('%H', dt), round(avg(pool), 0), round(avg(aqua), 0), round(avg(wellness), 0) "
                       "FROM data "
                       f"WHERE strftime('%w', dt) = '{day.number}'"
                       "GROUP BY strftime('%H', dt) "
                       "ORDER BY strftime('%H', dt)")
    else:
        cursor.execute("SELECT strftime('%H', dt), round(avg(pool), 0), round(avg(aqua), 0), round(avg(wellness), 0) "
                       "FROM data "
                       f"WHERE strftime('%Y-%m-%d', dt) = '{day.name}'"
                       "GROUP BY strftime('%H', dt) "
                       "ORDER BY strftime('%H', dt)")
    return [Record(int(r[0]), int(r[1]), int(r[2]), int(r[3])) for r in cursor.fetchall()]


def get_chart(cursor: sqlite3.Cursor, records: typing.List[Record], day: Day) -> Chart:
    return Chart(day=day,
                 days=get_days_count(cursor, day),
                 labels=str([r.hour for r in records]),
                 serie_pool=str([r.pool for r in records]),
                 serie_aqua=str([r.aqua for r in records]),
                 serie_wellness=str([r.wellness for r in records]))


def get_days_count(cursor: sqlite3.Cursor, day: Day) -> int:
    cursor.execute(f"SELECT DISTINCT date(dt) FROM data WHERE strftime('%w', dt) = '{day.number}'")
    return len(cursor.fetchall())


def publish_page(path: str, charts: typing.List[Chart]) -> None:
    page = pathlib.Path(path)

    if not page.parent.exists():
        page.parent.mkdir(parents=True)

    page.write_text(get_template().render(charts=charts, dt=datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")),
                    "UTF-8")
    print(f"Page was published: {page}")


def get_template() -> jinja2.Template:
    env = jinja2.Environment(
        loader=jinja2.PackageLoader("publisher", "templates"),
        autoescape=jinja2.select_autoescape(["html", "xml"])
    )
    return env.get_template("index.html")


def publish_current_month(conn: sqlite3.Connection) -> None:
    publish_month(conn, datetime.date.today())


def publish_month(conn: sqlite3.Connection, month_last_day: datetime.date) -> None:
    publish_page(f"pages/{month_last_day:%Y/%m/%Y-%m}.html",
                 get_charts(conn.cursor(), get_month_days(month_last_day)))


def get_month_days(month_last_day: datetime.date) -> typing.List[Day]:
    days = []

    for day in range(1, month_last_day.day + 1):
        days.append(Day(day, f"{month_last_day:%Y-%m}-{day:02d}", is_day_of_week=False))

    return days


def publish_passed_month(conn: sqlite3.Connection, year: int, month: int) -> None:
    last_day = datetime.date(year, month, calendar.monthrange(year, month)[1])
    publish_month(conn, last_day)


if __name__ == "__main__":
    main()
