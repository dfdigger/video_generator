from dataclasses import dataclass

@dataclass
class Word:
    text: str
    start: float
    end: float

@dataclass
class Line:
    words: list[Word]

    def start(self) -> float:
        return self.words[0].start

    def end(self) -> float:
        return self.words[-1].end

    def text(self) -> str:
        return " ".join(w.text for w in self.words)