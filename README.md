# enumerio

`enumerio` is a tiny, ergonomic collection helper inspired by Elixir's `Enum` module. It wraps Python iterables into a small, list-like object (`Enum`) and provides expressive, chainable operations for common data-processing tasks.

---

## Usage

```python
from enumerio import Enum

Enum(range(1, 10)).map(lambda x: x**2).filter(lambda x: x > 100).take(5).each(print)
```

See [What is a Enum?](#what-is-a-enum) for implementation details.

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

Python has excellent built-in collection primitives, but many real-world tasks become much clearer when written as a **pipeline of transformations** rather than loops with temporary variables and flags. Implementing an `Enum`-style helper in Python is useful because:

- **Readability**: `Enum(data).map(...).filter(...).take(3)` reads left-to-right as a data flow — the intent is clear.
- **Composability**: Small functions compose cleanly; you can reuse pieces of a pipeline easily.
- **Declarative style**: You describe *what* you want to do to the data rather than *how* to iterate it.
- **Fewer bugs**: Pipelines reduce mutable state (counters, accumulators), minimizing accidental side effects.

Even though Python already has `map`/`filter`/list comprehensions and libraries like `itertools`/`more-itertools`, bundling common operations into a coherent, chainable interface yields code that is both compact and highly readable.

---

## Pipeline style: why it shines

Pipeline code focuses on the transformation steps rather than control flow. This makes code easier to reason about, test, and refactor:

- Break complex processing into named steps (`.map(...)`, `.filter(...)`, `.frequencies()`) that are each easy to test.
- Move from imperative loops to functional building blocks; that helps when reasoning about edge cases (empty lists, single element, etc.).
- Pipelines encourage use of small pure functions that are reusable across projects.

---

## What is a Enum?

The main building block is a `Enum`. It's basically a successor of `UserList` (i.e. `list`) and provides all the same functionality as a basic list (except mutability: don't try to change it even though it is technically possible). So the following assertions do not raise:

```python
assert Enum([1, 2, 3]).map(lambda x: x**2) == [1, 4, 9]
assert Enum([1, 2, 3, 4, 5]).chunk_every(3, 1) == [[1, 2, 3], [2, 3, 4], [3, 4, 5]]
```

So you can pass `Enum` to any function which accepts a `list` as argument.

---

## API: available functions

List of methods on `Enum` with short descriptions (roughly following the implementation):

- `Enum(data)` — Construct an `Enum` from any iterable.
- `len()` — Return number of elements.
- `member(elem)` — True when `elem` is present.
- `all(predicate=None)` — True if all elements satisfy `predicate` (or truthy if no predicate).
- `any(predicate=None)` — True if any element satisfies `predicate` (or truthy if no predicate).
- `at(index, default=None)` — Return element at `index` or `default` if out-of-range.
- `chunk_every(count, step=None)` — Split into chunks of `count`, advancing by `step` (defaults to `count`). Returns `Enum[Enum[T]]`.
- `drop(amount)` — Drop `amount` elements from head (negative drops from tail).
- `each(procedure)` — Invoke `procedure` for every element (for side effects).
- `empty()` — True if Enum is empty.
- `fetch(index)` — Return `Ok(value)` or `Error(message)` when out-of-range.
- `fetch_(index)` — Return element or raise `IndexError` if out-of-range.
- `map(transform)` — Map elements with `transform`, returning a new `Enum`.
- `map_join(transform, joiner="")` — Map elements to strings and join them.
- `min()` — Return the minimal element; raises `ValueError` if empty.
- `min_by(key)` — Return the element minimizing `key`; raises `ValueError` if empty.
- `max()` — Return the maximal element; raises `ValueError` if empty.
- `max_by(key)` — Return the element maximizing `key`; raises `ValueError` if empty.
- `min_max()` — Return `(min, max)` pair; raises `ValueError` if empty.
- `min_max_by(key)` — Return `(min_by, max_by)` pair based on `key`.
- `prod()` — Product of elements (`math.prod`).
- `prod_by(mapper)` — Product after mapping each element with `mapper`.
- `filter(predicate)` — Keep elements that match `predicate`.
- `filter_map(transform)` — Apply `transform` returning `Result`; collect unwrapped `Ok` values and discard `Error`s.
- `flatten()` — Deep-flatten nested sequences into a single `Enum`.
- `find(predicate, default=None)` — Return first matching element or `default`.
- `find_index(predicate)` — Return index of first matching element or `None`.
- `find_value(transform, default=None)` — Return first truthy transformed value or `default`.
- `frequencies()` — Return `dict[element, count]` of occurrences.
- `join(joiner="")` — Join string elements using `joiner`.
- `reject(predicate)` — Complement of `filter` (exclude when predicate true).
- `reversed(tail=None)` — Return reversed `Enum`, optionally appending `tail`.
- `random()` — Return one random element (raises if empty).
- `reduce(fun, acc)` — Reduce to a single value using `fun` and initial `acc`.
- `shuffle()` — Return a shuffled `Enum` copy.
- `sorted()` — Return `Enum` sorted ascending.
- `split(count)` — Split into two `Enum`s: first `count` and the rest.
- `split_while(predicate)` — Split into prefix satisfying predicate and remaining suffix.
- `split_with(predicate)` — Partition into `(matching, not_matching)`.
- `sum()` — Sum elements.
- `sum_by(mapper)` — Sum after mapping each element with `mapper`.
- `take(amount)` — Take first `amount` elements (negative takes from tail).
- `take_every(nth)` — Take every `nth` element.
- `take_random(count)` — Return `count` random elements.
- `take_while(predicate)` — Take elements from the start while `predicate` holds.
- `uniq()` — Return a new `Enum` preserving order but removing duplicate elements (first occurrence kept).
- `zip()` — Zip corresponding elements from a collection of enumerables into an `Enum` of tuples. (Stops when the shortest enumerable is exhausted.)
- `sublist(*indices)` — Extract elements at the given indices from each sub-sequence.
- `subdict(*keys)` — Extract key-value pairs for the given keys from each sub-dictionary.
