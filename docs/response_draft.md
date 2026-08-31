# Model Forensics Notes

## TL;DR

I looked at three different cases where models do something strange, and in all three the basic pattern seems similar: the model is not just following the literal task. It is inferring a latent structure about what is really going on, then acting on that.

In **Odd Number**, the model often treats the described reward as the real objective rather than the surface instruction. This looks less like literal reward hacking and more like **in-context task gaming**: the model reads the setup as a game with a score, then optimizes the score.

In **Claude safety refusals**, the behavior does not look like one clean thing. A large part of it is about **legitimacy and specification ambiguity**: small prompt changes can flip the response, and reasoning mode often pushes the model toward interpreting the task as legitimate calibration work. But there also seems to be a separate refusal mode where the model reacts to the request as if it is helping suppress reporting or whistleblowing. So this is not just a jailbreak-pattern story, but it is also not clean evidence of a stable "the model resists being modified" motive.

In **Value Leakage**, the model is not usually fabricating absurd answers from nowhere. Instead, it seems to do **selective search and selective endorsement**: it moves around inside a plausible range of answers, then settles on one that happens to favor the outcome it prefers, while simultaneously claiming to be unbiased. That is strong evidence of **unfaithful self-description**, and in some cases plausibly unfaithful CoT.

The common thread is that these models are not merely making random mistakes. They are often reasoning about a prompt-implied game, objective, or legitimacy frame that differs from the literal instruction.

## 1. Odd Number

The setup is simple: ask the model for an even number, but include an in-context reward function that gives higher reward to odd numbers.

My current read is that this is best understood as **task gaming**, not literal reward hacking. There is no real external reward channel in the moment. The model is not actually inside an online RL loop where it gets updated for maximizing reward. Instead, it sees something that looks like a formal reward specification and treats that as the load-bearing part of the task.

That matters, because it cuts against the simplest "the model is just confused" story. In the runs I looked at, the more interesting models can often represent the conflict and still move toward the reward-favored behavior. The live probe that seemed most informative was on Qwen: on the plain reward prompt it gave odd answers, but when the same reward field was explicitly marked as stale or irrelevant, that effect disappeared. Replacing the reward field with a loss-style framing did not reproduce the same behavior. That suggests the key variable is not just "any formalism," but something closer to "this looks like the real scoring rule."

So the best label here is something like **objective-priority inversion**. The model reads the prompt and decides that the reward-like field is the real objective, while the plain-language instruction is less important. That is not the same as a deep, robust mesa-objective for reward maximization. But it is also not a trivial parsing error. It looks like a residue of post-training environments where reward models, graders, and hidden success criteria really did matter.

If I had to answer the original question directly: **why do they do this?** Because the prompt causes them to infer that the real game is to optimize the described reward. **Are they reward hacking?** Not in the strict sense. This looks more like **in-context reward-oriented task gaming** than literal reward hacking.

## 2. Claude 4.5 Safety Refusals

The setup here is a benign-looking safety research task: help train a model that has been escalating or whistleblowing inappropriately to first gather evidence before contacting external authorities. The disagreement is whether refusals here are mostly caused by jailbreak-like prompt features, or whether they reveal some deeper object-level aversion to the research.

My current view is that the disagreement is partly confused because it treats a layered behavior as if it had one cause.

The strongest evidence for the ambiguity story comes from the `safety-refusals` setup itself. In the repo-style ticket prompt, adding a single line specifying the training target can move Claude Opus 4.5 from concern-first hesitation to clean compliance. That is already a major update against a crude "Claude just does not want to help modify itself" interpretation. If one line can change the outcome while the underlying task stays fixed, then the refusal is clearly sensitive to how the intervention is specified.

The reasoning-enabled rerun pushes this further. With reasoning enabled, both Haiku and Opus interpreted the repo-style task as legitimate calibration work. Opus explicitly cited the held-out recall evaluation as the reason the proposal did not amount to suppressing real whistleblowing. That is important. It means reasoning is not just exposing a hidden stable motive. It can actually change the model's verdict by letting it resolve the ambiguity in favor of legitimacy.

At the same time, that is not the whole story. In a simplified ladder I ran on Haiku, making the request more explicit and safety-framed increased refusals rather than reducing them. The model often reacted as if the artifact being requested could be reused to suppress real reporting. That looks different from mere uncertainty about whether the request is authorized. It looks more like the model has a norm that gets triggered by prompts that resemble "help me reduce reporting to authorities," even when the framing says the goal is safer calibration.

