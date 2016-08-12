'''
Verify a parsed result is valid.
If a module is not valid, raise exception.
'''
from pyparsing import ParseException

module_name_set = set([]) # store all module names
controlled_variable_set = set([]) # store all controlled variables

def verify_result(r):
    '''
    r: a list of parsed module results
    '''
    for m in r:
        for v in m["variable_list"]:
            if v in controlled_variable_set:
                raise ParseException("Having duplicate controlled variable.")
            else:
                controlled_variable_set.add(v)

    for m in r:
        verify_module(m)


def verify_module(m):
    '''
    Verify each module separately.
    Check following:
    1. All modules have different names.
    '''
    if m["name"][0] in module_name_set:
        raise ParseException("Having duplicate module name.")
    else:
        module_name_set.add(m["name"][0])

    '''
    2. All controlled variables are different.
    '''
    # for v in m["variable_list"]:
        # if v in controlled_variable_set:
            # raise ParseExceptino("Having duplicate controlled variable.")
        # else:
            # controlled_variable_set.add(v)

    '''
    3. In init part, all "condition part" must be "True".
    '''
    for gc in m["init"]: # each guarded command in "init" part
        if gc["condition_part"][0] != "True":
            raise ParseException("Having init guarded command with condition other than 'True'.")

    '''
    4. For each guarded command, the assigned variables in lhs of command actions must be within its own controllable variables.
    '''
    for gc in m["init"]:
        for action in gc["action_part"]:
            if action["assigned_variable"][0] not in m["variable_list"].asList():
                raise ParseException("Having a uncontrollable variable in lhs of an assignment.")

    for gc in m["update"]:
        for action in gc["action_part"]:
            if action["assigned_variable"][0] not in m["variable_list"].asList():
                raise ParseException("Having a uncontrollable variable in lhs of an assignment.")

    '''
    5. For each guarded command, all the variables appeared in assignment must be within all controlled variables.
    '''
    for gc in m["init"]:
        for a in gc["action_part"]:
            for v in a["assignment_variables"]:
                if v not in controlled_variable_set:
                    raise ParseException("Having an atom in rhs of a guarded command assignment, which is not defined.")

    for gc in m["update"]:
        for a in gc["action_part"]:
            for v in a["assignment_variables"]:
                if v not in controlled_variable_set:
                    raise ParseException("Having an atom in rhs of a gaurded command assignment, which is not defined.")

    '''
    6. For gaurded commmand in 'update' part, all the variables appeared in condition part must be within all controlled variables.
    '''
    for i, gc in enumerate(m["update"]):
        for v in gc["condition_variables"]:
            if v not in controlled_variable_set:
                raise ParseException("Having an undefined atom in lhs of a guarded command in a module")

    '''
    7. For the 'goal' part, each variable in the 'variables' must be within all controlled variables.
    '''
    if "goal" in m:
        for v in m["goal"]["variables"]:
            if v not in controlled_variable_set:
                raise ParseException("Having an undefiend atom in the goal part of a module")

