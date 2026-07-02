# engine/prompt_formula.py
FORMULA_STRUCTURE = {
    "google": {"name": "Google Image FX", "structure": ["cinematography", "subject", "action", "setting", "style"], "template": "{cinematography} of a {subject} {action} in a {setting}, {style}."},
    "luma": {"name": "Luma Dream Machine", "structure": ["subject", "setting", "movement", "camera"], "template": "{subject} in a {setting}, {movement}, {camera}."},
    "midjourney": {"name": "Midjourney", "structure": ["subject", "style", "lighting", "ratio", "stylize", "chaos", "weird"], "template": "{subject}, {style} style, {lighting} --ar {ratio} --stylize {stylize} --chaos {chaos} --weird {weird}"},
    "deepseek": {"name": "DeepSeek Janus Pro", "structure": ["subject", "foreground", "background", "palette"], "template": "{subject}. Foreground: {foreground}. Background: {background}. Color palette: {palette}."}
}

class PromptFormula:
    def __init__(self, dna: dict, detector: dict, vpos: dict, user: dict):
        self.dna = dna; self.detector = detector; self.vpos = vpos; self.user = user
    def _get(self, key: str, default: str = "") -> str:
        if key in self.dna:
            val = self.dna[key]
            return ", ".join(val) if isinstance(val, list) else str(val)
        if self.detector and key in self.detector:
            val = self.detector[key]
            return ", ".join(val) if isinstance(val, list) else str(val)
        if self.vpos and key in self.vpos:
            val = self.vpos[key]
            return ", ".join(val) if isinstance(val, list) else str(val)
        if key in self.user:
            val = self.user[key]
            return ", ".join(val) if isinstance(val, list) else str(val)
        return default
    def google(self) -> str:
        return f"{self._get('cinematography', 'cinematic shot')} of a {self._get('subject', 'artist')} {self._get('action', 'performing')} in a {self._get('setting', 'room')}, {self._get('style', 'warm ambient')}."
    def luma(self) -> str:
        return f"{self._get('subject', 'artist')} in a {self._get('setting', 'room')}, {self._get('movement', 'gentle movement')}, {self._get('camera', 'slow pan, 4s loop')}."
    def midjourney(self) -> str:
        ratio = self.user.get("ratio", "16:9")
        stylize = self.user.get("stylize", 50)
        chaos = self.user.get("chaos", 10)
        weird = self.user.get("weird", 5)
        return f"{self._get('subject', 'artist')}, {self._get('style', 'cinematic')} style, {self._get('lighting', 'natural')} --ar {ratio} --stylize {stylize} --chaos {chaos} --weird {weird}"
    def deepseek(self) -> str:
        return f"{self._get('subject', 'artist')}. Foreground: {self._get('foreground', 'details')}. Background: {self._get('background', 'ambient')}. Color palette: {self._get('palette', 'neutral')}."

def compile_all_formulas(dna: dict, detector: dict, vpos: dict, user: dict) -> dict:
    f = PromptFormula(dna, detector, vpos, user)
    return {"google": f.google(), "luma": f.luma(), "midjourney": f.midjourney(), "deepseek": f.deepseek()}