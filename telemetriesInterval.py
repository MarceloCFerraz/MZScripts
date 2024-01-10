# https://stackoverflow.com/questions/127803/how-do-i-parse-an-iso-8601-formatted-date
# https://stackoverflow.com/questions/1345827/how-do-i-find-the-time-difference-between-two-datetime-objects-in-python
from utils import associates, utils
from dateutil import parser


def calculate_telemetries_interval(telemetries):
    """
    Calculate time intervals with a difference greater than 5 minutes within a list of telemetries.

    Parameters:
    - telemetries: A list of telemetry events.

    Returns:
    None
    """
    count = 0

    previous_stamp = parser.isoparse(  # python 3.6
        str(telemetries[0]["timestamp"])
    )

    for telemetry in telemetries:
        timestamp = parser.isoparse(  # python 3.6
            str(telemetry["timestamp"])
        )

        dif = timestamp - previous_stamp
        total_seconds = dif.total_seconds()

        if (
            total_seconds > 300
        ):  # get only stamps with difference greater than 5 minutes
            count += 1
            print(
                f">> {previous_stamp.date()} {previous_stamp.time()} - {timestamp.date()} {timestamp.time()} ({dif})"
            )

        previous_stamp = timestamp
    if count == 0:
        print(
            "\nNo difference greater than 5 minutes was found in the reported interval!"
        )


def main(env, orgId, associateId, startTime, endTime):
    """
    The main function that retrieves telemetries and searches for time intervals with a difference greater than 5 minutes.

    Parameters:
    - env: The environment.
    - orgId: The ID of the organization.
    - associateId: The ID of the associate.
    - startTime: The start time of the telemetry range.
    - endTime: The end time of the telemetry range.

    Returns:
    None
    """
    telemetries = associates.get_telemetries(
        env, orgId, associateId, startTime, endTime
    )

    print("> Calculating telemetries interval")

    calculate_telemetries_interval(telemetries)


env = utils.select_env()
orgId = utils.select_org(env)

associateId = input("Insert associateId: ")

startTime = str(input("Insert startTime (zulu format -> yyyy-mm-ddTHH:mm:ssZ): "))
endTime = str(input("Insert endTime (zulu format -> yyyy-mm-ddTHH:mm:ssZ): "))

main(env, orgId, associateId, startTime, endTime)
