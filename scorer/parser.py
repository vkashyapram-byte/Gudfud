import re
import yaml

class IngredientNode:
    def __init__(self, raw_text, parent=None, rank=0):
        self.raw_text = raw_text.strip()
        self.name = ""
        self.children = []
        self.parent = parent
        self.rank = rank
        self.declared_pct = None
        self.estimated_pct = None
        self.ins_codes = []
        self.canonical_id = None
        self.group = None
        self.estimate_method = None
        self.parse()

    def parse(self):
        # Extract percentage e.g. (23%) or 23 %
        pct_match = re.search(r'\(?(\d+(?:\.\d+)?)\s*%\)?', self.raw_text)
        if pct_match:
            self.declared_pct = float(pct_match.group(1))
            self.raw_text = re.sub(r'\(?\d+(?:\.\d+)?\s*%\)?', '', self.raw_text).strip()

        # Extract INS codes e.g. INS 472e, 503 (ii)
        ins_matches = re.finditer(r'(?:INS\s*)?(\d+[a-zA-Z]*(?:\s*\([ivx]+\))?)', self.raw_text, re.IGNORECASE)
        for m in ins_matches:
            code = m.group(1).strip()
            if code not in self.ins_codes:
                self.ins_codes.append(code)

        # Basic name extraction (strip trailing colons, brackets if any leftover)
        self.name = self.raw_text.split('[')[0].split('(')[0].strip(' ,:;-')

    def to_dict(self):
        return {
            "name": self.name,
            "raw_text": self.raw_text,
            "rank": self.rank,
            "declared_pct": self.declared_pct,
            "ins_codes": self.ins_codes,
            "children": [c.to_dict() for c in self.children]
        }

def parse_ingredients(text):
    if not text:
        return []

    def tokenize(s):
        tokens = []
        current = []
        depth_paren = 0
        depth_bracket = 0
        for char in s:
            if char == '(':
                depth_paren += 1
                current.append(char)
            elif char == ')':
                depth_paren = max(0, depth_paren - 1)
                current.append(char)
            elif char == '[':
                depth_bracket += 1
                current.append(char)
            elif char == ']':
                depth_bracket = max(0, depth_bracket - 1)
                current.append(char)
            elif char == ',' and depth_paren == 0 and depth_bracket == 0:
                tokens.append(''.join(current).strip())
                current = []
            else:
                current.append(char)
        if current:
            tokens.append(''.join(current).strip())
        return [t for t in tokens if t]

    def build_tree(tokens, parent=None, start_rank=1):
        nodes = []
        rank = start_rank
        for token in tokens:
            # We want to extract children if the token ends with a bracket block
            # But there could be trailing spaces.
            token = token.strip()
            
            # Check if it has children in trailing brackets
            children_part = None
            if token.endswith(']') or token.endswith(')'):
                # Find the matching open bracket from the right
                depth_paren = 0
                depth_bracket = 0
                for i in range(len(token)-1, -1, -1):
                    char = token[i]
                    if char == ')': depth_paren += 1
                    elif char == '(': 
                        depth_paren -= 1
                        if depth_paren == 0 and depth_bracket == 0:
                            children_part = token[i+1:-1]
                            token = token[:i].strip()
                            break
                    elif char == ']': depth_bracket += 1
                    elif char == '[': 
                        depth_bracket -= 1
                        if depth_bracket == 0 and depth_paren == 0:
                            children_part = token[i+1:-1]
                            token = token[:i].strip()
                            break
            
            # If the children part is just a Roman numeral, treat it as part of the token
            if children_part and re.match(r'^[ivxlc]+$', children_part.strip(), re.IGNORECASE):
                token = f"{token} ({children_part})"
                children_part = None

            # If the children part is just an alphanumeric code (like 472e), treat it as part of the token
            if children_part and re.match(r'^\d+[a-zA-Z]*$', children_part.strip()):
                token = f"{token} [{children_part}]"
                children_part = None

            node = IngredientNode(token, parent=parent, rank=rank)
            if children_part:
                # If the children part is just a percentage, we assign it and don't treat as children
                if re.match(r'^\d+(?:\.\d+)?\s*%$', children_part.strip()):
                    node = IngredientNode(token + f" ({children_part})", parent=parent, rank=rank)
                else:
                    child_tokens = tokenize(children_part)
                    node.children = build_tree(child_tokens, parent=node, start_rank=rank)
            
            nodes.append(node)
            rank += 1
        return nodes

    tokens = tokenize(text)
    return build_tree(tokens)
