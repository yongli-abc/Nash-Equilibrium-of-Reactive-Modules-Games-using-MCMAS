#!/usr/bin/env python
'''
This module will read in the RML file and parse it using the pyparsing library.
'''
import pyparsing as pp

# Define parsers for literals
boolean_literal = pp.Keyword("True") | pp.Keyword("False")

def build_identifier_parser():
    '''
    Return a parser for parsing identifiers.
    Identifiers ::= <alphas> <alphanum>* - <boolean-literal> - <temporal-operator>
    It's recommanded that only small-case letters are used.
    '''
    initial_letters = "abcdefghijklmnopqrstuvwxyzABCDEHIJKLMNOPQRSTUVWYZ_" # removed X F G
    body_letters = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTVWXYZ_1234567890" # removed U
    identifier_parser = ~boolean_literal + pp.Word(initial_letters, body_letters)
    return identifier_parser

def build_propositional_formula_parser():
    '''
    Return a parser for parsing propositional_formula.
    '''
    identifier_set = set([])

    def record_identifiers(t):
        identifier_set.add(t[0])
        return t

    identifier = build_identifier_parser()
    identifier.setParseAction(record_identifiers)
    unary_op = pp.Literal('!')
    binary_op = pp.oneOf("&& || ->")
    lpar = pp.Literal('(').suppress()
    rpar = pp.Literal(')').suppress()

    expr = pp.Forward()

    atom = boolean_literal \
         | identifier \
         | unary_op + expr \
         | pp.Group(lpar + expr + rpar)

    def add_identifiers_to_result(t):
        t["identifiers"] = identifier_set

    expr << atom + pp.ZeroOrMore(binary_op + expr)
    expr.setParseAction(add_identifiers_to_result)
    return expr

def build_LTL_formula_parser():
    '''
    Return a parser for parsing LTL formula.
    '''
    identifier_set = set([])

    def record_identifiers(t):
        identifier_set.add(t[0])
        return t

    identifier = build_identifier_parser()
    identifier.setParseAction(record_identifiers)

    unary_op = pp.oneOf("X F G !")
    binary_op = pp.oneOf("U && || ->")
    lpar = pp.Literal('(').suppress()
    rpar = pp.Literal(')').suppress()

    expr = pp.Forward()

    atom = boolean_literal \
         | identifier \
         | unary_op + expr \
         | pp.Group(lpar + expr + rpar)

    def add_identifiers_to_result(t):
        t["identifiers"] = identifier_set

    expr << atom + pp.ZeroOrMore(binary_op + expr)
    expr.setParseAction(add_identifiers_to_result)
    return expr

def build_guarded_command_parser():
    '''
    Return a parser for parsing guarded commands.
    '''
    # condition
    condition = build_propositional_formula_parser()

    def add_condition_variables(t):
        t["condition_variables"] = t["identifiers"]
        return t

    condition.addParseAction(add_condition_variables)

    # action
    assignment = build_propositional_formula_parser()

    def add_assignment_variables(t):
        t["assignment_variables"] = t["identifiers"]
        return t

    assignment.addParseAction(add_assignment_variables)

    action = build_identifier_parser()("assigned_variable") + pp.Literal(":=") + assignment("assignment")

    # action list
    action_list = pp.delimitedList(pp.Group(action))

    # assemble
    guarded_command = pp.Literal("[]") \
                    + condition("condition_part") \
                    + pp.Literal("~>") \
                    + action_list("action_part")

    return guarded_command

def build_RML_parser():
    '''
    Return the complete parser for parsing a RML module file.
    '''
    module_name = build_identifier_parser()
    variable = build_identifier_parser()
    guarded_command = build_guarded_command_parser()
    LTL_formula = build_LTL_formula_parser()

    # init-part
    init = pp.Keyword("init").suppress() + pp.OneOrMore(pp.Group(guarded_command))

    # update-part
    update = pp.Keyword("update").suppress() + pp.OneOrMore(pp.Group(guarded_command))

    # goal-part
    goal = pp.Keyword("goal").suppress() + LTL_formula("formula")
    def add_goal_variables(t):
        t["variables"] = t["identifiers"]
        return t

    goal.addParseAction(add_goal_variables)

    # module-body
    module_body = init("init") + update("update") + goal("goal")

    # variable-list
    variable_list = pp.delimitedList(variable)

    # module
    module = pp.Keyword("module").suppress() \
             + module_name("name") \
             + pp.Keyword("controls").suppress() \
             + pp.Group(variable_list)("variable_list") \
             + module_body \
             + pp.Keyword("end module").suppress()

    # RML_file
    RML_file = pp.OneOrMore(pp.Group(module))

    return RML_file
