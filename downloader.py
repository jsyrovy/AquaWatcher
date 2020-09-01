import dataclasses
import datetime
import pathlib

import bs4
import requests


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
    record = Record(pool=int(values[0].text), aqua=int(values[1].text), wellness=int(values[2].text))
    print(f"Data was downloaded: {record}")

    return record


def save_record(record: Record) -> None:
    path = pathlib.Path(f"data/{record.dt.year}/{record.dt:%m}/{record.dt:%Y-%m-%d}.csv")

    if not path.exists():
        path.parent.mkdir(parents=True)
        path.write_text("dt,pool,aqua,wellness\n")

    with path.open("a") as f:
        f.write(f"{record.dt:%Y-%m-%d %H:%M:%S},{record.pool},{record.aqua},{record.wellness}\n")

    print(f"Data was saved: {path}")


if __name__ == "__main__":
    save_record(get_record())
