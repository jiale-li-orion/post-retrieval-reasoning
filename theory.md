
---
## 3. Theory: Post-Recall Evidence Evaluation

We formalize post-recall memory reasoning. The central claim is not that retrieval is unimportant, but that retrieval is only the first stage of memory-based answering. Once relevant evidence has been recalled, the system must still expose a decision-sufficient view, bind the relevant variables, evaluate relations and operators over the recalled evidence, and constrain generation to evidence-valid answers. We call the first stage **access geometry** and the second stage **evaluation algebra**.

### 3.1 Evidence Structures and Semantic Answer Sets

A long-term memory system stores a finite typed evidence structure

$$\mathcal A=(E,R_1,\ldots,R_m),$$

where $E=\{e_1,\ldots,e_N\}$ is a set of evidence items, and each $R_j$ is a typed relation over evidence items, entities, events, timestamps, locations, sources, amounts, statuses, and states. Typical relations include

$$\mathsf{source},\mathsf{time},\mathsf{location},\mathsf{amount},\mathsf{status},\mathsf{same\text{-}event},\mathsf{newer\text{-}than},\mathsf{overrides},\mathsf{contradicts},\mathsf{supports}.$$

We treat $\mathcal A$ as a finite multi-sorted structure. Some relations are attributes, such as $\mathsf{amount}(e,a)$ or $\mathsf{status}(e,s)$; others are relational edges, such as $\mathsf{same\text{-}event}(e_i,e_j)$, $\mathsf{newer\text{-}than}(e_i,e_j)$, or $\mathsf{overrides}(e_i,e_j)$. This lets the memory store both raw evidence and the structural relations needed for downstream evaluation.

**Definition 1 (Semantic Answer Set).** A query $q$ induces a semantic answer relation $\varphi_q$ over $\mathcal A$. The evidence-defined answer set is

$$\mathcal Z_q(\mathcal A)=\{z\in\mathcal Z:\mathcal A\models \varphi_q(z)\},$$

where $\mathcal Z$ is a semantic answer space containing numeric values, entity identifiers, record tuples, state decisions, claim sets, lists, or structured records. A natural-language response $y\in\Sigma^\ast$ is evaluated through a semantic projection

$$\eta:\Sigma^\ast \rightharpoonup \mathcal Z,$$

so correctness means

$$\eta(y)\in \mathcal Z_q(\mathcal A).$$

If $\eta(y)$ is undefined, the response is not semantically evaluable and is treated as invalid. This separates surface fluency from evidence validity: the system is not correct because $y$ sounds plausible, but because its denotation belongs to the answer set defined by the evidence structure.

The access module returns a query-conditioned substructure

$$\mathcal A_q=R_{\mathsf{access}}(q,\mathcal A)\preceq \mathcal A.$$

Let $\mathcal A_q^\star$ denote a sufficient evidence substructure for answering $q$, meaning that evaluating $\varphi_q$ over $\mathcal A_q^\star$ yields the same semantic answer set as evaluating it over the full structure for the variables relevant to $q$. We say retrieval is **oracle** when

$$\mathcal A_q^\star \preceq \mathcal A_q.$$

The theoretical focus of this section is the post-recall regime: even when oracle evidence is available, the system may still fail because the recalled evidence is viewed, bound, evaluated, or decoded incorrectly.

### 3.2 From Evidence Semantics to Model Proposals

The recalled evidence does not enter the language model as a discrete structure. It is first exposed through a view and a serialization:

$$\mathcal A_q \xrightarrow{\mathsf{View}_q} S_q \xrightarrow{\mathsf{Ser}_q} V_q \xrightarrow{E_\theta} X^0\in\mathbb R^{n\times d}.$$

Here $\mathsf{View}_q$ selects which fields, relations, source pointers, timestamps, statuses, modality-specific signals, and source indices are exposed. $\mathsf{Ser}_q$ determines how this selected structure is presented: flattened text, table, graph description, state slots, tool trace, or executable program sketch. $E_\theta$ maps the serialized view into the model's input representation.

