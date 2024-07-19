from datetime import datetime, timedelta, timezone
from typing import List

import polars as pl


def unify_account_names(tickets: pl.DataFrame, account_name: str):
    if account_name == "Staples":
        tickets = tickets.with_columns(
            pl.col("Account").str.replace("Watco", account_name)
        )

    if account_name == "Endeavour":
        tickets = tickets.with_columns(
            pl.col("Account").str.replace("EDG", account_name)
        )

    if account_name == "ShopRite":
        tickets = tickets.with_columns(
            pl.col("Account")
            .replace("Lowes Foods", account_name)
            .replace("Cub", account_name)
            .replace("Capstone Logistics", account_name)
        )

    return tickets


def filter_tickets(
    tickets: pl.DataFrame, account_name: str, use_opened_by: bool = True
):
    tickets = (
        unify_account_names(tickets, account_name)
        .with_columns(
            pl.lit("").alias("Reason"),
            pl.col("State")
            .replace("Closed", "Solved")
            .replace("Cancelled", "Solved")
            .replace("Close", "Solved")
            .replace("Resolved", "Solved")
            .replace("Reopen", "Active")
            .replace("New", "Active")
            .replace("Open", "Active")
            .replace("On Hold", "Pending")
            .replace("Awaiting Info", "Pending"),
        )
        .filter(pl.col("Account") == account_name)
        .select(
            pl.col("Number"),
            pl.col("State"),
            pl.col("Contact").str.strip_chars(),
            pl.col("Short Description").str.strip_chars().replace("*", ""),
            pl.col("Opened"),
            pl.col("Updated"),
            pl.col("Assignment group"),
            pl.col("Reason"),
        )
        .sort(["State", "Number"])
        .rename({"Number": "Case Number"})
        .rename({"Contact": "Requester"})
        .rename({"Opened": "Opened At"})
        .rename({"Updated": "Last Updated At"})
        .with_columns()
    )

    return tickets


def read_excel(file_name: str) -> pl.DataFrame:
    try:
        df = pl.read_excel(file_name)
    except Exception:
        print(f"Error reading '{file_name}'")
        return pl.DataFrame()

    return df


def merge_files(
    open_cases_file: str,
    open_incidents_file: str,
    closed_cases_file: str,
    closed_incidents_file: str,
):
    # read excel files
    open_cases = read_excel(open_cases_file)
    open_incidents = read_excel(open_incidents_file)
    closed_cases = read_excel(closed_cases_file)
    closed_incidents = read_excel(closed_incidents_file)

    valid_tickets = []

    if not open_cases.is_empty():
        valid_tickets.append(open_cases)

    if not closed_cases.is_empty():
        valid_tickets.append(closed_cases)

    if not open_incidents.is_empty():
        valid_tickets.append(
            open_incidents.rename({"Company": "Account", "Caller": "Contact"})
        )

    if not closed_incidents.is_empty():
        valid_tickets.append(
            closed_incidents.rename({"Company": "Account", "Caller": "Contact"})
        )

    # create a dataframe with all the tickets
    all_tickets = pl.concat(valid_tickets)

    return all_tickets


def main(
    open_cases_file: str,
    open_incidents_file: str,
    closed_cases_file: str,
    closed_incidents_file: str,
    accounts: List[str],
    tz: int = -4,
):
    today = datetime.now(timezone(timedelta(hours=tz)))

    all_tickets = merge_files(
        open_cases_file, open_incidents_file, closed_cases_file, closed_incidents_file
    )

    if all_tickets.is_empty():
        print("No tickets found")
        return

    for account_name in accounts:
        filtered_tickets = filter_tickets(all_tickets, account_name)

        # print(filtered_tickets)
        filtered_tickets.write_excel(
            f"{account_name} Report - {today.strftime('%b %d')}.xlsx",
        )


if __name__ == "__main__":
    start = datetime.now()
    main(
        open_cases_file="Cases - All Open.xlsx",
        open_incidents_file="Incidents - All Open.xlsx",
        closed_cases_file="Cases - All Closed.xlsx",
        closed_incidents_file="Incidents - All Closed.xlsx",
        accounts=["Staples", "Endeavour"],  # , "Harvey Norman", "ShopRite"],
    )
    end = datetime.now()
    print(f"Time taken: {end - start}")
