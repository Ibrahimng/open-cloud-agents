# Homebrew Formula for Open Cloud Agents (ocagents)
class Ocagents < Formula
  desc "Universal CLI & specialist agents for Cloud Architecture, DevSecOps, SRE, and FinOps"
  homepage "https://ibrahimng.github.io/open-cloud-agents/"
  url "https://github.com/Ibrahimng/open-cloud-agents/archive/refs/tags/v1.3.0.tar.gz"
  sha256 "0000000000000000000000000000000000000000000000000000000000000000" # Updated on release tagging
  license "Apache-2.0"
  head "https://github.com/Ibrahimng/open-cloud-agents.git", branch: "main"

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
    system "#{bin}/ocagents", "info"
    system "#{bin}/ocagents", "list"
  end
end
