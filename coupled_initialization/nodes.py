"""Supported legacy node schema, compatible with current ComfyUI as well."""

from .noise import CoupledNoise, validate_seed, validate_strength


class CoupledInitialization:
    CATEGORY = "sampling/custom_sampling/noise"
    RETURN_TYPES = ("NOISE",)
    RETURN_NAMES = ("noise",)
    FUNCTION = "get_noise"
    DESCRIPTION = (
        "Coupled noise initialization for diverse generation. K is the image latent's "
        "batch size. Strength 0 uses native noise; 1 gives maximal K-repulsion. "
        "The first noise always matches native IID. "
        "Connect to SamplerCustomAdvanced. A single-image batch uses native noise."
    )
    SEARCH_ALIASES = ["coupledInitialization", "Coupled Initialization", "repulsive noise", "coupled noise", "antithetic"]

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "seed": ("INT", {
                    "default": 0, "min": 0, "max": 0xFFFFFFFFFFFFFFFF,
                    "control_after_generate": True,
                    "tooltip": "Seed for the whole gallery. Keep fixed for reproducible comparisons.",
                }),
                "strength": ("FLOAT", {
                    "default": 1.0, "min": 0.0, "max": 1.0, "step": 0.05,
                    "advanced": True,
                    "tooltip": "0: native noise. 1: maximum repulsion. Each image retains a standard Gaussian noise marginal.",
                }),
            },
        }

    @classmethod
    def VALIDATE_INPUTS(cls, seed, strength):
        try:
            validate_seed(seed)
            validate_strength(strength)
        except ValueError as error:
            return str(error)
        return True

    def get_noise(self, seed, strength=1.0):
        return (CoupledNoise(seed, strength),)
