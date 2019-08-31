A Complement of My Thesis: Naming Conventions and Choice of Proof Assistants
============================================================================

:date: 2019-08-15
:tags: DOT, programming languages, research, proof assistants
:category: Scala / DOT
:authors: Jason Hu
:summary: An explanation of why I separate decidability analysis and algorithmic
          analysis into Agda and Coq in the technical work of my master's thesis.

In my `thesis <https://gitlab.com/JasonHuZS/AlgDotCalculus>`_, I exclusively used Agda
for decidability analysis and and Coq for algorithmic analysis. This decision is based
on an unobvious technical observation. This blog explains this technical observation,
and why it would have been extremely difficult to work out the same undecidability
proof in Coq.

Summary
-------

To give a high-level summary, the main difficulties to establish the same proof in Coq
as in Agda are:

1. inference rules live in Prop instead of Type, 
2. names are represented by locally nameless and cofinite representation in
   formalization in Coq, and
3. termination checking in Coq requires a specified decreasing structure.

This difficulties are mainly encountered when attempting to show transitivity of
:math:`D_{<:}` normal form (Theorem 3.20).  These points requires more careful
technical setup to be fully clear.

``Type`` and ``Prop``
---------------------

Though the majority of my work is in Coq, the undecidability proofs discussed in
Chapter 3, were done in Agda. This is not simply for reasons like “wow, it would be
cool to use two proof assistants”, but for something more fundamental.

The first difficulty is about proof relevant universes versus proof irrelevant
universes. Up until Agda 2.5.4.2, Agda has no universe for propositions (but there is
one now in Agda 2.6+), which means the entire language resides in a predicative
universe hierarchy (called ``Set``\ s). On the other hand, Coq is way more
complicated. It has not only the predicative universe hierarchy as in Agda (called
``Type``\ s), but also other two universes, ``Set`` and ``Prop``. It is very
misleading that ``Set`` in Coq is not the same as ``Set``\ s in Agda. Specifically,
``Set`` in Coq is a small universe which can only contain data. ``Set``\ s in Agda
corresponds to ``Type``\ s in Coq.

The problem here is that ``Prop`` in Coq is a proof irrelevant universe. Proof
irrelevance is a concept stating that terms inhabited in types that are ``Prop`` are
purely logical and any two proofs of the same proposition are considered identical. A
``Prop`` in Coq can only be eliminated into data (``Set`` and ``Type``) when the
definition of the ``Prop`` satisfies *singleton elimination principle*.

In programming languages, it is a convention to put inference rules in
``Prop``. Therefore, libraries designed for programming languages researchers assumes
it is the case.

First, let me explain what ``Prop`` cannot do. Consider the following two types.

.. math::

   \begin{aligned}
     \exists x, P(x) \\
     \Sigma x, P(x)
   \end{aligned}

The first one is existential quantification, which is typical in logic.  It simply
confirms the existence of something but gives away no precise information of the
witness. The second one is called a :math:`\Sigma` type and represents a pair, where
the type of the second element depends on the value of the first element. For example,
let us assume

.. math::

   \begin{aligned}
     x \in \{\text{morning}, \text{noon}, \text{evening}\}
   \end{aligned}

and :math:`P` is meal. If :math:`x` is morning, then :math:`P(x)` is breakfast, and
cereal is one of the values. If :math:`x` is evening, then :math:`P(x)` is dinner, and
steak is one of the values. Having a :math:`\Sigma` type, I can know the time,
together with a concrete proof that there will be a meal at that time. This is because
:math:`\Sigma` type stores data. In general,

.. math::

   \begin{aligned}
     \Sigma x, P(x) \Rightarrow \exists x, P(x)\end{aligned}

This is because one can always forget about the information. Instead of saying the
information is about the dinner in the evening, I can always forget about the time and
only be concerned about the fact that there will be food for the day without even
caring about when it is. Clearly, I have lost information by going through this
direction.

Though consistent with the theory, the other way is not generally provable.

.. math::

   \begin{aligned}
     \exists x, P(x) \nRightarrow \Sigma x, P(x)\end{aligned}

