# Classevy
A good friend of mine is a teacher in elementary school and every year she
faces the same problem: having to divide her students into 2 classes. She wants
to divide them as evenly as possible based on multiple criteria:
- gender
- scores on math and spelling
- whether they need extra attention
- whether they have a learning (dis)advantage
- whether they have difficult behavior

On top of that, each student can name 3 other students with whom they'd like to
be in the same class (and at least 1 of those preferences should be satisfied).
Furthermore, the teacher can decide that particular students should or should
not be in the same class together.

Obviously, satisfying those conditions while balancing the other criteria, can
prove to be a difficult task for a regular human being. Fortunately, there's
computers.

I initially thought this would be perfect for a Genetic Algorithm to solve.
I've used GAs in the past to optimize electronic circuits so I'm quite familiar
with them (and to be honest, I'm not very familiar with any other optimization
algorithms), so I decided to give it a go.

However, it quickly turned out that brute-force optimizing those hard criteria
for which students should be in the same class as others, doesn't really work.
So I had to come up with some way to satisfy those conditions as an additional
step during the optimization.

The optimization bit, I put in a separate package called `optime`, available on
[GitHub](https://github.com/mtyt/optime) and
[PyPI](https://pypi.org/project/optime/).
The rest is in this package. The name of the package refers to my friend.
I hope she can try it for next school year and I hope her students won't mind
being guinea pigs in my Python projects.

The `data/` folder contains fictional examples of students. The criteria for
which to divide the classes evenly can be anything, as long as they are numeric.
So gender is represented by +/-1 or 0. Score can be 0-10 or 0-5 but not A-E.
The csv files should contain columns called:
- 'number' (should be unique for each student)
- 'name' (any string will do)
- 'not_together' (comma-separated student numbers for students that should *not*
be in the same class)
- 'together' (comma-separated student numbers for students that should
be in the same class)
- 'preferences' (comma-separated student numbers for students that this students
wants to be in the same class with - the algoritm will strive to satisfy at
least 1 preference.)

This project can be found on [GitHub](https://github.com/mtyt/classevy).