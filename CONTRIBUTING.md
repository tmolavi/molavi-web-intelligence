# Contributing to Molavi Web Intelligence Engine (MWIE)

We welcome contributions to the **Molavi Web Intelligence Engine**! MWIE is an open-source project committed to advancing transparent, cost-efficient, and self-hosted web intelligence for SEO, GEO, and autonomous AI agents.

---

## Code of Conduct

1. Be respectful and constructive.
2. Value evidence, reproducibility, and rigorous engineering over hype.
3. Adhere strictly to open-source licensing integrity and clean-room implementation practices.

---

## Development Workflow

1. **Fork and Clone:**
   ```bash
   git clone https://github.com/tmolavi/molavi-web-intelligence.git
   cd molavi-web-intelligence
   ```

2. **Install Dependencies:**
   ```bash
   pip install -e ".[dev]"
   ```

3. **Run Code Verification & Tests:**
   ```bash
   make lint
   make test
   ```

4. **Submit a Pull Request:**
   - Ensure all new features are accompanied by tests.
   - Maintain full backwards compatibility.
   - Keep commits atomic and descriptive.
