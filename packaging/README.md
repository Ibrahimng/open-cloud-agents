# 📦 Open Cloud Agents: Package Distribution Directory

This directory contains standalone packaging specifications and distribution metadata for the `ocagents` CLI across major system package managers.

---

## 🗂️ Package Formats

| Package Manager | Platform | Spec Path | Install Command |
|---|---|---|---|
| **Universal Shell** | macOS / Linux | [`install.sh`](../install.sh) | `curl -fsSL https://open-cloud-agents.github.io/ocagents/install.sh \| bash` |
| **PowerShell** | Windows | [`install.ps1`](../install.ps1) | `irm https://open-cloud-agents.github.io/ocagents/install.ps1 \| iex` |
| **Homebrew** | macOS / Linux | [`Formula/ocagents.rb`](../Formula/ocagents.rb) | `brew install Ibrahimng/tap/ocagents` |
| **Python / PyPI** | Universal | [`pyproject.toml`](../pyproject.toml) | `pipx install open-cloud-agents` |
| **Windows Package Manager** | Windows | [`packaging/winget/manifest.yaml`](./winget/manifest.yaml) | `winget install Ibrahimng.OpenCloudAgents` |
| **Alpine Linux (APK)** | Alpine / Docker | [`packaging/alpine/APKBUILD`](./alpine/APKBUILD) | `apk add ocagents` |
| **Debian / Ubuntu (APT)** | Debian / Ubuntu | [`packaging/debian/control`](./debian/control) | `apt install ocagents` |

---

## 🚀 Releasing New Versions

For the complete architectural design of our two-tier update system and automated CI/CD release channels, refer to [**Package Distribution & Streamlined Update Channels**](../docs/package-distribution-and-updates.md).

1. Update version number across:
   - `src/ocagents/__init__.py`
   - `src/ocagents/cli.py`
   - `pyproject.toml`
   - `Formula/ocagents.rb`
   - `packaging/winget/manifest.yaml`
   - `packaging/alpine/APKBUILD`
2. Run validation suite:
   ```bash
   python3 scripts/ci/validate_repo.py
   python3 scripts/agents/agent_pipeline.py --validate
   ```
3. Prepare docs for GitHub Pages hosting:
   ```bash
   python3 scripts/docs/prepare_docs.py
   ```

