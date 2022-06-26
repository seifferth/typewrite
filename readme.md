# Typewrite – convert text files into PDFs with a typewritten look

```
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
```

## Dependencies

typewrite should work on any UNIX-like operating system. It requires
`python3` and `lualatex` to be available in the `PATH`.
