"""
╔══════════════════════════════════════════════════════════════════════════════╗
║                      SYMBOL DELETE TASK PROMPTS                               ║
║                                                                               ║
║  Prompt templates for Symbol Worlds_SymbolEditing_2:                          ║
║  Delete a target symbol from a sequence.                                      ║
║                                                                               ║
║  Each prompt clearly specifies:                                               ║
║  - Which symbol to delete                                                     ║
║  - At which position (1-indexed)                                              ║
║  - The animation sequence (fade out → shift left)                             ║
╚══════════════════════════════════════════════════════════════════════════════╝
"""

import random


# ══════════════════════════════════════════════════════════════════════════════
#  DEFINE YOUR PROMPTS
# ══════════════════════════════════════════════════════════════════════════════

PROMPT_TEMPLATES = [
    "Delete symbol {symbol} at position {position} from the sequence. The video shows the target symbol fading out, then the remaining symbols shifting left to close the gap.",

    "Remove symbol {symbol} at position {position} from the sequence. Animate the symbol disappearing with a fade-out effect, followed by the other symbols moving left to fill the empty space.",

    "Delete the symbol {symbol} at position {position}. The deletion is shown by the target symbol gradually fading out, and the remaining symbols smoothly shifting left to maintain continuity.",

    "Remove the symbol {symbol} at position {position} in the sequence. Show the symbol fading away, then animate the remaining symbols shifting left to close the gap left by the deletion.",
]


def get_prompt(delete_symbol: str, position: int, sequence_length: int = 0) -> str:
    """
    Generate a prompt for symbol deletion task.

    Args:
        delete_symbol: The symbol to be deleted
        position: The 1-indexed position of the symbol to delete
        sequence_length: Length of the original sequence (not used in current templates)

    Returns:
        Formatted prompt string
    """
    # Note: sequence_length parameter kept for API compatibility but not used in current templates
    template = random.choice(PROMPT_TEMPLATES)
    return template.format(symbol=delete_symbol, position=position)


def get_all_prompts() -> list[str]:
    """Get all prompt templates."""
    return PROMPT_TEMPLATES
