from datetime import datetime, timedelta, timezone
from typing import List

import polars as pl


def pre_filter(tickets: pl.DataFrame, account_name: str):
    if account_name == "Staples":
        tickets.with_columns(pl.col("Account").replace("Watco", "Staples"))


def filter_tickets(tickets: pl.DataFrame, account_name: str):
    pre_filter(tickets, account_name)

    return (
        tickets.with_columns(
            pl.col("State")
            .replace("Cancelled", "Solved")
            .replace("Close", "Solved")
            .replace("Resolved", "Solved")
            .replace("Open", "Active")
            .replace("Awaiting Info", "Pending"),
        )
        .filter(pl.col("Account") == account_name)
        .select(
            pl.col("Number"),
            pl.col("State"),
            pl.col("Contact").str.strip(),
            pl.col("Short Description").str.strip().replace("*", ""),
            pl.col("Opened"),
            pl.col("Updated"),
            pl.col("Assignment group"),
        )
        .sort(["State", "Number"])
        .rename({"Number": "Case Number"})
        .rename({"Contact": "Requester"})
        .rename({"Opened": "Opened At"})
        .rename({"Updated": "Last Updated At"})
    )


def merge_files(open_tickets_file: str, closed_tickets_file: str):
    # columns = ["Account","State","Assigned To","Number","Opened by","Contact","Short Description","Opened","Updated","Assignment group"]
    # report headers: ID (case number), Requester(contact), Short Description, Hub, Opened, Updated, Assignment Group

    # headers = ["ID", "Requester", "Short Description", "Hub", "Opened", "Updated", "Assignment Group"]

    # read the excel files
    open_tickets = pl.read_excel(open_tickets_file)
    closed_tickets = pl.read_excel(closed_tickets_file)

    # create a dataframe with all the tickets
    all_tickets = pl.concat([open_tickets, closed_tickets])

    return all_tickets


def main(
    open_tickets_file: str, closed_tickets_file: str, accounts: List[str], tz: int = -4
):
    today = datetime.now(timezone(timedelta(hours=tz)))

    all_tickets = merge_files(open_tickets_file, closed_tickets_file)

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
    main(
        open_tickets_file="Cases - All Open.xlsx",
        closed_tickets_file="Cases - All Closed.xlsx",
        accounts=["Staples", "Endeavour"],
    )
