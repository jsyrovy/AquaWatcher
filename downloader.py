import dataclasses
import datetime
import json
import pathlib

import bs4
import requests

JSON_PATH = "downloader.json"
RAISE_AFTER_KEY = "raise_after"


@dataclasses.dataclass
class Record:
    pool: int
    aqua: int
    wellness: int
    dt: datetime.datetime = datetime.datetime.now()


def get_record() -> Record:
    r = requests.get("http://www.aquapce.cz")
    soup = bs4.BeautifulSoup(r.content, "html.parser")

    values = soup.find("div", class_="fast-info").find_all("span")
    assert len(values) == 3, f"Unexpected number of values: {len(values)}"

    record = Record(
        pool=int(values[0].text),
        aqua=int(values[1].text),
        wellness=int(values[2].text),
    )

    print(f"Data were downloaded: {record}")

    return record


def save_record(record: Record) -> None:
    path = pathlib.Path(
        f"data/{record.dt.year}/{record.dt:%m}/{record.dt:%Y-%m-%d}.csv"
    )

    if not path.parent.exists():
        path.parent.mkdir(parents=True)

    if not path.exists():
        path.write_text("dt,pool,aqua,wellness\n")

    with path.open("a") as f:
        f.write(
            f"{record.dt:%Y-%m-%d %H:%M:%S},"
            f"{record.pool},{record.aqua},{record.wellness}\n"
        )

    print(f"Data were saved: {path}")


def should_raise() -> bool:
    return get_raise_after() <= datetime.datetime.now()


def get_raise_after() -> datetime.datetime:
    try:
        with open(JSON_PATH) as f:
            return datetime.datetime.fromisoformat(json.load(f)[RAISE_AFTER_KEY])
    except FileNotFoundError:
        return datetime.datetime.max


def save_raise_after() -> None:
    with open(JSON_PATH, "w") as f:
        json.dump(
            {
                RAISE_AFTER_KEY: (
                    datetime.datetime.now() + datetime.timedelta(days=1)
                ).isoformat()
            },
            f,
            indent=4,
        )


if __name__ == "__main__":
    try:
        save_record(get_record())
    except Exception as e:
        if should_raise():
            save_raise_after()
            raise
        print(f"Error: {e}")
    else:
        save_raise_after()
