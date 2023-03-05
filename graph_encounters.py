#!/usr/bin/env python3
import os
import yaml
import logging
import textwrap
import argparse
import pygraphviz as pgv
import matplotlib.pyplot as plt
from shutil import get_terminal_size
from main import load_encounter

logging.basicConfig()
logger = logging.getLogger("root")
logger.setLevel("INFO")

DATADIR = "data"
ENCOUNTERS = "encounters"
ENCOUNTER_PATH = os.path.join(".", DATADIR, ENCOUNTERS)
EXPORT_PATH = os.path.join(".", "exports")
EXPORT_PDF = False
EXPORT_PNG = False


def find_encounter_files(path):
    encounter_files = os.listdir(path)
    return [x for x in encounter_files if x.endswith(".yaml")]


def main(encounter="preface"):
    G = pgv.AGraph(strict=False, directed=True)

    encounter_files = find_encounter_files(ENCOUNTER_PATH)

    for encounter_file in encounter_files:
        encounter_name = os.path.splitext(encounter_file)[0]
        G.add_node(encounter_name)
        encounter_filename = os.path.join(ENCOUNTER_PATH, encounter_file)
        encounter = load_encounter(encounter_filename)
        if encounter:
            reactions = encounter.get("reactions")
            if reactions:
                for reaction in reactions:
                    next_encounter = reaction.get("encounter")
                    if next_encounter:
                        G.add_edge(encounter_name, next_encounter)

    G.layout()

    # Always write out the .dot file, because that's always useful
    G.write(os.path.join(EXPORT_PATH, "encounters.dot"))
    if EXPORT_PNG:
        G.draw(os.path.join(EXPORT_PATH, "encounters.png"))
    if EXPORT_PDF:
        G.draw(os.path.join(EXPORT_PATH, "encounters.pdf"))


if __name__ == "__main__":
    main()
