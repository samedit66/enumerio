# enumerio

> [!WARNING]
> This project is under heavy development, some functions come and go, and this `README.md`
> may contain outdated information about supported features.

`enumerio` is a breath of fresh air library designed to make it easy to create pipelines of data transformations, heavily inspired by the `Elixir` porgramming language and its stunning `Enum` and `Map` modules.

---

## Usage

```python
from enumerio import Enum, _

Enum(range(1, 100)).map(_ ** 2).filter(_ > 100).take(5).each(print)
```

See [What is a Enum?](#what-is-a-enum) and [Underscore!?](#underscore) for implementation details.

---

## Installation

With `uv`:

```bash
uv add git+https://github.com/samedit66/enumerio.git
```

With `pip`:

```bash
pip install git+https://github.com/samedit66/enumerio.git
```

---

## Motivation

`Python` has excellent built-in collection primitives, but many real-world tasks become much clearer when written as a **pipeline of transformations** rather than loops with temporary variables and flags. 

---

## Highlights

- **Readability**: `Enum(data).map(...).filter(...).take(3)` reads left-to-right as a data flow — the intent is clear.
- **Composability**: Small functions compose cleanly; you can reuse pieces of a pipeline easily.
- **Declarative style**: You describe *what* you want to do to the data rather than *how* to iterate it.
- **Fewer bugs**: Pipelines reduce mutable state (counters, accumulators), minimizing accidental side effects.

Even though Python already has `map`/`filter`/list comprehensions and libraries like `itertools`/`more-itertools`, bundling common operations into a coherent, chainable interface yields code that is both compact and highly readable.

---

## Pipeline style: why it shines

Pipeline code focuses on the transformation steps rather than control flow. This makes code easier to reason about, test, and refactor:

- Break complex processing into named steps (`.map(...)`, `.filter(...)`, `.freq()`) that are each easy to test.
- Move from imperative loops to functional building blocks; that helps when reasoning about edge cases (empty lists, single element, etc.).
- Pipelines encourage use of small pure functions that are reusable across projects.

---

## What is a Enum?

The main building block is a `Enum`. It's basically a successor of `UserList` (i.e. `list`) and provides all the same functionality as a basic list (except mutability: don't try to change it even though it is technically possible). So the following assertions do not raise:

```python
assert Enum([1, 2, 3]).map(lambda x: x**2) == [1, 4, 9]
assert Enum([1, 2, 3, 4, 5]).chunked(3, 1) == [[1, 2, 3], [2, 3, 4], [3, 4, 5]]
```

So you can pass `Enum` to any function which accepts a `list` as argument.

Similary to `Enum`, `enumerio` provides the `Map` container, which is a successor of `UserDict`.

---

## Underscore!?

For those who, like me, finds `lambda`s too long to type so-called _smarter lambdas_ were added:

```python
# The following...
print(Enum(range(1, 10)).map(_ * 2).sum())

# ...is the same as:
print(Enum(range(1, 10)).map(lambda x: x * 2).sum())
```

This feature simplifies typing `lambda`s a lot and makes code very readable.

Unfortunately, they are very limited _right now_: just simple arithmetic and nothing more.

---

## API

`enumerio` provides two primary data structures:

* **`Enum`** — ordered, list-like pipelines
* **`Map`** — key/value pipelines

Both are immutable-style: every transforming operation returns a **new value** instead of modifying the original container, making them safe and composable in functional chains.

---

# Enum

An `Enum` wraps any iterable and exposes functional transformation utilities inspired by Elixir’s `Enum` module.

### Construction

* `Enum(data)` — Construct an `Enum` from any iterable or from positional values.
* `size()` — Number of elements.

---

### Accessors

* `at(index, default=None)` — Element at index or `default` if out of range.
* `fetch(index)` — `Ok(value)` or `Error(message)` when out of range.

---

### Boolean checks

* `all(predicate=None)` — All elements satisfy predicate (or truthy).
* `any(predicate=None)` — Any element satisfies predicate (or truthy).
* `empty()` — True if it contains no elements.
* `has(elem)` — True if `elem` exists in the Enum.

---

### Side-effects

* `each(procedure)` — Run side-effect function for every element.

---

### Transformation

