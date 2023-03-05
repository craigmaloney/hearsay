#!/usr/bin/env python3
import os
import logging
import json
import argparse
import random

from main import (
    load_characters,
    load_encounter,
    get_possible_reactions,
    display_encounter,
    display_reactions,
    process_reactions,
)

logging.basicConfig()
logger = logging.getLogger("root")
DATADIR = "data"
ENCOUNTERS = "encounters"
CHARACTERS = "characters"
SAVE_FILE = "save_file.json"


def main(encounter="preface", load_save=False, seed=None):
    if seed:
        random.seed(seed)
    else:
        random.seed()

    save_state = {}
    characters = load_characters()
    moves = []
    encounters = []

    # Load the character state if present
    if load_save:
        with open(SAVE_FILE, "r") as save_file:
            save_data = json.load(save_file)
            characters = save_data.get("characters")
            moves = save_data.get("moves")
            encounter = save_data.get("encounter")
            encounters = save_data.get("encounters")

    while encounter:
        # Save the character state
        save_state["characters"] = characters
        save_state["encounters"] = encounters
        save_state["encounter"] = encounter
        save_state["moves"] = moves
        save_json = json.dumps(save_state, indent=2, separators=(",", ": "))
        with open(SAVE_FILE, "w") as save_file:
            save_file.write(save_json)

        filename = os.path.join(".", DATADIR, ENCOUNTERS, f"{encounter}.yaml")
        encounter = load_encounter(filename)
        display_encounter(encounter, characters)
        reactions = get_possible_reactions(encounter, characters)
        display_reactions(reactions)
        num_responses = len(reactions)
        if num_responses == 0:
            return
        response_num = random.randint(1, num_responses)
        moves.append(response_num)
        print()
        print(f"> {response_num}")
        print()
        encounter = process_reactions(response_num, reactions, encounter, characters)
        encounters.append(encounter)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run the Hearsay Story Engine")
    parser.add_argument(
        "--encounter", type=str, help="Encounter to start from", default="preface"
    )
    parser.add_argument("--debug", help="Turn on debugging", action="store_true")
    parser.add_argument("--load", help="Load save file", action="store_true")
    parser.add_argument("--seed", help="Seed to use", type=int, default=None)
    args = parser.parse_args()
    if args.debug:
        logger.setLevel(logging.DEBUG)

    try:
        main(encounter=args.encounter, load_save=args.load, seed=args.seed)
        print()
        print("The end.")
    except (KeyboardInterrupt, EOFError):
        print()
        print("Exiting...")
    exit()
