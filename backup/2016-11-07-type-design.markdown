---
layout: post
categories: blog
tags: scala type java
title: Some Words on Type Hierarchy Design in Scala 
---


It's extremely normal that we will need to use concrete types to represent business entities in enterprise
programming. In Scala, due to its OO characteristics, it's very common and welcomed for Java programmers to design
type/class hierarchy in OO manner. However, Java type system and Scala one don't come even close and that makes Java
programmers have the tendency to make very small but significant mistakes.

## A common problem

The most basic one is generics. In Java, variance is not annotated in the declaration but usage. For instance, when
one needs to have a covariant `List`, one needs to do:

```java
List<? extends MyObject> myList = //...
```

But there is nothing wrong, from Javac's point of view, to declare a contra-variant `List`:

```java
List<? super MyObject> myList = //...
```

However, this code has substantial issues. How can this code even make sense? If we decide to declare `myList` to be
of this type, then it means, under the principle of PECS(producer extends, consumer super), `myList` is totally in a
consumer position. That basically only allows us to call `#add()` to it, without being able to extract the elements
inside, as `#get()` and its iterator have the generics appear in covariant position. So from a practical point of view,
a collection that cannot be read is hardly useful.

Since dealing with types is such a pain in the neck, Java programmers have picked up the habbit of not taking too
close look into the types. As a result, many type relations can be better formed remain half done. An example of
this will be to model the hierachy of animals(it's a projection from code that can be seen everywhere):

```scala
trait Animal {
  def father: Animal
  def mother: Animal
}

trait BreastFeeding
trait HasFurAndHairs

trait Mammal[T <: Animal with BreastFeeding with HasFurAndHairs]
  extends Animal with BreastFeeding with HasFurAndHairs { 

  def father: T
  def mother: T
}
```

Very often it's out of a seasoned Java programmer's hands. the intention of the generics is to make sure parents
accessor can be reasonably typed. However, this type is so difficult to use in reality to a level that it sucks so
badly. For instance, if we want to extra the grandfather out of a `Mammal` instance, we would neeed to define:

```scala
def grandfather[T <: Mammal[_]](m: T) = m.father.father
```

seems reasonable, and common sense tells us that `grandfather` should return the same type as `m`. But this code
won't compile for following reasons:

1. Due to a compiler bug, the type of `m.father` is totally wrong(it will be `Any` prio to 2.12) and therefore
   `m.father.father` cannot compile.
1. Even if we add `Animal` to be the constraint, `m.father` will give a type of 
   `Animal with BreastFeeding with HasFurAndHairs`. there is no way we can express `T` in fact is also of the 
   exact `Mammal` type. So we are potentially forced to perform type casting.

Moreover, this interface inherits the cumbersomeness of Java if we want to represent a subtype using this trait:

```scala
class Dog(val father: Dog, val mother: Dog) extends Mammal[Dog]

val dog: Mammal[_ <: Animal with BreastFeeding with HasFurAndHairs] = new Dog(null, null)
```

We have to repeate this long constraint everywhere it's used. The size of the code becomes unnecessarily huge. It
damages a more structural trait driven style.

## F-bounded

So the modelling has serious issue in terms of expressing type relations when ones try to think in Java. A more
reasonable way to write this is to make it F-bounded:

```scala
trait Mammal[+T <: Mammal[T]] extends Animal with BreastFeeding with HasFurAndHairs {
  def father: T
  def mother: T
}
```
This looks much better. It add 2 more information into the types:

1. The `father` and `mother` now are certain to be the same subtype of `Mammal`, as the constraint implies, 
   as long as the implementation is correct, and
1. Covariance makes instance able to be upcasted to a supremum and therefore the subset of type hierarchy forms a
    complete lattice.(I shall explain the idea of forming a complete lattice when designing type hierarchy
   in another blog.)

Besides the first point adds more expressiveness, the second point is substantially important: it allows a single unified
and certain type to represent all the types in the hierarchy, which will definitely come in handy in the future,
especially compared to the original invariant solution.

However, if we come closer and inspect the covariance, soon we will detect an issue, that the supremum of this
type is factually unwritable. As `T` has constraint of being `Mammal[T]`, it turns out the supremum requires itself
to appear in the generics, and it's an indefinite recursive loop at type level when we try to manually write it down:

```scala
val mammal: Mammal[Mammal[Mammal[...]]] /* it can never end */ = ??
```

Interestingly, we have 2 ways of fixing it. The first one will be existential type. It nicely gets away with this
whole recursive burden:

```scala
type MammalG = T forSome { type T <: Mammal[T] }
```

Basically what it says is the type `T` is of some subtype of `Mammal[T]` and therefore we have solved the
recursiveness issue. And this type alias also guarantees that for object of this type alias, its `#father` and
`#mother` will also be of type `MammalG`.

```scala
val m: MammalG = ??? // whatever it is
val mfather: MammalG = m.father
val mgrandFather: MammalG = m.father.father // both of them will compile

// console gives:
// Scala> :t m
// MammalG
// Scala> :t m.father
// T forSome { type T <: Mammal[T] }
// Scala> :t m.father.father
// T forSome { type T <: Mammal[T] }
```

But this way has its shortcoming: two `MammalG` instances cannot be proven of the same types:

```scala
val m1: MammalG = ??? // whereever it comes from

def eqCheck[A, B](a: => A, b: => B)(implicit f: A =:= B) = a // this will try to prove A and B are equal type

eqCheck(m1, m1.father) // cannot prove these 2 types are equal, though they are defined to be
                       // even foo(m1, m1) cannot be proved
```

This is a severe inconsistency. What it implies is one can assign an object of `MammalG` type to any `val` or `var`
that is of `MammalG` type as well, but one can never say two `val`s or `var`s holding the object of the very exact same
type, even though they can be holding the same object. And that further implies that the supremum of this partial order
set of the type hierachy(forward pointer needed) is actually not concrete: it's like talking about natural
numbers, because `sup(R) == infinity`, however, calling for comparison between infinities in this context can hardly make sense.

We almost get things done, but involving existential type which makes the supremum becomes inconcrete seems to be a fly
in the ointment.

## Type level fixed point

Another way of fixing it will be, noticing the infinitely nesting type relation, a type level fixed point. It's such a
general technique in turing complete type level programming, that it will show up anywhere in any circumstances.

```scala
trait Fix[T[_ <: Fix[T]]] {
  self: T[Fix[T]] =>

  final def unfix: T[Fix[T]] = this
}

trait MammalT[+T <: Fix[MammalT]]
  extends Animal
  with    BreastFeeding
  with    HasFurAndHairs
  with    Fix[MammalT] {

  def father: T
  def mother: T
}

type Mammal = Fix[MammalT] 
```

Hence we can define a `Dog` to be:

```scala
class Dog(val father: Dog, val mother: Dog) extends MammalT[Dog]
```

Please check closer: as we defined, `Mammal` now becomes `Fix[MammalT]`. if we substitute the definition in the
right place, we can yield following pseudo definition from this alias:

```scala
trait Mammal[+T <: Mammal] extends // blah blah blah
```

which is kind of reaching what we want to express. However, this buys us more: now `Mammal` is a very certain type
with no a single place of ambiguity. That means, we can now prove the supremum of this lattice equal:

```
scala> val dog = new Dog(null, null)
dog: Dog = Dog@ecdf726

scala> eqCheck(dog, dog.unfix.father)
res2: Dog = Dog@ecdf726

scala> eqCheck(dog, dog.father)
res3: Dog = Dog@ecdf726

scala> val mammal: Mammal = dog
mammal: Mammal = Dog@ecdf726

scala> eqCheck(mammal, mammal.unfix.father)
res4: Mammal = Dog@ecdf726
```

Feeling good to get rid of the fly.

Another aspect of this fix is to introduce type level fixed point application. Notice that all `MammalT[_]` now
implements a `Fix[_]` which turns around is capable of returning its own object. This `Fix[_]` higher order type
serves a purpose of delaying the type level of computation to the time when it's needed, i.e. to make
`MammalT[MammalT[MammalT[...]]]` to be `Fix[MammalT]`. The reason that we can compare equal this type instead is
simple: in a setting of pure mathmatical world but with finite computational resources, comparing infinitely long
structure is a valid operation but will not terminate; however, if we have a combinator that represents the shape of
that very structure, then it's decidable to perform extensional equality check. For examle, we don't have to know how
function `f` is defined to conclude `f(1) == f(1)` must hold within the presumed settings. 

Here, `Fix[_]` appears to describe the infinitely nesting structure and therefore the whole type becomes comparable. 
Compared to F-bounded, we use the type fixed point to constrain the generics in order to preserve the expressiveness.

One thing worth mentioning here is the way I define `Fix[_]` here; it's kind of different from how other people 
would have defined it, as a case class like this:

```scala
case class Fix[F[_]](unfix: F[Fix[F]])
```

This definition achives 2 purposes:

1. We are only interested in the usage that a type level fixed point to model a finite representation of the target
   type constraint, and
1. The instance of this very fixed point type has already reached its fixed point in the value domain, so that we can
   constrain the self type of `Fix[_]` to be limited to the form it's supposed to apply, and `#unfix` method to safely
   return the instance itself.


This two solutions have pros and cons. Though they both work, the supremum type of F-bounded solution involves
existential type, which is always troublesome to deal with. For most of the cases, the existential type will just do
what is expected, but the corner cases can be very subtle. On the other side, for type level fixed point,  we can 
consistently trust the type and it's guaranteed we won't hit corner cases, so we won't have to pay much attention to
some tiny details that doesn't really matter. The only price we need to pay is to once a while to call `#unfix` method
in order to please the type system.

## Type family

Another way to fix this is to break the loop of parametric generics and put the constraint in another place:

```scala
trait Mammal
  extends Animal
  with    BreastFeeding
  with    HasFurAndHairs {

  type T <: Mammal

  def father: T
  def mother: T
}
```

So we can implement `Dog`s as:

```scala
trait Dog extends Mammal {
  type T <: Dog
}

case class Husky(val father: Husky, val mother: Husky) extends Dog {
  type T = Husky
}
```

The key here is the type parameter `T`, and it is used to indicate the type bound. In `Mammal`, `type T <: Mammal` says
`T` needs to be of a subtype of `Mammal` and in `Dog`, it needs to be of a subtype of `Dog`. Until `Husky` is defined,
we state `T` in fact is `Husky` such that the whole hierarchy doesn't involve any loop in generics.

This small piece of code actually introduces a different way of looking at a type. In traits, we only specify the bound
of the type, which is supposed to comply to all of its implementation. This bound acts like a proof: at a certain
level, with a certain piece of information, a certain knowledge can be acquired logically. This way can also provide a
uniform upper bound for this `Mammal` framework.

## Generics might just be unnecessary

After all these blahblah, is that necessary to do all these things? Depends on which environment this discussion is
held. In fact, in the world of industry, these solutions can just appear to be complicated, as it takes time to refine
the ideas and the result is not immediate. The capabilities and strength can diverse across employees as well. So
pursuing an easier solution becomes a path to go in this situation.

Not surprisingly, a much simpler solution is right in front of us: just take away the generics:

```scala
trait Mammal extends Animal with BreastFeeding with HasFurAndHairs {
  def father: Mammal
  def mother: Mammal
}

class Dog(val father: Dog, val mother: Dog) extends Mammal
```

What's the problem of it? Well, you can claim that now `#father` and `#mother` lose the constraints and become free to
override to any types that are subtyping `Mammal`. Though the point is valid, it's very intuitive that what this code
is trying to convey, and type safety check is just something bonus in this situation. Moreover, in a company, the
practice is all about engineering, and a software engineering environment often involves design review and code review.
This kind of issues can be easily identified. However, by dropping generics, code becomes much much simpler to write
and the structure is very straightforward. Trading strict correctness to simpleness sounds a nice deal to me. I can't
help quoting this Zen of Python on the topic of simpleness:

> In [1]: import this  
> The Zen of Python, by Tim Peters
>
>
> Beautiful is better than ugly.  
> Explicit is better than implicit.  
> Simple is better than complex.  
> Complex is better than complicated.  
> // blah blah

// more. in fact, very often in Scala world, there are very common situations that people tend to introduce seemingly
 meaningful but essentially unnecessary generics. point that out.
