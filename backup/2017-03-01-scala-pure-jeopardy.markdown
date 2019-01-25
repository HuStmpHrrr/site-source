---
layout: post
title: Innocent-looking Methods Jeopardize Purity in Scala
categories: blog
tags: scala
---

Even though Scala now is widely considered a functional programming language, it's not meant for that in the very
beginning. Therefore, its designs for libraries or the language itself don't have that in mind. Turning into functional
programming language is more like a core team driven trend, but unfortunately, the designs that are done and the
failures introduced are very difficult to get rid of.


## Malfunctional Scala functors

As described in a previously [blog](/blog/2016/10/21/scala-map.html), functors in Scala are defined in a way that lacks
unified interface, and wrong for some data structures. It's the principle that a correct functor implementation
shouldn't distort the shape of the data structures, while, as shown in the blog, this is not necessarily true. This
effectively brings problems to the ones who want to strictly implement functional programming in Scala.

More discussion on this in the [blog](/blog/2016/10/21/scala-map.html).


## Innocent-looking but dangerous methods

Following presents another set of issues that is effectively the same cause as the previous section, but it's less
mathematically strict(let's put it in this way) and has impact an in reality. There are methods provided by the Scala 
builtin libraries that are so widely spread that it's virtually impossible to get rid of. What's worse is this type
of methods look very intuitive and innocent:

```scala
def first[A](c: Traversable[A]): Option[A] = c.headOption
```

You can't probably find an easier method than this. However, this method has already contained a bug; a bug that in
some case can bring serious effect to a program in functional style. Let's do it in a console:

```
scala> val s1 = Set(1, 2)
s1: scala.collection.immutable.Set[Int] = Set(1, 2)

scala> val s2 = Set(2, 1)
s2: scala.collection.immutable.Set[Int] = Set(2, 1)

scala> s1 == s2
res0: Boolean = true

scala> first(s1) -> first(s2)
res2: (Option[Int], Option[Int]) = (Some(1),Some(2))
```

What's wrong? It seems expected for the first glance. However, this result shows contradiction. In sets' semantics, we
will not consider ordering, and as a result, we will expect `s1` and `s2` to be compared equal, i.e. they represent the
same set. However, they don't have the same physical representation, and that leads to the problem of different 
traversal order, even if all components involved are meant to be pure. So the consequence is a nondeterministic result
returned by a function while taking the the arguments that compare equal.

In fact, all the functions that do traversal on a data structure with set semantics really need to be taken carefully
and that basically means all methods exposed by `Traversable` are vulnerable, for example, `fold`s, `scan`s, `last`,
`init`, etc. Things can be even worse if `Map[K, V]` is involved, where such set semantics is on `K`. More details are
discussed in a [previous blog](/blog/2016/10/21/scala-map.html).

And the worse scenario is when one tries to make a library general and accept interfaces at higher levels, like
`Iterable` or `Traversable`. In this case, the library is totally exposed to the vulnerabilities introduced by the
concrete implementation of that interface, and therefore the pureness of such general functional programming library
can be easily jeopardized.

## // To be continued


