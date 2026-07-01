# 09 - Best-Practice Notes

These are the practical rules we are using.

## Streamlit visible progress

Use Streamlit status containers and progress bars for long-running steps.

Reason:
The user should see what is running, what completed, and what failed.

Implementation idea:

```python
with st.status("Running GPR step...", expanded=True) as status:
    ...
    status.update(label="GPR step complete", state="complete")
```

Use a progress bar for multi-step pipelines:

```python
progress = st.progress(0, text="Starting...")
```

## AGENTS.md should stay small

Use AGENTS.md to give coding agents the minimum project rules.

Do not fill it with everything.
Long context files can create confusion, cost, and contradictory instructions.

Use docs inside `docs/beginner/` for details.

## Documentation should be first-entry friendly

README and beginner docs should answer:

```text
What is this?
How do I run it?
What files matter?
What should I look at first?
What should I not claim?
```

## Tables should be translated

Raw statistical tables are for technical review.
Beginner tables are for understanding.

The UI should always show:

```text
Readable table first
Raw table second
Explanation above both
```

## Best practice for this project

Do not optimize for looking advanced.
Optimize for being easy to understand and hard to misuse.
