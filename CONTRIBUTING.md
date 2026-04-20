# 🤝 Contributing to ArcSim

Thank you for your interest in contributing to ArcSim! This document provides guidelines for contributing.

---

## 🎯 Ways to Contribute

### 1. Try It and Share Feedback

The most valuable contribution is **using ArcSim on your infrastructure** and sharing your experience:

- Did it find real issues?
- Were there false positives?
- What detection rules would be valuable?
- How's the output format?

**Share feedback:** [Open a discussion](https://github.com/tomarakhil7/arcsim/discussions)

---

### 2. Report Bugs

Found a bug? Please [open an issue](https://github.com/tomarakhil7/arcsim/issues/new) with:

- ArcSim version
- Input files (sanitized if needed)
- Expected vs actual behavior
- Error messages/logs

---

### 3. Suggest Features

Have an idea for a new detection rule or feature?

**Before suggesting:**
1. Check [existing discussions](https://github.com/tomarakhil7/arcsim/discussions)
2. Describe the reliability risk it would catch
3. Provide examples of misconfigurations

**Ideal format:**
```
## Feature: [Detection Rule Name]

**What it detects:** [Description]

**Why it matters:** [Real-world impact]

**Example misconfiguration:**
[Code example]

**False positive concerns:** [Any edge cases]
```

---

### 4. Contribute Code

#### Getting Started

```bash
# Fork the repo
git clone https://github.com/yourusername/arcsim.git
cd arcsim

# Set up environment
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Run tests
python -m pytest tests/
```

#### Code Guidelines

- Follow existing code style
- Add tests for new detection rules
- Update documentation
- Keep functions focused and testable

#### Adding a New Detection Rule

1. Create detector in `arcsim/detectors/your_rule.py`
2. Add tests in `tests/test_your_rule.py`
3. Update `arcsim/main.py` to include new detector
4. Add example configs in `examples/`
5. Update README with rule documentation

**Example structure:**
```python
# arcsim/detectors/your_rule.py
from arcsim.models import Finding

def detect_your_rule(resources, environment):
    """
    Detect [what this checks].
    
    Args:
        resources: List of parsed resources
        environment: Environment context (production/staging)
    
    Returns:
        List of Finding objects
    """
    findings = []
    
    for resource in resources:
        # Your detection logic
        if is_misconfigured(resource):
            findings.append(Finding(
                severity="CRITICAL",
                rule_id="YOUR-RULE-001",
                title="Your Rule Title",
                resource_name=resource.name,
                message="Description of issue",
                impact="What could go wrong",
                mitigation="How to fix it",
                confidence="HIGH"
            ))
    
    return findings
```

---

### 5. Improve Documentation

Documentation improvements are always welcome:

- Fix typos or unclear explanations
- Add examples
- Improve setup instructions
- Write case studies

---

## 🔄 Pull Request Process

1. **Fork and branch:** Create a feature branch from `main`
2. **Make changes:** Implement your feature/fix
3. **Test:** Ensure all tests pass
4. **Commit:** Use clear, descriptive commit messages
5. **Push:** Push to your fork
6. **PR:** Open a pull request with description of changes

**PR Title Format:**
```
feat: Add new detection rule for X
fix: Correct false positive in Y detector
docs: Update README with Z example
test: Add test case for edge case
```

**PR Description Should Include:**
- What changed
- Why it changed
- How to test it
- Any breaking changes

---

## ✅ Testing Guidelines

### Running Tests

```bash
# Run all tests
python -m pytest tests/

# Run specific test file
python -m pytest tests/test_spof.py

# Run with coverage
python -m pytest --cov=arcsim tests/
```

### Writing Tests

- Test both positive and negative cases
- Include edge cases
- Use descriptive test names
- Keep tests isolated and fast

**Example:**
```python
def test_detects_spof_in_production():
    """Should flag single replica in production namespace."""
    resource = create_deployment(replicas=1, namespace="production")
    findings = detect_spof([resource], "production")
    assert len(findings) == 1
    assert findings[0].severity == "CRITICAL"

def test_allows_spof_in_staging():
    """Should not flag single replica in staging."""
    resource = create_deployment(replicas=1, namespace="staging")
    findings = detect_spof([resource], "staging")
    assert len(findings) == 0
```

---

## 📋 Code Review Process

All contributions go through code review:

- Maintainer will review within 3-5 days
- Address feedback promptly
- Be open to suggestions
- Discussion is encouraged!

---

## 🐛 Reporting Security Issues

**Do not open public issues for security vulnerabilities.**

Email: tomarakhil7@gmail.com

---

## 📜 Code of Conduct

### Our Standards

- Be respectful and inclusive
- Welcome newcomers
- Focus on what's best for the community
- Show empathy

### Unacceptable Behavior

- Harassment or discrimination
- Trolling or insulting comments
- Personal or political attacks
- Publishing others' private information

---

## 💡 Questions?

- Check [existing discussions](https://github.com/tomarakhil7/arcsim/discussions)
- Open a new discussion
- Email: tomarakhil7@gmail.com

---

## 🙏 Recognition

Contributors will be:
- Listed in release notes
- Mentioned in README
- Credited for their contributions

---

**Thank you for helping make infrastructure more reliable! 🚀**
