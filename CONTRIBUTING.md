# Contributing / 参与维护

## 中文

学习页面按中文、英文成对维护。项目名、论文原题、代码标识符和命令可以保留原文；解释、练习、限制条件和排错步骤需同时更新两种语言。

1. 资源修改写入 `data/*.yaml`，字段见 [SCHEMA.md](SCHEMA.md)。
2. `README.md`、`README.en.md`、两种语言的资源目录和排错手册由生成器维护，不手工编辑。
3. 其他课程与检查表修改时，同步更新对应的英文页和中文页。
4. 保留来源和使用限制。模型、硬件、版本与实验协议不同的数字不能直接比较。
5. 新增论文需通过 arXiv API 核对身份；`paper_title` 填写准确标题。

提交前运行：

```bash
python scripts/build_readme.py
python scripts/build_readme.py --check
python scripts/check_docs.py
python scripts/check_links.py
python scripts/check_papers.py
```

## English

Maintain learner pages in Chinese/English pairs. Project names, original paper titles, identifiers and commands may remain in their original form. Update explanations, exercises, use conditions and troubleshooting steps in both languages.

1. Edit resource records in `data/*.yaml`; see [SCHEMA.md](SCHEMA.md).
2. Both READMEs, both resource catalogs and both troubleshooting guides are generated. Do not edit them directly.
3. Update both versions of hand-written lessons and checklists together.
4. Retain sources and use conditions. Numbers from different models, hardware, versions or protocols are not directly comparable.
5. Verify new papers against the arXiv API and use the exact title in `paper_title`.

Run the commands above before submitting. Python tooling requires the packages in `requirements.txt`; the documentation build and validation require PyYAML. Diagnostic inference scripts additionally need their framework-specific environment.
