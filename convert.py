import pandas

fileName = "2023-07-24_loadscanReport.csv"
data = pandas.read_csv(fileName, sep=",", encoding="ANSI")

excelFile = fileName.replace(".csv", ".xlsx")
writer = pandas.ExcelWriter(excelFile, engine="xlsxwriter")

dtype_dict = {"ORDER": "str", "CONTAINER": "str", "POSTAL": "str"}

for i in range(len(data)):
    item = data.at[i, "ORDER"]  # Convert the value to a string
    if pandas.notna(item):
        print(f"ORDER -> {item}")
        data.at[i, "ORDER"] = repr(item)  # Update the value in the DataFrame

for i in range(len(data)):
    item = data.at[i, "CONTAINER"]  # Convert the value to a string
    print(f"CONTAINER -> {item}")
    if pandas.notna(item):
        data.at[i, "CONTAINER"] = repr(item)  # Update the value in the DataFrame

for i in range(len(data)):
    item = data.at[i, "POSTAL"]  # Convert the value to a string
    if pandas.notna(item):
        print(f"POSTAL -> {item}")
        data.at[i, "POSTAL"] = repr(item)  # Update the value in the DataFrame

data.to_excel(writer, sheet_name="All Data", index=False, encoding="ANSI")
