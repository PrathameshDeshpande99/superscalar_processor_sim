from utils import bit32

class ALU:
    def Adder(self, A: bit32, B: bit32, isAdd: bool, isSub: bool, isLd: bool, isSt: bool) -> bit32:
        # assert sum([isAdd, isSub, isLd, isSt]) == 1, "Exactly one of isAdd, isSub, isLd, isSt must be True"

        if isAdd or isLd or isSt:
            return A + B
        elif isSub:
            return A - B
        else:
            return 0

    def Multiplier(A, B, isMul):
        return 0

    def Divider(A, B, isDiv, isMod):
        return 0

    def ShiftUnit(A, B, isLsl, isLsr, isAsr):
        return 0

    def LogicalUnit(A, B, isAnd, isOr, isNot):
        return 0

    def isMov():
        return 0