The language model then applies residual transformations

$$X^{\ell+1}=X^\ell+F_\ell(X^\ell),\qquad \ell=0,\ldots,L-1.$$

During autoregressive decoding, the model induces a proposal distribution over response strings:

$$p_\theta(y\mid q,V_q)=\prod_{t=1}^{|y|} p_\theta(y_t\mid q,V_q,y_{<t}),$$

with

$$p_\theta(y_t\mid q,V_q,y_{<t})=\operatorname{softmax}(W_U h_t+b)_{y_t},$$

where $h_t\in\mathbb R^d$ is the final hidden state at decoding step $t$, and $W_U$ is the unembedding matrix.

This gives two distinct semantic layers:

$$\mathcal A\models \varphi_q(z) \qquad \text{discrete evidence semantics,}$$

and

$$p_\theta(y\mid q,V_q) \qquad \text{continuous language proposal.}$$

The first defines which answers are valid. The second assigns probability mass to strings. The central mismatch is that high probability under the proposal distribution does not imply evidence validity:

$$p_\theta(y\mid q,V_q)\text{ large} \nRightarrow \eta(y)\in \mathcal Z_q(\mathcal A).$$

Conversely, a semantically valid answer need not receive high probability:

$$\eta(y)\in \mathcal Z_q(\mathcal A) \nRightarrow p_\theta(y\mid q,V_q)\text{ large}.$$

This is not an impossibility theorem. It is a structural observation about objectives. Next-token prediction, instruction tuning, preference tuning, prompting, and chain-of-thought can move probability mass within $p_\theta$, but they do not by themselves impose the support constraint

$$\operatorname{supp}(p_\theta) \subseteq \{y:\eta(y)\in\mathcal Z_q(\mathcal A)\}.$$

Thus, a language model proposal is not an evidence-sound answer distribution unless an additional mechanism enforces evidence semantics.

### 3.3 View Sufficiency and Continuous Separation

The view pipeline compresses the recalled evidence. Whether this compression is harmless depends on whether it preserves the distinctions needed to answer the query.

Let $V_q=\mathsf{Ser}_q\circ\mathsf{View}_q$ be the combined view-and-serialization map.

**Definition 2 (Decision-Sufficient View).** A view $V_q$ is decision-sufficient for query $q$ if, for any two evidence structures $\mathcal A_1,\mathcal A_2$,

$$V_q(\mathcal A_1)=V_q(\mathcal A_2) \Longrightarrow \mathcal Z_q(\mathcal A_1)=\mathcal Z_q(\mathcal A_2).$$

Equivalently, if two answer-distinct evidence worlds collapse to the same view,

$$V_q(\mathcal A_1)=V_q(\mathcal A_2),\qquad \mathcal Z_q(\mathcal A_1)\cap \mathcal Z_q(\mathcal A_2)=\varnothing,$$

then no decoder that observes only $V_q(\mathcal A)$ can be correct on both worlds. This is the exact discrete form of view insufficiency.

A continuous version gives a margin condition. Let

$$\Psi_\theta(\mathcal A)=\pi\!\left(F_\theta(E_\theta(V_q(\mathcal A)))\right)\in\mathbb R^d$$

denote the hidden representation used by the decoder for the decision, where $F_\theta$ denotes the composed transformer computation and $\pi$ extracts the decision-relevant hidden state. Let $g_a(x)$ be the decoder logit assigned to semantic answer class $a$, and define

$$\Delta_{ab}(x)=g_a(x)-g_b(x).$$

**Theorem 1 (Continuous View Separation).** Let $\mathcal A_1,\mathcal A_2$ be two evidence structures with distinct semantic answers $a\neq b$, where $a\in\mathcal Z_q(\mathcal A_1)$ and $b\in\mathcal Z_q(\mathcal A_2)$. Assume $\Delta_{ab}$ is $L_{ab}$-Lipschitz on a region containing $\Psi_\theta(\mathcal A_1)$ and $\Psi_\theta(\mathcal A_2)$. If the decoder separates the two worlds with margin $\gamma>0$, meaning