This direction requires an axiom, called the *indefinite description* or *Hilbert’s*
:math:`\epsilon`. This axiom turns out to be very strong as it can be used to prove
the axiom of choice. In short, the proof irrelevant nature of universe ``Prop``
forgets the internal structures of derivations of inference rules and prevents
their treatment as pieces of data, because in ``Prop``, any two proofs of the same
conclusion are considered the same.

However, when considering undecidability proof, I have to consider interactions
between features in a judgment derivation using Gentzen's style of proof
induction. This, in turn, is to treat proofs as prices of structural data. This view
naturally contradicts to the philosophy of proof irrelevance.

This problem is fundamental. Technically, the barrier between ``Prop`` and ``Type`` is
firm in Coq. Since there is virtually no way to extract data information from ``Prop``
(except when the definition satisfies singleton elimination which is very often not
the case), if a proof step requires induction on a definition in ``Prop``, then it
forces all other dependent definitions into ``Prop`` as well. An alternative solution
is to turn this definition a ``Type``, which is not always possible.

In contrast, Agda has no proof irrelevant universe, so such problem simply does not
occur. Even in Agda 2.6, the majority of concepts are defined in `Set`\ s, which
limits the troubles created by proof irrelevance. 

In my opinion, most of the proof techniques in programming languages are representable
in first order fragment of intuitionistic type theory, so requirement of ``Prop`` does
not look justified. For other proofs that cannot be shown in the first order fragment,
it is likely that having ``Prop`` is not going to resolve this issue.  It appears
``Prop`` does not give many advantages from this perspective. Therefore, working with
proof relevant universes had been a much better choice.

It might still have been still possible to establish transitivity of :math:`D_{<:}`
normal form. However, a particular name representation had introduced significant
difficulties to the problem which makes establishment of the property very unlikely.

Name Representations
--------------------

In informal presentation of programming languages, we often use Barendregt's
convention of :math:`\alpha` conversions. That is, all terms and types are considered
the same if free variables are the permuted. In formal analysis, however, such
equivalence is too abstract to represent. Very often, other name representations are
used instead. Among these representation, de Bruijn indices are one choice. In de
Bruijn indices, each name is presented as a natural number, indexing the
telescope. Intuitively, de Bruijn indices take a quotient of the set of terms and
types over all names.

Another possibility is locally nameless representation with cofinite quantification
(or LN-cofinite in short). In this representation, a name has dual representation: a
string when bound in the telescope, or a de Bruijn index when is closed in a term or a
type. 

There are many advantages of LN-cofinite in the context of soundness proofs. However,
this name representation does not have all advantages over other name representations,
and there is one particular issue with LN-cofinite which gives substantial trouble
with interacting with ``Prop``. 

Cofinite quantification
~~~~~~~~~~~~~~~~~~~~~~~

[1]_ introduced LN-cofinite as an answer to the POPLmark challenges. In LN-cofinite,
when a fresh name is needed, such free name is specified by a universal
quantification, with a condition of not being contained in a specific finite name
store, hence *cofinite*. For ease of presentation, I will use :math:`F_{<:}^-` has an
example. Note that there are other ways to resolve the situation in :math:`F_{<:}^-`,
because it is not as complicated as :math:`D_{<:}`. I use :math:`F_{<:}^-` only
because it has less rules and it is exposed to the same problem.

.. math::
   \begin{aligned}
   &\dfrac{ }{\Gamma \vdash T <: \top} \text{(Top)} \quad
   \dfrac{ }{\Gamma \vdash X <: X} \text{(Refl)} \quad
   \dfrac{X <: T \in \Gamma \quad \Gamma \vdash T <: U}{\Gamma \vdash X <: U}
   \text{(Var)} \\\\
   &\dfrac{\Gamma \vdash S_2 <: S_1 \quad \Gamma ; X <: S_2 \vdash U_1 <: U_2}{\Gamma
   \vdash \forall X <: S_1. U_1 <: \forall X <: S_2. U_2} \text{(All)}
   \end{aligned}

