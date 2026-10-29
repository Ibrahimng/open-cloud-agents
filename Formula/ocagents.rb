# Homebrew Formula for Open Cloud Agents (ocagents)
class Ocagents < Formula
  desc "Universal CLI & specialist agents for Cloud Architecture, DevSecOps, SRE, and FinOps"
  homepage "https://open-cloud-agents.github.io/ocagents/"
  url "https://github.com/open-cloud-agents/ocagents/archive/refs/tags/v1.3.0.tar.gz"
  sha256 "7878b85cb6cbe642a21f787601e03d723a5994d04bcf5687714f6d0da474c3a1"
  license "Apache-2.0"
  head "https://github.com/open-cloud-agents/ocagents.git", branch: "main"

  depends_on "python@3.12"

  def install
    pkgshare.install "agents", "skills", "rules", "scripts", "src"

    (bin/"ocagents").write <<~EOS
      #!/usr/bin/env bash
      export OCAGENTS_HOME="#{opt_pkgshare}"
      exec "#{Formula["python@3.12"].opt_bin}/python3.12" "#{opt_pkgshare}/src/ocagents/cli.py" "$@"
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
