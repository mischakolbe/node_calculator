# EXAMPLE: soft_approach_value

import node_calculator.core as noca

"""Task:
Approach a given value slowly.
"""

"""
# Sudo-Code based on Harry Houghton's video: youtube.com/watch?v=xS1LpHE14Uk
in_value = <someInputValue>
transition_range = <transitionRange>
target_value = <someStartValue>

if (in_value > (target_value - transition_range)):
    if (transition_range > 0):
        exponent = -(in_value - (target_value - transition_range)) / transition_range
        soft_value = target_value - transition_range * exp(exponent)
    else:
        soft_value = target_value
else:
    soft_value = in_value

driven.attr = soft_value
"""

import math

driver = noca.Node("driver")
in_value = driver.tx
driven = noca.Node("driven.tx")
transition_range = driver.add_float("transitionRange", value=1)
target_value = driver.add_float("someStartValue", value=5)

exponent = -(in_value - (target_value - transition_range)) / transition_range
soft_approach_value = target_value - transition_range * math.e ** exponent

approaching_condition = noca.Op.condition(
    transition_range > 0,
    soft_approach_value,
    target_value
)

overall_condition = noca.Op.condition(
    in_value > (target_value - transition_range),
    approaching_condition,
    in_value
)

driven.attrs = overall_condition


# Will be in the NodeCalculator Operators by default soon. Maybe it's already in there...
