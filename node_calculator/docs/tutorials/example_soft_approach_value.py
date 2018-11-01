# EXAMPLE: soft_approach_value

import node_calculator.core as noca

"""Task:
Approach a target value slowly, once the input value is getting close to it.
"""

"""
# Sudo-Code based on Harry Houghton's video: youtube.com/watch?v=xS1LpHE14Uk
in_value = <inputValue>
fade_in_range = <fadeInRange>
target_value = <targetValue>

if (in_value > (target_value - fade_in_range)):
    if (fade_in_range > 0):
        exponent = -(in_value - (target_value - fade_in_range)) / fade_in_range
        result = target_value - fade_in_range * exp(exponent)
    else:
        result = target_value
else:
    result = in_value

driven.attr = result
"""

import math

driver = noca.Node("driver")
in_value = driver.tx
driven = noca.Node("driven.tx")
fade_in_range = driver.add_float("transitionRange", value=1)
target_value = driver.add_float("targetValue", value=5)

# Note: Factoring the leading minus sign into the parenthesis requires one node
# less. I didn't do so to maintain the similarity to Harry's example.
# However; I'm using the optimized version in noca.Op.soft_approach()
exponent = -(in_value - (target_value - fade_in_range)) / fade_in_range
soft_approach_value = target_value - fade_in_range * math.e ** exponent

is_range_valid_condition = noca.Op.condition(
    fade_in_range > 0,
    soft_approach_value,
    target_value
)

is_in_range_condition = noca.Op.condition(
    in_value > (target_value - fade_in_range),
    is_range_valid_condition,
    in_value
)

driven.attrs = is_in_range_condition

# NOTE: This setup is now a standard operator: noca.Op.soft_approach()
