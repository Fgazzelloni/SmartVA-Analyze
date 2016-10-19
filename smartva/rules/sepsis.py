# https://stash.ihme.washington.edu/projects/VA/repos/business_rules/browse/doc/md/sepsis.md
from smartva.data.constants import *
from smartva.utils.utils import value_from_row, int_or_float

CAUSE_ID = 42


def logic_rule(row):
    value_of = value_from_row(row, int_or_float)

    female = value_of(SEX) == FEMALE

    age = MATERNAL_AGE_LOWER < value_of(AGE) <= MATERNAL_AGE_UPPER

    pregnant = value_of(Adult.PREGNANT) == YES

    period_overdue = value_of(Adult.PERIOD_OVERDUE) and value_of(Adult.PERIOD_OVERDUE_DAYS) > PERIOD_OVERDUE_CUTTOFF

    abortion = value_of(Adult.AFTER_ABORTION) == YES

    postpartum = value_of(Adult.AFTER_CHILDBIRTH) == YES

    lower_belly_pain = (value_of(Adult.BELLY_PAIN) == YES and 
        (value_of(Adult.BELLY_PAIN_LOCATION1) == BellyPain.LOWER_BELLY
         or value_of(Adult.BELLY_PAIN_LOCATION2) == BellyPain.LOWER_BELLY))

    fever = value_of(Adult.FEVER) == YES

    discharge = value_of(Adult.OFFENSIVE_VAGINAL_DISCHARGE) == YES

    sepsis_symptoms = fever & lower_belly_pain & discharge

    return female and age and (abortion or (postpartum and sepsis_symptoms))