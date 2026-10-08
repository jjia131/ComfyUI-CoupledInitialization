"""Coupled Initialization: coupled noise initialization for ComfyUI."""

from .coupled_initialization.nodes import CoupledInitialization

NODE_CLASS_MAPPINGS = {"CoupledInitialization": CoupledInitialization}
NODE_DISPLAY_NAME_MAPPINGS = {"CoupledInitialization": "Coupled Initialization"}

__all__ = ["NODE_CLASS_MAPPINGS", "NODE_DISPLAY_NAME_MAPPINGS"]
