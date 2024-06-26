import sys

from collections import defaultdict

from tolstack.StackDim import StackDim
from tolstack.StackUtils import parse_string_to_numeric, percent_to_fraction

from tolstack.StackExpr import StackExpr

from tolstack.StackTree import TreeParser

from tolstack.StackTypes import DistType
from tolstack.StackTypes import get_dist_from_code


class StackParser:

    def __init__(self):
        self.constants = dict()
        self.dimensions = dict()
        self.where_used = defaultdict(set)
        self.expressions = dict()
        self.category = None
        self.TP = None

    def parse(self, file_lines):
        for line in file_lines:
            if line.startswith("*"):
                # Get the category name without '*'
                self.category = line.strip()[1:].split(",")[0].lower()

                # assume sections are in order; set up tree parser
                if self.category == "expressions":
                    self.TP = TreeParser(self.constants | self.dimensions)
            elif self.category:
                self._handle_category(line.strip())

    def _handle_category(self, line):
        match self.category:
            case "constants":
                self._handle_constants(line)
            case "dimensions":
                self._handle_dimensions(line)
            case "expressions":
                self._handle_expressions(line)
            case _:
                print(
                    f"No parsing definition found for '{self.category}'",
                    file=sys.stderr,
                )

    def _handle_constants(self, line):
        tokens = line.split(",")

        if len(tokens) < 2:
            print(
                f"Attempting to define constant {tokens[0]}, but not enough items in input record",
                file=sys.stderr,
            )
            return

        _key = tokens[0].strip()

        _nom = parse_string_to_numeric(tokens[1])
        if _nom is None:
            print(
                f"Attempting to define constant {tokens[0]}, but cannot convert '{tokens[1]}' to a numeric value.",
                file=sys.stderr,
            )
            return

        _note = None
        if len(tokens) == 3:
            _note = tokens[2].strip()

        _const = StackDim(
            key=_key,
            nominal=_nom,
            plus=0,
            minus=0,
            disttype=DistType.CONSTANT,
            note=_note,
        )
        self.constants[_key] = _const

    def _handle_dimensions(self, line):
        tokens = line.split(",")

        if len(tokens) < 4:
            print(
                f"Attempting to define dimension {tokens[0]}, but not enough items in input record",
                file=sys.stderr,
            )
            return

        _key = tokens[0].strip()

        _nom = parse_string_to_numeric(tokens[1])
        if _nom is None:
            print(
                f"Attempting to define dimension {tokens[0]}, but cannot convert '{tokens[1+i]}' to a numeric value.",
                file=sys.stderr,
            )
            return

        _vals = []
        for i in range(2):
            string = tokens[2 + i]
            if "%" in string:
                numeric = percent_to_fraction(string)
                _vals.append(numeric * _nom if numeric else None)
            else:
                _vals.append(parse_string_to_numeric(string))
            if _vals[i] is None:
                print(
                    f"Attempting to define dimension {tokens[0]}, but cannot convert '{string}' to a numeric value.",
                    file=sys.stderr,
                )
                return
        if len(tokens) < 5:
            _dist = DistType.UNIFORM
        else:
            _dist = get_dist_from_code(tokens[4])
            if _dist is None:
                print(
                    f"Attempting to define dimension {tokens[0]}, but cannot convert '{tokens[4]}' to a known distribution type.",
                    file=sys.stderr,
                )
                return

        _PN = None
        if len(tokens) > 5:
            _PN = tokens[5]

        _note = None
        if len(tokens) > 6:
            _note = tokens[6]

        _dim = StackDim(
            key=_key,
            nominal=_nom,
            plus=_vals[0],
            minus=_vals[1],
            disttype=_dist,
            PN=_PN,
            note=_note,
        )
        self.dimensions[_key] = _dim

    def _handle_expressions(self, line):
        tokens = [token.strip() for token in line.split(",")]

        if len(tokens) < 4:
            print(
                f"Attempting to define expression {tokens[0]}, but not enough items in input record",
                file=sys.stderr,
            )
            return

        _key = tokens[0]

        _val = tokens[1]

        _root = self.TP.construct_tree(_key, _val)

        _lower = parse_string_to_numeric(tokens[2]) if tokens[2] else float("-inf")

        _upper = parse_string_to_numeric(tokens[3]) if tokens[3] else float("inf")

        _method = tokens[4] if tokens[4] else "W"

        _note = None
        if len(tokens) > 5:
            _note = tokens[5]

        _expr = StackExpr(
            key=_key,
            expression=_val,
            lower=_lower,
            upper=_upper,
            method=_method,
            root=_root,
            note=_note,
        )
        _expr.set_value_map(self.TP.value_map)

        self.expressions[_key] = _expr

        # Assemble "where used" for each input variable
        for var_key in _expr.referenced_values():
            self.where_used[var_key].add(_expr.key)

    def format_constants(self):
        _out = ""
        for key, val in self.constants.items():
            _out += f"  {key:>8}{val}\n"
        return _out[:-1]

    def format_dimensions(self):
        _out = ""
        for key, val in self.dimensions.items():
            _out += f"  {key:>8}{val}\n"
        return _out[:-1]

    def format_expressions(self):
        _out = ""
        for key, val in self.expressions.items():
            _out += f"  {key:>8}{val}\n"
        return _out[:-1]


if __name__ == "__main__":
    # Example Usage:
    file_lines = [
        "*CONSTANTS",
        "element1",
        "element2",
        "*DIMENSIONS",
        "elementA",
        "elementB",
        "*EXPRESSIONS",
        "elementX",
        "*OUTPUT",
        "an output",
    ]

    StackParser.parse(file_lines)
