import re

# Precedence levels of operators
PRECEDENCE = {'+': 1, '-': 1, '*': 2, '/': 2, '^': 3}

# Define a regex pattern for operators, parentheses, and operands
TOKEN_RE = r'(\b\w+\b|[()+\-*/^])'

# Define a regex pattern for variables (dimensions, expressions, etc.)
VARIABLE_RE = r'\w+'

# Given an expression containing values and operators, tokenize it, stripping whitespace
def tokenize(expression):
    # Use the findall method from the re module to extract all tokens
    tokens = re.findall(TOKEN_RE, expression)
    
    return tokens

 # Helper function to determine if a token is an operator
def is_operator(token):
    return token in PRECEDENCE

def is_variable(token):
    return re.fullmatch(VARIABLE_RE, token)

# Helper function to get precedence of an operator
def get_precedence(op):
    return PRECEDENCE[op]

def parse_string_to_numeric(s):
    try:
        return float(s)
    except ValueError:
        return None
    
def infix_to_rpn(expression):
    # Stack for operators and parentheses
    operator_stack = []
    # Output list for RPN
    output = []
    
    # Tokenize the input expression (split by spaces for simplicity)
    tokens = tokenize(expression)
    
    for token in tokens:
        if is_variable(token):  # Operand (number or variable)
            output.append(token)
        elif is_operator(token):  # Operator
            while (operator_stack and operator_stack[-1] != '(' and
                get_precedence(operator_stack[-1]) >= get_precedence(token)):
                output.append(operator_stack.pop())
            operator_stack.append(token)
        elif token == '(':  # Left parenthesis
            operator_stack.append(token)
        elif token == ')':  # Right parenthesis
            while operator_stack and operator_stack[-1] != '(':
                output.append(operator_stack.pop())
            operator_stack.pop()  # Discard the left parenthesis
    
    # Pop any remaining operators from the stack
    while operator_stack:
        output.append(operator_stack.pop())
    
    return output