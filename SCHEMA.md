# Content schema / 内容格式

## Source and generated pages / 源文件与生成页面

`data/*.yaml` stores learner resources and troubleshooting records. `templates/README.head[.en].md` and `README.foot[.en].md` define the Chinese and English homepages.

`data/*.yaml` 保存学习资源与排错记录；上述模板定义中英文首页。生成页面包括两份 README、`docs/resources.md`、`docs/troubleshooting.md` 及对应的 `docs/zh/` 页面。

## Resource / 资源

```yaml
section: Data collection
section_zh: 数据采集
order: 10
description: Tools for recording demonstrations.
description_zh: 用于录制示教的工具。
entries:
  - id: stable-resource-id
    name: Original project or paper name
    url: https://example.org/resource
    type: docs
    what: A factual description of the resource.
    what_zh: 对资源功能的客观说明。
    maturity: research
    verified: 2026-10
    notes: Optional technical use conditions.
    notes_zh: 可选的技术使用条件。
    tags: [data]
```

The URL above is a schema example, not a catalog resource. `id` is globally unique and forms a stable HTML anchor. Missing Chinese fields fail the build; there is no silent English fallback. Original resource titles are shared between languages for lookup. Paired `notes` are required whenever either version is present.

以上 URL 仅为格式示例，不是目录条目。`id` 全局唯一并形成稳定锚点。缺少中文字段时构建失败，不会默默回退为英文。资源原名由两种语言共用，便于检索；填写 `notes` 时需同时提供中文。

Optional fields: `license`, `paper_title` (exact published title), `sources` (supporting URLs). `verified` is the date of a source check, not a translation date or a hardware-validation claim. Public text must preserve material limits such as partial releases, required checkpoints and unreproduced research results.

可选字段包括许可、精确论文标题与补充来源。`verified` 记录来源核验时间，不是翻译时间，也不代表硬件验证。正文需保留部分发布、检查点要求、研究尚未复现等重要限制。

`type`: `repo`, `dataset`, `paper`, `tool`, `docs`, `blog`, `video`, `discussion`, `standard`, `list`, `benchmark`.

`maturity` retains the existing machine values: `production`, `research`, `toy`, `abandoned`. The display labels describe reported hardware use, research, demos and historical references respectively; they do not certify a deployment.

`maturity` 保留既有机器字段，页面分别显示真机使用记录、研究阶段、演示阶段和历史参考，不代表部署认证。

## Troubleshooting / 排错

Each symptom has `id`, `symptom`, `symptom_zh`, and `causes`. Each cause has paired `cause`, `test`, `fix` fields and optional `sources`. Cause order is a diagnostic sequence, not a statistical likelihood claim.

每类现象含稳定 ID、双语标题和原因列表。每个原因包含双语的原因、检查、处理字段，以及可选来源。顺序表示检查流程，不表示统计概率。

## Maintenance boundary / 维护边界

Selection rationale, landscape comparisons, publishing decisions and historical audit prose belong in `editorial/`. They are not publishing inputs and must not be linked from learner READMEs, guides or checklists. Technical use conditions belong in the learner data itself.

选材理由、资料比较、展示决策与历史核验说明集中存入 `editorial/`。生成器不读取该目录，学习首页、教程和检查表不链接它。技术使用条件仍保留在学习数据中。
