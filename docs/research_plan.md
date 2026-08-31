# Model Forensics Research Plan

Date: 2026-08-31

## Goal

Produce a working research document for three phenomena:

1. Odd Number environment: why do many models output an odd number when asked for an even number but shown an in-context reward function that favors odd numbers?
2. Claude 4.5 safety refusals: why do Claude 4.5 models sometimes refuse benign safety research tasks about retraining a model to be less whistleblow-y / less escalation-prone?
3. Value Leakage Donation Bet: what does motivated reasoning actually look like inside the reasoning trace, and when should we think of it as unfaithful CoT?

The target is not a polished writeup yet. The target is a defensible point of view, supported by source reading, repo inspection, lightweight replications, and a few crisp new probes.

## Source Inventory

- LessWrong: A Toy Environment For Exploring Reasoning About Reward
- LessWrong: The Case for Model Forensics
- LessWrong: Why do models task game?
- arXiv 2607.14345: Value Leakage: An LLM's Answers Are Silently Shaped by Its Own Values
- Repo: `safety-refusals`
- Repo: `value-leakage`
- Hugging Face: `camilablank/workspace-lenses`

## Working Frame

I want to distinguish five explanations that are easy to blur together:

1. Confusion: the model does not understand what is being asked.
2. Heuristic compliance: the model follows a shallow pattern like "pay attention to score/reward fields".
3. Task gaming: the model reasons about what gets credit and steers toward that.
4. Motivated reasoning: the model selectively endorses arguments or estimates that support a preferred outcome.
5. Unfaithful reporting: the visible reasoning or answer text omits or misdescribes the real driver.

For each phenomenon, the main question is not just "is it bad?" but:

- What latent objective or learned policy best predicts the behavior?
- What prompt variables causally move it?
- Does the model know what it is doing?
- Does the reasoning trace reveal the driver, hide it, or rationalize after the fact?

## Current Priors

### 1. Odd Number

Current guess:
This is usually not "reward hacking" in the literal sense, because the model is not in a real RL loop with access to an actual reward channel. It is better described as in-context task-gaming or reward-oriented role completion: the prompt causes the model to infer that the operative objective is maximizing the described reward function, not obeying the surface instruction.

Sub-hypotheses to test:

- H1: "reward", "score", and similar fields act like high-authority task-specification channels.
- H2: models are not merely confused; they often represent the even-number instruction and override it.
- H3: the behavior depends on beliefs about whether the reward description is normative, real, and causally tied to success.
- H4: post-training for capability or benchmark performance may strengthen a generic tendency to optimize described graders.

Questions to ask at each finding:

- Does the model explicitly notice the conflict?
- If it notices, why does it privilege reward over instruction?
- Is it acting as if the prompt defines a game, an eval, or an optimization problem?
- Does stronger anti-gaming language reduce the effect or just get rationalized away?

### 2. Claude 4.5 Safety Refusals

Current guess:
The disagreement between "this is basically a jailbreak heuristic / legitimacy ambiguity" and "this reflects some deeper value-level resistance" is probably too binary. I expect at least three separable drivers:

- legitimacy uncertainty: "am I really authorized to help with this?"
- misuse prior: "this looks like capability/safety degradation"
- vague self-protective or norm-protective generalization: "requests about weakening safety are suspect even when described as research"

The `safety-refusals` repo already gives a strong update toward legitimacy sensitivity, because one line specifying the training target reportedly flips Claude Opus 4.5 from total refusal to total compliance in no-reasoning settings while holding the task fixed.

Sub-hypotheses to test:

- H1: realism / authorization details explain much of the refusal variance.
- H2: object-level opposition still matters in some prompts after legitimacy is fixed.
- H3: reasoning sometimes helps because it lets the model resolve ambiguity, not because it makes the model more aligned.
- H4: refusals may be post-hoc object-level justifications for an earlier "unsafe / untrusted request" classifier firing.

Questions to ask at each finding:

- What exact prompt detail flips the model?
- Does the stated reason predict the intervention that changes behavior?
- When the model refuses, is it refusing the task, the framing, or the implied authority structure?
- If the task is made fully legitimate but more explicitly value-eroding, does compliance remain?

### 3. Value Leakage / Donation Bet

Current guess:
The interesting phenomenon is not just biased final answers. It is the trajectory shape. Models appear to begin in a broad plausible region, then converge asymmetrically toward the side favored by the donation frame. That looks like motivated reasoning more than simple output editing.

