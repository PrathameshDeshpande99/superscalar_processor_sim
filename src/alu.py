"""
Module defining the Arithmetic Logic Unit (ALU) for the superscalar processor.
"""

from utils import bit32

class ALU:
    """
    Arithmetic Logic Unit (ALU) responsible for mathematical and logical operations.
    """
    def Adder(self, A: bit32, B: bit32, isAdd: bool, isSub: bool, isLd: bool, isSt: bool) -> bit32:
        """
        Perform addition or subtraction operation.

        Args:
            A (bit32): The first operand.
            B (bit32): The second operand.
            isAdd (bool): True if addition.
            isSub (bool): True if subtraction.
            isLd (bool): True if load instruction (uses addition for address calculation).
            isSt (bool): True if store instruction (uses addition for address calculation).

        Returns:
            bit32: The result of the operation.
        """
        # assert sum([isAdd, isSub, isLd, isSt]) == 1, "Exactly one of isAdd, isSub, isLd, isSt must be True"

        if isAdd or isLd or isSt:
            return A + B
        elif isSub:
            return A - B
        else:
            return 0

    def Multiplier(A, B, isMul):
        """Perform multiplication operation."""
        return 0

    def Divider(A, B, isDiv, isMod):
        """Perform division or modulo operation."""
        return 0

    def ShiftUnit(A, B, isLsl, isLsr, isAsr):
        """Perform shift operations: logical left, logical right, arithmetic right."""
        return 0

    def LogicalUnit(A, B, isAnd, isOr, isNot):
        """Perform logical AND, OR, or NOT operations."""
        return 0

    def isMov():
        """Check if instruction is a move operation."""
        return 0