* `map(transform)` — Map elements.
* `map_join(transform, joiner="")` — Map to string then join.
* `flat_map(transform)` — Map elements into iterables then concat them.
* `filter(predicate)` — Keep matching elements.
* `reject(predicate)` — Remove matching elements.
* `filter_map(transform)` — Keep only `Ok(value)` results.
* `concat()` — Concatenate an Enum of iterables.
* `flatten()` — Recursively flatten nested iterables.
* `uniq()` — Remove duplicates preserving order.
* `into(type_or_function, transform=None)` — Convert to another structure (e.g. `list`, `Map`).
* `reduce(fun, acc)` — Reduce elements into a single value.
* `with_index(start)` — Map elements into 2-element tuples (index, element).

---

### Searching

* `find(predicate, default=None)` — First matching element.
* `find_index(predicate)` — Index of first match.
* `find_value(transform, default=None)` — First truthy transformed value.

---

### Grouping & counting

* `freq()` — `Map[element, count]`.
* `freq_by(key_fun)` — Apply `key_fun` to each element and then count them.
* `group_by(key_fun, value_fun=None)` — Group elements into a `Map`.

---

### Slicing & selection

* `take(amount)` — First `amount` elements (negative = from tail).
* `take_every(nth)` — Every nth element.
* `take_random(count)` — Random selection.
* `take_while(predicate)` — Take from start while predicate true.
* `drop(amount)` — Drop first `amount` (negative from tail).
* `drop_every(nth)` — Drop every nth element.
* `drop_while(predicate)` — Drop prefix while predicate true.
* `split(count)` — `(first, rest)`.
* `split_while(predicate)` — `(prefix_matching, rest)`.
* `split_with(predicate)` — `(matching, non_matching)`.
* `chunked(count, step=None, discard=False)` — Chunk into sub-Enums.

---

### Ordering & randomness

* `sorted()` — Sorted ascending.
* `rev()` — Reverse order.
* `shuffle()` — Random order.
* `random()` — Random element.

---

### Aggregation

* `sum()` — Sum of elements.
* `sum_by(mapper)` — Sum after mapping.
* `prod()` — Product of elements.
* `prod_by(mapper)` — Product after mapping.
* `min()` — Minimum element.
* `min_by(key)` — Minimum by key.
* `max()` — Maximum element.
* `max_by(key)` — Maximum by key.
* `min_max()` — `(min, max)`
* `min_max_by(key)` — `(min_by, max_by)`

---

### Working with nested data

* `sublist(*indices)` — Extract indices from each sequence.
* `subdict(*keys)` — Extract keys from each mapping.
* `select(*keys)` — Select values by key/index.
* `zip()` — Zip inner iterables.
* `zip_with(zipper)` — Zip inner iterables, transforming them with `zipper`.
* `join(joiner="")` — Join string elements.

---

# Map

`Map` wraps a dictionary and provides functional operations inspired by Elixir’s `Map` module.
Many operations interoperate with `Enum` to allow pipelines across both collections.

### Construction

* `Map(mapping_or_pairs)` — Create from a dict or iterable of `(key, value)` pairs.

---

### Basic operations

* `has_key(key)` — True if key exists.
* `delete(key)` — Remove a key.
* `drop(*keys)` — Remove multiple keys.
* equality (`==`) — Compares underlying dictionary.

---

### Transforming

* `map(transform)` — Apply `(key, value) -> result`, returning an `Enum`.
* `filter(predicate)` — Keep entries where predicate true.
* `reject(predicate)` — Remove entries where predicate true.

---

### Accessors

* `pairs()` — `Enum[(key, value)]`
* `to_keys()` — `Enum[key]`
* `to_values()` — `Enum[value]`
* `take(*keys)` — New `Map` containing only specified keys (missing keys ignored)

---

# Interoperability

`Enum` and `Map` are designed to flow into each other:

```python
Enum(users) \
    .group_by(lambda u: u.country) \
    .map(lambda country, users: (country, users.size())) \
    .into(Map)
```

Typical terminal conversions:

* `Enum(...).into(list)`
* `Enum(...).into(tuple)`
* `Enum(...).into(Map)`
* `Map(...).pairs().into(list)`
