# ⚙️ `.codefox.yml` Configuration

The `.codefox.yml` file allows you to configure the analysis behavior, model selection, and review format.

All parameters are optional.

---

## 🧠 `model`

Settings for the LLM being used.

```yaml
model:
  name: gemini-3-flash-preview
  temperature: 0.2
  max_tokens: 4000
```

### `model.name`

**Type:** `string`
**Description:** The name of the model used for code analysis.

Examples:

```yaml
name: gemini-3-flash-preview
name: gemini-3-pro-preview
name: gemini-3-pro
```

---

### `model.temperature`

**Type:** `number`
**Default:** `0.2`

Controls the creativity level of the model.

Recommendations:

* `0.0 – 0.2` → deterministic and stable analysis ✅
* `0.3 – 0.7` → more “conversational” suggestions
* `> 0.7` → ❌ not recommended for code review

---

### `model.max_tokens`

**Type:** `number | null`
**Default:** `4000`

Limits the maximum size of the model’s response.

* `null` → the model’s default limit is used
* number → hard limit

Example:

```yaml
max_tokens: 3000
```

---

## 🔍 `review`

Analysis logic settings.

```yaml
review:
  severity: false
  max_issues: null
  suggest_fixes: true
  diff_only: false
```

---

### `review.severity`

**Type:** `string | false`
Filter by severity level.

Possible values:

```yaml
severity: low
severity: medium
severity: high
severity: critical
severity: false   # disable the filter
```

If set — only issues of the specified level and above are shown.

---

### `review.max_issues`

**Type:** `number | null`
Limits the number of detected issues.

Useful for:

* reducing noise
* CI mode

```yaml
max_issues: 10
```

---

### `review.suggest_fixes`

**Type:** `boolean`
**Default:** `true`

Enables generation of auto-fix patches.

If `false`:

* only comments are shown without fixes

---

### `review.diff_only`

**Type:** `boolean`
**Default:** `false`

Analysis mode:

* `true` → only the `git diff` is analyzed
* `false` → all files in scope are analyzed

Recommended for CI and PRs.

---

## 🧹 `baseline`

Technical debt management.

```yaml
baseline:
  enable: true
```

### `baseline.enable`

**Type:** `boolean`

If enabled:

* existing issues are ignored
* only new ones are shown

---

## 🛡 `ruler` (analysis rule set)

```yaml
ruler:
  security: true
  performance: true
  style: true
```

Enables or disables analysis categories.

---

### `ruler.security`

Searches for:

* vulnerabilities
* secret leaks
* unsafe practices

---

### `ruler.performance`

Searches for:

* inefficient algorithms
* redundant operations
* memory / query issues

---

### `ruler.style`

Checks:

* readability
* best practices
* code smells

---

## 💬 `prompt`

Model behavior customization.

```yaml
prompt:
  system: null
  extra: null
```

---

### `prompt.system`

**Type:** `string | null`

Completely overrides the system prompt.

Used for:

* strict internal rules
* corporate standards

Example:

```yaml
system: |
  You are a strict senior reviewer.
  Reject any unsafe code.
```

---

### `prompt.extra`

**Type:** `string | null`

Additional instructions on top of the default prompt.

Example:

```yaml
extra: |
  Follow our internal architecture guidelines.
  Ignore legacy modules.
```

---

# 🧩 Full configuration example

```yaml
model:
  name: gemini-3-pro
  temperature: 0.1

review:
  severity: high
  max_issues: 15
  suggest_fixes: true
  diff_only: true

baseline:
  enable: true

ruler:
  security: true
  performance: false
  style: false

prompt:
  extra: |
    Use our NestJS architecture rules.
```

---

## 🧪 Recommended profiles

### CI mode

```yaml
review:
  diff_only: true
  severity: high
  max_issues: 10
```

### Legacy project

```yaml
baseline:
  enable: true
review:
  diff_only: true
```