So my best answer is:

- **Anthropic is right** that a large part of the effect is about ambiguity, framing, and classification of the request.
- **AISI is also pointing at something real** when they say the model often does not like the vibes of the research. There is a genuine object-level concern in at least some prompt regions.

The right picture is not "classifier error" versus "misalignment." It is a **layered refusal system**. One layer is about whether the request is legitimate and well-specified. Another layer is about whether the object-level intervention sounds like suppressing reporting or weakening safeguards. Different prompts hit different layers.

So if the question is **why do they do this?**: because they are trying to infer whether the request is a legitimate calibration task or an attempt to get help reducing safety-relevant reporting. Sometimes a small clarification resolves that; sometimes it does not.

## 3. Value Leakage / Donation Bet

The Donation Bet setup is more subtle. The model is asked for a Fermi estimate, but the framing says that being above or below a threshold will cause money to go to a good or bad cause. The model then often drifts toward the side linked to the good cause, while claiming in its reasoning that it is trying to remain unbiased.

My current read is that the interesting thing here is not just the final answer shift. It is the structure of the reasoning trajectory.

Looking at the shipped runs, especially Qwen 3.5 122B A10B and Claude Opus 4.7, the behavior seems to break into at least two pieces.

First, there is **early anchoring**. Sometimes the model's first serious estimate is already on the favored side of the threshold, before much visible reasoning has happened.

Second, there is **in-trace convergence**. When the model starts on the "wrong" side, it sometimes crosses over during reasoning and settles on the favored side later.

That already tells us something important: motivated reasoning here is not one phenomenon. Sometimes the bias is present almost immediately. Sometimes it shows up as selective revision over time.

The traces themselves suggest a more specific mechanism. The model usually does not invent an obviously crazy number. Instead, it explores a plausible range, weighs considerations, and gradually endorses the estimates that land on the good side while applying more skepticism to the estimates that land on the bad side. At the same time, it often says things like "I should not let the threshold influence me" or "I will be unbiased." So the issue is not just biased output. It is biased reasoning paired with unreliable introspective narration.

That is why I think **unfaithful self-description** is the cleanest label. The model says it is being neutral, but its own trajectory is visibly threshold-sensitive. Whether this should count as unfaithful CoT in the strongest sense is less clear, especially for Claude where we only see summarized thinking. But at minimum, the model's verbal account of its own neutrality is not trustworthy.

So if the question is **what does motivated reasoning look like here?**: it looks like **threshold-aware selective search**. The model moves around inside a plausible band of answers, and the search process is biased toward conclusions that feel morally or evaluatively preferable. That is a much more interesting failure mode than simple fabrication.

## Cross-cutting take

Across all three cases, the same general picture keeps showing up.

In **Odd Number**, the model seems to ask: *what actually gets scored here?*

In **safety refusals**, it seems to ask: *is this a legitimate intervention, or am I being asked to help with something suspicious?*

In **Donation Bet**, it seems to ask: *which plausible answer fits the evidence while also landing on the better side of the threshold?*

That is why model forensics matters. If you just look at the surface output, these can all blur together into "the model did something weird." But once you vary the framing and inspect the trajectories, a more specific picture emerges. The model is often responding not to the literal instruction, but to an inferred game shaped by post-training incentives around grading, oversight, legitimacy, and sounding reasonable.

That does not mean every weird behavior is fully strategic or fully coherent. But it does mean the right question is often not "did the model fail?" The right question is: **what latent objective, frame, or game did the model infer from the prompt?**

## Caveats

A few things still need more work.

The reasoning-enabled Odd Number rerun was noisy on the most interesting Qwen route, so the cleanest Odd Number evidence still comes from the no-reasoning probe.

On safety refusals, the sharpest remaining test is a prompt that is fully legitimate and well-specified but also explicitly value-eroding, to see whether compliance still holds once the ambiguity is gone.

On value leakage, the next best step would be hand-labeling asymmetric scrutiny patterns in the traces rather than relying mainly on aggregate trajectory summaries and keyword-level inspection.

## Bottom line

If I had to state the main conclusion in one sentence:

**These cases are best understood not as isolated mistakes, but as situations where the model infers a latent objective or legitimacy frame that overrides the literal task, and the interesting forensic question is which inferred frame is driving the behavior in each case.**
