---
id: copier-uv-bleeding-fyf
status: closed
deps: []
links: []
created: 2025-12-26T21:46:58.56701+01:00
type: bug
priority: 2
---
# Template tells user to run "prek autoupdate" before git init

After running `copier copy`, the template outputs instructions to run `prek autoupdate`, but the generated project is not yet a git repository. This causes an error:

```
error: Command `get git root` exited with an error:
fatal: not a git repository (or any of the parent directories): .git
```

The template should either:

1. Initialize git as part of the post-copy tasks, OR
2. Update the instructions to tell users to run `git init` first
