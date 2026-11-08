"""Экранная клавиатура со сканированием: 3 команды (ЛЕВАЯ/ПРАВАЯ/НОГИ) покрывают всё."""
from collections import deque
from .predict import suggest
from .config import LEFT, RIGHT, FEET

LETTERS = ["абвгдежз", "иклмнопр", "стуфхцчш", "щъыьэюяй"]
SPECIAL = ["␣", "⌫", "↵", "ОЧИСТИТЬ"]

class Scanner:
    def __init__(self):
        self.text = ""; self.level = "row"; self.row = 0; self.col = 0
    # строки: 0 — подсказки, 1..4 — буквы, 5 — спецсимволы
    @property
    def word(self): return self.text.split(" ")[-1]
    def rows(self):
        return [suggest(self.word)] + [list(r) for r in LETTERS] + [SPECIAL]
    def cells(self): return ["↩"] + self.rows()[self.row]
    def state(self):
        return {"text": self.text, "level": self.level, "row": self.row, "col": self.col,
                "rows": self.rows()}
    def press(self, cmd):
        rows = self.rows(); n = len(rows)
        if self.level == "row":
            if cmd == RIGHT: self.row = (self.row + 1) % n
            elif cmd == LEFT: self.row = (self.row - 1) % n
            elif cmd == FEET: self.level, self.col = "col", 0
            return None
        m = len(self.cells())
        if cmd == RIGHT: self.col = (self.col + 1) % m
        elif cmd == LEFT: self.col = (self.col - 1) % m
        else:
            item = self.cells()[self.col]
            if item == "↩": self.level = "row"; return None
            self._apply(item); self.level, self.col = "row", 0
            self.row = 0 if self.row == 0 else self.row
            return item
    def _apply(self, item):
        if item == "⌫": self.text = self.text[:-1]
        elif item == "␣": self.text += " "
        elif item == "↵": self.text += "\n"
        elif item == "ОЧИСТИТЬ": self.text = ""
        elif len(item) > 1:
            self.text = self.text[:len(self.text) - len(self.word)] + item + " "
        else: self.text += item
    def _key(self): return (self.text, self.level, self.row, self.col)
    def plan(self, target, max_len=200):
        """BFS: кратчайшая последовательность команд до нужного текста."""
        import copy
        start = copy.deepcopy(self)
        q = deque([(start, [])]); seen = {start._key()}
        while q:
            s, path = q.popleft()
            if s.text == target: return path
            if len(path) > max_len: continue
            for cmd in (RIGHT, LEFT, FEET):
                t = copy.deepcopy(s); t.press(cmd)
                if not target.startswith(t.text) and not (t.text.endswith(" ") is False and False):
                    if not target.startswith(t.text): 
                        # допускаем временное несовпадение только через ⌫ — пропускаем для скорости
                        continue
                k = t._key()
                if k in seen: continue
                seen.add(k); q.append((t, path + [cmd]))
        return None
