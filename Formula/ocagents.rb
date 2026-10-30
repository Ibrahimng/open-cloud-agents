# Homebrew Formula for Open Cloud Agents (ocagents)
class Ocagents < Formula
  include Language::Python::Virtualenv

  desc "Universal CLI & specialist agents for Cloud Architecture, DevSecOps, SRE, and FinOps"
  homepage "https://open-cloud-agents.github.io/ocagents/"
  url "https://github.com/open-cloud-agents/ocagents/archive/refs/tags/v1.3.0.tar.gz"
  sha256 "415449f310f1c583414764b543352770fb8a40d5289e22e2744db969d291e621"
  license "Apache-2.0"
  head "https://github.com/open-cloud-agents/ocagents.git", branch: "main"

  depends_on "python@3.12"

  resource "pyyaml" do
    url "https://files.pythonhosted.org/packages/54/ed/79a089b6be93607fa5cdaedf301d7dfb23af5f25c398d5ead2525b063e17/pyyaml-6.0.2.tar.gz"
    sha256 "d584d9ec91ad65861cc08d42e834324ef890a082e591037abe114850ff7bbc3e"
  end

  def install
    pkgshare.install "agents", "skills", "rules", "scripts"
    venv = virtualenv_create(libexec, "python3.12")
    venv.pip_install resources
    venv.pip_install buildpath

    (bin/"ocagents").write <<~EOS
      #!/usr/bin/env bash
      export OCAGENTS_HOME="${OCAGENTS_HOME:-#{opt_pkgshare}}"
      exec "#{libexec}/bin/ocagents" "$@"
    EOS

    (bin/"oca").write <<~EOS
      #!/usr/bin/env bash
      exec "#{bin}/ocagents" "$@"
    EOS

    chmod 0755, bin/"ocagents"
    chmod 0755, bin/"oca"
  end

  test do
    assert_match "Open Cloud Agents", shell_output("#{bin}/ocagents info")
    assert_match "Principal Cloud Architect", shell_output("#{bin}/ocagents list")
  end
end
