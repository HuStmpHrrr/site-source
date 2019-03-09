Comparison Between Different DOTs
=================================

:date: 2019-03-09
:tags: DOT, programming languages, research
:category: Research
:authors: Jason Hu
:summary: A comparison between different versions of Dependent Object Types
          (DOTs). The thought put in this blog might or might not be published in the
          future, but nonetheless something worth mentioning before I entirely forget
          about it.

Introduction
############

Last week, Ondřej, Marianna and I was discussing the differences between two different
definitions of Dependent Object Types (DOTs). The original motivation was that I had
to make the technical decision of which DOT I am supposed to work on for my Master's
thesis. Though the decision was made before the discussion occurred, I think the
discussion was very fruitful, and it should be made public. I am not sure if the
content from this blog will eventually become a paper, because it depends on my
timeline, as well as Ondřej's. On the other hand, I suppose it's very important for a
researcher who attends to work on DOT, and wanting to make their technical decision as
well.

Here, I will focus my discussion on OOPSLA DOT [1]_ and Wadlerfest DOT [2]_.

The Comparison
##############

Following are some discussion on the calculi, but before that, I should probably
describe a main feature in these calculi to make the problem clearer.

Path Dependent Types
--------------------

In Scala, a class can have type members. In DOT, we call it type tags.

.. code-block:: scala

  class Foo {
    type A >: Foo <: Bar
  }
  val x : Foo = ???
  // then in the future, one may refer to the type inside of Foo
  val y : x.A = ???

In the notation `>:` means that `Foo` is some subtype of `A`, and `<:` means `Bar` is
some supertype of `A`. Now consider the following piece of code.

.. code-block:: scala

  val z1 : Foo = ???
  val z2 : x.A = z1
  val z3 : Bar = z2

`x.A` in the second is what we called path dependent types. We refer to the hidden
type inside of the object via member access. This piece of code shows something very
strange. To begin with, the code has nothing to do with particular `Foo` or
`Bar`. That means one can turn any types into any other types. From theoretical point
of view, in the core calculus, we don't really need this assignment sequence to
achieve the same result. Instead, we rely on a fundamental property from the calculus,
transitivity.

.. math::

   \frac{\Gamma \vdash S <: T \quad \Gamma \vdash T <: U}{\Gamma \vdash S <: U}
  
Relying in transitivity, we can derive `z1` having type `Bar` immediately. However,
such derivation can only be made possible, if `x` is in the context to begin
with. Namely, there needs to be some instance of `Foo` we can refer to: note that path
dependent types only works for existing variables. 

This is a core feature in the new Scala, Dotty, and these two calculi are supposed to
model the behavior of path dependent types. 

   
Context Truncation in OOPSLA DOT
--------------------------------

In OOPSLA DOT, we can discover that the :math:`Sel` rules have the following form
(e.g. :math:`Sel_1`).

.. math::

   \frac{\Gamma_{[x]} \vdash x :_! (L : T .. \top)}{\Gamma \vdash T <: x.L}


In this notation, :math:`\Gamma_{[x]}` denotes that the bindings after :math:`x` from
context :math:`\Gamma` are truncated (but :math:`x` is kept). 

On the other hand, Wadlerfest DOT has no such truncation.

.. math::

   \frac{\Gamma \vdash x : \{L : S .. U \}}{\Gamma \vdash S <: x.L}

This treatment, effectively, is used to regulate the behavior of path dependent
types. Consider the following (strange) program.

.. code-block:: scala

  def foo(x : List[Any])(y : { type A >: List[Any] <: List[Nothing] }) : Nothing = x.head

Consider the generic type of `List` can be accessed via `x.T`. In Wadlerfest DOT, this
is a valid program, as witnessed by the following proof.

.. math::

   \dfrac
   {\dfrac{x,y \vdash x : List[Any] \quad x,y \vdash List[Any] <: List[Nothing]}
   {x,y \vdash x : List[Nothing]}}
   {x,y \vdash x.T <: Nothing}
  
For brievity, I omitted the types bound to the variables in the context, and some
sub-derivations that are obvious to see. However, in OOPSLA DOT, the subderivation of
:math:`x,y \vdash List[Any] <: List[Nothing]` doesn't work. This is because the
context truncation in the :math:`Sel` rules. Since :math:`x,y \vdash x.T <: Nothing`
is a conclusion of :math:`Sel_2` rule, any sub-derivations after that point have lost
:math:`y`, and that makes this derivation impossible in the OOPSLA DOT.

That's why I called context truncation behavior is **regulating** the behavior of path
dependent types. Due to the context truncation, there is no way to impose further
subtyping relation after the definition of some object. Whereas in Wadlerfest DOT,
there is no such problem.

:math:`:!` Typing Doesn't Have :math:`Pack` rule
------------------------------------------------


   

.. [1] OOPSLA DOT, OOPSLA 16, http://lampwww.epfl.ch/~amin/dot/soundness_oopsla16.pdf
.. [2] Wadlerfest DOT, Wadlerfest, https://infoscience.epfl.ch/record/215280/files/paper_1.pdf
