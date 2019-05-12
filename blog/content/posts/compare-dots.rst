Comparison Between Different DOTs
=================================

:date: 2019-03-09
:tags: DOT, programming languages, research
:category: Scala / DOT
:authors: Jason Hu
:summary: A comparison between different versions of Dependent Object Types
          (DOTs). The thought put in this blog might or might not be published in the
          future, but nonetheless something worth mentioning before I entirely forget
          about it.

Introduction
############

Last week, Ondřej, Marianna and I were discussing the differences between two
different definitions of Dependent Object Types (DOTs). The original motivation was
that I had to make the technical decision of which DOT I am supposed to work on for my
`Master's thesis <https://gitlab.com/JasonHuZS/AlgDotCalculus>`_. Though the decision
was made before the discussion occurred, I think the discussion was very fruitful, and
it should be made public. I am not sure if the content from this blog will eventually
become a paper, because it depends on my timeline, as well as Ondřej's. On the other
hand, I suppose it's very important for a researcher who attempts to work on DOT, and
wants to make their technical decision as well.

Here, I will focus my discussion on OOPSLA DOT [1]_ and Wadlerfest DOT [2]_. Due to
limitation of space, it would directly dive into the technical details, without going
through the definition of the calculi. Going through all the definitions of DOTs
should really be the content of a survey paper, which is not what I am doing now, so
I'd expect this article might appear to be difficult for beginners.

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

In the notation :math:`>:` means that `Foo` is some subtype of `A`, and :math:`<:`
means `Bar` is some supertype of `A`. Now consider the following piece of code.

.. code-block:: scala

  val z1 : Foo = ???
  val z2 : x.A = z1
  val z3 : Bar = z2

`x.A` in the second line is what we called *path dependent types*. We refer to the
hidden type inside of the object via member access. This piece of code shows something
very strange. To begin with, the code has nothing to do with particular `Foo` or
`Bar`. That means one can turn any types into any other types. From theoretical point
of view, in the core calculus, we don't really need this assignment sequence to
achieve the same result. Instead, we rely on a fundamental property from the calculus,
transitivity.

.. math::

   \frac{\Gamma \vdash S <: T \quad \Gamma \vdash T <: U}{\Gamma \vdash S <: U} (Trans)
  
Relying on transitivity, we can derive `z1` having type `Bar` immediately. However,
such derivation can only be made possible, if `x` is in the context to begin
with. Namely, there needs to be some instance of `Foo` we can refer to: note that path
dependent types only works for existing variables. We refer to this characteristic of
connecting two arbitrary types with a path dependent type (or *path* in short), **bad
bounds**.

This is a core feature in the new Scala, Dotty, and these two calculi are supposed to
model the behavior of path dependent types. 

   
Context Truncation in OOPSLA DOT
--------------------------------

In OOPSLA DOT, we can discover that the :math:`Sel` rules have the following form
(e.g. :math:`Sel_1`).

.. math::

   \frac{\Gamma_{[x]} \vdash x :_! (L : T .. \top)}{\Gamma \vdash T <: x.L} (Sel_1)


In this notation, :math:`\Gamma_{[x]}` denotes that the bindings after :math:`x` from
context :math:`\Gamma` are truncated (but :math:`x` is kept).  

On the other hand, Wadlerfest DOT has no such truncation.

