#!/usr/bin/env python3

"""Extracts various mappings of Han characters / words from the
ZhConversion.php file of mediawiki.

The current version only extracts the hant-to-hans mapping.
TODO(pingooo): extract (CN, TW) and (CN, HK) word mappings from the same file.

To run this script:
$ ./extract_mappings_from_mediawiki.py path_to_ZhConversion.php > ../hant_hans.csv
"""

import csv
import enum
import re
import sys
from typing import Any, Dict, Set, Tuple

class SectionName(enum.Enum):
    """The sections of input file."""
    HEADER = 1
    ZH2HANT = 2
    ZH2HANS = 3
    ZH2TW = 4
    ZH2HK = 5
    ZH2CN = 6

SectionDictType = Dict[str, Set[str]]
SectionDataType = Dict[SectionName, Tuple[Any, SectionDictType]]
SINGLE_CHAR_PATTERN = re.compile("'([^'])'\s*=>\s*'([^'])'", re.UNICODE)
MULTI_CHAR_PATTERN = re.compile("'([^']+)'\s*=>\s*'([^']+)'", re.UNICODE)


def get_section(line: str, section_data: SectionDataType) -> SectionDictType:
    """Returns the section dict for the section starting with the input line."""
    for _, (pattern, section_dict) in section_data.items():
        if pattern.search(line):
            return section_dict
    return {}


def read_mapping(filename: str) -> SectionDataType:
    """Reads all mappings in the mediawiki data file."""
    section_data = {
        SectionName.ZH2HANT: (re.compile('zh2Hant'), dict()),
        SectionName.ZH2HANS: (re.compile('zh2Hans'), dict()),
        SectionName.ZH2TW: (re.compile('zh2TW'), dict()),
        SectionName.ZH2HK: (re.compile('zh2HK'), dict()),
        SectionName.ZH2CN: (re.compile('zh2CN'), dict()),
    }
    section_dict = {}
    for line in open(filename):
        if line.startswith('public static'):
            section_dict = get_section(line, section_data)
            continue
        match = MULTI_CHAR_PATTERN.search(line)
        if not match:
            continue
        key, value = match.groups()
        if key in section_dict:
            section_dict[key].add(value)
        else:
            section_dict[key] = set([value])
    return section_data


def extract_hant_to_hans_map(section_dict: SectionDictType) -> Dict[str, str]:
    """Returns a map of single character hant to hans."""
    single_char_map = dict()
    for hant, hans_set in section_dict.items():
        if len(hant) > 1:  # Ignore hant longer than 1 character.
            continue
        if len(hans_set) > 1:
            raise ValueError(f'Too many hans {hans_set} for hant {hant}')
        single_char_map[hant] = next(iter(hans_set))
    return single_char_map


def write_hant_to_hans_map(ts_map: Dict[str, str]) -> None:
    """Writes the single character hant-to-hans map to stdout as a CSV."""
    writer = csv.writer(sys.stdout)
    writer.writerow(['hant', 'hans'])
    for hant, hans in ts_map.items():
        writer.writerow([hant, hans])


if __name__ == '__main__':
    section_data = read_mapping(sys.argv[1])
    hant_to_hans_map = extract_hant_to_hans_map(section_data[SectionName.ZH2HANS][1])
    write_hant_to_hans_map(hant_to_hans_map)
