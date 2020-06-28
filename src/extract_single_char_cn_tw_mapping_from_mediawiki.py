#!/usr/bin/env python3

import csv
import enum
import re
import sys
from typing import Any, Dict, List

import argparse

class ParseMode(enum.Enum):
    HEADER = 1
    ZH2HANT = 2
    ZH2HANS = 3
    ZH2TW = 4
    ZH2HK = 5
    ZH2CN = 6


SECTIONS = {
    ParseMode.ZH2HANT: (re.compile('zh2Hant'), dict()),
    ParseMode.ZH2HANS: (re.compile('zh2Hans'), dict()),
    ParseMode.ZH2TW: (re.compile('zh2TW'), dict()),
    ParseMode.ZH2HK: (re.compile('zh2HK'), dict()),
    ParseMode.ZH2CN: (re.compile('zh2CN'), dict()),
}

SINGLE_CHAR_PATTERN = re.compile("'([^'])'\s*=>\s*'([^'])'", re.UNICODE)
MULTI_CHAR_PATTERN = re.compile("'([^']+)'\s*=>\s*'([^']+)'", re.UNICODE)


def extract_mode(line: str) -> Tuple[ParseMode, Dict[str, Any]]:
    for mode, (pattern, section_dict) in SECTION.items():
        match = pattern.search(line)
        if match:
            return mode, section_dict
    return ParseMode.HEADER, {}


def read_mapping(filename: str) -> None:
    parse_mode, section_dict = ParseMode.HEADER, {}
    for line in open(filename):
        if line.startswith('public static'):
            parse_mode, section_dict = extract_mode(line)
            continue
        match = MULTI_CHAR_PATTERN.search(line)
        if not match:
            continue
        key, value = match.groups()
        section_dict.get(key, set()).add(value)


def print_mapping():
    for mode, (_, section_dict) in SECTIONS.items():
        print(f'Mode {mode}')
        for index, (key, value) in enumerate(section_dict.items()):
            if index >= 10:
                break
            print(f'{key}: {value}')


def extract(filename: str):
    section_dicts = read_mapping(filename)
    writer = csv.writer(sys.stdout)
    writer.writerow(['TW', 'CN'])
    seen = dict()  # str -> set()
    tw_first = False  # The leading entries in ZhConversion.php is CN => TW
    for line in open(filename):
        match = ZH_TO_HANS_PATTERN.search(line)
        if not match:
            continue
        if tw_first:
            tw, cn = match.group(1), match.group(2)
        else:
            cn, tw = match.group(1), match.group(2)
        if cn in seen:  # reversed
            tw, cn = cn, tw
            tw_first = not tw_first
        cn_set = seen.get(tw, set())
        if cn not in cn_set:
            writer.writerow([tw, cn])
        cn_set.add(cn)


if __name__ == '__main__':
    read_mapping(sys.argv[1])
    print_mapping()
    # extract(sys.argv[1])
