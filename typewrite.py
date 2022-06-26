#!/usr/bin/env python3

import sys, subprocess
from tempfile import TemporaryDirectory

_texhead = r"""
\documentclass[a4paper]{minimal}
\usepackage[
    lmargin=2.3cm,rmargin=0.3cm,
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
  \immediate\pdfextension obj {
""".strip()
_textfilefoot = r"""
  }
\egroup
""".lstrip()
_textstreamend = b"""
\n\nendstream\nendobj\n
% This is the end of the file content's plain text version. What follows
% are mostly binary blobs used for displaying this file as pdf.
"""

def typewrite(text: str) -> bytes:
    textlength = len(text.encode('utf-8'))
    streamhead = f'<< /Length {textlength+3} >>\nstream\n\n' \
                                                .encode('utf-8')
    with TemporaryDirectory() as outdir:
        with open(f'{outdir}/document.tex', 'w') as f:
            f.write(_textfilehead)
            f.write(                                        # Add padding
                (len(streamhead)+textlength+len(_textstreamend)-7) * 'x'
            )
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
        textoffset = pdf.find(b'\n1 0 obj\n') + 9
        objoffset = textoffset + len(streamhead) + len(_textstreamend) + \
                    textlength
        return pdf[:textoffset] + streamhead + text.encode('utf-8') + \
               _textstreamend + \
               pdf[objoffset:]

_cli_help = """
Usage: typewrite <INPUT.TXT> <OUTPUT.PDF>

Produce a pdf version of a plain text file with a typewritten look.

The original plain text version will be included as the first object
in the pdf file and will not be used for anything. This way the pdf
file can simply be opened in a text editor in order to extract the
original plain text version located at the top of the file.

Typewrite processes form-feed characters to adjust page breaks
accordingly. In all other cases it simply breaks pages after 57 lines
of text. It is therefore possible to use old-school page formatting
commands like 'pr --length=57' to prepare text for typewrite.
""".lstrip()

if __name__ == "__main__":
    if '-h' in sys.argv or '--help' in sys.argv:
        print(_cli_help); exit(0)
    with open(sys.argv[1]) as infile:
        with open(sys.argv[2], 'wb') as outfile:
            outfile.write(typewrite(infile.read()))
