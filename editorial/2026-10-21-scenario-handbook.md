# Scenario handbook update — 2026-10-21

## Scope

The requested reading pattern is condition → action → configuration → acceptance, with source links as evidence. Added a paired question index and three paired reference pages: deployment pauses, training monitoring and dataset-format decisions. Homepage lookup tables precede the existing learning sequence. Technical selection conditions remain in learner pages; this publishing record is not linked there.

## Evidence and distinctions

- Treat pause permission as process- and controller-specific. Preserve independent low-level feedback; distinguish asynchronous queues from blending and RTC. Timing examples are engineering calculations, not measured robot results.
- Record actual logging fields from pinned LeRobot, openpi and GR00T sources. Distinguish monitoring from evaluation and checkpointing. TensorBoard code is an integration fragment, not a training launcher.
- The inspected GR00T data guide requires its LeRobot v2 flavor and modality metadata; openpi pins its own LeRobot dependency. The inspected LeRobot v3 guide mentions tasks.jsonl while code defaults to tasks.parquet; explicitly disclose this discrepancy and follow the reader version.
- The 14-dimensional example is a declared six-joint-plus-gripper assumption per arm, not a humanoid default. Container, semantic and model-batch checks are separate.
- Retain raw data when embodiment is unknown; do not equate ego video, retargeted motion and verified robot command supervision.

## Validation scope

Validate paired headings/navigation, generated files, resource links, paper metadata, source URLs and example syntax/arithmetic before publication. No model weights or datasets are downloaded, no training is run, and no robot or monitoring service is operated. Exact source revisions are recorded in the adjacent JSON file.

## Publication checks

- Generated-page check, language/navigation validation and all 6 generator tests passed.
- 30 learner pages and 168 paired resources checked; 167 catalog URLs resolved.
- 42 arXiv records resolved and declared titles matched; pre-existing descriptive-name/duplicate-source warnings remain informational.
- All 16 distinct HTTPS source links in the new guides returned HTTP 200.
- Four Python/JSON code blocks parsed; timing arithmetic and action-slice dimensions checked.
- Whitespace checks passed. These checks do not establish training performance or hardware behavior.