Notice that this definition of :math:`F_{<:}^-` uses Barendregt's convention as it
implicitly requires :math:`\alpha` conversion in the All rule when drawing a fresh
:math:`X` as a type variable.  A formal definition using LN-cofinite would define the
All rule alternatively as follows:

.. math::
   \dfrac{\Gamma \vdash S_2 <: S_1 \quad \Pi X, X \notin L \to \Gamma ; X <: S_2 \vdash U_1 <: U_2}{\Gamma
   \vdash \forall X <: S_1. U_1 <: \forall X <: S_2. U_2} \text{(All')}

I use :math:`\Pi` to denote universal quantification in type theory, in order to
distinguish the symbol :math:`\forall` which has been used as a part of the syntax in
:math:`F_{<:}^-`.

Notice that, in this formal definition, :math:`L` is a finite name store. The second
premise in All' holds for any :math:`X` that is not contained in :math:`L`.  That is,
in this judgment, it remembers a finite set of names :math:`L`, and the fresh names
drawn in the second premise must avoid :math:`L`. Since the set of all names are
countably infinite, excluding a finite number of them will not exclude all names. In
a universal type, e.g.  :math:`\forall X <:S.U`, :math:`X` on the other hand, is
presented by a de Bruijn index, and it is 0 in this case.

Noncanonical derivation of cofinite quantification
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

LN-cofinite captures much intuition, but there are gaps between it and Barendregt's
convention. In particular, with :math:`\alpha` conversion, we usually consider a
given derivation has fixed subderivations; namely, the shape of any subderivation is
fixed up to permutations of names. This assumption, unfortunately, is *false* with
LN-cofinite. 

Let us consider the All' rule again:

.. math::
   \dfrac{\Gamma \vdash S_2 <: S_1 \quad \Pi X, X \notin L \to \Gamma ; X <: S_2 \vdash U_1 <: U_2}{\Gamma
   \vdash \forall X <: S_1. U_1 <: \forall X <: S_2. U_2} \text{(All')}

In this rule, the second premise resides in a universal quantification, which is a
function space in the type theory. Since it is a :math:`\Pi` type, the proof term is
some function. Consider the following implementation:

.. code-block:: coq

      fun X (X_notin_L : X `notin` L) =>
        if X == Y then (* ... a proof term specialized for Y *)
        else if X == Z then (* ... a proof term specialize for Z *)
        else (* ... other proof terms *)

In particular, proof terms when :math:`Y` is picked and :math:`Z` is picked do not
have to look the same. This is even worse when transitivity and reflexivity are a part
of the definition. For any derivation :math:`D` which witnesses :math:`\Gamma \vdash S
<: U`, following derivation is also a witness of the same conclusion:

.. math::
   \dfrac{\Gamma \vdash S <: U \quad \Gamma \vdash U <: U\text{(Refl)}}{\Gamma \vdash S <: U}\text{(Trans)}

Define this trivial expansion of derivation tree :math:`f(D)`. Since a set of names
excluding any finite set remains countably infinite, there exists an isomorphism
between this set and natural numbers. Call this isomorphism :math:`I`. Consider a
proof :math:`H` witnessing :math:`\Pi X, X \notin L \rightarrow
\Gamma; X <: S' \vdash U_X <: U'_X`.  Then one can derive a proof term, so that
the forms of the subtyping derivations between return types generated by different
type variables are completely “distorted”.

.. math::

   \begin{aligned}
     H' &: \Pi X, X \notin L \Rightarrow \Gamma; X <: S' \vdash U_X <: U'_X \\
     H' &:= \lambda X (N : X \notin L). Rec(I(X), H(X, N))  \\
     Rec(0, D) &:= D \\
     Rec(1 + n, D) &:= Rec(n, f(D))
     \end{aligned}

The idea is that :math:`H'` expands an existing proof :math:`H` using the expansion
function above so that a pair of derivations generated by two difference choices of
names are not going to be the same.

In the construction of :math:`H'`, I first extract an existing proof from
:math:`H`. Then for any given valid choice of name :math:`X`, the isomorphism
:math:`I` between the set of names and natural numbers converts :math:`X` to a natural
number. This natural number is used to count the number of interations of applications
of :math:`f` to the existing proof. Since any two distinct names are not mapped to the
same natural numbers, and there are infinite number of names, it is clear that sizes
of derivations in :math:`F_{<:}^-` are in generally not measurable by natural numbers.

On the other hand, we assume derivations are trees and therefore their depths can be
measured by natural numbers. This distinction is not quite compatible with the
classical view of Gentzen's style proof induction.


Termination Checking
--------------------

Before turning our attention to the problem with LN-cofinite, it is worth briefly
mentioning the strategies of termination checking in Coq and Agda.

Though very often inferred, termination checking in Coq indeed requires a specified
``struct`` parameter so that the termination checker knows which structure the
fixpoint decreases on. This strategy works similar in both ``Prop`` and ``Type`` in
Coq.

On the other hand, in Agda, the strategy is slightly different. In Agda, the
termination checker directly checks each call site of the function being defined (or
functions in the context of mutual definitions) to ensure the parameters are
decreasing in a lexicographical order. Note that this method is weaker than the one used
in Coq, though ultimately equivalent as it can be done manually in Coq by using some
well-founded induction.

That being said, sometimes this distinction can induce significant differences of
engineering effort. The problem is much easier to surface when considering
well-founded induction of some ``Prop``, e.g. well-founded induction on the depth of
the derivations.


Interacting with ``Prop``
-------------------------

There are various proofs in my thesis requiring well-founded induction on the number
of steps in the derivation of a judgment. On paper, this is usually not a problem; as
indicated earlier, we often consider a derivation is a (finite) tree and therefore
there is always a maximum depth of a derivation, following Gentzen's style. However,
in a previous section, I showed that this view is not well compatible with
LN-cofinite, as there are subderivations living in function spaces. Note that I will
be using :math:`F_{<:}^-` as an example here for ease of presentation. However, there
are workarounds for the problem presented here, so :math:`F_{<:}^-` itself does not
suffer much from it. My point is that, in more sophisticated proofs like transitivity
of :math:`D_{<:}`, due to the intervene of complex inductive scheme, a workaround does
not seem to exist, and therefore the problem about to be presented here is more
significant for those calculi. 

Let us consider how to measure the size of a derivation if it is defind in
``Type``. As shown previously, natural numbers are not big enough, so the following
definition is used instead.

.. code-block:: coq

    Inductive card : Type :=
    | base : card
    | rec : card -> card
    | clsr : forall L, card -> (forall x, x `notin` L -> card) -> card.

In this definition, ``card`` stands for cardinal. If the subtyping relation is defined
in ``Type``, then a function can be defined to convert the derivation to ``card``. One
can easily define a well-founded relation on ``card``, and therefore it is possible to
do well-founded induction with LN-cofinite.  However, if the subtyping relation is
defined in ``Prop``, as it is usually done, then ``card`` does not measure the size of
a derivation anymore.

The first trouble is, one cannot define a function converting a derivation to a
``card``, because it would require elimination from ``Prop`` to ``Type``, which is in
general not possible except when the ``Prop`` satisfies singleton elimination
principle.

A possible solution to this, is to use a relation to associate every derivation with a
measure. That is the following equivalence:

.. math::

   \begin{aligned}
     \Gamma \vdash S <: U \Leftrightarrow \exists c, \Gamma \vdash [ c ] S <: U
   \end{aligned}

The equivalence shows an equivalence between the original subtyping relation and an
enriched subtyping relation, denoted by :math:`\Gamma \vdash [ c ] S <: U`. In this
relation, :math:`\Gamma`, :math:`S` and :math:`U` represent precisely what
:math:`\Gamma \vdash S <: U` means. In addition to that, a fourth parameter :math:`c`
represents the cardinal of :math:`\Gamma \vdash S <: U`, defined by ``card``
aboved. That is, :math:`c` is used to remember the cardinal of a given subtyping
derivation.  For completeness, the full definition of this four-place relation is
defined as follows:

.. math::
   \begin{aligned}
   &\dfrac{ }{\Gamma \vdash [\texttt{base}] T <: \top} \text{(C-Top)} \quad
   \dfrac{ }{\Gamma \vdash [\texttt{base}] X <: X} \text{(C-Refl)} \\\\\
   &\dfrac{X <: T \in \Gamma \quad \Gamma \vdash [\texttt{c}] T <: U}{\Gamma \vdash [\texttt{rec
   c}] X <: U}
   \text{(C-Var)} \\\\
   &\dfrac{\Gamma \vdash [\texttt{c}] S_2 <: S_1 \quad \Pi\; X\; (NI : X \notin L), \Gamma ;
   X <: S_2 \vdash [\texttt{d X NI}] U_1 <: U_2}{\Gamma
   \vdash [\texttt{clsr c d}] \forall X <: S_1. U_1 <: \forall X <: S_2. U_2} \text{(C-All)}
   \end{aligned}

Reviewing these rules, one can realize that indeed the cardinal measures a
derivation. It is easy to show that 

.. math::

   \begin{aligned}
     \exists c, \Gamma \vdash [ c ] S <: U \Rightarrow \Gamma \vdash S <: U
   \end{aligned}

This can be proved by forgetting :math:`c`.

However, the other direction is not quite easy.

.. math::

   \begin{aligned}
     \Gamma \vdash S <: U \Rightarrow \exists c, \Gamma \vdash [ c ] S <: U
   \end{aligned}

This is because the subtyping relation lives in ``Prop`` and that the All' rule uses a
function space for its subderivation. Consider a proof attempt by induction. The All'
rule generates the following antecedents in the proof context:

1. :math:`\Gamma \vdash S_2 <: S_1`,
2. :math:`\Pi X, X \notin L \to \Gamma ; X <: S_2 \vdash U_1 <: U_2`,
3. :math:`\Gamma \vdash [\texttt{c}] S_2 <: S_1`,
4. :math:`\Pi X, X \notin L \to \exists d, \Gamma ; X <: S_2 \vdash [\texttt{d}] U_1 <: U_2`,

The goal is

.. math::

   \exists e, \Gamma \vdash [\texttt{e}] \forall X <: S_1. U_1 <: \forall X <: S_2. U_2

According to the C-All rule, this :math:`e` is constructed by ``clsr``, and `c` is
already known. The trouble is :math:`d`, which has type :math:`\Pi X, X \notin L \to
\texttt{card}`.  This ought to be constructed from the fourth antecedent. However,
this cannot be done. Notice that this target type is in ``Type``, while the fourth
antecedent lives in ``Prop``. Due to the isolation between ``Prop`` and ``Type``, one
cannot construct a ``Type`` out of ``Prop`` (clearly this function space does not
satisfy singleton elimination).

Looking at the form of the fourth antecedent, to derive :math:`\Pi X, X \notin L \to
\texttt{card}`, at least the axiom of Choice seems necessary. Surely this can be done
by postulating it, as Choice is compatible with Coq. If one resists postulating axioms
in type theory, it has come to a deadend. Yet, if de Bruijn indices are used, there is
no need to use other axioms. Namely, :math:`\Gamma \vdash S <: U \Rightarrow \exists
c, \Gamma \vdash [ c ] S <: U` can already be proven purely constructively with de
Bruijn indices. 

Conclusion
----------

In this blog, I showed that how LN-cofinite interacts with ``Prop`` and introduces the
need of some external axiom. This is quite unexpected, as it has nothing to do with
Barendregt's convention at all, but is a very technical detail of the choice of name
representation. With Gentzen's style proof induction, one treats proof derivations as
trees which directly conflicts with the nature of LN-cofinite. It means that the
choice of name representation is highly non-trivial depending on the problems and the
use of ``Prop`` universe needs to be carefully reviewed. 

.. [1] The Locally Nameless Representation, https://www.chargueraud.org/research/2009/ln/main.pdf
