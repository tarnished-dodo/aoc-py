import importlib
import os
import re
from re import Pattern

import click
from click import Context, Parameter


def extract_group_values_from_filenames(dir_content: list[str], pattern: Pattern, group_name: str) -> list[int]:
    matches = []

    for item in dir_content:
        match = pattern.search(item)
        if match:
            matches.append(int(match.group(group_name)))

    return matches


def get_available_years() -> list[int]:
    dir_content = os.listdir("src/aoc_py/")
    year_pattern = re.compile(r"year_(?P<year>\d+)")

    return extract_group_values_from_filenames(dir_content, year_pattern, "year")


def get_available_days(year: int) -> list[int]:
    dir_content = os.listdir(f"src/aoc_py/year_{year}/")
    day_pattern = re.compile(r"day_(?P<day>\d+)")

    return extract_group_values_from_filenames(dir_content, day_pattern, "day")


def validate_day(ctx: Context, _param: Parameter, value: int | None) -> int | None:
    year = ctx.params.get("year")
    if year is None:
        return value

    valid_days = get_available_days(year)

    if value not in valid_days:
        raise click.BadParameter(
            f"Day {value} not available for year {year}. Valid: {', '.join(str(d) for d in valid_days)}"
        )

    return value


@click.command()
@click.version_option()
@click.option(
    "--year",
    type=click.Choice(get_available_years()),
    required=True,
    help="Year of the Advent of Code to run. Must match a folder under src/aoc_py/.",
)
@click.option(
    "--day",
    type=int,
    callback=validate_day,
    required=True,
    help="Day of the Advent of Code to run. Must exist for the selected year.",
)
@click.option("--part", type=click.Choice([1, 2]), default=1, help="Part of the day to run (1 or 2). Defaults to 1.")
def menu(year: int, day: int, part: int) -> None:
    module = importlib.import_module(f"aoc_py.year_{year}.day_{day:02d}")
    try:
        func = getattr(module, f"part_{part}")
    except AttributeError as err:
        part_param = next(p for p in click.get_current_context().command.params if p.name == "part")
        raise click.BadParameter(f"Day {day} of year {year} does not have part {part}", param=part_param) from err

    func()


if __name__ == "__main__":
    menu()
