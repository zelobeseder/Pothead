"""
Hell Modulator — Process Engine
Handles all signal modulation computations.
"""

import math
import json
import os


WAVEFORMS = ("Sine", "Square", "Sawtooth", "Triangle")
MODULATION_TYPES = ("AM", "FM", "PM")


def generate_waveform(waveform: str, frequency: float, amplitude: float,
                      sample_rate: int, duration: float) -> list[float]:
    """Generate a raw waveform as a list of float samples."""
    num_samples = int(sample_rate * duration)
    samples = []
    for i in range(num_samples):
        t = i / sample_rate
        phase = 2 * math.pi * frequency * t
        if waveform == "Sine":
            value = amplitude * math.sin(phase)
        elif waveform == "Square":
            value = amplitude * (1.0 if math.sin(phase) >= 0 else -1.0)
        elif waveform == "Sawtooth":
            value = amplitude * (2 * (t * frequency - math.floor(t * frequency + 0.5)))
        elif waveform == "Triangle":
            value = amplitude * (2 * abs(2 * (t * frequency - math.floor(t * frequency + 0.5))) - 1)
        else:
            value = 0.0
        samples.append(value)
    return samples


def apply_am_modulation(carrier: list[float], modulator: list[float],
                        depth: float) -> list[float]:
    """Apply amplitude modulation to a carrier using a modulator signal."""
    result = []
    length = min(len(carrier), len(modulator))
    for i in range(length):
        result.append(carrier[i] * (1.0 + depth * modulator[i]))
    return result


def apply_fm_modulation(carrier_freq: float, modulator: list[float],
                        depth: float, sample_rate: int) -> list[float]:
    """Apply frequency modulation."""
    result = []
    phase = 0.0
    for i, mod_val in enumerate(modulator):
        instantaneous_freq = carrier_freq + depth * carrier_freq * mod_val
        phase += 2 * math.pi * instantaneous_freq / sample_rate
        result.append(math.sin(phase))
    return result


def apply_pm_modulation(carrier: list[float], modulator: list[float],
                        depth: float) -> list[float]:
    """Apply phase modulation."""
    result = []
    length = min(len(carrier), len(modulator))
    for i in range(length):
        phase_offset = depth * math.pi * modulator[i]
        angle = math.asin(max(-1.0, min(1.0, carrier[i]))) + phase_offset
        result.append(math.sin(angle))
    return result


def process_profile(profile: dict, duration: float = 1.0) -> dict:
    """
    Run modulation for a given profile dictionary.

    Returns a dict with:
        - 'signal': list of output samples
        - 'peak': peak amplitude
        - 'rms': RMS amplitude
        - 'profile': the source profile
    """
    waveform = profile.get("waveform", "Sine")
    frequency = float(profile.get("frequency", 440.0))
    amplitude = float(profile.get("amplitude", 0.8))
    mod_type = profile.get("modulation_type", "AM")
    mod_depth = float(profile.get("modulation_depth", 0.5))
    carrier_freq = float(profile.get("carrier_frequency", 1000.0))
    sample_rate = int(profile.get("sample_rate", 44100))

    modulator = generate_waveform(waveform, frequency, amplitude, sample_rate, duration)
    carrier = generate_waveform("Sine", carrier_freq, 1.0, sample_rate, duration)

    if mod_type == "AM":
        signal = apply_am_modulation(carrier, modulator, mod_depth)
    elif mod_type == "FM":
        signal = apply_fm_modulation(carrier_freq, modulator, mod_depth, sample_rate)
    elif mod_type == "PM":
        signal = apply_pm_modulation(carrier, modulator, mod_depth)
    else:
        signal = modulator

    if signal:
        peak = max(abs(s) for s in signal)
        rms = math.sqrt(sum(s * s for s in signal) / len(signal))
    else:
        peak = 0.0
        rms = 0.0

    return {"signal": signal, "peak": peak, "rms": rms, "profile": profile}


def load_profile_from_file(path: str) -> dict:
    """Load a profile from a JSON file."""
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def list_profiles(profiles_dir: str) -> list[str]:
    """Return a list of .json profile file paths in a directory."""
    if not os.path.isdir(profiles_dir):
        return []
    return [
        os.path.join(profiles_dir, fn)
        for fn in sorted(os.listdir(profiles_dir))
        if fn.lower().endswith(".json")
    ]


if __name__ == "__main__":
    # Self-test: process the default profile
    _dir = os.path.dirname(os.path.abspath(__file__))
    _default = os.path.join(_dir, "profiles", "default.json")
    if os.path.exists(_default):
        _profile = load_profile_from_file(_default)
        _result = process_profile(_profile, duration=0.1)
        print(f"Profile: {_result['profile']['name']}")
        print(f"Samples: {len(_result['signal'])}")
        print(f"Peak: {_result['peak']:.4f}")
        print(f"RMS:  {_result['rms']:.4f}")
    else:
        print("Default profile not found.")
