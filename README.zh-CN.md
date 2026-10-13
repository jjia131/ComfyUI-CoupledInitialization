<div align="center">

<img src="assets/banner-reassemble.gif" alt="Coupled Initialization：面向多样化生成的耦合噪声初始化" width="100%">

**更多样的结果，同样的开销，一个节点即可。**

[![License](https://img.shields.io/badge/license-MIT-477c80?style=flat-square)](LICENSE)
[![Dependencies](https://img.shields.io/badge/dependencies-none-477c80?style=flat-square)](pyproject.toml)
[![arXiv](https://img.shields.io/badge/arXiv-2605.11311-b31b1b?style=flat-square)](https://arxiv.org/abs/2605.11311)
[![ICLR 2026](https://img.shields.io/badge/ICLR-2026-4a5568?style=flat-square)](https://proceedings.iclr.cc/paper_files/paper/2026/file/20b6b87ca17792337f414d948af7b0e8-Paper-Conference.pdf)

[安装](#安装) · [使用](#使用) · [工作流](#示例工作流) · [原理](#原理) · [论文](#论文与引用) · [English](README.md)

</div>

---

**Coupled Initialization** 在不增加生成开销的情况下提升一组图像的多样性。在现有工作流中添加一个节点即可使用，无需训练或额外依赖。

[示例工作流](#示例工作流)在相同的 prompt、seed 和采样设置下，对比原生 IID 噪声与耦合噪声。

### 独立噪声与耦合噪声对比

SD1.5 FP16 · 512×512 · K = 2 · seed 538271 · CFG 7 · Euler/Karras · 28 步 · strength 1。
Prompt：*一座建在古树里的奇幻图书馆……* 耦合噪声带来不同的拱廊构图，同时保留树中图书馆的主题。

| 独立初始化 | 耦合初始化 |
| :---: | :---: |
| <img src="assets/examples/sd15_library_reference.png" alt="共同参考图：古树中的图书馆" width="205"> <img src="assets/examples/sd15_library_iid_second.png" alt="独立噪声的第二张图：树间的灯笼" width="205"><br><sub>共同参考图 → 第二张候选图</sub> | <img src="assets/examples/sd15_library_reference.png" alt="共同参考图：古树中的图书馆" width="205"> <img src="assets/examples/sd15_library_coupled_second.png" alt="耦合噪声的第二张图：树中的拱廊图书馆" width="205"><br><sub>共同参考图 → 第二张候选图</sub> |

这个 seed 下，两份初始噪声的平均平方距离从独立噪声的 **2.01** 增加到耦合噪声的 **3.96（1.97 倍）**。
K = 2 且 strength = 1 时，理论上的预期平方距离翻倍。

## 安装

本地使用时，把插件目录链接到 `ComfyUI/custom_nodes`：

```bash
ln -s /path/to/ComfyUI-CoupledInitialization ComfyUI/custom_nodes/ComfyUI-CoupledInitialization
```

之后重启 ComfyUI 即可，没有任何 Python 依赖。

## 使用

添加 **Coupled Initialization** 节点（菜单路径 `sampling → custom_sampling → noise`），把它的
**noise** 输出接到 **SamplerCustomAdvanced → noise**，替换掉原来的 `RandomNoise`，再把
empty latent 的 **batch_size** 设为 K。

| 输入 | 取值范围 | 默认值 | 说明 |
| --- | --- | --- | --- |
| `seed` | 0 至 2⁶⁴−1 | `0` | 整组图片的种子。与 IID 对比时保持固定。 |
| `strength` | 0.0 至 1.0 | `1.0` | `0` 完全复现原生 IID 噪声；`1` 为最大排斥。 |
| **K** | ≥ 1 | 由 latent 决定 | K 来自 latent 的 `batch_size`。建议先试 2 或 3；K = 1 使用原生噪声。 |

batch 中的第一份噪声保持不变，可作为原生噪声的对照参考。
当 **K = 2 且 strength = 1** 时，这一对正好是 `(ε, −ε)`，即我们 ICLR 2026 论文
[Antithetic Noise in Diffusion Models](https://arxiv.org/abs/2506.06185) 研究的 antithetic noise。

## 示例工作流

| 模型 | 采样设置 | K = 2 | K = 3 |
| --- | --- | --- | --- |
| **SD1.5** | CFG 7、karras、28 步、512×512 | [工作流](examples/sd15_k2_comparison.json) | |
| **SDXL** | CFG 3、karras、30 步 | [工作流](examples/sdxl_k2_comparison.json) | [工作流](examples/sdxl_k3_comparison.json) |
| **FLUX.1-schnell** | BasicGuider、simple、4 步 | [工作流](examples/flux_schnell_k2_comparison.json) | [工作流](examples/flux_schnell_k3_comparison.json) |

每个工作流包含 Coupled Initialization 和原生 `RandomNoise` 两条生成分支，共用同一个
guider、sampler、sigmas 和 latent，只改变初始噪声。

SD1.5 工作流使用 Comfy-Org 的 [FP16 checkpoint](https://huggingface.co/Comfy-Org/stable-diffusion-v1-5-archive/blob/main/v1-5-pruned-emaonly-fp16.safetensors)。导入工作流前，请把模型文件放进 `models/checkpoints`。

## 原理

![K = 2 时，独立噪声的初始分散程度低于反向耦合噪声](assets/coupling-diagram.svg)

Coupled Initialization 先按 ComfyUI 原本的方式取得整个 batch 的噪声，再沿 batch 维做一次线性变换，使任意两份
噪声之间的相关系数为 `ρ = −strength / (K − 1)`。当 `strength = 1` 时，这已是 K 个联合高斯变量
所能达到的最负相关。每份噪声仍保持标准高斯边缘分布，所以模型看到的输入分布没有改变，改变的
只是这一组噪声的*联合*分布。

<details>
<summary>兼容性</summary>

<br>

* 模型：以标准高斯噪声初始化的 diffusion 和 flow 模型。
* 采样接口：`SamplerCustomAdvanced`，以及其他接收 `NOISE` 对象的节点。
* 张量格式：形状为 `[batch, channels, height, width]` 的图像 latent。
* 精度：半精度 batch 的归约在 float32 下进行；float64 输入保留双精度。
* 批次索引：`strength > 0` 时使用互不重复的 `batch_index`。可从新建的 empty latent 开始；需要重复索引时，将 `strength` 设为 0。

</details>

## 论文与引用

本插件基于以下两篇论文，科研使用时请引用：

* **[Couple to Control: Joint Initial Noise Design in Diffusion Models](https://arxiv.org/abs/2605.11311)**
  [Jing Jia](https://jjia131.github.io/)、[Liyue Shen](https://liyueshen.engin.umich.edu/)、[Guanyang Wang](https://guanyangwang.github.io/)。arXiv，2026。
* **[Antithetic Noise in Diffusion Models](https://arxiv.org/abs/2506.06185)**
  [Jing Jia](https://jjia131.github.io/)、[Sifan Liu](https://liusf15.github.io/)、[Bowen Song](https://efzero.github.io/)、[Wei Yuan](https://statistics.rutgers.edu/people-pages/graduate-students/graduate-student-detail/167-fourth-year/624-wei-yuan)、[Liyue Shen](https://liyueshen.engin.umich.edu/)、[Guanyang Wang](https://guanyangwang.github.io/)。ICLR 2026。

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

[MIT 许可证](LICENSE) · [引用元数据](CITATION.cff) · [English](README.md)

</div>