$$\Delta_{ab}(\Psi_\theta(\mathcal A_1))\ge \gamma,\qquad \Delta_{ab}(\Psi_\theta(\mathcal A_2))\le -\gamma,$$

then

$$\|\Psi_\theta(\mathcal A_1)-\Psi_\theta(\mathcal A_2)\|_2 \ge \frac{2\gamma}{L_{ab}}.$$

**Proof.** From the margin assumptions,

$$\Delta_{ab}(\Psi_\theta(\mathcal A_1))- \Delta_{ab}(\Psi_\theta(\mathcal A_2)) \ge 2\gamma.$$

By $L_{ab}$-Lipschitz continuity,

$$\left| \Delta_{ab}(\Psi_\theta(\mathcal A_1))- \Delta_{ab}(\Psi_\theta(\mathcal A_2)) \right| \le L_{ab} \|\Psi_\theta(\mathcal A_1)-\Psi_\theta(\mathcal A_2)\|_2.$$

Combining the two inequalities yields

$$2\gamma \le L_{ab} \|\Psi_\theta(\mathcal A_1)-\Psi_\theta(\mathcal A_2)\|_2,$$

and therefore

$$\|\Psi_\theta(\mathcal A_1)-\Psi_\theta(\mathcal A_2)\|_2 \ge \frac{2\gamma}{L_{ab}}.$$

$\square$

If the individual logit functions $g_a, g_b$ are each $L$-Lipschitz, then $L_{ab}\le 2L$ and the bound becomes $\|\Psi_\theta(\mathcal A_1)-\Psi_\theta(\mathcal A_2)\|_2 \ge \gamma/L$.[^1]

