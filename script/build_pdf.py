"""Convert presentation_script.md to presentation_script.pdf.

Handles the Markdown used in the script: ## headings, paragraphs, `[click]`
cues, "-> next slide" lines, - bullet lists, *italic*, **bold** and tables.
Usage: python3 build_pdf.py   (needs lualatex)
"""
import pathlib
import re
import subprocess

HERE = pathlib.Path(__file__).resolve().parent
SRC = HERE / "presentation_script.md"
BUILD = HERE / "build"
TITLE = "Presentation Script: Energy-Aware Hybrid Recommender Systems Across the User Lifecycle"


def inline(text):
    text = text.replace("\\", r"\textbackslash{}")
    for ch in "&%$#_{}":
        text = text.replace(ch, "\\" + ch)
    text = text.replace("~", r"\textasciitilde{}").replace("^", r"\textasciicircum{}")
    text = text.replace("→", r"$\rightarrow$").replace("α", r"$\alpha$")
    text = re.sub(r"\*\*(.+?)\*\*", r"\\textbf{\1}", text)
    text = re.sub(r"\*(.+?)\*", r"\\emph{\1}", text)
    text = re.sub(r"`(.+?)`", r"\\texttt{\1}", text)
    text = re.sub(r'"(.+?)"', r"``\1''", text)
    return text


def convert(md):
    out, para, items, table = [], [], [], []

    def flush():
        if para:
            out.append(inline(" ".join(para)) + "\n")
            para.clear()
        if items:
            out.append("\\begin{itemize}\n" + "".join(f"  \\item {inline(i)}\n" for i in items) + "\\end{itemize}\n")
            items.clear()
        if table:
            rows = [r for r in table if not re.fullmatch(r"\|[\s:|-]+\|", r)]
            cells = [[c.strip() for c in r.strip("|").split("|")] for r in rows]
            n = len(cells[0])
            body = [" & ".join(inline(c) for c in row) + r" \\" for row in cells]
            out.append("\\begin{center}\\small\n\\begin{tabular}{" + "l" * n + "}\n\\toprule\n"
                       + body[0] + "\n\\midrule\n" + "\n".join(body[1:]) + "\n\\bottomrule\n\\end{tabular}\n\\end{center}\n")
            table.clear()

    for line in md.splitlines():
        s = line.strip()
        if not s or s == "---":
            flush()
        elif s.startswith("# "):
            flush()
        elif s.startswith("## "):
            flush()
            out.append(f"\\section*{{{inline(s[3:])}}}\n")
        elif s == "`[click]`":
            flush()
            out.append("\\click\n")
        elif s.startswith("→"):
            flush()
            out.append("\\nextslide\n")
        elif s.startswith("- "):
            if para:
                flush()
            items.append(s[2:])
        elif s.startswith("|"):
            table.append(s)
        else:
            para.append(s)
    flush()
    return "\n".join(out)


PREAMBLE = r"""\documentclass[11pt,a4paper]{article}
\usepackage[margin=2.2cm]{geometry}
\usepackage{fontspec}
\usepackage{booktabs}
\usepackage{xcolor}
\usepackage{titlesec}
\usepackage{parskip}
\usepackage[hidelinks]{hyperref}
\definecolor{TUMBlue}{HTML}{0065BD}
\titleformat{\section}{\large\bfseries\color{TUMBlue}}{}{0pt}{}
\titlespacing*{\section}{0pt}{1.6em}{0.5em}
\newcommand\click{\par{\small\color{TUMBlue}\textbf{[click]}}\par}
\newcommand\nextslide{\par{\small\color{gray}$\rightarrow$ next slide}\par}
\setlength{\parskip}{0.7em}
\linespread{1.15}
\begin{document}
{\LARGE\bfseries """ + TITLE + r"""\par}
\vspace{1em}
"""


def main():
    BUILD.mkdir(exist_ok=True)
    tex = BUILD / "presentation_script.tex"
    tex.write_text(PREAMBLE + convert(SRC.read_text()) + "\n\\end{document}\n")
    subprocess.run(["lualatex", "-interaction=nonstopmode", "-halt-on-error", tex.name],
                   cwd=BUILD, check=True, stdout=subprocess.DEVNULL)
    (BUILD / "presentation_script.pdf").replace(HERE / "presentation_script.pdf")
    print("wrote", HERE / "presentation_script.pdf")


if __name__ == "__main__":
    main()
