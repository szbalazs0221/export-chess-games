import calendar
from pathlib import Path
import re
import requests
import os

from datetime import datetime, timezone
from chessdotcom import ChessDotComClient

DOWNLOADS_PATH = downloads_path = str(Path.home() / "Downloads")
LICHESS_API_KEY = os.environ.get("LICHESS_API_KEY")
USERNAME = "balaggio"
HUMAN_READABLE_FORMAT = "%Y %m %d"
YEAR = int(os.environ.get("YEAR_TO_USE"))
MONTH = int(os.environ.get("MONTH_TO_USE"))
TIME_CONTROL_MAP = {
    "Blitz": ["180+2", "180", "300"],
    "Rapid": ["600+0", "900"],
    "Classical": ["1800"],
}


def figure_out_date_params():
    # current_month = datetime.now().month
    current_month = 8
    last_day_number_for_month = calendar.monthrange(YEAR, current_month)[1]
    first_day_of_month = datetime(
        year=YEAR, month=current_month, day=1, tzinfo=timezone.utc
    )
    last_day_of_month = datetime(
        year=YEAR,
        month=current_month,
        day=last_day_number_for_month,
        hour=23,
        minute=59,
        second=59,
        tzinfo=timezone.utc,
    )
    first_day_as_unix_ts = int(first_day_of_month.timestamp() * 1000)
    last_day_as_unix_ts = int(last_day_of_month.timestamp() * 1000)
    print(
        f"From date: {first_day_of_month.strftime('%Y %m %d')} to {last_day_of_month.strftime('%Y %m %d')}"
    )

    return first_day_as_unix_ts, last_day_as_unix_ts


def export_lichess_games():
    print(f"Exporting lichess games for {YEAR} {MONTH}")
    from_date, to_date = figure_out_date_params()

    url = f"https://lichess.org/api/games/user/{USERNAME}"
    headers = {
        "Authorization": f"Bearer {LICHESS_API_KEY}",
    }
    params = {
        "clocks": True,
        "since": from_date,
        "until": to_date,
        "rated": "true",
    }

    response = requests.get(url, headers=headers, params=params)
    pgns = response.text
    if response.status_code == 200:
        with open(
            f"{DOWNLOADS_PATH}/{YEAR}_{MONTH}_lichess_games.pgn", "w", encoding="utf-8"
        ) as file:
            file.write(add_custom_tag_to_games(pgns))
            print("Games exported successfully.")
    else:
        print(f"Failed to export games: {response.status_code}")


def export_chess_com_games():
    print(f"Export chess.com games for {YEAR} {MONTH}")
    client = ChessDotComClient(user_agent="Export app")
    response = client.get_player_games_by_month_pgn(
        username=USERNAME, year=YEAR, month=9
    )
    print(response)
    final_data = add_custom_tag_to_games(response.pgn.data)
    with open(
        f"{DOWNLOADS_PATH}/{YEAR}_{MONTH}_chess_com_games.pgn", "w", encoding="utf-8"
    ) as file:
        file.write(final_data)
    print("Games exported successfully.")


def add_custom_tag_to_games(pgns: str):
    # separate the pgn by the linebreaks first
    pgn_parts = pgns.splitlines()
    result = []
    for part in pgn_parts:
        result.append(part)
        if "[TimeControl" in part:
            # figure out the timecontrol
            match = re.search('"\d*(\+\d*)?"', part)
            indexes = match.span()
            time_control_string = part[indexes[0] + 1 : indexes[1] - 1]
            print(f"Found {time_control_string = } in {part}")
            time_control_type = get_time_control_type_by_value(time_control_string)
            result.append(f'[Type "{time_control_type}"]')
    return "\n".join(result)


def get_time_control_type_by_value(time_control_string: str):
    for time_control_type in TIME_CONTROL_MAP.keys():
        if time_control_string in TIME_CONTROL_MAP[time_control_type]:
            print(f"Found time control type for {time_control_string}")
            return time_control_type
    raise Exception(f"Doesn't have a type for {time_control_string =}")


if __name__ == "__main__":
    export_lichess_games()
    export_chess_com_games()
