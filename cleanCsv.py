import csv

import pandas

import replanPackages
from utils import utils

if __name__ == "__main__":
    fileName = "3385-reattempts-2024-01-10.csv"
    data = []
    date = "2024-01-10"
    hubName = "3385"

    with open(fileName, "r") as file:
        reader = csv.reader(file)

        for row in reader:
            if not str(row).startswith("C/O"):
                data.append(row)

    dataFrame = pandas.DataFrame(data)

    # print(dataFrame)

    barcodes = dataFrame[3]  # containers column

    env = utils.select_env()
    orgId = utils.select_org(env)
    pkgs = []
    barcodes = []

    replanPackages.main(
        env=env,
        orgId=orgId,
        keys=[barcodes[i] for i in range(1, len(barcodes))],
        keyType="bc",
        next_delivery_date=date,
        hubName=hubName,
    )
