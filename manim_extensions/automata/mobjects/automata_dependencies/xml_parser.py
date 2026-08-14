import json
import xmltodict

def parse_xml_file(file_name: str) -> dict[str, object]:
    """Converts parses the xml from given file,
    then jsonify into a dictionary.

    Parameters
    ----------
    file_name
    The path to the target file.
    """
    with open(file_name,'rb') as f:
        return xmltodict.parse(f)