[^1]: This follows from $|\Delta_{ab}(x)-\Delta_{ab}(x')|\le |g_a(x)-g_a(x')|+|g_b(x)-g_b(x')|\le 2L\|x-x'\|$. The exact constant can be tightened if more is known about the logit functions, but the qualitative scaling is unchanged.

**Corollary 1 (View Insufficiency Implies Margin Instability).** If the view and representation pipeline maps two answer-distinct evidence worlds to hidden states whose distance is less than $2\gamma/L_{ab}$, no $L_{ab}$-Lipschitz decoder can separate them with margin $\gamma$. In particular, if a flattened view discards a critical field or relation—such as whether a receipt is finalized, whether a booking overrides an older booking, whether a photo location was actually visited, or whether a record is stale—then answer-distinct worlds may collapse in representation space. In that case, the failure is not merely retrieval failure; the exposed view is not decision-sufficient.

### 3.4 Binding Instability in Multi-Evidence Evaluation

Hard memory queries often require simultaneously binding multiple variables: hotel name to date range, receipt to amount, photo to location, video to event role, old booking to updated booking, or stale record to current state. Standard attention provides soft alignment, not discrete variable binding.

For a query vector $q_j$ attending over key-value pairs $\{(k_i,v_i)\}_{i=1}^n$,

$$\tilde v_j=\sum_{i=1}^n\alpha_{ji}v_i,\qquad \alpha_{ji}= \frac{\exp(q_j^\top k_i/\tau)}{\sum_{m=1}^n\exp(q_j^\top k_m/\tau)}.$$

**Lemma 1 (Single-Variable Soft Binding Error).** Suppose the correct support set for variable $j$ is $S_j$, and all values in $S_j$ have the same target value $v_j^\star$. Define the binding mass

$$B_j=\sum_{i\in S_j}\alpha_{ji},$$

and let

$$D_j=\max_i\|v_i-v_j^\star\|_2.$$

Then

$$\|\tilde v_j-v_j^\star\|_2 \le (1-B_j)D_j.$$

**Proof.** Since all values in $S_j$ equal $v_j^\star$,

$$\tilde v_j = \sum_{i\in S_j}\alpha_{ji}v_j^\star + \sum_{i\notin S_j}\alpha_{ji}v_i = B_jv_j^\star + \sum_{i\notin S_j}\alpha_{ji}v_i.$$

Therefore,

$$\tilde v_j-v_j^\star = \sum_{i\notin S_j}\alpha_{ji}(v_i-v_j^\star).$$

By the triangle inequality,

$$\|\tilde v_j-v_j^\star\|_2 \le \sum_{i\notin S_j}\alpha_{ji}\|v_i-v_j^\star\|_2 \le \sum_{i\notin S_j}\alpha_{ji}D_j = (1-B_j)D_j.$$

$\square$

If a downstream operation $g$ is $L_g$-Lipschitz, the error propagates as

$$\|g(\tilde v_j)-g(v_j^\star)\|_2 \le L_g(1-B_j)D_j.$$

Thus, even a small amount of off-support attention can be amplified by downstream computation.

For multi-variable evaluation, let the $r$-th variable have binding mass

$$B_r=1-\delta_r.$$

The quantity $\delta_r$ can be interpreted either as a soft binding risk surrogate or, under a stochastic attention interpretation, as an upper bound on the probability of misbinding the $r$-th variable.

**Proposition 1 (Multi-Variable Binding Fragility).** Suppose a query requires $k$ variables to be correctly bound. If

$$P(\mathsf{misbind}_r)\le \delta_r$$

for each variable $r$, then

$$P(\exists r:\mathsf{misbind}_r) \le \sum_{r=1}^k\delta_r.$$

If binding events are conditionally independent given the query and evidence, and $P(\mathsf{correct}_r)=1-\delta_r$, then

$$P(\mathsf{all\ variables\ correctly\ bound}) = \prod_{r=1}^k(1-\delta_r).$$

In the homogeneous case $\delta_r=\delta$,

$$P(\mathsf{all\ correct}) = (1-\delta)^k \le e^{-k\delta}.$$

**Proof.** The first inequality follows from the union bound:

$$P(\exists r:\mathsf{misbind}_r) \le \sum_{r=1}^kP(\mathsf{misbind}_r) \le \sum_{r=1}^k\delta_r.$$

The product form follows from conditional independence. The exponential bound follows from $1-\delta\le e^{-\delta}$ for $\delta\in[0,1]$. $\square$

This proposition does not say that attention cannot bind variables. It says that multi-evidence evaluation is jointly fragile: the task succeeds only when all relevant bindings are stable simultaneously. Graph retrieval, schema cleaning, and better prompting can increase individual $B_r$, but they do not guarantee joint correctness unless the system explicitly represents variables, preserves relations, and checks the resulting state.

**Remark 1 (Soft Binding as Continuous Relaxation).** Attention-based soft binding is a continuous relaxation of discrete variable binding, analogous to the relaxation of Boolean logic to $[0,1]$ in differentiable logic (van Krieken et al., 2022). Just as t-norms do not preserve all Boolean equivalences, soft binding does not preserve correctness under composition: even when each individual binding mass $B_r$ is high, the joint correctness decays exponentially in $k$. The connection to differentiable logic underscores a broader principle: continuous relaxations enable optimization but do not by themselves guarantee that discrete semantic constraints are satisfied. Without a verifier or discrete projection, soft satisfaction is not logical satisfaction.

### 3.5 Access-Evaluation Separation

Memory systems often optimize **access geometry**: writing, indexing, embedding, retrieval, reranking, graph expansion, and neighborhood selection. These operations aim to maximize

$$P(\mathcal A_q^\star\preceq R_{\mathsf{access}}(q,\mathcal A)).$$

Hard memory reasoning requires **evaluation algebra**: operations over recalled evidence, such as

$$\mathsf{select\text{-}source}, \mathsf{bind\text{-}field}, \mathsf{bind\text{-}relation}, \mathsf{latest}, \mathsf{override}, \mathsf{join}, \mathsf{group}, \mathsf{sum}, \mathsf{count}, \mathsf{state\text{-}update}, \mathsf{abstain}.$$

**Definition 3 (Query Taxonomy).** A query is a **lookup query** if its answer is recoverable as a projection of a single retrieved evidence item:

$$f_q(\mathcal A)=\pi(e^\star).$$

A query is an **aggregation query** if its answer requires operations over multiple evidence items, relations, and constraints:

$$f_q(\mathcal A)=F(e_{i_1},\ldots,e_{i_k},R,\mathcal C).$$

Lookup queries are access-dominated. Once $e^\star$ is retrieved and its relevant field is visible, answering is mostly a projection problem. Aggregation queries are evaluation-dominated. Even with oracle evidence, the system must bind multiple variables, evaluate relations, resolve conflicts, compute quantities, or abstain under missingness.

**Definition 4 (Success Decomposition).** Let $\mathsf{AccessOK}$ be the event that the sufficient evidence substructure is included in the recalled context:

$$\mathcal A_q^\star\preceq \mathcal A_q.$$

Let $\mathsf{ViewOK}$ be the event that the exposed view is decision-sufficient for $q$. Let $\mathsf{EvalOK}$ be the event that the required evaluation over the viewed evidence is executed correctly. Then successful post-recall answering requires

$$\mathsf{Success} = \mathsf{AccessOK} \land \mathsf{ViewOK} \land \mathsf{EvalOK}.$$

Under oracle evidence,

$$P(\mathsf{AccessOK})=1,$$

so the remaining accuracy is governed by

$$P(\mathsf{ViewOK}\land\mathsf{EvalOK}\mid \mathsf{AccessOK}).$$

If the oracle protocol also fixes a decision-sufficient view, then the remaining error is evaluation error:

$$\mathsf{Acc}^{\mathsf{oracle\text{-}view}} = P(\mathsf{EvalOK}).$$

**Principle 1 (Access-Evaluation Separation).** Improving access geometry can directly improve lookup accuracy by making relevant evidence more likely to appear in context. For aggregation queries, however, access improvement is not sufficient once the required evidence has already been recalled. Under oracle evidence, the bottleneck shifts from evidence access to view sufficiency and evaluation reliability.

This principle should not be read as saying that retrieval quality never affects aggregation. In realistic systems, retrieval can change distractor load, ordering, source coverage, and view construction. The point is narrower and stronger: once sufficient evidence is present, further gains require making the evidence evaluable, not merely closer.

Graphs illustrate the distinction. As **graph-as-index**, edges are used for retrieval, spreading activation, neighborhood expansion, or reranking. As **graph-as-algebra**, edges such as

$$\mathsf{newer\text{-}than},\mathsf{overrides},\mathsf{same\text{-}event},\mathsf{contradicts},\mathsf{supports}$$

enter the evaluation procedure as executable constraints. A graph that only places related evidence into a prompt remains an access device. It becomes an evaluation device only when its relations participate in query evaluation.

### 3.6 Decision-Sufficient State

Post-recall reasoning does not require preserving all recalled text. It requires constructing a state sufficient for the downstream decision.

Let $H$ be an evidence history and let $P^\star(Y\mid q,H)$ denote the task-level answer distribution induced by the true evidence semantics or environment, not the language model's proposal distribution.

**Definition 5 (Task-Conditioned Decision State).** For a query distribution, define an equivalence relation over evidence histories:

$$H\sim_q H' \iff P^\star(Y\mid q,H)=P^\star(Y\mid q,H').$$

