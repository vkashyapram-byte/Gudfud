import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from scorer.parser import parse_ingredients

def test_hide_and_seek_parser():
    # As found from the database (with OCR bracket correction)
    text = "REFINED WHEAT FLOUR (MAIDA), CHOCOLATE (23%) [SUGAR, COCOA SOLIDS, COCOA BUTTER, DEXTROSE, EMULSIFIER OF VEGETABLE ORIGIN (SOY LECITHIN), ARTIFICIAL FLAVOURING SUBSTANCES - VANILLA CAKE], SUGAR, REFINED PALM OIL, INVERT SUGAR SYRUP, RAISING AGENTS 503 (ii), RAISING AGENTS 500 (ii), IODISED SALT, EMULSIFIER OF VEGETABLE ORIGIN [472e]"
    
    nodes = parse_ingredients(text)
    
    assert len(nodes) == 9, f"Expected 9 top-level nodes, got {len(nodes)}"
    
    # 1. Refined Wheat Flour
    assert nodes[0].name == "REFINED WHEAT FLOUR"
    assert nodes[0].rank == 1
    
    # 2. Chocolate
    assert nodes[1].name.startswith("CHOCOLATE")
    assert nodes[1].declared_pct == 23.0
    assert nodes[1].rank == 2
    assert len(nodes[1].children) == 6, f"Expected 6 children for chocolate, got {len(nodes[1].children)}"
    assert nodes[1].children[0].name == "SUGAR"
    assert nodes[1].children[0].rank == 2  # Inherits parent rank
    
    # Check INS extraction
    # RAISING AGENTS 503 (ii)
    assert "503 (ii)" in nodes[5].ins_codes or "503(ii)" in "".join(nodes[5].ins_codes).replace(" ", "")
    # EMULSIFIER 472e
    assert "472e" in nodes[8].ins_codes
    
    print("All parser tests passed!")

if __name__ == "__main__":
    test_hide_and_seek_parser()
