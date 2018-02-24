## User manual

This section tells you everything you need to know about the
user-facing features of `straight.el`. For implementation details, see
the [developer manual][developer-manual]. It may also be helpful to
get some perspective on the overarching concepts of `straight.el` from
the [conceptual overview][conceptual-overview].

### Bootstrapping `straight.el`

In order to use `straight.el`, you will need to somehow get it loaded
into Emacs. (This is easy for `package.el`, since `package.el` is
built in to Emacs. `straight.el` must work a little harder.)

`straight.el` comes with a file to do just this, `bootstrap.el`. All
you need to do is load that file. You can do this with `M-x load-file`
or by a call to `load` in your init-file. However, there is an obvious
shortcoming: `bootstrap.el` will only be available once `straight.el`
is already installed.

You could just invoke `git clone` from your init-file, if
`straight.el` is not installed, but then you would have to manually
take care of selecting the correct branch, parsing your version
lockfile to check out the right revision, and so on. Instead, you can
just use this snippet, which uses a copious amount of magic to take
care of all these details for you:

<!-- longlines-start -->

    (let ((bootstrap-file (concat user-emacs-directory "straight/repos/straight.el/bootstrap.el"))
          (bootstrap-version 3))
      (unless (file-exists-p bootstrap-file)
        (with-current-buffer
            (url-retrieve-synchronously
             "https://raw.githubusercontent.com/raxod502/straight.el/develop/install.el"
             'silent 'inhibit-cookies)
          (goto-char (point-max))
          (eval-print-last-sexp)))
      (load bootstrap-file nil 'nomessage))

<!-- longlines-stop -->

Despite the reference to `develop`, this snippet actually installs
from the `master` branch by default, just like every other package.
Furthermore, the correct revision of `straight.el` is checked out, if
you have one specified in your lockfile. Even better, you can
[override the recipe for `straight.el`][straight.el-recipe], just like
for any other package.

### Installing packages programmatically

The primary entry point to `straight.el` is the `straight-use-package`
function. It can be invoked interactively (for installing a package
temporarily) or programmatically (for installing a package
permanently). This section covers the programmatic usage;
see [later][interactive-usage] for interactive usage.

Here is the basic usage of `straight-use-package`:

    (straight-use-package 'el-patch)

This will ensure that the package `el-patch` is installed and loaded.
(Note that `straight-use-package` takes a symbol, not a string, for
the name of the package.) Precisely, this is what happens:

* If the local Git repository for `el-patch` is not available, it is
  cloned, and the appropriate revision is checked out (if one is
  specified in your version lockfiles).
* If the local Git repository has been modified since the last time
  the package was built, it is rebuilt. This means:
    * The `.el` files are symlinked into a separate directory to
      isolate them from other, irrelevant files.
    * The main package file is checked for dependencies, which are
      installed recursively if necessary using `straight-use-package`.
    * The `.el` files are byte-compiled.
    * Autoloads are extracted from the `.el` files and saved into a
      separate file.
* The package's directory is added to Emacs' `load-path`.
* The package's autoloads are evaluated.

Package authors should note that `straight.el` checks for dependencies
that are specified in the [`package.el` format][package.el-format]. To
spare you reading that documentation, this is either a
`Package-Requires` header in `PACKAGENAME.el`, or an argument to a
`define-package` invocation in `PACKAGENAME-pkg.el`. Despite
the [many shortcomings][package.el-disadvantages] of `package.el`, it
has done a good job of creating a standardized format for dependency
declarations.

Note that loading a package does not entail invoking `require` on any
of its features. If you wish to actually load the files of the
package, you need to do this separately. This is because most packages
do not need to be loaded immediately, and are better served by the
autoload system.

#### Installing with a custom recipe

`straight-use-package` can also take a list instead of a symbol. In
that case, the first member of the list is a symbol giving the package
name, and the remainder of the list is
a [property list][property-lists] providing information about how to
install and build the package. Here is an example:

    (straight-use-package
     '(el-patch :type git :host github :repo "your-name/el-patch"
                :upstream (:host github
                           :repo "raxod502/el-patch")))

If you give `straight-use-package` just a package name, then a recipe
will be looked up by default (see the section
on [recipe lookup][recipe-lookup]). You can see the default recipe for
a package by invoking [`M-x straight-get-recipe`][interactive-usage].

To learn more, see the section on [the recipe format][recipe-format].

#### Additional arguments to `straight-use-package`

The full user-facing signature of `straight-use-package` is:

    (straight-use-package PACKAGE-OR-RECIPE &optional NO-CLONE NO-BUILD)

As discussed [previously][straight-use-package-usage], by default
`straight-use-package` will do three things:

* Register the recipe provided with `straight.el`.
* Clone the package's local repository, if it is absent.
* Rebuild the package if necessary, and load it.

By providing the optional arguments, you may cause processing to halt
before all three of these tasks are completed. Specifically, providing
`NO-CLONE` causes processing to halt after registration but before
cloning, and providing `NO-BUILD` causes processing to halt after
cloning (if necessary) but before building and loading.

`straight.el` supports lazy-loading by means of a special value for
`NO-CLONE`, the symbol `lazy`. If this symbol is passed, then
processing will halt at the clone step, unless the package is already
cloned. This means that the package is built and loaded if it is
already installed, but otherwise installation is deferred until later.
When you want to trigger the lazy installation, simply call
`straight-use-package` again, but without `NO-CLONE`. (There is no
need to pass the recipe again; see [recipe lookup][recipe-lookup].)

You can also pass functions for `NO-CLONE` or `NO-BUILD`, which will
be called with the package name as a string; their return values will
then be used instead.

Note that if it makes no sense to build a package, then you should put
`:no-build t` in its [recipe][recipe-format], rather than specifying
`NO-BUILD` every time you register it with `straight.el`. (This is
especially relevant when writing recipes
for [recipe repositories][customizing-recipe-repositories].)

#### Variants of `straight-use-package`

For convenience, `straight.el` provides some functions that wrap
`straight-use-package` with particular arguments, to cover all of the
common cases. Each of these functions takes only a package name or
recipe, and no additional arguments.

* `straight-register-package`: always stop after the registration
  step. This may be useful for specifying the recipe for an optional
  dependency (see [recipe lookup][recipe-lookup], but see
  also [recipe overrides][overriding-recipes]).
* `straight-use-package-no-build`: always stop before the build step.
  This is used by [`straight-freeze-versions`][lockfiles] to make sure
  packages are cloned, since building them is unnecessary for writing
  the lockfiles.
* `straight-use-package-lazy`: stop at the clone step if the package's
  local repository is not already cloned. This is used for
  lazy-loading.

#### Customizing when packages are built

By default, when `straight.el` is bootstrapped during Emacs init, it
uses a bulk `find(1)` command to identify files that were changed
since the last time a package depending on them was built. These
packages are then rebuilt when they are requested via
`straight-use-package`. For about 100 packages on an SSD, this takes
about 500ms. You can save this time by customizing
`straight-check-for-modifications`.

The default value is `at-startup`. If you change this to `never`, then
`straight.el` will not check for package modifications, and you will
have to manually (or programmatically) call `straight-rebuild-package`
when you modify a file and need a package rebuilt.

You can also change it to `live`, which means that `straight.el` will
use `before-save-hook` in order to detect modifications as you make
them. This saves init time, but has a caveat: namely, that
modifications made outside Emacs or in some way that bypasses
`before-save-hook` are not detected. Pull requests extending the
number of cases in which `straight.el` is able to detect live
modifications are welcome.

#### Customizing how packages are built

By specifying a non-nil value for the `:no-build` attribute in a
package's [recipe][recipe-format], you may prevent the package from
being built at all. This is usually useful for recipe repositories
which do not bundle executable Lisp code. (Make sure to
use [`straight-use-recipes`][customizing-recipe-repositories] for
registering recipe repositories.)

By specifying a non-nil value for the `:no-autoloads` attribute in a
package's recipe, you may prevent any autoloads provided by the
package from being generated and loaded into Emacs. This is mostly
useful if the package provides a large number of autoloads, you know
you need only a few of them, and you wish to optimize your startup
time (although this is almost certainly premature optimization unless
you *really* know what you're doing). You can also customize the
variable `straight-disable-autoloads` to effect this change on all
recipes which do not explicitly specify a `:no-autoloads` attribute.

### The recipe format

The general format for a `straight.el` recipe is:

    (package-name :keyword value :keyword value ...)

Note that if you wish to pass a recipe to `straight-use-package`, you
will need to quote it. If you need to compute part of the recipe
dynamically, use backquoting:

    (straight-use-package
     `(el-patch :type git :repo ,(alist-get 'el-patch my-package-urls)))

Here is a comprehensive list of all keywords which have special
meaning in a recipe (unknown keywords are ignored but preserved):

* `:local-repo`

  This is the name of the local repository that is used for the
  package. If a local repository by that name does not exist when you
  invoke `straight-use-package`, one will be cloned according to the
  package's [version-control settings][vc-backends].

  Multiple packages can use the same local repository. If so, then a
  change to the local repository will cause both packages to be
  rebuilt. Typically, if multiple packages are drawn from the same
  repository, both should specify a `:files` directive.

  If you do not provide `:local-repo`, then it defaults to a value
  derived from the [version-control settings][vc-backends], or as a
  last resort the package name.

* `:files`

  This is a list specifying which files in a package's local
  repository need to be symlinked into its build directory, and how to
  arrange the symlinks. For most packages, the default value
  (`straight-default-files-directive`) will suffice, and you do not
  need to specify anything.

  If you do need to override the `:files` directive (this happens most
  commonly when you are taking a single package from a repository that
  holds multiple packages), it is almost always sufficient to just
  specify a list of globs or filenames. All matching files will be
  linked into the top level of the package's build directory.

  In spite of this, the `:files` directive supports an almost
  comically powerful DSL (with nested excludes and everything!) that
  allows you full flexibility on how the links are made; see the
  docstring of `straight-expand-files-directive` for the full details.

* `:no-build`

  If this is non-nil, then it causes the build step to be skipped
  entirely and unconditionally. You should specify this
  for [recipe repository recipes][customizing-recipe-repositories].

* `:type`

  This specifies the version-control backend to use for cloning and
  managing the package's local repository. It defaults to the value of
  `straight-default-vc`, which defaults to `git`.

  The only version-control backend currently supported is `git`,
  although more backends may be added.

* backend-specific keywords

  Depending on the value of `:type`, additional keywords (relevant to
  how the package's repository is cloned and managed) will be
  meaningful. See the next section.

#### Version-control backends

Defining a version-control backend consists of declaring a number of
functions named as `straight-vc-BACKEND-METHOD`, where `BACKEND` is
the name of the version-control backend being defined and `METHOD` is
a backend API method. The relevant methods are:

* `clone`: given a recipe and a commit object, clone the repository
  and attempt to check out the given commit.
* `normalize`: given a recipe, "normalize" the repository (this
  generally means reverting it to a standard state, such as a clean
  working directory, but does not entail checking out any particular
  commit).
* `fetch-from-remote`: given a recipe, fetch the latest version from
  its configured remote, if one is specified.
* `fetch-from-upstream`: given a recipe, fetch the latest version from
  its configured upstream, if one is specified.
* `merge-from-remote`: given a recipe, merge the latest version
  fetched from the configured remote, if any, to the local copy.
* `merge-from-upstream`: given a recipe, merge the latest version
  fetched from the configured upstream, if any, to the local copy.
* `pull-from-remote`: given a recipe, pull the latest version of the
  repository from its configured remote, if one is specified.
* `pull-from-upstream`: given a recipe, pull the latest version of the
  repository from its configured upstream, if one is specified.
* `push-to-remote`: given a recipe, push the current version of the
  repository to its configured remote, if one is specified.
* `check-out-commit`: given a local repository name and a commit
  object, attempt to check out that commit.
* `get-commit`: given a local repository name, return the commit
  object that is currently checked out.
* `local-repo-name`: given a recipe, return a good name for the local
  repository, or nil.
* `keywords`: return a list of keywords which are meaningful for this
  version-control backend.

Most of these methods are highly interactive: they don't actually do
anything without prompting you to confirm it, and very often they will
offer you a number of different options to proceed (including starting
a recursive edit and allowing you to do whatever you would like).

Also, all of the methods in this section
take [`straight.el`-style recipes][recipe-formats]; see the section
on [defining VC backends][defining-vc-backends] in the developer
manual for more details.

#### Git backend

These are the keywords meaningful for the `git` backend:

* `:repo`: the clone URL for the Git repository.
* `:host`: either nil or one of the symbols `github`, `gitlab`,
  `bitbucket`. If non-nil, then `:repo` should just be a string
  "username/repo", and the URL is constructed automatically.
* `:branch`: the name of the branch used for primary development, as a
  string. If your version lockfiles do not specify a commit to check
  out when the repository is cloned, then this branch is checked out,
  if possible. This branch is also viewed as the "primary" branch for
  the purpose of normalization and interaction with the remote.
* `:nonrecursive`: if non-nil, then submodules are not cloned. This is
  particularly important for the EmacsMirror recipe repository, which
  contains every known Emacs package in existence as submodules.
* `:upstream`: a plist which specifies settings for an upstream, if
  desired. This is meaningful for the `pull-from-upstream` method. The
  allowed keywords are `:repo`, `:host`, and `:branch`.

This section tells you how the `git` backend, specifically, implements
the version-control backend API:

* `clone`: clones the repository, including submodules if
  `:nonrecursive` is not provided. Checks out the commit specified in
  your revision lockfile, or the `:branch`, or `origin/HEAD`. If an
  `:upstream` is specified, fetches that remote as well.
* `normalize`: verifies that remote URLs are set correctly, that no
  merge is in progress, that the worktree is clean, and that the
  primary `:branch` is checked out.
* `fetch-from-remote`: checks that remote URLs are set correctly, then
  fetches from the primary remote.
* `fetch-from-upstream`: checks that remote URLs are set correctly,
  then fetches from the upstream remote.
* `merge-from-remote`: performs normalization, then merges from the
  primary remote into the primary local `:branch`.
* `merge-from-upstream`: performs normalization, then merges from the
  upstream remote into the primary local `:branch`.
* `pull-from-remote`: performs normalization, then pulls from the
  primary remote and merges with the primary `:branch`.
* `pull-from-upstream`: performs normalization, then pulls from the
  configured `:upstream`, if there is one. Merges with the primary
  `:branch`.
* `push-to-remote`: performs normalization, pulls from the primary
  remote if necessary, and then pushes if necessary.
* `check-out-commit`: verifies that no merge is in progress and that
  the worktree is clean, then checks out the specified commit.
* `get-commit`: returns HEAD as a 40-character string.
* `local-repo-name`: if `:host` is non-nil, then `:repo` will be of
  the form "username/repository", and "repository" is used. Otherwise,
  if the URL is of the form `.../<something>.git`, then `<something>`
  is used. Otherwise, nil is returned.
* `keywords`: see the list of keywords above.

You can customize the following user options:

* `straight-vc-git-default-branch`: if `:branch` is unspecified, then
  this is used instead. Defaults to "master".
* `straight-vc-git-primary-remote`: the name to use for the primary
  remote. Defaults to "origin". This cannot be customized on a
  per-repository basis.
* `straight-vc-git-upstream-remote`: the name to use for the upstream
  remote. Defaults to "upstream". This cannot be customized on a
  per-repository basis.
* `straight-vc-git-default-protocol`: the default protocol to use for
  automatically generated URLs when `:host` is non-nil. It can be
  either `https` or `ssh`, and defaults to `https` because this
  requires less work to set up.
* `straight-vc-git-force-protocol`: if this is non-nil, then HTTPS and
  SSH URLs are not treated as equivalent, so that bulk version-control
  operations will offer to re-set your remote URLs from HTTPS to SSH
  or vice versa, depending on the value of
  `straight-vc-git-default-protocol`. This is nil by default.

### Recipe lookup

If you only provide a symbol (package name) to `straight-use-package`,
then the recipe is looked up automatically. By default, [MELPA] and
[EmacsMirror] are searched for recipes, in that order. This means that
one or more of them may need to be cloned. Recipe repositories are
actually just the same as ordinary packages, except that their recipes
specify `:no-build`, so they are not symlinked or added to the
`load-path` or anything.

Note that dependencies always use the default recipes, since the only
information `straight.el` gets about a package's dependencies are
their names.

This leads to a few interesting questions regarding requesting a
package multiple times. For example, you might need to load two
features using [`use-package`][use-package] that are provided from the
same package, or one of the packages you have installed is also
requested as a dependency by another package. `straight.el` uses a
number of heuristics to try to make these interactions as intuitive
and painless as possible:

* The first time a package is registered with `straight.el`, its
  recipe (either the recipe that you provided, or the one that was
  looked up from a recipe repository) is recorded. In future
  registration, if you just provide the package name to
  `straight-use-package`, the existing recipe is reused.

  Note, however: *if* you want to use a custom recipe for a given
  package, you must load it *before* all of its dependencies.
  Otherwise, the package will first be registered as a dependency,
  using the default recipe.

* If a package has already been registered with `straight.el`, and you
  attempt to load it again with an explicit recipe which is different
  from the one previously registered, the new recipe is used but a
  warning is signalled.

* If you attempt to register a package which shares a `:local-repo`
  (either by default, or due to explicit specification) with a
  previously registered package, and the two packages specify
  different values for their version-control keywords (see
  [version-control backends][vc-backends]), then the new recipe is
  used but a warning is signalled. If the repository was already
  cloned, this means the second recipe will have no effect.

  But if the second recipe was fetched automatically from a recipe
  repository, all of its version-control keywords will be silently
  overwritten with the ones from the first recipe, to avoid conflicts
  (although if there are conflicts in other parts of the recipe, a
  warning will still be displayed).

#### Customizing recipe repositories

The recipe repository system is designed to be extended. Firstly, you
can control which recipe repositories are searched, and in what order
of precedence, by customizing `straight-recipe-repositories`. The
default value is:

    (melpa org-elpa emacsmirror)

To define a new recipe repository called `NAME`, you should do the
following things:

* Define a function `straight-recipes-NAME-retrieve`, which takes a
  package name as a symbol and returns a recipe for that package if it
  is available, else nil. This is used for recipe lookup. This
  function may assume that the local repository for the recipe
  repository has already been cloned, and that `default-directory` has
  been set to that local repository. This is used for recipe lookup
  during the course of `straight-use-package`.
* Define a function `straight-recipes-NAME-list`, which takes no
  arguments and returns a list of strings representing packages for
  which recipes are available. It is permissible to return some
  strings for which recipes are actually not available, for
  performance reasons. However, this is discouraged. (The [MELPA]
  backend uses this functionality, since all files in the `recipes`
  directory are potentially recipes, but only the Git-based ones can
  actually be used.)
* Call `straight-use-recipes` with the recipe for your recipe
  repository. Make sure to include `:no-build` in the recipe, unless
  you also want to use the recipe repository as an executable Emacs
  Lisp package. Alternatively, you can take the manual approach:
    * Call `straight-use-package-lazy` with the recipe for your recipe
      repository.
    * Add the symbol for your recipe repository's name (the car of the
      recipe you provided, that is) to `straight-recipe-repositories`,
      at the appropriate place.

### Overriding recipes

You can always use `straight-register-package` to specify a specific
recipe for a package without cloning or building it, so that just in
case that package is requested later (possibly as a dependency, or in
somebody else's code) your recipe will be used instead of the default
one. However, this does not help in the case that a specific recipe is
passed to `straight-use-package`.

Also, it is obviously impossible to call `straight-register-package`
before `straight.el` has been loaded, so you can't use it to specify a
custom recipe for `straight.el` itself.

To remedy these difficulties, `straight.el` provides a mechanism for
specifically overriding the recipe for a particular package. You can
use it by customizing `straight-recipe-overrides`, or by calling
`straight-override-recipe`.

`straight-recipe-overrides` is an association list
from [profile names][profiles] to *override alists*. If you don't care
about the profile system, you can just use a single override
specification, with the profile name nil. Each override alist is just
a list of recipes. Because the car of a recipe is just the package
name as a symbol, this list of recipes is also an alist whose keys are
recipe names and whose values are the plists for those recipes.

Even if an explicit recipe is supplied to `straight-use-package`, the
one given in `straight-recipe-overrides` will be used instead, if such
a recipe is specified there.

For convenience, you may add to `straight-recipe-overrides` by passing
a recipe to `straight-override-recipe`. This will register it in the
override alist for the current profile. Note that if you do this, you
will probably want to explicitly set `straight-recipe-overrides` to
nil before bootstrapping `straight.el`. This will make it so that if
you remove a call to `straight-override-recipe` from your init-file
and then reload it, the entry will actually be removed from
`straight-recipe-overrides`.

#### Overriding the recipe for `straight.el`

As was briefly mentioned earlier, you can actually override the recipe
of `straight.el` itself using `straight-recipe-overrides`! How does
this work? Well, it's basically black magic. If you want the details,
go read the [developer manual][straight.el-recipe-internals]. All you
need to know is that you can set `straight-recipe-overrides`, and it
will magically work. The only caveat is that if you change the
`:local-repo` for `straight.el`, then you will also need to adjust the
value of `bootstrap-file` in the [bootstrap snippet][bootstrap]
accordingly, since otherwise your init-file will not know where to
find `straight.el`. (You must use `straight-recipe-overrides` instead
of `straight-override-recipe`, since the latter function definition
hasn't been loaded yet before `straight.el` is installed and
bootstrapped.)

Here is the default recipe used for `straight.el`, if you don't
override it:

    (straight :type git :host github
              :repo "raxod502/straight.el"
              :files ("straight.el")
              :branch ,straight-repository-branch)

Note that even though the bootstrap snippet references the `develop`
branch of `straight.el`, the default recipe installs from `master`.

If all you want to do is change which branch you are installing
`straight.el` from, simply customize the variable
`straight-repository-branch`, which is provided for this purpose.
(Although using `straight-recipe-overrides` will work just as well, at
least until the recipe happens to be changed upstream and your
init-file isn't updated.)

### Interactive usage

The primary usage of `straight.el` is expected to be in your
init-file. For example, this is where you will need to put the
bootstrap code as well as any packages that you always want to be
installed. However, there are three important interactive uses of
`straight.el`: temporary installation of packages, various helpful
utility functions,
and [version control operations][repository-management].

To install a package temporarily, run `M-x straight-use-package`. All
registered recipe repositories will be cloned, and you will be
presented with a combined list of all recipes available from them.
Simply select a package and it will be cloned, built, and loaded
automatically. This does not affect future Emacs sessions.

If you provide a prefix argument to `M-x straight-use-package`, then
you are presented with a list of registered recipe repositories. After
you select one, you are shown a list of recipes specifically from that
recipe repository. This is helpful if you do not want to clone all
registered recipe repositories, or you have a particular recipe
repository in mind.

You can also call `M-x straight-get-recipe`, which has the same
interface as `M-x straight-use-package`, except that instead of the
package being cloned, built, and loaded, its recipe is copied to the
kill ring. If you are writing a custom recipe, this may be helpful,
because you may be able to reuse parts of the existing recipe,
particularly the `:files` directive.

Normally, packages are rebuilt automatically if needed, when Emacs
restarts. If you for some reason want them to be rebuilt at another
time, you can call `M-x straight-check-all` to rebuild all packages
that have been modified since their last build. Alternatively, use
`M-x straight-rebuild-all` to unconditionally rebuild all packages.
Note that this will probably take a while. There are also `M-x
straight-check-package` and `M-x straight-rebuild-package`, which
allow you to select a particular package to check or rebuild.

Finally, you may use `M-x straight-prune-build` in order to tell
`straight.el` to forget about any packages which were not registered
since the last init transaction
(see [the transaction system][transactions]). This may improve
performance, although only slightly, and will clean up stale entries
in the `build` directory. You can call this function in your init-file
if you really wish your filesystem to be as clean as possible,
although it's not particularly recommended as the performance
implications are uninvestigated. If you do call it in your init-file,
be sure to only call it on a fully successful init; otherwise, an
error during init will result in some packages' build information
being discarded, and they will need to be rebuilt next time.

### Version control operations

`straight.el` provides a number of highly interactive workflows for
managing your package's local repositories, using the
configured [version-control backends][vc-backends]. They are as
follows:

* `M-x straight-normalize-package`: normalize a package
* `M-x straight-normalize-all`: normalize all packages
* `M-x straight-fetch-package`: fetch from a package's configured
  remote; with prefix argument, also fetch from upstream if present
* `M-x straight-fetch-all`: fetch from all packages' configured
  remotes; with prefix argument, also fetch from upstreams if present
* `M-x straight-merge-package`: merge the latest version fetched from
  a package's configured remote into the local copy; with prefix
  argument, also merge from upstream
* `M-x straight-merge-all`: merge the latest versions fetched from
  each package's configured remote into its local copy; with prefix
  argument, also merge from upstreams
* `M-x straight-pull-package`: combination of `M-x
  straight-fetch-package` and `M-x straight-merge-package`
* `M-x straight-pull-all`: combination of `M-x straight-fetch-all` and
  `M-x straight-merge-all`
* `M-x straight-push-package`: push a package to its remote, if
  necessary
* `M-x straight-push-all`: push all packages to their remotes, if
  necessary

See the sections on [version-control backends][vc-backends] and the
[Git backend][git-backend] in particular for more information about
the meanings of these operations.

### Lockfile management

`straight.el` determines your package management configuration from
two, and only two, sources: the contents of your init-file, and your
version lockfiles (which are optional). Your init-file specifies the
configuration of `straight.el` (for example, the values of
`straight-recipe-overrides` and `straight-default-vc`), the packages
you want to use, and their recipes. Your version lockfiles specify the
exact revisions of each package, recipe repository, and even
`straight.el` itself. Together, they lock down your Emacs
configuration to a state of no uncertainty: perfect reproducibility.

To write the current revisions of all your packages into version
lockfiles, run `M-x straight-freeze-versions`. This will first check
that `straight.el` has an up-to-date account of what packages are
installed by your init-file, then ensure that all your local changes
are pushed (remember, we are aiming for perfect reproducibility!). If
you wish to bypass these checks, provide a prefix argument.

Version lockfiles are written into `~/.emacs.d/straight/versions`. By
default, there will be one, called `default.el`. It is recommended
that you keep your version lockfiles under version control with the
rest of your Emacs configuration. If you symlink your init-file into
`~/.emacs.d` from somewhere else, you should also make sure to symlink
your version lockfiles into `~/.emacs.d/straight/versions`. On a new
machine, do this *before* launching Emacs: that way, `straight.el` can
make sure to check out the specified revisions of each package when
cloning them for the first time.

To restore your packages to the revisions specified in your version
lockfiles, run `M-x straight-thaw-versions`. This will interactively
check for local changes before checking out the relevant revisions, so
don't worry about things getting overwritten.

#### The profile system

`straight.el` has support for writing multiple version lockfiles,
instead of just one. Why? Consider a large Emacs configuration such as
[Radian], [Spacemacs], or [Prelude], which is used by many different
people. There are two parts to the configuration that is actually
loaded: the "default" part, and the local customizations that each
user has added. Generally, these configurations have a mechanism for
making local customizations without forking the entire project.

So Radian will have some set of packages that it requires, and my
local customizations of Radian have some other set of packages that
they require. In order for me to maintain Radian, I need to be able to
separate Radian's packages (which go into a versions lockfile in the
Radian repository) from my own local packages (which go into a
versions lockfile in my own private local dotfiles repository).
`straight.el` provides this ability through the *profile system*.

The idea is that whenever a package is registered, either directly or
as a dependency, it is associated with a given profile. Any given
package can be associated with multiple profiles.

When you call `straight-use-package`, which profile the registered
packages are associated with is determined by the value of
`straight-current-profile`, which defaults to nil. In Radian, for
example, `straight-current-profile` is bound to `radian` while the
Radian libraries are being loaded, and it is bound to `radian-local`
while the user's local customizations are being loaded. This results
in Radian packages being associated with the `radian` profile, and the
user's local packages being associated with the `radian-local`
profile.

When you call `M-x straight-freeze-versions`, one or more version
lockfiles are written, according to the value of `straight-profiles`.
This variable is an association list whose keys are symbols naming
profiles and whose values are filenames for the corresponding version
lockfiles to be written into `~/.emacs.d/straight/versions`. You
should make sure that each potential value of
`straight-current-profile` has a corresponding entry in
`straight-profiles`, since otherwise some packages might not be
written into your lockfiles.

When customizing [`straight-recipe-overrides`][overriding-recipes],
note that if multiple profiles are set to override the same recipe,
then the last one listed in `straight-profiles` will take precedence.
Similarly, when using `M-x straight-thaw-versions`, if different
lockfiles specify revisions for the same local repository, the last
one in `straight-profiles` will take precedence.

### The transaction system

Package managers like `package.el` store mutable state outside your
init-file, including the set of packages that are installed.
`straight.el` does not do this, so it has a rather different way of
determining what packages are installed. To `straight.el`, a package
is part of your Emacs configuration if it is passed to
`straight-use-package` when your init-file is loaded.

Note that this means packages installed interactively (using `M-x
straight-use-package`) are not considered part of your Emacs
configuration, since the invocation of `straight-use-package` does not
happen in your init-file.

This raises an interesting question: if you *add* a package to your
init-file, how can you convince `straight.el` that it really is part
of your init-file, and not just part of a temporary
`straight-use-package` form that you evaluated ad-hoc? The answer is
simple: *reload your entire init-file*. That way, `straight.el` will
see whether or not that package is registered during your init-file.

`straight.el` can tell when you have started to load your init-file by
when its bootstrap code is invoked. When Emacs is first started, it
can tell when the init-file is done loaded using `after-init-hook`.
But unfortunately there is no way to tell when a *re-init* has
finished. This is where the transaction system comes in.

You can use the `straight-transaction` macro to wrap a block of code
in a single transaction. This allows `straight.el` to perform various
optimizations, and also to analyze the results of that block of code
on your package management state as a single operation. In particular,
if you call `straight-mark-transaction-as-init` within the transaction
body, then `straight.el` considers that block of code as having the
effect of reloading your init-file. Importantly, the transaction block
tells `straight.el` when your init-file has *finished* loading. This
allows it to correctly identify whether your package management state
perfectly reflects your init-file, or whether you need to reload your
init-file. (This information is used by `M-x
straight-freeze-versions`.)

Here is an example of a properly implemented interactive function to
reload the init-file:

    (defun radian-reload-init ()
      "Reload init.el."
      (interactive)
      (straight-transaction
        (straight-mark-transaction-as-init)
        (message "Reloading init.el...")
        (load user-init-file nil 'nomessage)
        (message "Reloading init.el... done.")))

The transaction system is also used for performing various
optimizations. The details of these optimizations are relegated to
the [developer manual][transactions-implementation], but the
user-facing impact is as follows: any time you are evaluating more
than one `straight-use-package` form, the operation will be faster if
you wrap it in a `straight-transaction` block. If the operation
happens to correspond to a reloading of the init-file, then you should
call `straight-mark-transaction-as-init`: this will not increase
performance further, but it will allow the `straight-freeze-versions`
function to know that the resulting package management state is a
clean reflection of the state of your init-file.

Here is an example of an `eval-buffer` function that correctly takes
advantage of the transaction system for performance, and also marks
the transaction as an init-file reloading when appropriate:

    (defun radian-eval-buffer ()
      "Evaluate the current buffer as Elisp code."
      (interactive)
      (message "Evaluating %s..." (buffer-name))
      (straight-transaction
        (if (null buffer-file-name)
            (eval-buffer)
          (when (string= buffer-file-name user-init-file)
            (straight-mark-transaction-as-init))
          (load-file buffer-file-name)))
      (message "Evaluating %s... done." (buffer-name)))

There is one final user-facing note about the transaction system,
which is important when you want to load your init-file after Emacs
init has already completed, but before `straight.el` has been loaded
(so you cannot just wrap the call in `straight-transaction`). To cover
this edge case (which arises, for example, when you wish to profile
your init-file using something like `esup`), you should use the
following pattern:

    (unwind-protect
        (let ((straight-treat-as-init t))
          "load your init-file here")
      (straight-finalize-transaction))

### Using `straight.el` to reproduce bugs

One of the major reasons I wanted to write `straight.el` was that
existing package managers were not good for reproducing bugs. For
instance, some of them would load all installed packages when the
package manager was initialized! Obviously that is not acceptable for
a "minimal test case".

On the contrary, bootstrapping `straight.el` does not load anything
except for `straight.el` itself (the default recipe repositories are
registered, but not cloned until needed). You should normally be
loading `straight.el` by means of the [bootstrap snippet][bootstrap],
but when you are in `emacs -Q`, here is how you can initialize
`straight.el`:

    M-x load-file RET ~/.emacs.d/straight/repos/straight.el/bootstrap.el RET

You can also do this from the command line, perhaps by creating an
alias for it:

    $ emacs -Q -l ~/.emacs.d/straight/repos/straight.el/bootstrap.el

Let's say you are making a bug report for Projectile. To load just
Projectile and all of its dependencies, run:

    M-x straight-use-package RET projectile RET

Note that this will use the currently checked-out revisions of
Projectile and all of its dependencies, so you should take note of
those in order to make your bug report.

### Integration with `use-package`

By default, `straight.el` installs a new keyword `:straight` for
`use-package` which may be used to install packages via `straight.el`.
The algorithm is extremely simple. This:

    (use-package el-patch
      :straight t)

becomes:

    (straight-use-package 'el-patch)

And this:

    (use-package el-patch
      :straight (:host github :repo "raxod502/el-patch"
                 :branch "develop"))

becomes:

    (straight-use-package
     '(el-patch :host github :repo "raxod502/el-patch"
                :branch "develop"))

If the feature you are requiring with `use-package` is different from
the package name, you can provide a full recipe:

    (use-package tex-site
      :straight (auctex :host github
                        :repo "emacsmirror/auctex"
                        :files (:defaults (:exclude "*.el.in"))))

And you may also provide just the package name:

    (use-package tex-site
      :straight auctex)

If you don't provide `:straight`, then by default nothing happens. You
may customize `straight-use-package-by-default` to make it so that
`:straight t` is assumed unless you explicitly override it with
`:straight nil`.

Previously, `straight.el` used a different syntax for its
`use-package` integration. For backwards compatibility, you can use
this syntax instead by customizing `straight-use-package-version`.

You can disable `use-package` integration entirely by customizing
`straight-enable-use-package-integration`.

### "Integration" with `package.el`

By default, `package.el` will automatically insert a call to
`package-initialize` into your init-file as soon as Emacs starts,
which is ridiculous. It will also do this when you perform any package
management operation. A separate system inserts some `custom` forms
into your init-file when you install a package. `straight.el` disables
all of these "features" by setting `package-enable-at-startup` to nil
and enabling some advices. You can override this behavior by
customizing `straight-enable-package-integration`, however.

### Miscellaneous

By default, straight.el explains what it is doing in the echo area,
like this:

    Looking for cider recipe → Cloning melpa...

If your terminal does not support Unicode characters nicely, you can
customize `straight-arrow` to display something else for the arrow.