The equivalence class

$$\sigma_q(H)$$

is the task-conditioned decision state for query $q$. It is the coarsest representation of history that preserves all information relevant to the answer distribution.

For lookup queries, $\sigma_q(H)$ may be a single field of a single evidence item. For aggregation queries, $\sigma_q(H)$ may require current records, stale records, source priority, event clusters, role labels, numeric fields, missingness indicators, and conflict status. This reframes memory compression. The question is not how much text can be kept, but which state variables are sufficient for the decision.

A flattened evidence view may preserve semantic accessibility while failing to approximate $\sigma_q(H)$. It may let the model retrieve the relevant item but omit the state variable, relation, or source priority required to evaluate the query. In that case, the failure is not lack of memory access; it is failure to construct a decision-sufficient state.

### 3.7 Harness as Semantic Projection

The language model supplies a proposal distribution. A harness constrains that proposal using evidence semantics.

**Definition 6 (Verifier).** A verifier is a function

$$V_f:\Sigma^\ast\times\mathcal Q\times\mathcal A\to\{0,1\},$$

where $V_f(y,q,\mathcal A)=1$ means that candidate answer $y$ passes the verifier under query $q$ and evidence structure $\mathcal A$.

The verifier-induced semantic valid set is

$$\widehat{\mathcal Z}_q(\mathcal A) = \{\eta(y):V_f(y,q,\mathcal A)=1\}.$$

