# https://stash.ihme.washington.edu/projects/VA/repos/business_rules/browse/doc/md/tetanus.md
from smartva.data.constants import *
from smartva.utils.utils import value_from_row, int_or_float

CAUSE_ID = 7


def logic_rule(row):
    value_of = value_from_row(row, int_or_float)

    convulsions = value_of(Neonate.CONVULSIONS) == YES

    stop_suckling = value_of(Neonate.NORMAL_SUCKLING) == YES and value_of(Neonate.STOPPED_NORMAL_SUCKLING) == YES

    return convulsions and stop_suckling