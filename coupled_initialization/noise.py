"""Gaussian coupling across the batch dimension of image latents."""

import math
import numbers

import torch


def validate_strength(strength):
    if isinstance(strength, bool) or not isinstance(strength, numbers.Real):
        raise ValueError("Coupled Initialization: strength must be a number in [0, 1].")
    strength = float(strength)
    if not math.isfinite(strength) or not 0.0 <= strength <= 1.0:
        raise ValueError("Coupled Initialization: strength must be finite and in [0, 1].")
    return strength


def validate_seed(seed):
    if isinstance(seed, bool) or not isinstance(seed, numbers.Integral):
        raise ValueError("Coupled Initialization: seed must be an integer.")
    if not 0 <= seed <= 0xFFFFFFFFFFFFFFFF:
        raise ValueError("Coupled Initialization: seed must be in [0, 2**64 - 1].")
    return int(seed)


def validate_image_batch(samples):
    if not isinstance(samples, torch.Tensor) or samples.is_nested:
        raise ValueError("Coupled Initialization expects a regular image latent tensor.")
    if samples.layout != torch.strided or samples.ndim != 4:
        raise ValueError(
            "Coupled Initialization v0.1 expects image latents [batch, channels, height, width]. "
            "Video and nested latents are not supported in this version."
        )
    if not samples.is_floating_point() or any(size < 1 for size in samples.shape):
        raise ValueError("Coupled Initialization expects a nonempty floating-point image batch.")


def couple_noise(eps, strength=1.0):
    """Transform IID Gaussian rows; rho = -strength / (K - 1).

    The first row is unchanged, for a shared reference image with native IID.
    Each row retains its standard Gaussian marginal in exact arithmetic.
    Only the gallery dimension (axis 0) is coupled. Half-precision reductions
    are computed in float32; float64 inputs retain double precision.
    The identity endpoints return the input exactly, including its dtype.
    """
    strength = validate_strength(strength)
    validate_image_batch(eps)
    k = eps.shape[0]
    if strength == 0.0 or k == 1:
        return eps
    work = eps.float() if eps.dtype in (torch.float16, torch.bfloat16) else eps
    rho = -strength / (k - 1)
    tail = work[1:]
    mean = tail.mean(dim=0, keepdim=True)
    # Conditional covariance of the remaining rows given the first:
    # (1-rho) I + (rho-rho**2) 11^T. Its mean-mode eigenvalue is
    # (1-rho)(1-strength); its other eigenvalues are 1-rho.
    result = rho * work[:1] + math.sqrt(1.0 - rho) * (tail - mean)
    if strength < 1.0:
        result = result + math.sqrt((1.0 - rho) * (1.0 - strength)) * mean
    return torch.cat((eps[:1], result.to(dtype=eps.dtype)), dim=0)


class CoupledNoise:
    """ComfyUI NOISE protocol: a seed and generate_noise(input_latent)."""

    def __init__(self, seed, strength=1.0):
        self.seed = validate_seed(seed)
        self.strength = validate_strength(strength)

    def generate_noise(self, input_latent):
        if not isinstance(input_latent, dict) or "samples" not in input_latent:
            raise ValueError("Coupled Initialization requires a LATENT containing samples.")
        samples = input_latent["samples"]
        validate_image_batch(samples)
        indices = input_latent.get("batch_index")
        if self.strength > 0.0 and samples.shape[0] > 1 and indices is not None:
            if len(indices) != samples.shape[0]:
                raise ValueError("Coupled Initialization: batch_index length must equal batch size.")
            if any(isinstance(i, bool) or not isinstance(i, numbers.Integral) or i < 0 for i in indices):
                raise ValueError("Coupled Initialization: batch_index entries must be nonnegative integers.")
            if len(set(indices)) != len(indices):
                raise ValueError(
                    "Coupled Initialization needs distinct base noises for repulsion, but this "
                    "latent repeats batch_index values. Create a fresh empty latent with "
                    "batch_size=K, or use strength=0 for native repeated-noise behavior."
                )

        # Delegate seed, batch-index and CPU-noise conventions to the host.
        # Import lazily so the mathematical transform can be tested standalone.
        import comfy.sample

        eps = comfy.sample.prepare_noise(samples, self.seed, indices)
        return couple_noise(eps, self.strength)
