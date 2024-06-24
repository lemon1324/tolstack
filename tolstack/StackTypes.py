from enum import Enum


class DistType(Enum):
    UNIFORM = 1
    NORMAL_1S = 2
    NORMAL_2S = 3
    NORMAL_3S = 4
    CONSTANT = 98
    DERIVED = 99


class EvalType(Enum):
    WORSTCASE = 1
    STATISTICAL_1S = 2
    STATISTICAL_2S = 3
    STATISTICAL_3S = 4
    UNKNOWN = 99

    def __str__(self) -> str:
        match self:
            case EvalType.WORSTCASE:
                return "Worst Case"
            case EvalType.STATISTICAL_1S:
                return "Statistical ±1σ"
            case EvalType.STATISTICAL_2S:
                return "Statistical ±2σ"
            case EvalType.STATISTICAL_3S:
                return "Statistical ±3σ"
            case EvalType.UNKNOWN:
                return "Unknown"
            case _:
                return super().__str__()


def get_dist_from_code(code):
    _code = code.strip().upper()
    match _code:
        case "U":
            return DistType.UNIFORM
        case "1S":
            return DistType.NORMAL_1S
        case "2S":
            return DistType.NORMAL_2S
        case "3S":
            return DistType.NORMAL_3S
        case "C":
            return DistType.CONSTANT
        case "D":
            return DistType.DERIVED
        case _:
            return None


def get_code_from_dist(disttype: DistType):
    match disttype:
        case DistType.UNIFORM:
            return "U"
        case DistType.NORMAL_1S:
            return "1S"
        case DistType.NORMAL_2S:
            return "2S"
        case DistType.NORMAL_3S:
            return "3S"
        case DistType.CONSTANT:
            return "C"
        case _:
            return "D"


def get_eval_from_code(code):
    _code = code.strip().upper()
    match _code:
        case "W":
            return EvalType.WORSTCASE
        case "1S":
            return EvalType.STATISTICAL_1S
        case "2S":
            return EvalType.STATISTICAL_2S
        case "3S":
            return EvalType.STATISTICAL_3S
        case _:
            return EvalType.UNKNOWN
