import numpy as np

PROFILES = {
    "contrast_high": {
        "scale": 0.28,
        "min_amp": 0.35,
        "max_amp": 4.0,
        "power": 1.8,
        "method": "power"
    },
    "contrast_medium": {
        "scale": 0.28,
        "min_amp": 0.35,    
        "max_amp": 4.0,
        "power": 1.5,
        "method": "power"
    },
    "contrast_low": {
        "scale": 0.28,
        "min_amp": 0.35,
        "max_amp": 4.0,
        "power": 1.2,
        "method": "power"
    },
    "linear": {
        "scale": 0.28,
        "min_amp": 0.35,
        "max_amp": 4.0,
        "method": "linear"
    },
    "exponential": {
        "scale": 0.3,
        "min_amp": 8.0,
        "max_amp": 30.0,
        "exp_factor": 0.6,
        "method": "exponential"
    },
    "logarithmic": {
        "scale": 0.28,
        "min_amp": 0.35,
        "max_amp": 4.0,
        "log_weight": 0.5,
        "method": "logarithmic"
    },
    "dynamic": {
        "scale": 0.5,
        "min_amp": 0.14,
        "max_amp": 5.5,
        "log_weight": 5.5,
        "method": "dynamic"
    },

}

def visual_amplitude(mass, profile, min_mass=None, max_mass=None):
    scale = profile["scale"]
    min_amp = profile["min_amp"]
    max_amp = profile["max_amp"]
    method = profile["method"]

    if method == "linear":
        # Линейная формула (базовая)
        amp = scale * mass

    elif method == "power":
        # Степенная формула (контраст через степень)
        power = profile.get("power", 1.8)
        amp = scale * (mass ** power)

    elif method == "exponential":
        # Экспоненциальная формула (агрессивный контраст)
        exp_factor = profile.get("exp_factor", 0.5)
        amp = scale * (np.exp(exp_factor * mass) - scale)

    elif method == "logarithmic":
        # Логарифмическая формула (мягкий контраст)
        log_weight = profile.get("log_weight", 0.5)
        amp = scale * (log_weight * mass + (1 - log_weight) * np.log(mass + 1))

    elif method == "dynamic":
        # Динамический скейл на основе диапазона (адаптивный)
        if min_mass is not None and max_mass is not None and max_mass > min_mass:
            norm_mass = (mass - min_mass) / (max_mass - min_mass)
            power = profile.get("power", 1.8)
            amp = scale * (norm_mass ** power)
        else:
            # Fallback к степенной, если диапазон не указан
            power = profile.get("power", 1.8)
            amp = scale * (mass ** power)

    else:
        # По умолчанию линейная
        amp = scale * mass

    return np.clip(amp, min_amp, max_amp)



# Альтернативные формулы в комментах для экспериментов:

# Степенная функция (контраст зависит от показателя)

# amp = scale * (mass ** 1.5)
# amp = scale * (mass ** 2.0)

# Логарифмический + линейный (мягче)

# amp = scale * (0.5 * mass + 0.5 * np.log(mass + 1))

# Экспоненциальный скейл (агрессивный контраст)

# amp = scale * np.exp(0.5 * mass) - scale

# Динамический скейл на основе диапазона (более гибкий)

# norm_mass = (mass - min_mass) / (max_mass - min_mass) if max_mass > min_mass else 0.5
# amp = scale * (norm_mass ** 1.8)

# Квадратный корень (мягче степени 1.5)

# amp = scale * np.sqrt(mass)

# Кубический корень (ещё мягче)

# amp = scale * (mass ** (1/3))


#    "exponential": {
#        "scale": 0.28,
#        "min_amp": 0.35,
#        "max_amp": 4.0,
#        "exp_factor": 0.5,
#        "method": "exponential"
#    },
