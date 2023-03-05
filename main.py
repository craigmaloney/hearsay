#!/usr/bin/env python3
import os
import yaml
import json
import logging
import textwrap
import argparse
from shutil import get_terminal_size

logging.basicConfig()
logger = logging.getLogger("root")
DATADIR = "data"
ENCOUNTERS = "encounters"
CHARACTERS = "characters"
SAVE_FILE = "save_file.json"


def underline(text):
    print("-" * len(text))


def load_characters():
    """Loads all of the characters
    Params
    ------
    None

    Returns
    -------
    characters: dict
        The characters of the game
    """
    characters = {}
    character_path = os.path.join(".", DATADIR, CHARACTERS)
    character_files = os.listdir(character_path)
    for character_filename in character_files:
        if not character_filename.endswith(".yaml"):
            continue
        logger.debug(f"Loading character {character_filename}")
        with open(os.path.join(character_path, character_filename), "r") as file:
            character = yaml.safe_load(file)
            logger.debug(character)
            name = character.get("name")
            characters[name] = character
    return characters


def load_encounter(encounter_filename):
    """Loads the encounter and returns the encounter dictionary
    Params
    ------
    encounter_filename : str
        The encounter file to load

    Returns
    -------
    encounter : dict
        The encounter dictionary
    """

    logger.debug(f"Loading encounter {encounter_filename}")
    try:
        with open(encounter_filename, "r") as file:
            encounter = yaml.safe_load(file)
            logger.debug(encounter)
    except FileNotFoundError:
        encounter = None
    return encounter


def meets_condition(characters, condition):
    all_conditions = True

    if condition:
        for expression in condition:
            character = expression.get("character")
            parameter = expression.get("parameter")
            if character and parameter:
                greater_than = expression.get("greater_than")
                less_than = expression.get("less_than")
                greater_than_equal = expression.get("greater_than_equal")
                less_than_equal = expression.get("less_than_equal")
                equals = expression.get("equals")
                p_values = characters[character]["p_values"]
                if greater_than is not None:
                    all_conditions = all_conditions and (
                        p_values[parameter] > greater_than
                    )
                if less_than is not None:
                    all_conditions = all_conditions and (
                        p_values[parameter] < less_than
                    )
                if greater_than_equal is not None:
                    all_conditions = all_conditions and (
                        p_values[parameter] >= greater_than_equal
                    )
                if less_than_equal is not None:
                    all_conditions = all_conditions and (
                        p_values[parameter] <= less_than_equal
                    )
                if equals is not None:
                    all_conditions = all_conditions and (p_values[parameter] == equals)
    return all_conditions


def get_possible_reactions(encounter, characters):
    """Retrieves the possible reactions for an encounter
    Params
    ------
    encounter: dict
        The encounter to display
    characters: dict
        The characters that might be affected by the encounter

    Returns
    -------
    reaction_list: list
        The list of possible reactions
    """
    reaction_list = []
    if encounter and characters:
        reactions = encounter.get("reactions", {})
        for reaction in reactions:
            condition_met = meets_condition(characters, reaction.get("condition"))
            if condition_met:
                reaction_list.append(reaction)
    return reaction_list


def display_encounter(encounter, characters):
    """Displays the encounter and response selections
    Params
    ------
    encounter: dict
        The encounter to display
    characters: dict
        The characters that might be affected by the encounter

    Returns
    -------
    None
    """

    # Check if we actually got an encounter
    if not encounter:
        return

    print()  # Give us some space between encounters
    # Get the terminal width
    width = get_terminal_size()[0]
    # Display the encounter title
    title = encounter.get("title", "No title")
    print(title)
    underline(title)

    # Display the description of the encounter
    description = encounter.get("description", "No description found.")
    for line in description.splitlines():
        line_wrapped = textwrap.fill(line, width=width, replace_whitespace=False)
        print(line_wrapped)
    print()


def display_reactions(reactions):
    """Displays the possible response selections
    Params
    ------
    reactions: list
        The possible reactions to display
    Returns
    -------
    None
    """
    # Display the possible reactions
    for number, reaction in enumerate(reactions):
        reaction_name = reaction.get("reaction", "Nothing to do")
        print(f"{number + 1}. {reaction_name}")


def get_reaction(reactions):
    """Get the user's reaction
    Params
    ------
    reactions: list
        The possible reactions to display

    Returns
    -------
    response_num : int
        The number of the choice from the user
    """

    response = None
    while response is None:
        response = input("> ")
        if response == "q" or response == "quit":
            return None
        try:
            response_num = int(response)
        except (TypeError, ValueError):
            print("Invalid Response")
            response = None
            continue
        if response_num < 1 or response_num > len(reactions):
            print(f"Please enter a number between 1 and {len(reactions)}")
            response = None
            continue
    return response_num


def process_reactions(response_num, reactions, encounter, characters):
    """Process the reactions for the encounter
    Params
    ------
    response_num: int
        Number of the reaction to process.
    reactions: list
        The possible reactions to display
    encounter: dict
        The encounter to display
    characters: dict
        The characters that might be affected by the encounter

    Returns
    -------
    encounter : string
        The next encounter to load
    """

    # Check if we actually got an encounter
    if not encounter:
        return

    if not reactions:
        print("Nothing to react to")
        return
    index = response_num - 1
    result = reactions[index].get("result", "No result")
    encounter = reactions[index].get("encounter", None)
    changes = reactions[index].get("change")
    if changes:
        for change in changes:
            logger.debug(f"{change} change")
            name = change.get("name")
            if name:
                for key in change.keys():
                    if key == "name":
                        continue
                    try:
                        old_p_value = characters[name]["p_values"][key]
                        new_p_value = old_p_value + change[key]
                        logger.debug(
                            f"{name}[{key}]: Old was {old_p_value}, New is {new_p_value}"
                        )
                        characters[name]["p_values"][key] = new_p_value
                    except KeyError as e:
                        logging.error(f"Can't set p_value for {name}[{key}]")
                        raise e

    print(result)
    return encounter


def press_return():
    """Ask the player to press return"""
    print("(Press Return)")
    input("> ")


def main(encounter="preface", load_save=False):
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
        response_num = get_reaction(reactions)
        if response_num is None:
            return
        moves.append(response_num)
        encounter = process_reactions(response_num, reactions, encounter, characters)
        encounters.append(encounter)
        press_return()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run the Hearsay Story Engine")
    parser.add_argument(
        "--encounter", type=str, help="Encounter to start from", default="preface"
    )
    parser.add_argument("--debug", help="Turn on debugging", action="store_true")
    parser.add_argument("--load", help="Load save file", action="store_true")
    args = parser.parse_args()
    if args.debug:
        logger.setLevel(logging.DEBUG)

    try:
        main(encounter=args.encounter, load_save=args.load)
        print()
        print("The end.")
    except (KeyboardInterrupt, EOFError):
        print()
        print("Exiting...")
    exit()
