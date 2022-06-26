#!/usr/bin/env python3

import sys, subprocess
from tempfile import TemporaryDirectory

_texhead = r"""
\documentclass[a4paper]{minimal}
\usepackage[
    lmargin=2.3cm,rmargin=2.3cm,
    tmargin=2.7cm,bmargin=2.7cm,
]{geometry}
%!TEX program=lualatex
\providecommand\ttgreyone{.2}
\providecommand\ttgreytwo{.2}
\providecommand\ttrotatebold{0}
\providecommand\ttdownbold{0}
\providecommand\ttrightbold{0}
\providecommand\ttdownshifttwo{0}
\providecommand\ttrotatenormal{0}
\providecommand\ttrightnormal{0}
\providecommand\ttdownnormal{0}
\usepackage{typewriter}

\begin{document}
\pagestyle{empty}
\begin{verbatim}
""".lstrip()
_texfoot = r"""
\end{verbatim}
\end{document}
""".lstrip()
_texformfeed = r"""
\end{verbatim}
\newpage
\begin{verbatim}
""".lstrip()

_textfilehead = r"""
\bgroup
  \pdfvariable objcompresslevel=0
  \immediate\pdfextension obj file {
""".strip()
_textfilefoot = r"""
  }
\egroup
\immediate\pdfextension obj {
This is some placeholder text that will be removed later on. Its purpose
is to provide some padding that can be used in post-processing the pdf
file later on.
}
""".lstrip()
_textobjend = b"""
\nendstream\nendobj\n
% This is the end of the file content's plain text version. What follows
% are mostly binary blobs used for displaying this file as pdf.
"""

def typewrite(filename: str):
    with open(filename) as f:
        text = f.read()
    with TemporaryDirectory() as outdir:
        with open(f'{outdir}/document.tex', 'w') as f:
            f.write(_textfilehead)
            f.write(filename)
            f.write(_textfilefoot)
            f.write(_texhead)
            f.write(text.replace('\f', _texformfeed))
            f.write(_texfoot)
        subprocess.run(['lualatex',
                        '--interaction=nonstopmode',
                        f'--output-directory={outdir}',
                        f'{outdir}/document.tex'],
                       text=True, check=True)
        with open(f'{outdir}/document.pdf', 'rb') as f:
            pdf = f.read()
        textlength = len(text.encode('utf-8')) + 183
        textoffset = pdf.find(b'\n1 0 obj\n') + 9
        streamhead = f'<< /Length {textlength} >>\nstream\n'.encode('utf-8')
        return pdf[:textoffset] + streamhead + text.encode('utf-8') + \
               _textobjend + pdf[textoffset+textlength:]

_cli_help = """
Usage: typewrite <INPUT.TXT> <OUTPUT.PDF>
""".lstrip()

if __name__ == "__main__":
    if '-h' in sys.argv or '--help' in sys.argv:
        print(_cli_help); exit(0)
    with open(sys.argv[2], 'wb') as outfile:
        outfile.write(typewrite(sys.argv[1]))