The verifier is **sound** if

$$V_f(y,q,\mathcal A)=1 \Longrightarrow \eta(y)\in\mathcal Z_q(\mathcal A).$$

Equivalently,

$$\widehat{\mathcal Z}_q(\mathcal A)\subseteq\mathcal Z_q(\mathcal A).$$

The verifier is **$\epsilon$-sound relative to a proposal distribution** $p_\theta$ if

$$P_{y\sim p_\theta}\left( \eta(y)\notin\mathcal Z_q(\mathcal A) \mid V_f(y,q,\mathcal A)=1 \right) \le \epsilon.$$

**Theorem 2 (Harness Soundness).** Define the harness-conditioned distribution

$$p_H(y\mid q,V_q,\mathcal A) = \frac{ p_\theta(y\mid q,V_q)\mathbf 1[V_f(y,q,\mathcal A)=1] }{ \sum_{y'}p_\theta(y'\mid q,V_q)\mathbf 1[V_f(y',q,\mathcal A)=1] },$$

whenever the denominator is nonzero. If the denominator is zero, the system must abstain, inspect the source, or invoke a stronger evaluation procedure.

If $V_f$ is sound, then

$$\operatorname{supp}(p_H) \subseteq \{y:\eta(y)\in\mathcal Z_q(\mathcal A)\}.$$

If $V_f$ is $\epsilon$-sound relative to $p_\theta$, then

$$P_{y\sim p_H}\left( \eta(y)\notin\mathcal Z_q(\mathcal A) \right) \le \epsilon.$$

**Proof.** For the sound case, any $y$ with nonzero probability under $p_H$ must satisfy $V_f(y,q,\mathcal A)=1$, because the indicator zeros out all candidates that fail the verifier. By soundness,

$$V_f(y,q,\mathcal A)=1 \Longrightarrow \eta(y)\in\mathcal Z_q(\mathcal A).$$

Thus every $y\in\operatorname{supp}(p_H)$ is evidence-valid, proving

$$\operatorname{supp}(p_H) \subseteq \{y:\eta(y)\in\mathcal Z_q(\mathcal A)\}.$$

For the $\epsilon$-sound case, $p_H$ is exactly the proposal distribution $p_\theta$ conditioned on the event $V_f(y,q,\mathcal A)=1$. Therefore,

$$P_{y\sim p_H}\left( \eta(y)\notin\mathcal Z_q(\mathcal A) \right) = P_{y\sim p_\theta}\left( \eta(y)\notin\mathcal Z_q(\mathcal A) \mid V_f(y,q,\mathcal A)=1 \right) \le \epsilon.$$

$\square$

Here “projection” means support restriction or semantic conditioning, not Euclidean projection. Soft controls such as prompting, chain-of-thought, schema formatting, instruction tuning, or preference tuning reshape $p_\theta$. A harness changes admissibility by restricting which parts of $p_\theta$ can survive.

**Verifier taxonomy.** Harnesses differ by verifier strength.

1. **Exact verifiers** are sound under their formal semantics: calculators, database queries, deterministic code execution, proof checkers, type checkers, and complete schema validators.

2. **Deterministic structural verifiers** are sound for the structural property they check: source consistency, timestamp ordering, exact ID matching, field type validation, or explicit status comparison. They may not verify all semantic aspects of an answer.

3. **Approximate verifiers** include LLM judges, learned critics, heuristic consistency checkers, and entailment models. These should be treated as $\epsilon$-sound at best, with risk controlled by empirical calibration.

4. **Representation-level harnesses** are weak diagnostic mechanisms. For example, a hidden-state margin can trigger abstention or source inspection when the model appears far from any memorized basin (Liang et al., 2025). Such mechanisms do not prove answer validity, but they can detect epistemic risk before output-level verification.

The theoretical role of a harness is not merely to help the language model “think better.” It either externalizes an operator unstable in continuous residual space, or restricts the proposal distribution to candidates that satisfy evidence-defined constraints.

### 3.8 Adaptive Evaluation Policy

Different queries require different levels of intervention. A lookup query may be answered directly from a retrieved field. A multi-evidence numerical or state-resolution query may require source inspection, structured state construction, an external operator, and verification.

Define a policy

$$\pi(q,\mathcal A_q) \in \{ \mathsf{direct}, \mathsf{structured\text{-}view}, \mathsf{scratchpad}, \mathsf{source\text{-}inspect}, \mathsf{operator\text{-}harness}, \mathsf{verifier} \}.$$

Each policy has risk

$$r(\pi) = P(\eta(\hat y)\notin\mathcal Z_q(\mathcal A))$$

and cost $c(\pi)$. The system objective is

$$\min_\pi \mathbb E[r(\pi)+\lambda c(\pi)]$$

or, under a hard budget,

$$\min_\pi \mathbb E[r(\pi)] \quad \text{s.t.} \quad \mathbb E[c(\pi)]\le B.$$

This objective unifies soft and hard interventions. A structured view changes what information is exposed. A scratchpad changes the internal trajectory by making intermediate variables explicit. Source inspection changes the evidence available to the model. An operator harness executes a discrete computation externally. A verifier restricts admissible outputs.

The policy should therefore be query-adaptive. Direct answering is reasonable when the query is lookup-like, the view is decision-sufficient, and the expected binding complexity is low. Stronger interventions are warranted when the query requires many variable bindings, numerical aggregation, temporal ordering, conflict resolution, source inspection, or abstention under missingness.

### 3.9 Core Thesis

$$
\boxed{
\text{Existing memory systems optimize the geometry of access. Hard memory reasoning requires the algebra of evaluation.}
}
$$

Access geometry makes relevant evidence easier to retrieve. Evaluation algebra turns recalled evidence into a decision-sufficient state by binding fields, resolving stale or conflicting records, distinguishing roles, clustering events, computing quantities, inspecting source modalities, and abstaining under missingness.

The gap is structural. Improving retrieval reduces the probability that evidence is missing. It does not by itself ensure that available evidence is exposed in a decision-sufficient view, that variables are jointly bound, that discrete operators are executed correctly, or that the final answer is evidence-valid. A view may be sufficient for semantic access while insufficient for query evaluation. Soft binding degrades with variable count. Unconstrained decoding can place probability mass on semantically invalid outputs. These failures can persist under oracle retrieval.

Reliable long-term memory systems must therefore maintain source-indexed, modality-aware evidence representations and execute verifiable aggregation over them. The role of the language model is to propose, plan, and communicate. The role of the memory system is to preserve state, expose sufficient variables, execute discrete evaluation, inspect original sources when needed, and constrain answers to the evidence-defined valid set.