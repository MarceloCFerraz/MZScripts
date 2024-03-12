import re
import xml.etree.ElementTree as ET


def extract_and_clean_ids(file_path):
    """Reads a text file, extracts lines starting with 'scannableId',
    removes the ID numbers, and returns a list of clean lines.
    """

    scannable_ids = []
    with open(file_path, "r") as file:
        for line in file:
            if line.startswith('"scannableId":'):
                # Extract the ID number using a regular expression
                id_match = re.search(r'"scannableId": "(\d+)"', line)
                if id_match:
                    clean_line = line.replace(r'"scannableId": "', "").replace(
                        '",\n', ""
                    )  # Remove the ID portion
                    scannable_ids.append(clean_line)

    return scannable_ids


def extract_and_save_docbols(
    xml_file_path, scannable_ids, new_file_path, comment_addition="retry"
):
    """Extracts DocBOL elements, updates comments, and saves them to a new XML file,
    ensuring only one scannable ID from the list is included per DocBOL.
    """

    tree = ET.parse(xml_file_path)
    modified_docbols = []

    for doc_fw_import in tree.findall(".//DocFWImport"):
        for request in doc_fw_import.findall("Request"):
            for doc_master_bol in request.findall("DocMasterBOL"):
                for doc_bol in doc_master_bol.findall("DocBOL"):
                    scannable_id_found = (
                        False  # Track if a matching scannable ID was found
                    )

                    for bol_line in doc_bol.findall("BOLLine"):
                        if (
                            scannable_id_found
                        ):  # Skip processing if an ID was already found
                            break

                        if (
                            bol_line.attrib.get("ProductKey") in scannable_ids
                            or bol_line.find("UDF").attrib.get("UDFString1")
                            in scannable_ids
                        ):
                            # Found a match
                            scannable_id_found = True
                            pickup_location = doc_bol.find("PickupLocation")
                            if pickup_location is not None:
                                old_comment = pickup_location.attrib.get("Comment", "")
                                new_comment = old_comment + " " + comment_addition
                                pickup_location.attrib["Comment"] = new_comment
                            modified_docbols.append(doc_fw_import)
                            break  # Stop checking BOLLines within this DocBOL

    # Save modified DocBOLs directly
    with open(new_file_path, "w") as output_file:
        output_file.write('<?xml version="1.0"?>\n')
        output_file.write(
            '<Root xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns:xsd="http://www.w3.org/2001/XMLSchema">\n'
        )
        for doc_bol in modified_docbols:
            output_file.write(ET.tostring(doc_bol, encoding="unicode"))
        output_file.write("</Root>")


if __name__ == "__main__":
    # you still need to get which orders failed manually. To do so, I recommend
    # going to Orders page,
    # open the failed/partial file page,
    # open network tab,
    # search for the request `request?requestId=058cf377-48e6-43e9-82c9-9c21e32f674a`
    # open the `response`
    # use a regex like this to get all lines that failed: refId.*\n(.*\n){17}.*status": "FAILED"
    text_file_name = "failed_edg_orders.txt"
    # you'll need to download this file in: https://s3.console.aws.amazon.com/s3/buckets/sftpgateway-i-0465216ee091572f6?region=us-west-2&bucketType=general&prefix=edg/uploads/done/&showversions=false
    # Make your life easier by getting the correct file name in the orders page (MV). Just remember to change from upper case to the format below
    xml_file_name = "DocFWImportBatch_NEXD_NXS_Eden_20242902120703.xml"
    # name this however you want. I recommend putting this file in another folder and naming it with the original file name
    new_xml_file_name = "modified_docbols.xml"

    # Get scannable IDs from the text file
    scannable_ids = extract_and_clean_ids(text_file_name)

    # Process the XML file and save the results
    extract_and_save_docbols(xml_file_name, scannable_ids, new_xml_file_name)
