'''
This file generates the ISPL file.
'''
import itertools

# Define some global variables
count_commands_list = [] # a list of counting 'update' guarded commands in each module
count_env_protocols = 1 # the number of protocols in environment agent

'''
'------ Some helper functions ------
'''
def find_module_name(result, var_name):
    # find the module name containing the specified variable name
    for m in result:
        if var_name in m["variable_list"].asList():
            return m["name"][0]

    raise NameError("Variable " + var_name + " not found in any module.")

def translate_formula(prop_list, level, result, module_idx):
    s = "(" if level != 0 else ""

    for i, item in enumerate(prop_list):
        if item == "True":
            if module_idx == -2: # formulae section
                s += "const_true"
            else:
                s += "true"
        elif item == "False":
            if module_idx == -2: # formulae section
                s += "!const_true"
            else:
                s += "false"
        elif item == "&&":
            s += " and "
        elif item == "||":
            s += " or "
        elif item == "!":
            s += "!"
        elif item == "G":
            s += "G "
        elif item == "F":
            s += "F "
        elif item == "X":
            s += "X "
        elif item == "U":
            s += " U "
        elif type(item) == type([]):
            s += translate_formula(item, level+1, result, module_idx)
        elif item == "->":
            if level != 0:
                s = "(!" + s + ")"
            else:
                s = "!(" + s + ")"

            s += " or (" + translate_formula(prop_list[i+1:], 0, result, module_idx) + ")"
            break
        else:
            # item is an identifier
            containing_module = find_module_name(result, item)
            if module_idx == -1: # Environemnt agent
                s += containing_module + "_" + item + " = true"
            elif module_idx == -2: # Formulae section
                s += item
            else: # Standard agent
                if containing_module == result[module_idx]["name"][0]:
                    s += item + " = true"
                else:
                    s += "Environment." + containing_module + "_" + item + " = true"

    s += ")" if level != 0 else ""
    return s

'''
'------ End of helper functions ------
'''
def generate_ispl(result):
    global count_commands_list
    global count_env_protocols

    # Pre-work
    for module in result:
        count_commands_list.append(len(module["update"]))
        count_env_protocols = count_env_protocols * len(module["update"])

    s = ""

    '''
    1. Generate Environment agent.
    '''
    s += generate_environment(result)
    print "Generated Environment agent."

    '''
    2. Generate each standard agent.
    '''
    for i, m in enumerate(result):
        s += generate_standard_agent(result, i)
        print "Generated agent {}".format(str(i))
    print "Generated Standard agent."

    '''
    3. Generate Evaluation section.
    '''
    s += generate_evaluation(result)
    print "Generated Evaluation section."

    '''
    4. Generate InitStates section.
    '''
    s += generate_initstates(result)
    print "Generated InitStates section."

    '''
    5. Generate Formulae section.
    '''
    s += generate_formulae(result)
    print "Generated Formulae section.",

    return s

def generate_environment(result):
    '''
    Generate the environment section.
    '''
    s = ""
    s += "Agent Environment\n    Obsvars:\n"

    for module in result:
        module_name = module["name"][0]
        for variable in module["variable_list"]:
            s += "        " + module_name + "_" + variable + " : boolean;\n"

    s += "        const_true : boolean;\n" # used for const true conditions
    s += "    end Obsvars\n"
    s += "    Actions = { skip };\n"
    s += "    Protocol:\n        Other : { skip }; \n    end Protocol\n"
    s += "    Evolution:\n"

    # Generate the Evolution part
    iter_list = []
    for count in count_commands_list:
        iter_list.append(range(count))

    for indices in itertools.product(*iter_list):
        # each iteration generate one line in Evolution section
        # generate the evolution assignment first

        # now generate the evolution condition
        ass_str_list = []
        cond_str_list = []
        for module_idx, gc_idx in enumerate(indices):
            for ass in result[module_idx]["update"][gc_idx]["action_part"]:
                assigned_variable = ass["assigned_variable"][0]
                assignment = translate_formula(ass["assignment"].asList(), 0, result, -1)
                ass_str_list.append(result[module_idx]["name"][0] + "_" + assigned_variable + " = " + assignment)

            cond_str = result[module_idx]["name"][0] + ".Action = gc" + str(gc_idx)
            cond_str_list.append(cond_str)

        s += "        (" + \
             " and ".join(ass_str_list) + \
             ") if " + \
             " and ".join(cond_str_list) + \
             ";\n"

    s += "    end Evolution\n" + \
         "end Agent\n\n"
    return s

