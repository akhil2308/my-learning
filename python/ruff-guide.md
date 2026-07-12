`ruff` is currently taking the Python world by storm. It is an extremely fast Python linter and code formatter, written in **Rust**.

In the past, Python developers had to maintain a complex stack of tools:

  * **Black** (for formatting)
  * **Isort** (for sorting imports)
  * **Flake8** (for style checks)
  * **Pylint** (for logic checks)
  * **PyUpgrade** (for modernizing syntax)

**Ruff replaces all of them.** It is 10–100x faster than existing tools and uses a single configuration file.

Here is a deep dive into how to use it for your FastAPI project.

-----

### 1\. The Core Concept: Linting vs. Formatting

Ruff does two distinct jobs:

1.  **Linting (`ruff check`):** Looks for bugs, unused variables, and bad coding practices.
2.  **Formatting (`ruff format`):** Rewrites your code to look pretty (fixes indentation, spacing, quotes).

### 2\. Installation

Since you are using `uv`:

```bash
uv pip install ruff
```

### 3\. Practical Examples (Before vs. After)

Here is what Ruff does to your code when you run it.

#### A. Sorting Imports (The `I` rule)

Ruff organizes imports alphabetically and separates standard libraries from third-party ones.

**Before:**

```python
from my_app import utils
import os
import fastapi
from datetime import datetime
```

**After (`ruff check --fix`):**

```python
import os
from datetime import datetime

import fastapi

from my_app import utils
```

#### B. Modernizing Syntax (The `UP` rule)

If you target Python 3.10+, Ruff automatically updates old syntax.

**Before:**

```python
x: List[str] = []
y = "User: %s" % user_id
```

**After:**

```python
x: list[str] = []       # Native list (no need for Typing import)
y = f"User: {user_id}"  # f-strings are faster
```

#### C. Catching Bugs (The `F` rule)

**Code:**

```python
def calculate(x):
    y = 10  # Ruff detects 'y' is never used
    return x * 2
```

**Ruff Output:** `F841 Local variable 'y' is assigned to but never used`

-----

### 4\. Configuration for your Project

Add this to your `pyproject.toml`. This is the configuration your friend was hinting at, but I have added comments so you understand every line.

```toml
[tool.ruff]
# The version of Python you are targeting. 
# Ruff will suggest modern syntax based on this.
target-version = "py311"

# maximum line length (standard is 88 or 100)
line-length = 100

[tool.ruff.lint]
# ------------------------------------------------------------------
# The "Select" list is where the magic happens.
# E, W   = pycodestyle (standard spacing/style errors)
# F      = Pyflakes (logical errors, unused variables, imports)
# I      = isort (sort imports)
# UP     = pyupgrade (upgrade old syntax to new syntax)
# B      = flake8-bugbear (finds likely bugs/pitfalls)
# SIM    = flake8-simplify (suggests simpler logic)
# ------------------------------------------------------------------
select = ["E", "W", "F", "I", "UP", "B", "SIM"]

# Rules to ignore
# E501 = Line too long (we let the formatter handle this, or ignore rare cases)
ignore = ["E501"]

[tool.ruff.format]
# Use double quotes for strings (standard in Python)
quote-style = "double"
# Indent with spaces, not tabs
indent-style = "space"
```

### 5\. How to Run It

**To find errors:**

```bash
ruff check .
```

**To AUTO-FIX errors (imports, old syntax, etc):**

```bash
ruff check . --fix
```

**To format code (spacing, indentation):**

```bash
ruff format .
```

-----

### 6\. The "Senior Dev" Setup: VS Code Integration

You shouldn't have to run these commands manually. You want VS Code to fix your code every time you press `Ctrl + S`.

1.  Install the **Ruff** extension in VS Code (by Astral Software).
2.  Open your VS Code `settings.json` (or create `.vscode/settings.json` in your project) and add this:

<!-- end list -->

```json
{
  "[python]": {
    "editor.defaultFormatter": "charliermarsh.ruff",
    "editor.formatOnSave": true,
    "editor.codeActionsOnSave": {
      "source.fixAll": "explicit",
      "source.organizeImports": "explicit"
    }
  }
}
```

**Now, whenever you save a file:**

1.  It sorts your imports.
2.  It upgrades your syntax.
3.  It formats your spacing.
4.  It removes unused imports.