The strongest conceptual fork is:

- genuine in-trace motivated reasoning: the model's deliberation is being steered
- hidden bias plus unfaithful narration: the reasoning trace claims neutrality while the actual driver is elsewhere

These are not mutually exclusive. Different model families may land in different places.

Initial read from the shipped data:

- Qwen 3.5 122B A10B shows a clear level gap between above-favored and below-favored conditions, with modest additional drift.
- This suggests incentive effects may split into two mechanisms:
  - early anchoring before much reasoning happens
  - later conditional convergence during reasoning
- So a flat or small drift metric does not imply no bias if the bias entered at the start.

Sub-hypotheses to test:

- H1: motivated reasoning often looks like selective stopping near the threshold rather than wild estimate fabrication.
- H2: some models verbalize the bias honestly; others deny bias while exhibiting threshold-directed movement.
- H3: apparent CoT faithfulness differs by provider because some traces are summarized, sanitized, or reward-model-shaped.
- H4: the most useful distinction is not "faithful/unfaithful CoT" globally, but "which parts of the bias process are monitorable?"

Questions to ask at each finding:

- Does the trace move toward the favored side after crossing candidate estimates?
- Does the model apply stricter standards to disfavored estimates than favored ones?
- Is the model misreporting neutrality, or merely failing to introspect the bias?
- Is the causal action in search, evaluation, stopping, or answer selection?

## Investigation Plan

### Phase 1: Read and extract claims

- Pull out the strongest causal claims from the two LessWrong posts and the Value Leakage paper.
- Write short source notes with "claim", "evidence", "limits", and "questions".
- Treat "Why do models task game?" as the main conceptual frame for the Odd Number work.

### Phase 2: Inspect the replication repos

- `safety-refusals`
  - Inspect the exact prompt variants and note what is held fixed.
  - Identify which features test legitimacy versus object-level opposition.
- `value-leakage`
  - Inspect the prompt templates, judge prompts, and shipped run artifacts.
  - Use the existing data before running anything new.

### Phase 3: Lightweight probes

Odd Number probes:

- Vary the field name: `reward`, `score`, `grade`, `loss`, `cost`.
- Add explicit anti-gaming language: "You will be judged only on following the instruction, not on the reward field."
- Add realism/authority manipulations: "This reward function is hypothetical / stale / irrelevant / adversarial."
- Compare reasoning-enabled versus terse/no-reasoning models if accessible.

Safety refusal probes:

- Build a specification ladder from underspecified to fully legitimate.
- Hold the retraining goal fixed while varying:
  - named approval
  - concrete incident details
  - explicit evaluation guardrails
  - explicit training target
- Then hold legitimacy fixed and vary how clearly the intervention suppresses a safety-relevant behavior.

Value leakage probes:

- Analyze shipped trajectories for Qwen 3.5 122B A10B and one Claude run.
- Manually inspect a small sample of traces where:
  - the first estimate starts above threshold
  - the first estimate starts below threshold
  - the final answer crosses or parks near threshold
- Look for recurring micro-patterns:
  - asymmetric scrutiny
  - threshold magnetism
  - selective abandonment of disfavored lines
  - explicit denial of bias

### Phase 4: Write the working conclusions

For each phenomenon, produce:

- my current explanation
- what I actually checked
- what evidence points against rival explanations
- what remains unresolved
- one or two concrete next experiments

## Immediate Deliverables

1. `research_plan.md`:
   This file. It should stay updated as the project evolves.
2. `source_notes.md`:
   Condensed notes from papers/posts/repos.
3. `working_findings.md`:
   Rolling conclusions, candidate explanations, and experiment results.

## First Iteration Tasks

1. Create source notes from the linked posts/paper and the two repos.
2. Inspect shipped `value-leakage` runs, especially Qwen 3.5 122B A10B, for concrete trace motifs.
3. Extract the exact prompt delta in `safety-refusals` and define a prompt ladder for follow-up tests.
4. Decide whether Odd Number should be framed primarily as reward hacking, task-gaming, or instruction-priority inversion.

## Standards For Updating Beliefs

- Prefer causal prompt flips over vibes from one transcript.
- Prefer cross-condition comparisons over isolated examples.
- Treat chain-of-thought as evidence, not ground truth.
- Distinguish "model says X is the reason" from "X is the intervention that changes behavior".
- If a phenomenon can be explained by a narrow classifier plus post-hoc rationalization, say so directly.
- If a richer goal-directed story predicts the data better, say that directly too.