def generate_standard_agent(result, idx):
    '''
    Generate the ith module in result.
    '''
    module = result[idx]
    s = ""
    name = module["name"][0]
    s += "Agent " + name + "\n" + \
         "    Vars:\n"

    for v in module["variable_list"]:
        s += "        " + v + " : boolean;\n"

    s += "    end Vars\n" + \
         "    Actions = { "

    action_count = len(module["update"])
    action_str_list = ["gc" + str(i) for i in range(action_count)]
    action_str_list.append("skip")

    s += ", ".join(action_str_list) + " };\n" + \
         "    Protocol:\n"

    for i, gc in enumerate(module["update"]):
        gc_condition = gc["condition_part"]

        # if it's the true = true case, use Environment.const_true
        condition = ""
        if len(gc_condition) == 1 and gc_condition[0] == "True":
            condition = "Environment.const_true = true"
        else:
            condition = translate_formula(gc_condition.asList(), 0, result, idx)

        s += "        " + condition + " : { gc" + str(i) + " };\n"


    s += "        Other : { skip };\n" + \
         "    end Protocol\n" + \
         "    Evolution:\n"

    for i, gc in enumerate(module["update"]):
        ass_str_list = []
        for ass in gc["action_part"]:
            ass_str_list.append(ass["assigned_variable"][0] + " = " + translate_formula(ass["assignment"].asList(), 0, result, idx))

        s += "        " + " and ".join(ass_str_list) + " if Action = gc" + str(i) + ";\n"

    s += "    end Evolution\n" + \
         "end Agent\n\n"

    return s

def generate_evaluation(result):
    '''
    Generate the evaluation section.
    '''
    s = "Evaluation\n"
    for module in result:
        for var in module["variable_list"]:
            s += "    " + var + " if " + module["name"][0] + "." + var + " = true;\n"
    s += "    const_true if Environment.const_true = true;\n"
    s += "end Evaluation\n\n"
    return s

def generate_initstates(result):
    '''
    Generate the InitStates section.
    '''
    s = "InitStates\n    "

    module_init_list = []
    for idx, module in enumerate(result):
        module_name = module["name"][0]

        gc_init_list = []
        for gc in module["init"]:
            # record all controleld variables for this module, for the purpose of default initialization
            controlled_variables = set(module["variable_list"].asList())

            action_init_list = []
            for action in gc["action_part"]:
                variable = action["assigned_variable"][0]
                controlled_variables.remove(variable) # initialized variable
                assignment = action["assignment"]

                action_init_list.append(module_name + "." + variable + " = " + translate_formula(assignment.asList(), 0, result, idx))
                action_init_list.append("Environment." + module_name + "_" + variable + " = " + translate_formula(assignment.asList(), 0, result, idx))

            # default initialization for uninitialized variables
            for uninit_v in controlled_variables:
                action_init_list.append(module_name + "." + uninit_v + " = false")
                action_init_list.append("Environment." + module_name + "_" + uninit_v + " = false")

            gc_init_list.append("(" + " and ".join(action_init_list) + ")")

        module_init_list.append("(" + " or\n".join(gc_init_list) + ")")
    module_init_list.append("Environment.const_true = true")
    s += " and ".join(module_init_list) + ";\n"
    s += "end InitStates\n\n"
    return s

def generate_formulae(result):
    '''
    Generate the Formulae section.
    '''
    s = "Formulae\n" + \
        "    <<ste>> (Environment, ste) (\n" + \
        "        "

    for i in range(len(result)):
        s += "<<st" + str(i) + ">> "

    for i, module in enumerate(result):
        s += "(" + module["name"][0] + ", st" + str(i) + ") "

    s += "(\n"

    and_list = []

    for i, module in enumerate(result):
        and_str = "            (([[alt_st" + str(i) + "]] (" + module["name"][0] + ", alt_st" + str(i) + ") !(" + translate_formula(module["goal"]["formula"].asList(), 0, result, -2) + ")) or (" + translate_formula(module["goal"]["formula"].asList(), 0, result, -2) + "))\n"
        and_list.append(and_str)

    s += "            and\n".join(and_list)

    s += "        )\n"
    s += "    );\n" + \
         "end Formulae"
    return s
