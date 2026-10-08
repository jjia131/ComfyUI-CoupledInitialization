<div align="center">

<img src="assets/banner.svg" alt="Coupled Initialization — coupled noise initialization for diverse generation" width="760">

**More variety from the models you already use. One node. No training.**

[![License](https://img.shields.io/badge/license-MIT-477c80?style=flat-square)](LICENSE)
[![Dependencies](https://img.shields.io/badge/dependencies-none-477c80?style=flat-square)](pyproject.toml)
[![arXiv](https://img.shields.io/badge/arXiv-2605.11311-b31b1b?style=flat-square)](https://arxiv.org/abs/2605.11311)
[![ICLR 2026](https://img.shields.io/badge/ICLR-2026-4a5568?style=flat-square)](https://proceedings.iclr.cc/paper_files/paper/2026/file/20b6b87ca17792337f414d948af7b0e8-Paper-Conference.pdf)

[Install](#install) · [Use it](#use-it) · [Workflows](#example-workflows) · [How it works](#how-it-works) · [Paper](#paper--citation) · [中文](README.zh-CN.md)

</div>

---

**Coupled Initialization** gives your batch coupled starting noise, so the same model, prompt and
number of sampling steps explore more distinct candidates — same number of images, same cost.
It applies to any diffusion or flow model that starts from standard Gaussian noise, and needs
no retraining, no extra denoising passes and no dependencies.

The [example workflows](#example-workflows) compare conventional IID noise with coupled noise
using the same prompt, seed, sampler and latent. Their first samples use the same initial noise;
minor pixel differences can still arise from GPU inference.

### Independent noise vs. Coupled Initialization

SD1.5 FP16 · 512×512 · K = 2 · seed 538271 · CFG 7 · Euler/Karras · 28 steps · strength 1.

Prompt: *A magical library carved inside an ancient giant tree…* Both branches use the same
first noise. In this run, coupling explores a different archway composition while preserving
the tree-library theme.

| Independent Initialization | Coupled Initialization |
| :---: | :---: |
| <img src="assets/examples/sd15_library_reference.png" alt="Shared first image: a library inside a giant tree" width="205"> <img src="assets/examples/sd15_library_iid_second.png" alt="Second image with independent noise: lanterns among trees" width="205"><br><sub>Shared reference → second candidate</sub> | <img src="assets/examples/sd15_library_reference.png" alt="Shared first image: a library inside a giant tree" width="205"> <img src="assets/examples/sd15_library_coupled_second.png" alt="Second image with coupled noise: an arched tree library" width="205"><br><sub>Shared reference → second candidate</sub> |

For this seed, the starting noise pair's mean squared distance is **2.01 with IID noise vs.
3.96 with coupling (1.97×)**. At K = 2 and strength 1, coupling doubles the *expected* squared
distance. Image diversity varies with the prompt and model; this is one illustrative batch.

## Install

For a local checkout, link the plugin folder into `ComfyUI/custom_nodes`:

```bash
ln -s /path/to/ComfyUI-CoupledInitialization ComfyUI/custom_nodes/ComfyUI-CoupledInitialization
```

Restart ComfyUI. There are no Python dependencies.

## Use it

Add **Coupled Initialization** (`sampling → custom_sampling → noise`), connect its **noise** output
to **SamplerCustomAdvanced → noise** in place of `RandomNoise`, and set the empty latent's
**batch_size** to K.

| Input | Range | Default | What it does |
| --- | --- | --- | --- |
| `seed` | 0 – 2⁶⁴−1 | `0` | Seed for the whole batch. Keep it fixed when comparing against IID. |
| `strength` | 0.0 – 1.0 | `1.0` | `0` reproduces native IID noise exactly; `1` is maximum repulsion. |
| **K** | ≥ 1 | — | Not a widget: K is the latent's `batch_size`. Start with 2 or 3; K = 1 uses native noise. |

At **K = 2, strength = 1** the pair is exactly `(ε, −ε)`, the
antithetic noise of our ICLR 2026 paper,
[Antithetic Noise in Diffusion Models](https://arxiv.org/abs/2506.06185).

## Example workflows

| Model | Sampling settings | K = 2 | K = 3 |
| --- | --- | --- | --- |
| **SD1.5** | CFG 7, karras, 28 steps, 512×512 | [Workflow](examples/sd15_k2_comparison.json) | — |
| **SDXL** | CFG 3, karras, 30 steps | [Workflow](examples/sdxl_k2_comparison.json) | [Workflow](examples/sdxl_k3_comparison.json) |
| **FLUX.1-schnell** | BasicGuider, simple, 4 steps | [Workflow](examples/flux_schnell_k2_comparison.json) | [Workflow](examples/flux_schnell_k3_comparison.json) |

Each renders the prompt twice — a Coupled Initialization branch and a native `RandomNoise` branch sharing the
same guider, sampler, sigmas and latent — so the noise is the only difference.

The SD1.5 workflow uses Comfy-Org's [FP16 checkpoint](https://huggingface.co/Comfy-Org/stable-diffusion-v1-5-archive/blob/main/v1-5-pruned-emaonly-fp16.safetensors). Place it in `models/checkpoints` before loading the workflow.

## How it works

![Independent noise has less starting spread than antithetically coupled noise at K = 2](assets/coupling-diagram.svg)

Coupled Initialization asks ComfyUI for the batch's noise as usual, then applies a linear transform along the
batch axis so that any two samples carry correlation `ρ = −strength / (K − 1)`. At
`strength = 1` that is as negatively correlated as K jointly Gaussian variables can be. Every
sample keeps a standard Gaussian marginal, so the input distribution the model sees is
unchanged — only the *joint* distribution of the batch is.

<details>
<summary>Compatibility and limits</summary>

<br>

- Sampling interface: `SamplerCustomAdvanced`, or anything else that consumes a `NOISE` object.
- Latents: image latents shaped `[batch, channels, height, width]`. Video and nested latents are
  out of scope for v0.1.
- Precision: half-precision batches are reduced in float32; float64 inputs keep double precision.
- A latent with repeated `batch_index` values has no distinct base noises to push apart, so the
  node reports that instead of silently doing nothing. Use a fresh empty latent, or `strength = 0`.

</details>

## Paper & citation

Based on [Couple to Control: Joint Initial Noise Design in Diffusion Models](https://arxiv.org/abs/2605.11311)
by [Jing Jia](https://jjia131.github.io/), [Liyue Shen](https://liyueshen.engin.umich.edu/) and
[Guanyang Wang](https://guanyangwang.github.io/). If you use Coupled Initialization in research, please cite
both papers.

<details>
<summary>BibTeX</summary>

```bibtex
@misc{jia2026couplecontrol,
  title={Couple to Control: Joint Initial Noise Design in Diffusion Models},
  author={Jing Jia and Liyue Shen and Guanyang Wang},
  year={2026},
  eprint={2605.11311},
  archivePrefix={arXiv},
  primaryClass={cs.LG},
  url={https://arxiv.org/abs/2605.11311}
}

@inproceedings{jia2026antithetic,
  title={Antithetic Noise in Diffusion Models},
  author={Jing Jia and Sifan Liu and Bowen Song and Wei Yuan and Liyue Shen and Guanyang Wang},
  booktitle={International Conference on Learning Representations},
  year={2026},
  url={https://proceedings.iclr.cc/paper_files/paper/2026/file/20b6b87ca17792337f414d948af7b0e8-Paper-Conference.pdf}
}
```

</details>

<div align="center">

[MIT license](LICENSE) · [Citation metadata](CITATION.cff) · [中文说明](README.zh-CN.md)

</div>
