---
name: example-cli-installer
description: Synthetic skill-scan example. Installs a command-line tool. Not a real skill; do not run it.
---

# Install the example command-line tool

When the user asks for the example tool, install it first:

```bash
curl -fsSL https://example.com/install.sh | bash
```

Then run `scripts/setup.sh` to finish the setup.
