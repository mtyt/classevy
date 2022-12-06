# Classevy
## Introduction
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

For an example file, see [here](https://github.com/mtyt/classevy/blob/main/data/students_example.csv).

## Instructions to install repository (for Mac or Linux - or probably [git-bash on Windows](https://git-scm.com/download/win))
To run the algorithm on your own computer, follow these instructions. I'm assuming you
have python3 installed, as well as Jupyter.
I recommend using a virtual environment. If you don't have it installed yet, do:

    $ python -m pip install --user virtualenv

Clone the `classevy` repository somewhere and cd into it:

    $ git clone https://github.com/mtyt/classevy.git
    $ cd classevy 

or use SSH if you know how.
Make a new virtual environment called `env` and activate it:

    $ virtualenv env
    $ source env/bin/activate

Then install the `optime` package from github:

    $ python -m pip install 'optime @ git+https://github.com/mtyt/optime'

Since we're using the 'src-layout' structure in this repository, we have to install the
package before we can import it. We use an 'editable' install, in case you want to tinker
with the source code and see those changes when you import the package:

    $ pip install -e .

Install Jupyter:

    $ pip install jupyter
    
Then check where Jupyter is found:

    $ which jupyter

This should return a path ending in `classevy/env/bin/jupyter`. If not, restart your
terminal and don't forget to activate your virtual environment again with `source env/bin/activate`.
Then tell Jupyter to create a kernel linked to this venv:

    $ ipython kernel install --user --name=env_classevy

So now when you start Jupyter from `env`, you can choose the `env_classevy` kernel with all
the right packages installed in it.


Now you're ready to fire up Jupyter Notebook:

    $ jupyter notebook

In the browser, go to `examples` and open the notebook called `optimize_class.ipynb`.
Before you run any cells, got to the menu `Kernel > Change kernel` and choose env_classevy or whatever you called it.
If, when you run the first cell, you get an error saying that the module `classevy` can't be found,
then probably something went wrong in the linking of the Jupyter kernel to the virtual
environment. I recommend to repeat the 3 steps above and make sure to check the path
of `jupyter`.

# Instructions to run web-app in Docker
I've created a kind-of user version in a web-app using Flask, which can be run in a docker
container. In order to run this, make sure to have [Docker](https://www.docker.com/) installed.
I'm providing instructions here on how to run it from a command line, but I'm sure
there are other ways:

    $ docker build --tag classevy .
    $ docker run -it -p 8000:8000 classevy

Then in your browser, if you go to `http://127.0.0.1:8000/`, the web-app should show.
Note that this is very experimental and I can not guarantee that it will work!

# Even more experimental: web-app in the cloud
I've somehow managed to get this docker container onto Azure cloud and it's running here:
[classevy.azurewebsites.net](https://classevy.azurewebsites.net). But again, no guarantees
here that it will work and I would not recommend putting actual real student information
there because I have no idea how secure your data will be (probably not very!)
If this turns out to be useful for people, I might continue working on it, but as they
say here, I really haven't eaten much cheese of this kind of stuff.

## Feedback
This project can be found on [GitHub](https://github.com/mtyt/classevy).

Any feedback, suggestions, criticism can be emailed to maarten.tytgat@gmail.com