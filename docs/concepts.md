## Conceptual overview

This section describes, at a high level, how the different mechanisms
in `straight.el` play together. This illustrates how `straight.el`
manages to accomplish all of
its [guiding principles][guiding-principles].

### TL;DR

`straight.el` operates by cloning Git repositories and then symlinking
files into Emacs' load path. The collection of symlinked files
constitutes the package, which is defined by its recipe. The recipe
also describes which local repository to link the files from, and how
to clone that repository, if it is absent.

When you call `straight-use-package`, the recipe you provide is
registered with `straight.el` for future reference. Then the package's
repository is cloned if it is absent, the package is rebuilt if its
files have changed since the last build (as determined by `find(1)`),
and its autoloads are evaluated.

You can also provide only a package name, in which case the recipe
will be looked up in one of several configurable recipe repositories,
which are just packages themselves (albeit with the build step
disabled).

`straight.el` determines which packages are installed solely by how
and when `straight-use-package` is invoked in your init-file, so some
optimizations and validation operations require you to provide
additional contextual information by declaring "transaction" blocks.

### What is a package?

A *package* is a collection of Emacs Lisp (and possibly other) files.
The most common case is just a single `.el` file, but some packages
have many `.el` files, and some even have a directory structure.

Note that a package is defined only as a collection of files. It
doesn't necessarily correspond to a Git repository, or an entry on
MELPA, or anything like that. Frequently there is a relationship
between all of these concepts, but that relationship does not always
have to be direct or one-to-one.

A package also has a name, which must be unique. This is the name that
is used for the folder holding the package's files. It is frequently
the same as the name of a Git repository, or an entry on MELPA, but
again this does not have to be the case.

### Where do packages come from?

If you really wanted all of your packages to be unambiguously defined,
you could just copy and paste all of their files into version control.
But that would defeat the purpose of using a package manager like
`straight.el`. In `straight.el`, packages are defined by two sources
of information:

* a *local repository*
* a *build recipe*

The local repository is just a directory containing some files. Of
course, it also has a name, which may or may not be the same as the
package's name. Frequently, the local repository is also a Git
repository, but this is not necessary.

The build recipe is not a literal data structure. It is a concept that
represents a certain subset of the package's recipe. Specifically, the
`:files`, `:local-repo`, and `:no-build` keywords.

To transform this *information* into an actual package that Emacs can
load, `straight.el` *builds* the package. This means that some
symbolic links are created in the package's directory that point back
into the local repository's directory. Exactly how these symlinks are
created is determined by the `:files` directive, and which local
repository the symlinks point to is determined by the `:local-repo`
directive.

After the symlinks are created, the resulting files are byte-compiled,
and their autoloads are generated and written into a file in the
package's directory.

If `:no-build` is specified, however, this entire process is skipped.
This mechanism is used for recipe repositories.

### What does this look like on disk?

The local repositories are kept in `~/.emacs.d/straight/repos`, and
the built packages are kept in `~/.emacs.d/straight/build`. If you
have initialized `straight.el` and loaded package `el-patch`, then
your `~/.emacs.d/straight` directory will look roughly like this (some
irrelevant details have been omitted for pedagogical purposes):

<!-- longlines-start -->

    straight
    ├── build
    │   ├── el-patch
    │   │   ├── el-patch-autoloads.el
    │   │   ├── el-patch.el -> ~/.emacs.d/straight/repos/el-patch/el-patch.el
    │   │   └── el-patch.elc
    │   └── straight
    │       ├── straight-autoloads.el
    │       ├── straight.el -> ~/.emacs.d/straight/repos/straight.el/straight.el
    │       └── straight.elc
    └── repos
        ├── el-patch
        │   ├── CHANGELOG.md
        │   ├── LICENSE.md
        │   ├── README.md
        │   └── el-patch.el
        └── straight.el
            ├── LICENSE.md
            ├── Makefile
            ├── README.md
            ├── bootstrap.el
            ├── install.el
            └── straight.el

<!-- longlines-stop -->

As you can see, the package names are `el-patch` and `straight`. While
`el-patch` is built from a local repository of the same name,
`straight` is built from a local repository by the name `straight.el`.
Also note that only `.el` files are symlinked, since only they are
relevant to Emacs.

### Where do repositories come from?

Local repositories provide a way to define packages without specifying
the contents of all of their files explicitly. But that's not helpful
without a higher-level way to define local repositories without
specifying the contents of all of *their* files. In `straight.el`,
local repositories are defined by two sources of information:

* a *fetch recipe*
* the *version lockfiles*

