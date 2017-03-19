import os
import re

"""Utility for reading Rightmove BLM files."""


def read(file_path: str) -> dict:
    """
    Parse a Rightmove BLM file and return its headers, definitions and data as a dictionary.

    :param file_path: The path to the BLM file.
    """

    if not os.path.isfile(file_path):
        raise FileNotFoundError("The file `%s` must exist and be a BLM file" % file_path)

    file_contents = open(file_path, 'r').read()
    headers = parse_headers(file_contents)
    definitions = parse_definitions(headers, file_contents)
    data = parse_data(headers, definitions, file_contents)

    return {'headers': headers, 'definitions': definitions, 'data': data}


def parse_headers(file_contents: str) -> dict:
    """
    Return a dictionary containing the BLM files headers.

    :param file_contents: The contents of the BLM file.

    :return: dict
    """

    match = re.search(r'#HEADER#(.*?)#', file_contents, re.MULTILINE | re.DOTALL)

    if match is None:
        raise Exception('No #HEADER# provided')

    headers = {}
    lines = match.group(1).split("\n")

    for line in lines:
        if line.strip() != '':
            parts = line.split(' : ')
            value = re.sub(r'(^[\'"]|[\'"]$)', '', parts[1].strip())
            headers[parts[0].strip()] = value

    return headers


def parse_definitions(headers: dict, file_contents: str) -> list:
    """
    Return a list containing the BLM files definitions.

    :param headers: A dictionary of headers.
    :param file_contents: The contents of the BLM file.

    :return: list
    """

    if not headers:
        raise Exception('Please set headers first')

    match = re.search(r'#DEFINITION#(.*?)#', file_contents, re.MULTILINE | re.DOTALL)

    if not match:
        raise Exception('No #DEFINITION# provided')

    definitions = list(map(str.strip, match.group(1).split(headers['EOF'])))

    if definitions[-1] == headers['EOR']:
        del definitions[-1]

    return definitions


def parse_data(headers: dict, definitions: list, file_contents: str) -> list:
    """
    Return a list containing the BLM files properties as dictionaries.

    :param headers: A dictionary of headers.
    :param definitions: A list of definitions.
    :param file_contents: The contents of the BLM file.

    :return: list
    """
    if not definitions:
        raise Exception('Please set definitions first')

    match = re.search(r'#DATA#(.*)#END#', file_contents, re.MULTILINE | re.DOTALL)

    if not match:
        raise Exception('No #DATA# provided (or no #END# defined)')

    data = []

    rows = list(map(str.strip, match.group(1).split(headers['EOR'])))

    for i, row in enumerate(rows):
        fields = list(map(str.strip, row.split(headers['EOF'])))

        if len(fields) > 1:
            data.append({})

            for k, field in enumerate(fields):
                if k < len(definitions):
                    data[i][definitions[k]] = field

    return data
