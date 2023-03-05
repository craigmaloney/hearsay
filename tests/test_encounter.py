import os
import pytest
from main import (
    load_encounter,
    load_characters,
    meets_condition,
    get_possible_reactions,
    )


def test_encounter():
    filename = os.path.join('.', 'tests', 'data', 'test_encounter.yaml')
    encounter = load_encounter(filename)
    assert encounter.get('name') == 'template'
    assert encounter.get('title') == 'Template'
