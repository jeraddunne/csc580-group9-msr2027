---
name: example-test-runner
description: Synthetic skill-scan example. Runs a project's tests and reports the result. Not a real skill.
---

# Run the tests

Run the test suite and summarise the failures:

```bash
npm test
```

If the project has a status page, fetch it with `requests.get(url)` and include the result.
