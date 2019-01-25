---
layout: post
title: "Common Misunderstandings of Functional Programming"
categories: blog
tags: fp languages scala haskell
---

I have been working in the industry for 2 years, and seen and read about a number of others' opinions regarding
some programming concepts, especially in functional programming area(FP). It turns out that there are some 
concepts that are not supposed to be confused, however becoming widely accepted in a wrong interpretation.
Hence here is an aggregation of those misunderstandings and I will be trying to clarify a bit after identifying them.


## Immutability != FP

It's true that functional programming mostly relies on immutability, and some early functional programming language
implementations explicitly utilized that. But it's not true that having builtin immutable data and encouraging
programming in immutable style make the language or the code "functional".

On the other hand, modern FP doesn't require you always program immutably as well. Conceptually, immutability 
is used to preserve the property of referencial transparency, which is a term I am very hesitant to use, but not
necessary for all the case. For instance, in haskell, `ST` monad is used to provide a local mutation context 
within which data can be mutated, that is transparent to the outside world. That means so called referencial
transparency actually has a contextual implication. More on this term, please reference 
[Referential Transparency](#referential-transparency).

## Lambda != FP

It's often heard that "Java/C# have already been functional programming languages since lambda is supported". Once
again, though lambda expression is the essential building block of a fplang construct, but it's not true to consider
the languages to be functional and the programmers that use the feature once a while a "functional programmers".

In essense, it's not necessary for, in this example, Java to have lambda expressions. For instance, in Java 8, now
we are allowed to write code that uses classic combinators like `map`, `filter` over a sequential collection:

```java
List<Integer> intList = // from somewhere else

IntStream intListPlus1 = intList.stream().mapToInt(i -> i + 1)
```

But if we look at the interface of `mapToInt`(or its brothers), we can find out it is [defined][stream-map] as:


```java
<R> Stream<R> map(Function<? super T,? extends R> mapper)
```

The corresponding [interface][function]:

```java
@FunctionalInterface
public interface Function<T, R> {
    R apply(T t);
}

```

Essentially lambda expression in Java is just a simple way of writing implementation of single function interfaces.
This is a very typical object oriented technique called *injection*, through an interface. Though the form is 
a lambda expression, the essence of object orientation still doesn't help in terms of designing programs in a functional
way. Lambda as a language construct is only a part of the fruits fp has.


## FP does not look like natural languages

It's especially frequently found among scala programmers, who consider the form of functional programming is close
to natural languages, e.g. English. This misunderstanding comes from the syntactical feature of the scala language 
itself.

For example, in `scalatest`, one can write a test case like this to make it read naturally in English([quote][scalatest]):

```scala
  "A Stack" should "pop values in last-in-first-out order" in {
    val stack = new Stack[Int]
    stack.push(1)
    stack.push(2)
    stack.pop() should be (2)
    stack.pop() should be (1)
  }
```

It's very superficial. A FP language most likely is based on lambda calculi or combinatory logic, which are both mathematical
models of computation. By design, FP is intended to be a more mathematically precise computational description, instead
of something like natural language approximation.

## Syntactical sugar != FP

It seems factual that functional programming languages provide much more syntactical sugar than those are not. For instance,
Haskell and Scala support:

1. pattern matching
1. monadic comprehension(do-notation and for comprehension repectively)
1. flexible and customizable syntax

However, NONE of these are necessarily FP specific, though they are rare to see in any other types of languages.
A counter example of this would be [Rust][rust], which is an imparative language with pattern matching.


## Referential Transparency

Referential transparency(RT) is a very ambiguous and controversal concept which is very easy for people to misunderstand
(or might not be able to be understood) with its sheerly innocent looking. There are a number of excellent StackOverflow 
answers that talk about it, e.g. [don't say RT][rtso1] and [RT explained philosophically][rtso2], that kind of give the
feeling of imprecision and bias of the most accepted interpretation of this term.

Though this term is very ambiguous, as most people use it to mean([wiki][wikirt]):

> An expression is said to be referentially transparent if it can be replaced with its corresponding value without
> changing the program's behavior.

I will be interpreting this term using this definition. However, when I mention the similar concept in other contexts,
I believe `pure` is a much better term to reflect the mathematical meaning, and shorter,  or `combinator`(functions the
output of which strictly depends on the inputs only) when functions are the main target instead of expressions 
in the discussions. 

It's very interesting to see only functional programmer mentioning this word, but it's fairly rare to see this word appear
in those essential fp related literatures. That said, the concrete, rigorous definition of this concept in terms of fp 
world is no where to be found(hence the controverse comes).

Following ways are the ones common in which people can easily take it wrong.


### RT is not functional programming specific

It's very common for so-called functional programmers to talk about referential transparency and they might make it
sound that RT is only or mostly a FP feature and all other languages doesn't have this nice property at all since they
follow the operational semantics, e.g. imperative languages like C. 

In [HaskellWiki][haskwiki-rt]:

> Referential transparency is an oft-touted property of (pure) functional languages,
> which makes it easier to reason about the behavior of programs.

The comment is inaccurate, and if we compare it with the definition from wikipedia, it has already given a feeling of why
the concept of RT is ambiguous and understood in the same way by people as Hamlet. 

It's false to say "C cannot be referentially transparent" or "functions in haskell are RT". In [this classic paper][fund-concept],
the author discussed RT in an command based language model, which is imperative, by distinguishing L-value and R-value 
and discribing the assignment as a state transition. 

> If we consider L-values as well as R-values, however, we can preserve referential transparency
> as far as L-values are concerned. This is because L-values, being generalised addresses, 
> are not altered by assignment commands.

Consequently, assignment operations become expressed by compositions of state transition functions, which in fact
can be well considered RT in the most common understanding of what RT should be, e.g.:

```
a := v1
b := v2
c := v3
```

and 

```
let 
    theta l r sigma = U (L l sigma, R r sigma) sigma

where sigma is the global state
      L     is the function that accesses the L-value of the expression l
      R     is the function that accesses the R-value of the expression r
      U     is the function that updates the R-value of L-value, and returns a new state
```

then we can transform the original sequence of "non-RT" assignments to

```
theta c v3 . theta b v2 . theta a v1,

where . is the function composition function, and (f . g) x == f (g x)
```

Thus RTness in imperative can be totally explained by separate the consideration fo L-value and R-value. In this sense, 
we can reason following sequence of commands:

```java
int a = 10, b = 20;
a++;
b -= a;
```

this sequence of commands stores 2 new R-values to 2 already existing 2 L-values in the store, respectively. The stores 
remain the same ones, obviously, and the assignments are the state transitions that happen to the stores. In this sense,
the value of assignment operation becomes the state transition function similar to the one previously shown.


Doesn't that sound like bullshitting? Well, in the right case, state transition and assignment are interchangable. In haskell,
there is a *deep magic* phantom type call `RealWorld` that does the exact thing I described previously([quote][hackage-rw]):

> data RealWorld :: *
>
> RealWorld is deeply magical. It is primitive, but it is not unlifted (hence ptrArg). 
> We never manipulate values of type RealWorld; it's only used in the type system, to parameterise State#.
>
> stToIO :: ST RealWorld a -> IO a
>
> A monad transformer embedding strict state transformers in the IO monad. The RealWorld parameter indicates
> that the internal state used by the ST computation is a special one supplied by the IO monad, 
> and thus distinct from those used by invocations of runST.

For those new to Haskell, `ST` is a type of monad in haskell, meaning *S*tate *T*ransformer. The definition of `stToIO` 
indicates that a sequence of state transition/transformation can eventually be converted to a side-effectful IO operation,
which again states my previous argument. Depending on how the computation is modeled, the meaning of referencial transparancy 
drifts so much, that we might make the conclusion that is true on both sides of the coin.


Even if we focus the semantics on a single function, it's still not true to say only functions in certain languages are RT.
In GCC, for instance, we are allowed to give an attribute to a function that serves as a hint to compiler, saying the function
is `pure`, [quote][gcc-attr]:

> Such a function can be subject to common subexpression elimination and loop optimization just as an arithmetic operator 
> would be. These functions should be declared with the attribute pure. For example,
>
>          int square (int) __attribute__ ((pure));
>
> says that the hypothetical function square is safe to call fewer times than the program says. 

The mistaken part of the understanding here is to consider only languages with denotational meanings can be RT, and most of 
non-functional languages are operational, meaning programs in these languages executed based on a sequence of commands. 
In this aspect, saying RT being a language depedent property would not still be in favor, not to mention tying this property
to functional programming languages alone.

### RT is about expressions

The introduction of RT to programming languages brings mathematical analysis of the behavior of the software, and very 
interestingly, RT/purity is not even a thing in math since they come by nature. In the whole world of mathematics, not
only functions are RT but also every expressions(many people use many words, like referents, denotations, etc).

```
1 + (2 * 3)
```
and

```
1 + 6
```

and

```
7
```

are exactly the **same**, and in functional programming languages, they are undistinguishable. The definition of **same**
needs to be clarified: 2 objects are the same if and only if they denote the same mathematical object. No wonder, nobody
can argue that all 3 expressions above denote different mathematical meaning than any others.

The common misunderstanding here comes into 2 ways:

1. stating RT is **value** related. It's probably due to terminology abusement that value here is a overloaded word. But 
the use here sends a wrong signals to people that RT is a decription of evaluation process. It's fundamentally wrong in
terms of mathematical sense, since `3 + 4` is also `7`, but there no way for this expression appear in the evaluation 
path of any of the first 2 expressions. However, RT allows us to substibute any expression to any other one within
the universe of equivalence. Only considering evaluation happens to be so superficial that only two out of infinity are
taken into account.

2. stating RT is about **functions**. As functions can also be a part of expressions, by looking at expressions, we definitely
cover the cases for functions. However, the other way around only considers the subset of it. Fun enough, the argument
of RTness of a function holds only provided all the expressions in the definition body satisfy RT.


[stream-map]: https://docs.oracle.com/javase/8/docs/api/java/util/stream/Stream.html#map-java.util.function.Function-
[function]: http://hg.openjdk.java.net/jdk8/jdk8/jdk/file/687fd7c7986d/src/share/classes/java/util/function/Function.java
[scalatest]: http://www.scalatest.org/quick_start
[rtso1]: http://stackoverflow.com/questions/4865616/purity-vs-referential-transparency
[rtso2]: http://stackoverflow.com/questions/210835/what-is-referential-transparency/11740176#11740176
[rust]: https://www.rust-lang.org/en-US/
[wikirt]: https://en.wikipedia.org/wiki/Referential_transparency
[haskwiki-rt]: https://wiki.haskell.org/Referential_transparency
[fund-concept]: https://github.com/papers-we-love/papers-we-love/blob/master/plt/fundamental-concepts-in-programming-languages.pdf
[hackage-rw]: http://hackage.haskell.org/package/base-4.9.0.0/docs/Control-Monad-ST.html#t:RealWorld
[gcc-attr]: https://gcc.gnu.org/onlinedocs/gcc/Common-Function-Attributes.html#Common-Function-Attributes