The fetch recipe is, like the build recipe, a concept representing a
certain subset of the package's overall recipe. The situation is more
interesting here because `straight.el` supports multiple
version-control backends. The version-control backend specified by the
fetch recipe is determined by the `:type` directive (which defaults to
`straight-default-vc`). Each version-control backend then accepts some
set of additional directives. For example, the `git` backend accepts:

* `:repo`
* `:host`
* `:branch`
* `:nonrecursive`
* `:upstream`

If a local repository is not present, then its fetch recipe describes
how to obtain it. This is done using the `straight-vc-clone` function,
which delegates to one of the backend implementations of the `clone`
operation, according to `:type`.

However, even with a particular repository source specified, there is
still the question of which version of the repository to use. This is
where the version lockfiles come in. When a local repository is
cloned, the version lockfiles are searched to see if there is a
particular commit specified for that local repository's name. If so,
that commit is checked out. (For the `git` backend, commits are
40-character strings representing SHA-1 hashes, but the representation
of a commit identifier could be different across different backends.)

The `straight-freeze-versions` and `straight-thaw-versions` methods
also use backend-delegating methods; in this case, they are
`straight-vc-get-commit` and `straight-vc-check-out-commit`.

The fetch recipe and version lockfiles, together with the
configuration options for `straight.el`, precisely define the state of
a local repository. Of course, you may make any changes you want to
the local repository. But this information defines a "canonical" state
that you may revert to at any time.

When this information is combined with the build recipe, `straight.el`
is able to construct canonical, universal versions of your Emacs
packages that will be the same everywhere and forever.

Note that you do not have to provide fetch recipes or version
lockfiles. You may manage your local repositories manually, if you
wish, although this has obvious disadvantages in terms of
repeatability and maintainability.

### What does it mean to load a package?

A prerequisite to loading a package is making sure the package has
been built. After that is done, loading the package means adding its
directory to the load path and evaluating its autoloads file.

Adding the directory to the load path means that you can use `require`
to load the package's files. Note that `straight.el` does not do this
for you, since loading packages immediately is usually not necessary
and it immensely slows down Emacs startup.

Evaluating the autoloads file means that calling the functions that
are defined in the autoloads file will automatically `require` the
files that define those functions. All modern packages define their
functions in autoloads and are designed to be loaded on-demand when
those functions are called. Antiquated packages may need you to
explicitly define autoloads, or to just `require` the package right
away.

### Where do recipes come from?

`straight-use-package` does not require an actual recipe. You can just
give it a package name, and it will look up the recipe. This is done
using *recipe repositories*. Recipe repositories are set up as a
swappable backend system, much like the version-control backend
system.

A recipe repository consists of four parts:

* a fetch recipe for the local repository (this will typically include
  the `:no-build` directive, since recipe repositories usually do not
  need to be built)
* a function that, provided the local repository is already available,
  returns a list of all packages that have recipes in the recipe
  repository
* a function that, given a package name, returns the recipe for that
  package, or nil if the recipe repository does not provide a recipe
  for the package
* an entry in `straight-recipe-repositories` indicating that the
  recipe provided actually corresponds to a recipe repository
  (otherwise it would just be a regular package)

Note that recipe repositories are implemented as regular packages!
This means that all the usual package management operations work on
them as well. It also means that you use `straight-use-package` to
register them (although typically you will provide arguments to
`straight-use-package` so that the recipe repository is only
registered, and not cloned until it is needed;
see
[the section on `straight-use-package`][straight-use-package-overview]).

If you give `straight-use-package` just a package name, then each
recipe repository in `straight-recipe-repositories` is checked for a
recipe for that package. Once one is found, it is used. Otherwise, an
error is signaled (unless the package is built-in to Emacs, according
to `package.el`).

Note that `straight.el` uses its own recipe format which is similar,
but not identical, to the one used by MELPA. The recipe repository
backends abstract over the formatting differences in different recipe
sources to translate recipes into the uniform format used by
`straight.el`. When you run `M-x straight-get-recipe`, the translated
recipe is what is returned.

### What happens when I call `straight-use-package`?

There are three actions that `straight-use-package` can take:

* Register a package's recipe with `straight.el`.
* Clone a package's local repository, if it is missing.
* Build a package, if it has been changed since the last time it was
  built, and load it.

These actions must be performed in order. Depending on the arguments
you pass to `straight-use-package`, one, two, or all three may be
performed.

The normal case is to do all three. The fetch recipe is only required
if the local repository is actually missing, but the build recipe is
always required.

Deferred installation can be accomplished by telling
`straight-use-package` to stop if the local repository is not already
available. The deferred installation can be triggered by invoking
`straight-use-package` again, but telling it to go ahead and clone the
repository (this is the default behavior). Because
`straight-use-package` already registered the package's recipe the
first time, you don't have to provide it again.

