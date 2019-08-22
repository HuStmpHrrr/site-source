Subtyping with Algebra
======================

:date: 2019-05-12
:tags: DOT, programming languages, research, type theory, proof assistants
:category: Scala / DOT
:authors: Jason Hu
:summary: Study subtyping in an algebraic approach!

Introduction
############

When the subtyping relation in a programming language is rich enough, the relation
starts to induce some algebraic structure. For example, DOT has intersection types,
which admits bounded semi-lattice structure, both order theoretically and
algebraically. However, intersection types in DOT have only been studied in its order
theoretic nature (probably not even, because order theory studies nothing about the
contexts!), but nothing about its algebra.

Motivation
##########

In my work of `Master's thesis <https://gitlab.com/JasonHuZS/AlgDotCalculus>`_, I
studied a simplified version of DOT, :math:`D_{\wedge}` (pronounced *Dee
Intersect*). This calculus has intersection types and data field members. For example,
:math:`\{a : S \wedge U\}` denotes a data field member, the tag of which is :math:`a`
and the type is :math:`S \wedge U`. In general, intersection types specify refinement
of information. The subtyping rules are as follows.

.. math::

   \dfrac{ }{\Gamma \vdash S \wedge U <: S}(\text{And-E1})
   \quad
   \dfrac{ }{\Gamma \vdash S \wedge U <: U}(\text{And-E2})
   
.. math::
   \dfrac{\Gamma \vdash T <: S \quad \Gamma \vdash T <: U}
   {\Gamma \vdash T <: S \wedge U}(\text{And-I})

The first two rules says that one can feel free to drop information from intersection
types, and the third rule asserts that the intersection type is the greatest subtype
of :math:`S` and :math:`U`. If :math:`\Gamma` is not specified, then these rules are
an axiomatization of order theoretic meet-semilattice. Together with :math:`\top`
type, which is the supertype of all types, this forms an order theoretic bounded
meet-semilattice structure.

So far so natural. However, it's textbook knowledge that order theoretic
meet-semilattice and algebraic meet-semilattice are interchangeable. Namely, order
theoretic meet-semilattice induces algebraic structure. Define the *induced type
equivalence relation* as follows.

.. math::

   \Gamma \vdash S \approx U \equiv \Gamma \vdash S <: U \times \Gamma \vdash U <: S

Namely, two types are equivalent, if they are a subtype of each other in the given
context. So it's easy to see that.

.. math::
   
   \Gamma \vdash S \wedge U \approx U \wedge S

This property is called *commutativity*. In general, regardless of the contexts,
algebraic bounded semilattice admits all following properties.

.. math::

   \top \wedge T &\approx T &(\text{identity}) \\
   S \wedge U &\approx U \wedge S &(\text{commutativity}) \\
   (S \wedge T) \wedge U &\approx S \wedge (T \wedge U) &(\text{associativity}) \\
   T \wedge T &\approx T &(\text{idempotency})

One can prove all of the above using the subtyping relation above.

What's more, one might expect that intersection types distribute accross data field
members. Namely,

.. math::

   \Gamma \vdash \{ a : S \} \wedge \{a : U\} \approx \{a : S \wedge U\}

Note that the type on the left is already provably a supertype of the right, because
intersection types are the greatest subtypes. However, this type cannot be shown a
subtype of the right. This requires an axiom, like following

.. math::

   \dfrac{ }
   {\Gamma \vdash \{ a : S \} \wedge \{a : U\} <: \{a : S \wedge U\}}
   (\text{Fld-Distr})
   
This rule is required to be an axiom because it cannot be proved by any other existing
rules. This is normally how it's done in other people's work, but looking at this
rule, it's easy to realize that it is the algebraic relation that is wanted, not this
particular subtyping relation. This axiom is here just to make sure the subtyping
relation *induces* a desired algebraic relation, but nothing more. Therefore, a
question arises: why not reason about the algebraic structure directly?

Algebraic Structure in Subtyping
################################