.. math::

   \frac{\Gamma \vdash x : \{L : S .. U \}}{\Gamma \vdash S <: x.L} (Sel_1')

This treatment, effectively, is used to regulate the behavior of path dependent
types. Note that in OOPSLA DOT, the typing is done via a variant with a bang
subscript. This difference will be discussed in the next section.  For the current
problem, consider the following (strange) program.

.. code-block:: scala

  def foo(x : List[Any])
         (y : { type A >: List[Any] <: List[Nothing] })
      : Nothing = x.head

Consider the generic type of `List` can be accessed via `x.T`. In Wadlerfest DOT, this
is a valid program, as witnessed by the following proof.

.. math::

   \dfrac
   {\dfrac{x,y \vdash x : List[Any] \quad x,y \vdash List[Any] <: List[Nothing]}
   {x,y \vdash x : List[Nothing]}}
   {x,y \vdash x.T <: Nothing} (Sel_1/Sel_1')
  
For brievity, I omitted the types bound to the variables in the context, and some
sub-derivations that are obvious to see. However, in OOPSLA DOT, the subderivation of
:math:`x,y \vdash List[Any] <: List[Nothing]` doesn't work. This is because the
context truncation in the :math:`Sel` rules. Since :math:`x,y \vdash x.T <: Nothing`
is a conclusion of :math:`Sel_2` rule, any sub-derivations after that point have lost
:math:`y`, and that makes this derivation impossible in the OOPSLA DOT. There doesn't
seem to other way to achieve the same conclusion in OOPSLA DOT either.

That's why I called context truncation behavior is **regulating** the behavior of path
dependent types. Due to the context truncation, how a path dependent type can behave
is fixed at its definition time.  There is no way to impose further subtyping relation
after that. Whereas in Wadlerfest DOT, this is possible. 

:math:`:!` Typing Doesn't Have :math:`Pack` rule
------------------------------------------------

As briefly mentioned above, there is yet another distinction between these two DOTs,
which is the bang type (:math:`:!`) in OOPSLA DOT. In OOPSLA DOT, there are following
two rules.

.. math::

   \frac{\Gamma \vdash x : T^x}{\Gamma \vdash x : \{z \Rightarrow T^z\}} (VarPack)
   \quad
   \frac{\Gamma \vdash x :_{(!)} \{z \Rightarrow T^z\}}{\Gamma \vdash x :_{(!)} T^x} (VarUnpack)

The subscript :math:`(!)` means that there is variant of the same rule for bang typing
(and without the subscript denote the regular typing). The formulation of these two
rules means that during bang typing, there cannot be :math:`VarPack` rule. The entries
for bang typing is :math:`Sel` rules (see one rule in the previous section). In
Wadlerfest DOT, the similar rules are
   
.. math::

   \frac{\Gamma \vdash x : T^x}{\Gamma \vdash x : \mu\{z : T^z\}} (Rec-I)
   \quad
   \frac{\Gamma \vdash x : \mu\{z : T^z\}}{\Gamma \vdash x : T^x} (Rec-E)

The syntax is different but :math:`\{x \Rightarrow T^x\}` and :math:`\mu\{x : T^x\}`
are the same thing. They both denote object types, which means all members in their
definitions can refer back to the object reference, and therefore their sibling
definitions as well. Now, consider how disallowing :math:`VarPack` rule (or
correspondingly :math:`Rec-I` rule) impact the expressiveness of the calculus.

.. math::

   T_1 &= \{A : \bot .. \top \} \\
   T_2 &= \{A : \bot .. \bot \} \\
   T_3 &= \{ foo : x.A \} \\
   T_4 &\text{ is irrelevant and not }\top.

The we can consider the following program. 

.. math::

  \text{def bar}& (y : \{ B :  \{z \Rightarrow T_1 \wedge T_4 \} .. \{ z \Rightarrow T_2 \wedge T_4\} \} ) \\
                & (x : \{x \Rightarrow T_1 \wedge T_3 \} \wedge T_4) \\
      : & \bot = x.foo

In Wadlerfest, this program is going to compile, because :math:`x : \{x \Rightarrow
T_1 \wedge T_4\}` can be shown, by first :math:`Rec-E` rule and then :math:`Rec-I`
rule. After that, :math:`y` can be used to prove :math:`x : \{x \Rightarrow T_2 \wedge
T_4\}`. At this point, we've already got :math:`\{A : \bot .. \bot\}` and been able to
show :math:`x.foo : \bot` indeed. 

This, however, is impossible, because there is no way to show :math:`x : \{x
\Rightarrow T_2 \wedge T_4\}` inside of :math:`Sel` rules, in which :math:`VarPack`
rule is forbidden. This gives another point OOPSLA DOT is less expressive than
Wadlerfest DOT.

Multi-Inherience in DOTs
--------------------------

The next disappointment is coming from both DOTs. Notice that in Scala, a very general
pattern is to have traits mixed together, and during implementation, the programmers
are forced to resolve the multi-inheritance problem, or the compiler will reject the
program. For example, consider the following program.

.. code-block:: scala

  trait Foo
  trait Bar
  trait WrapFoo { def unwrap : Foo }
  trait WrapBar { def unwrap : Bar }
  // ...
  val x : WrapFoo & WrapBar = ???
  val y : Foo & Bar = x.unwrap
  
In Dotty, `&` denotes the intersection type as shown above as :math:`\wedge`. This is
not a problem, because the programmer needs to resolve what type `unwrap` is supposed
to have. e.g.

.. code-block:: scala

  val x : WrapFoo & WrapBar =
    new WrapFoo with WrapBar {
      def unwrap : Foo & Bar = new Foo with Bar
    }

The second point here, is that from `x.unwrap`, we are able to obtain `Foo & Bar`,
which is more specific than any other types. 

However, this is achievable in none of both.

In Wadlerfest DOT, there is a very close-looking rule.

.. math::

   \frac{\Gamma \vdash x : S \quad \Gamma \vdash x : U}
   {\Gamma \vdash x : S \wedge U} (And-I)

This looks very close, except that it only operates on variables. To achieve `x.unwrap
: Foo & Bar` as shown above, there are two possible fixes for Wadlerfest DOT.

The first one is to generalize the rule above to work for terms.

.. math::

   \frac{\Gamma \vdash t : S \quad \Gamma \vdash t : U}
   {\Gamma \vdash t : S \wedge U} (And-I')

Another solution is to assert that intersection :math:`\wedge` and data fields are
*distributive* from subtyping rule

.. math::

   \frac{ }
   {\Gamma \vdash \{a : S \} \wedge \{a : U\} <: \{ a : S \wedge U \}}

These two fixes would also apply for OOPSLA DOT.

It's quite awkward to have overlooked this missing features for all well-known
versions of DOTs for so long. 

To Be Fair: What Wadlerfest DOT Is Missing?
-------------------------------------------

If I stop here, then I would probably make myself look like I am unilaterally
criticizing, so I guess to make the game fair, I should point out a number of things
that can be done in OOPSLA DOT, but not Wadlerfest DOT.

1. Wadlerfest DOT has no union types (:math:`\vee`).
2. Objects / recursive types in Wadlerfest DOT have no subtyping relation between
   them. This is what led to the comparison to begin with. It's unimaginably strange
   that, in an object-oriented setting, there isno subtyping relation among objects.

Takeaways
#########

I guess the point of comparing these two calculi are not really for the sake of
comparing them. The purpose should be to learn something from the comparison itself.

By looking afar, I think the distinctions between the calculi are in no sence
obvious. On the other hand, when people refer to these different versions of DOTs,
each with different expressiveness, **the** DOT. I think this is a terrible
practice. It would probably make sense, to refer to early versions and a later refined
version, DOT, but once the calculus is stablized, it becomes awkward to connect these
calculi by colliding their names, and makes people think they are different
representations of the same thing, while it's not the case.

It can be seen there are lots of informal arguments around DOTs. These arguments, very
frequently, are used to connect Dotty and the calculi themselves. For instance, one
might need to show that *what* derivation tree in the calculus corresponds to a
desirable type / subtyping relation. However, given how complex the Scala language is,
I suppose it's highly non-trivial to present a consistent encoding from Scala to the
calculus, while this piece of difficult work is normally hand-waved in a discussion
section. For example, In both DOTs, none of the following types mean the same:

.. math::

   \{ A : \bot .. \top \} &\wedge \{ A : \bot .. T \} \\
   \{ x \Rightarrow A : \bot .. \top \} &\wedge \{ A : \bot .. T \} \\
   \{ x \Rightarrow A : \bot .. \top \} &\wedge \{ x \Rightarrow A : \bot .. T \} \\
   \{ A : \bot .. T \} & \\
   \{ x \Rightarrow A : \bot .. T \} &

On the other hand, their distinctions are largely hand-waved, because semantically,
they should really be the same.

Another persepective is that at this point, the specification of the core calculus has
become too complicated. When we try to prove the soundness of the calculi, we are
effectively examining the correctness of the specification using some *internal*
properties. However, there are other external aspects: for example, does it represent
Dotty or Scala?

The last question indicates that the specification of the calculus has already become
non-trivial for experts to understand, and for experts to state what are their
expectations. Subsequently, only misunderstandings follow. In the old days, when
:math:`F_{<:}` was still a problem, people have studied it for years. At the level of
difficulties of DOT, I think it would worth the same level of effort. 
   
.. [1] OOPSLA DOT, OOPSLA 16, http://lampwww.epfl.ch/~amin/dot/soundness_oopsla16.pdf
.. [2] Wadlerfest DOT, Wadlerfest, https://infoscience.epfl.ch/record/215280/files/paper_1.pdf
