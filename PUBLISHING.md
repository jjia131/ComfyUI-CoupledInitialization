# Release checklist

Everything still needed to get this from a folder to a published node, in order.

## 1. Fill the gaps

- [x] Set the GitHub account `jjia131` in [pyproject.toml](pyproject.toml) (`Repository`).
- [x] Set the Registry publisher ID `jjia-momo` in [pyproject.toml](pyproject.toml).
- [ ] Review the [banner](assets/banner.svg), [logo](assets/logo.svg), and
  [comparison gallery](README.md#independent-noise-vs-coupled-initialization).

## 2. Test it locally

- [ ] Link this folder to `ComfyUI/custom_nodes/ComfyUI-CoupledInitialization` and restart ComfyUI. It has
  no dependencies, so nothing else should be needed.
- [ ] Confirm **Coupled Initialization** appears under `sampling → custom_sampling → noise`, and
  that searching `coupledInitialization`, `coupled noise` or `antithetic` finds it.
- [ ] Load `examples/sd15_k2_comparison.json` with an SD1.5 checkpoint and queue it. Both
  branches should render; their first samples share the same initial noise. GPU inference may
  introduce small pixel differences.

## 3. Comfy Registry account

- [ ] Create a publisher and a publishing API key at [registry.comfy.org](https://registry.comfy.org/).
- [ ] Confirm the node ID `coupledInitialization` (the `name` in `pyproject.toml`) is still free. Keep the
  first version at `0.1.0`.

## 4. Push to GitHub

Create a public repository named `ComfyUI-CoupledInitialization`, with `__init__.py` at its root.

```bash
cd '/path/to/ComfyUI-CoupledInitialization'
git init -b main
git add -A
git commit -m "coupledInitialization 0.1.0"
git remote add origin https://github.com/jjia131/ComfyUI-CoupledInitialization.git
git push -u origin main
```

- [ ] On the repository page, check that the banner displays, the author links resolve,
  the citation box appears (GitHub reads `CITATION.cff`), and all five
  `examples/*.json` links download.

## 5. Publish to the Registry

```bash
pip install comfy-cli
comfy node publish        # run from this git checkout; paste the API key at the prompt
```

- [ ] Confirm the entry at `registry.comfy.org/nodes/coupledInitialization`.
- [ ] Once live, add ComfyUI Manager and `comfy node install coupledInitialization` install
  instructions and a Registry badge to the READMEs.
- [ ] Create the GitHub release and tag `v0.1.0`.

## 6. Optional polish

- [ ] Set the repository's social preview image to `assets/logo.svg`, and point
  `[tool.comfy] Icon` at its `raw.githubusercontent.com` URL so the Registry card shows the mark.
- [ ] Add repository topics: `comfyui`, `comfyui-nodes`, `diffusion`, `sampling`.

## Later releases

The version appears in **three** files and they must agree: `pyproject.toml`,
`coupled_initialization/__init__.py` (`__version__`) and `CITATION.cff`. Bump all three, push, then
`comfy node publish` again.

See the [official publishing guide](https://docs.comfy.org/registry/publishing). The Registry
packages Git-tracked files, so commit everything you intend to ship before publishing.