This is very interesting way of thinking about subtyping. Algebraic approaches are not
rare in type theoretic study, but somehow, subtyping doesn't quite look "type
theoretic". On the other hand, people seem to avoid this way of thinking because it
simply adds a great deal of difficulties in the study. This is because algebraic
structure in its essence is "more precise" than subtyping relation, and therefore
subtyping relation can only be built after the algebra is defined, but not the other
way around. Visually, a hierarchy like

.. math::

   \text{Type (raw)} \to \text{Algebra (without context)} \to \text{Subtyping (with contexts)}

needs to be defined.
   
Another reason is what we have in proof assistants is not sufficient to
reason about these nested structures efficiently. To give a good feeling of how
cumbersome it can be, I formalized a very primitive algebraic relation in
:math:`D_{\wedge}` `here <https://gitlab.com/JasonHuZS/AlgDotCalculus/blob/master/agda/DintAlg.agda>`_.
   
.. code-block:: agda

  infix 5 _≃_
  data _≃_ : Typ → Typ → Set where
    refl   : ∀ {T} → T ≃ T
    tran   : ∀ {S T U} → S ≃ T → T ≃ U → S ≃ U
    symm   : ∀ {S U} → S ≃ U → U ≃ S
    assoc  : ∀ {S T U} → S ∩ (T ∩ U) ≃ S ∩ T ∩ U
    comm   : ∀ {S U} → S ∩ U ≃ U ∩ S
    idem   : ∀ {T} → T ∩ T ≃ T
    ⊤∩     : ∀ {T} → ⊤ ∩ T ≃ T
    ⊥∩     : ∀ {T} → ⊥ ∩ T ≃ ⊥
    ∩-cong : _∩_ Preserves₂ _≃_ ⟶ _≃_ ⟶ _≃_

There are more axioms than listed above. This is because some axioms are needed to
impose the equivalence relation which does not originally hold if a relation is
defined from scratch. At last, the congruence property `∩-cong` also needs to be
asserted to ensure the equivalence is congruence everywhere in the intersection
types. Then it follows the properties of this equivalence, like proving this
equivalence respects the subtyping relation, as well as other algebraic
theorems. Moreover, this equivalence is very hard to work with, so to make things a
bit easier, more auxiliary concepts need to be defined. What a pain.

Cubical Type Theory
####################

This sort of algebraic study is painful, because even the basic structure of the
relation requires *proofs*. For example, this relation is not an equivalence by birth;
it is only after a proof is established. Due to this, the congruence properties
require more proofs and it's probably the most boring thing to do.

However, this is not a deadend. Cubical type theory is a richer theory than
intuitionistic type theory and a more helpful one when reasoning about "algebras up to
equivalences". In cubical type theory, higher inductive types (HIT) allow data to
carry internal algebraic structure. For example, one can define :math:`S \wedge U = U
\wedge S` by definition. This means from the outside world, when a :math:`D_{\wedge}`
type is perceived, it's that type up to algebra as desired above. What's more, it's
perfectly congurent, due to the type theory.

Then looking back to what was wanted above,

.. math::

   \{ a : S \} \wedge \{a : U\} \approx \{a : S \wedge U\}

If we define

.. math::

   f(T) \equiv \{a : T\}

then

.. math::

   f(S) \wedge f(U) \approx f(S \wedge U)

simply means that data field members are semi-lattice homomorphism. From category
theoretic point of view, :math:`f` is considered functorial. Everything starts to look
very simple from this point on. Moreover, the subtyping relation can remain untouched.
It simply gives more structure to the underlying definition of types in
:math:`D_{\wedge}`. The theory therefore gives more structure than
intuitionistic type theory in order to study the problem, which does not seem to be
explored at the moment. I am very interested to see how this new type theory can
change the way people think about problems in.

Conclusion
##########

Every problem in DOT is very difficult and tricky. At least it is the case at this
moment. One good way to tackle this problem should be to lower the difficulty of the
problem itself by improving the tools, not necessarily to invest more time on tackle a
hard problem. I feel that cubical type theory is the right type theory to talk about
DOT. However, changing the way of thinking is never an easy task to begin with. I hope
one day type theory can be so advanced that even DOT becomes a piece of cake.