In some extraordinary circumstances (such as when `straight.el` is
bootstrapping its own installation), it may be desirable to clone a
package's local repository if it is missing, but to stop before
building and loading the package. This can also be done by
`straight-use-package`.

### What does it mean to register a package?

Package registration is the first action taken by
`straight-use-package`, before building and cloning. First, if only a
package name was provided to `straight-use-package`, a recipe is
obtained from the configured recipe repositories. Next, the resulting
recipe is recorded in various caches.

This is important, since it allows for several things to happen:

* if you later want to perform another operation on the package using
  `straight.el`, you do not need to provide the recipe again
* if you use a custom recipe for Package A, and Package B requires
  Package A as a dependency, your custom recipe is remembered and
  re-used when Package A is used as a dependency, to avoid conflicts.
* when multiple packages are built from the same local repository, and
  you have specified a custom fetch recipe for one of those packages,
  `straight.el` can intelligently merge that fetch recipe into the
  automatically retrieved recipes of dependencies, in order to avoid
  conflicts.
* `straight.el` knows which packages you have installed, if you want
  to perform interactive operations on them.
* if you accidentally provide two different recipes for the same
  package, `straight.el` can issue a helpful warning, since this may
  lead to surprising behavior.

### How does `straight.el` know when to rebuild packages?

When you request for `straight.el` to load a package (using
`straight-use-package`), it first checks if the package needs to be
rebuilt. This means that some of the files in its local repository
have been modified since the last time the package was built.
`straight.el` uses an optimized `find(1)` command to check for package
modifications, and it uses some caching mechanisms to perform bulk
`find(1)` operations on multiple packages, to speed up these checks
(although it never performs optimizations that may result in erroneous
behavior).

This check occurs during Emacs init, when your init-file makes calls
to `straight-use-package`. You may notice a significant delay on the
first `straight-use-package` call, because this is when `straight.el`
performs a bulk `find(1)` call and caches the results for later usage
(this speeds up init considerably). The total delay is likely to be on
the order of 100ms for a double-digit number of packages.

The rebuild detection system is what allows for you to make changes to
packages whenever you would like, without performing any additional
operations.

(Packages are also rebuilt when their recipes change, of course.)

### How does `straight.el` know what packages are installed?

`straight.el` does not require you to declare a central list of
packages anywhere, like Cask does. Instead, it determines what
packages are to be loaded implicitly, by your invocations of
`straight-use-package` during Emacs initialization. Furthermore,
`straight.el` allows you to install packages after initialization
using `M-x straight-install-package` (or even by evaluating
`straight-use-package` forms). However, `straight.el` still provides
advanced features such as bulk package management and version locking.
This creates some interesting challenges which other package managers
do not have to deal with.

`straight.el` solves these problems using a concept called
*transactions*. Transactions are a way of grouping calls to
`straight-use-package`. They are actually used in many contexts to
support various optimizations, but perhaps their most important use is
in defining the packages that are loaded by your init-file.

During initial Emacs init, `after-init-hook` is used to determine when
your init-file has finished loading. Thus `straight.el` can tell the
difference between packages loaded by your init-file, and packages
installed interactively.

However, you may want to add packages to your init-file without
restarting Emacs. How can this be done? You need simply re-evaluate
your whole init-file within a single transaction. Practically, this is
done by having your function to reload your init-file wrap the `load`
call in a `straight-transaction` block. This allows `straight.el` to
tell exactly which packages are now referenced by your init-file.

So what is the use of this? Well, an operation like `M-x
straight-freeze-versions` requires an exact knowledge of what packages
are required by your init-file, so that it does not write
interactively installed packages into your lockfiles. The
`straight-freeze-versions` function uses the information it gains from
the transaction system in order to prompt you to reload your init-file
if you have installed packages since the last time your init-file was
loaded (and `straight.el` therefore was able to determine which
packages were actually part of your init-file).

Finally, a note on the use of transactions for optimizations. There
are a number of setup and tear-down operations associated with package
management. For example, to keep track of when packages need to be
rebuilt, `straight.el` keeps a persistent build cache. Normally, this
cache needs to be read and written after every package install. But
that is very slow: much better is to load it at the first package
install, and to save it at the last package install. The question then
is how to identify the last package install. This is not possible in
general (although in the special case of initial Emacs init,
`after-init-hook` can be used), so `straight.el` falls back on the
transaction system. By wrapping the entire operation in a transaction,
`straight.el` can safely optimize the loading and saving of the build
cache, significantly improving performance. For this reason, reloading
your init-file is likely to be rather slow if you do not wrap the call
in a transaction using `straight-transaction`.
