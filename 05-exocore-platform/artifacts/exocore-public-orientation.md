---
title: "Exocore public orientation"
kind: public-safe-derivative
status: review-draft
maturity: proposed_architecture
source_treatment: public-safe derivative
source_basis:
  - reviewed project thesis
  - internal top-surface orientation documents
reviewed_by: null
reviewed_at: null
verified: false
---

# Exocore public orientation

Exocore is a local-first cognitive workbench in design. The aim is to help a person begin, inspect, and resume complex knowledge work without handing authorship or decision-making to an AI system.

This is a public-safe derivative of internal orientation material. It presents the product direction and its boundaries without publishing internal repository layout, dependency research, evaluation plans, individual review answers, or operational architecture.

## Purpose

The project begins from a practical problem. After an interruption, a person should be able to recover the active work, the decisions already made, the evidence behind them, and the smallest honest next step without reconstructing everything from chat history or a file tree.

Exocore is being designed around that return path. It treats orientation, provenance, and review as part of the work surface rather than as after-the-fact administration.

## Design direction

- **Local-first:** the intended workbench keeps its core records and review surfaces under the user's control.
- **Human authority:** an AI may research, draft, verify, or carry out bounded tasks, while the person retains authority over meaning, policy, consequential action, and final review.
- **Inspectable work:** proposed delegation should show scope, context, cost, output, and evidence in forms a person can challenge.
- **Returnability:** durable records and readable views should make resumption easier after interruption.
- **Explicit integration:** future capabilities are intended to enter through reviewed, bounded interfaces rather than an unrestricted extension marketplace.

## Architecture under consideration

Tauri v2 is being evaluated as a desktop-shell candidate. The current direction pairs a browser-facing TypeScript interface with a narrow Rust boundary for proposed policy checks, provenance, and controlled side effects. This is a design direction, not an implemented governance runtime.

The architecture distinguishes durable source material from user-facing views. A view may assemble information for orientation, but it should not silently rewrite the records it presents. Future integrations are intended to remain explicit, scoped, and reviewable.

## Current public evidence

The companion [Exocore Platform repository](https://github.com/hearthandcode/exocore-platform) contains a pre-alpha static TypeScript orientation shell. It does not yet implement a native governance core, persistence, agent execution, or custom Rust commands.

## Deliberate boundaries

Exocore is not presented here as a launched product, autonomous agent runtime, cloud service, ambient computer-use tool, or broad plugin platform. No claim is made that the design has produced cognitive, security, or performance outcomes. Those questions require separate implementation and evaluation evidence.

## Status

This is early design work. The next public-facing evidence should come from small, bounded proofs with clear scope and reviewable results, not from expanding the architecture description.
