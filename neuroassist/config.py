from dataclasses import dataclass
LEFT, RIGHT, FEET, REST = 0, 1, 2, 3
CLASS_NAMES = {0: "LEFT", 1: "RIGHT", 2: "FEET", 3: "REST"}
CLASS_RU = {0: "левая рука", 1: "правая рука", 2: "ноги", 3: "покой"}

@dataclass
class Config:
    fs: int = 250
    channels: tuple = ("C3", "Cz", "C4")
    band_mu: tuple = (8, 13)
    band_beta: tuple = (13, 30)
    notch_hz: float = 50.0
    window_s: float = 2.0
    step_s: float = 0.25
    classes: tuple = (LEFT, RIGHT, FEET, REST)
    vote_k: int = 6
    min_conf: float = 0.80
    refractory_s: float = 1.0
    calib_trials_per_class: int = 30
    trial_s: float = 4.0
    imagery_from_s: float = 1.0
    imagery_to_s: float = 3.5
