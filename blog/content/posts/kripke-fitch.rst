Modal Systems in Kripke and Fitch styles
========================================

:date: 2022-06-20
:tags: modal logic
:category: Types
:authors: Jason Hu
:summary: A comparison of formulations of modal type systems in Kripke and Fitch
          styles



Summary
-------

Primary difference is that Kripke style uses context stacks while Fitch style uses
locks.  But this difference is syntactic, and primarily philosophical, not
technical. One can probably find an easy correspondence but they have different
sources of inspirations.

Kripke style, as indicated by its name, is inspired from Kripke semantics. On the
other hand, Fitch style is popularized by Clouston, who followed Borghuis. In
Borghuis' PhD thesis, he derived modal pure type systems (PTS) from Fitch's
subcoordinate proof diagrams. Borghuis never used Fitch style to refer to a type
system. He only used it to refer to that particular kind of subcordinate proof
diagrams. Technically, Fitch in Fitch style really denotes the particular proof
diagrams or form of proof presentation which Fitch invented and Borghuis
considered. However, Fitch-style systems do not really have this form of subordination
in their formulations, nor do Fitch-style systems use context stacks as Borghuis
originally did (he called them generalized contexts). This makes Fitch style more or
less a historically inaccurate name, at least less accurate than Borghuis style. 

**TODO: More Comparison**
