## Comparison to other package managers

(Disclaimer: while I try to be as objective and comprehensive as
possible here, I'm obviously biased. Please submit corrections if I
have unfairly disparaged your favorite package manager!)

There are many package managers for Emacs, ranging from simple scripts
to download files from EmacsWiki to full-featured package management
solutions like `straight.el`. Here are the most feature-rich
alternatives to `straight.el`:

* [`package.el`][package.el]: de facto standard, bundled with Emacs.
* [Quelpa]: allows you to use external sources like GitHub with
  `package.el`. Essentially a local [MELPA].
* [Cask]: another `package.el` wrapper. Specify your dependencies in a
  `Cask` file; can be used for project management or an Emacs
  configuration.
* [el-get]: ridiculously OP in terms of how many different sources you
  can pull packages from (`package.el`, every known VCS, distro
  package managers, `go get`(!!)).
* [Borg]: assimilates packages as Git submodules into `.emacs.d`,
  relying on [EmacsMirror].
* "Screw package managers! I'll just handle it all myself!"

### TL;DR

Here is a summary of the main differences in philosophy between the
package managers:

* Use `package.el` if you want package management to be as easy as
  possible, and do not much care for installing packages from specific
  sources, keeping track of their versions, or doing local development
  on them.
* Use Quelpa if you like `package.el` but really wish you could
  specify the sources of your packages.
* Use Cask if you like `package.el` but wish it came with some project
  management tools, as well.
* Use el-get if you want to easily install packages from as many
  different sources as possible.
* Use Borg if you like a more lightweight approach to package
  management that leverages existing solutions, if contributing
  changes to packages upstream is important to you, and if using Git
  submodules isn't a deal-breaker.
* Use the manual approach if you need to contribute changes to a
  package that is versioned in something other than Git.
* Use `straight.el` if you like reproducibility in your Emacs
  configuration, you regularly contribute changes to packages
  upstream, you think deferred installation is a really great idea, or
  you are writing an Emacs configuration to be used by others.

And here is a brief list of the main reasons you might not want to use
`straight.el`:

* `straight.el` is largely unusable if you do not have Git installed,
  although it is still possible to use the package-building features
  if you manage your repositories manually (you also cannot use the
  magic bootstrap snippet, in that case). If you don't want to install
  Git, you'll have to use `package.el` or take the manual approach.
* `straight.el` is not built in to Emacs. If you want something that
  will work right out of the box, you're stuck with `package.el` or
  the manual approach.
* `straight.el` takes a minute or two to update all your packages,
  since it does not rely on a centralized server. If you want quick
  update checking, you'll have to use `package.el`.
* `straight.el` does not provide any user interface for package
  management. For that, you'll have to use `package.el`, el-get, Cask,
  or Borg (which expects you to use [`epkg`][epkg] for browsing
  packages).
* `straight.el` does not currently support using only stable versions
  of packages (i.e. tagged revisions), although this is
  a [planned feature][tag-only-issue]. If this is important to you,
  you probably want to go with `package.el` (with GNU ELPA and MELPA
  Stable), Cask, or Quelpa.
* `straight.el` does not currently support arbitrary build commands
  like `make`, although this is
  a [planned feature][build-command-issue]. This feature is supported
  by el-get and Borg.
* If you don't like having to modify your init-file to do package
  management, then `straight.el` is absolutely not for you. You want
  `package.el`, Quelpa, el-get, or Borg.
* If you really want to contribute changes to packages that are not
  versioned in Git, then `straight.el` will not help you. You'll have
  to manage the package's repository manually. Unfortunately, there is
  no existing package manager that supports both non-Git
  version-control systems and contributing changes upstream. You'll
  have to go with the manual approach.
* `straight.el` does not provide project management tools. It is a
  package manager. If you want project management tools, check out
  Cask.
* `straight.el` is quite new and moving fast. Things might break. The
  other package managers can generally be ranked as follows, from most
  active to least active: el-get, Quelpa, Borg, Cask, `package.el`
  (glacial).

### Comparison to `package.el`

* `package.el` downloads pre-built packages from central servers using
  a special (undocumented?) HTTP protocol, while `straight.el` clones
  Git (or other) repositories and builds packages locally.

#### Advantages of `straight.el`

* `straight.el` allows you to install a package from any branch of any
  Git repository. `package.el` only allows you to install a package
  from a `package.el`-compliant central server.
* `straight.el` allows you to check out any Git revision of any
  package. `package.el` only allows you to install the latest version,
  and there is no way to downgrade.
* `straight.el` supports EmacsMirror, while `package.el` does not.
* `straight.el` uses your init-file as the sole source of truth for
  package operations. `package.el` loads every package you ever
  installed at startup, even if some of those packages are no longer
  referenced by your init-file.
* `straight.el` supports 100% reproducibility for your Emacs packages
  with version lockfiles. `package.el` cannot provide reproducibility
  for the set of packages installed, the central servers they were
  installed from, or the versions in use.
* `straight.el` allows you to make arbitrary changes to your packages
  locally. While it is possible to make local changes to `package.el`
  packages, these changes cannot be version-controlled and they will
  be silently overwritten whenever `package.el` performs an update.
* `straight.el` allows you to perform arbitrary version-control
  operations on your package's Git repositories, including
  contributing changes upstream. `straight.el` has explicit support
  for specifying both an upstream and a fork for a package.
  Contributing changes upstream with `package.el` is impossible.
* `straight.el` is designed with `emacs -Q` bug reports in mind.
  `package.el` is unsuitable for minimal bug reproductions, since it
  automatically loads all of your packages on any package operation,
  even in `emacs -Q`.
* `straight.el` operates quietly when all is going well. `package.el`
  displays all messages, errors, and warnings that come from
  byte-compilation and autoload generation.
* `straight.el` considers modifying the user's init-file extremely
  uncouth. `package.el` aggressively inserts a call to
  `package-initialize` into the init-file if it is not already
  present, whenever any package management operation is performed.
* `straight.el` has a profile system that allows users of someone
  else's Emacs configuration to manage an additional subset of
  packages, or to overriding upstream package configuration, without
  forking the upstream. `package.el` has no such concept.
* `straight.el` is developed openly on GitHub, using a
  modern [issue tracker][issues] and continuous integration
  from [Travis CI][travis-build]. It welcomes contributions of any
  type. `straight.el` is licensed under the permissive MIT license and
  does not require a copyright assignment. `straight.el` is developed
  actively and has explicit support for installing development
  versions of itself, as well as for contributing upstream changes.
  `package.el` is maintained as a part of Emacs core, meaning that the
  contribution process is poorly documented and discouraging. Releases
  of `package.el` coincide with releases of Emacs, which are
  infrequent and inflexible. There is no issue tracker specifically
  for `package.el`, only the Emacs bug tracker and the emacs-devel
  mailing list. Contributing to `package.el` requires a
  poorly-documented, cumbersome copyright assignment process and is
  done by submitting patches to an antiquated mailing list,
  unsupported by modern code review tooling or continuous integration.

#### Advantages of `package.el`

* `package.el` does not require that you have Git installed, since the
  central server deals with where the packages originally came from.
  `straight.el` cannot be used at all without Git.
* `package.el` is built in to Emacs and does not require additional
  configuration to get started with. `straight.el` requires the
  use of a 10-line bootstrap snippet in your init-file.
* `package.el` can perform bulk package updates more quickly since it
  relies on central servers.
* `package.el` has a user interface for package management that also
  displays package metadata. `straight.el` has no user interface for
  package management; any UI is provided by the user's
  `completing-read` framework.
* `package.el` does not require you to touch your init-file to install
  packages, while `straight.el` absolutely refuses to permanently
  install a package without an explicit reference to it in your
  init-file (although this may be considered an advantage, depending
  on your perspective).
* Using MELPA Stable, `package.el` can install only stable versions of
  packages. By default, `package.el` also installs only stable
  versions of packages from GNU ELPA. These modes of operation are
  unsupported by `straight.el` at this time, although this is
  a [planned feature][tag-only-issue].

#### Additional notes

* `package.el` and `straight.el` usually take approximately the same
  time to install packages, despite the fact that `straight.el` is
  cloning entire Git repositories. This is because network latency and
  byte-compilation are the dominant factors.
* Some `package.el` servers build packages from non-Git upstreams.
  `package.el` can install these packages, while `straight.el` cannot.
  However, since `package.el` has no version-control support, this is
  more or less equivalent to installing those packages from the
  [EmacsMirror], which `straight.el` can do by default.

### Comparison to Quelpa

* Quelpa allows for fetching packages from arbitrary sources and
  building them into a format that can be installed by `package.el`.
  `straight.el` has a philosophy which is fundamentally incompatible
  with `package.el`, and non-compatibility with `package.el` is one of
  its design goals.

#### Advantages of `straight.el`

* `straight.el` has out-of-the-box compatibility with MELPA and
  EmacsMirror, while Quelpa only has support for MELPA. [EmacsMirror]
  is not supported by default, although it is easy to specify an
  EmacsMirror repository in a recipe. While Quelpa allows you to
  specify custom recipe folders, it does not have support for cloning
  these folders automatically from version control, nor for generating
  the recipes in any way other than copying them literally from files.
  `straight.el` allows you full flexibility in this regard.
* `straight.el` has integrated support for selecting particular Git
  revisions of packages. This process is more manual in Quelpa, as it
  requires placing the commit hash into the recipe, which disables
  updates.
* `straight.el` uses your init-file as the sole source of truth for
  package operations. Since Quelpa is based on `package.el`, it also
  loads every package you ever installed at startup, even if those
  packages are no longer referenced by your init-file. Furthermore,
  there is an additional caching layer, so that deleting a package
  from the `package.el` interface and removing it from your init-file
  still does not actually delete it.
* `straight.el` supports 100% reproducibility for your Emacs packages
  with version lockfiles. Quelpa can theoretically provide some
  measure of reproducibility, but this requires significant manual
  effort since all packages are not associated with specific revisions
  by default, nor is the revision of MELPA saved anywhere.
* `straight.el` allows you to make arbitrary changes to your packages
  locally. While it is possible to make local changes to Quelpa
  packages, there are two places to do so: the built package, which is
  the default destination of `find-function`, and the original
  repository. Changes to the former are not version-controlled and
  will be silently overwritten by `package.el` operations, while
  changes to the latter will be silently overwritten by Quelpa
  operations.
* `straight.el` has explicit support for configuring both an upstream
  repository and a fork for the same package. Quelpa does not have
  such a concept.
* `straight.el` allows you complete control over how your repositories
  are managed, and the default behavior is to draw all packages
  versioned in a single repository from a single copy of that
  repository. Quelpa is hardcoded to require a separate repository for
  each package, so that installing Magit requires three copies of the
  Magit repository.
* `straight.el` builds packages using symlinks, meaning that
  `find-function` works as expected. Quelpa builds packages by
  copying, a feature inherited from MELPA. This means that
  `find-function` brings you to the built package, instead of the
  actual repository, which is not version-controlled and will be
  overwritten whenever `package.el` performs an update.
* `straight.el` allows you to perform arbitrary version-control
  operations on your package's Git repositories. Quelpa allows this,
  but all local changes will be silently overridden whenever Quelpa
  performs an update.
* `straight.el` is designed with `emacs -Q` bug reports in mind.
  Since Quelpa is based on `package.el`, it is also unsuitable for
  minimal bug reproductions, since it automatically loads all of your
  packages on any package operation, even in `emacs -Q`.
* `straight.el` operates quietly when all is going well. Since Quelpa
  is based on `package.el`, it displays all messages, errors, and
  warnings that come from byte-compilation and autoload generation. It
  also displays additional messages while cloning Git repositories,
  downloading files, and building packages from their repositories
  into `package.el` format.
* `straight.el` does not modify your init-file. Since Quelpa is based
  on `package.el`, it inherits the behavior of aggressively inserting
  a call to `package-initialize` into your init-file on any package
  management operation.
* `straight.el` has a profile system that allows users of someone
  else's Emacs configuration to manage an additional subset of
  packages, or to overriding upstream package configuration, without
  forking the upstream. Quelpa has no such concept.

#### Advantages of Quelpa

* Quelpa supports all the version-control systems supported by MELPA,
  which is to say almost every commonly and uncommonly used VCS.
  `straight.el` only supports Git, although it is designed to support
  other version-control backends.
* Quelpa allows for installing only stable versions of packages, from
  any source. This mode of operation is unsupported by `straight.el`,
  although it is a [planned feature][tag-only-issue].
* Since Quelpa is based on `package.el`, it inherits a user interface
  for package management that also displays package metadata.
  `straight.el` has no such interface.

#### Additional notes

* `straight.el` and Quelpa both allow you to manage your package's
  local repositories manually, if you wish.
* In principle, `straight.el` and Quelpa have identical package
  installation times, since they are performing the same operations.
  In practice, Quelpa is slightly slower since it builds packages by
  copying rather than symlinking, and it clones multiple copies of the
  same Git repository when multiple packages are built from it.
* `straight.el` encourages you to keep a tight handle on your package
  versions by default. Quelpa encourages you to stick to the latest
  versions of your packages, and to upgrade them automatically.

### Comparison to Cask

I have not used Cask extensively, so please feel especially free to
offer corrections for this section.

* Cask installs packages using the `package.el` protocol, based on a
  `Cask` file written in the Cask DSL. `straight.el` eschews
  `package.el` entirely, and clones packages from source based on how
  you invoke `straight-use-package` in your init-file.
* Cask focuses more on being a build manager, like Maven or Leiningen,
  while `straight.el` focuses *exclusively* on being a package
  manager.

#### Advantages of `straight.el`

* `straight.el` has out-of-the-box compatibility with EmacsMirror,
  while Cask only supports `package.el`-compliant repositories.
  However, it is easy to specify an EmacsMirror repository in a
  recipe. Cask does not support custom package sources. `straight.el`
  supports MELPA and EmacsMirror, and allows you to add any other
  sources you would like.
* `straight.el` has integrated support for selecting particular Git
  revisions of packages. This process is more manual in Cask, as it
  requires placing the commit hash into the recipe, which disables
  updates.
* `straight.el` uses your init-file as the sole source of truth for
  package operations. Since Cask is based on `package.el`, it loads
  every package you ever installed at startup, even if some of those
  packages are no longer referenced by your `Cask` file.
* `straight.el` determines your package management configuration
  implicitly by detecting how you call `straight-use-package` in your
  init-file and making the appropriate changes immediately. Cask
  requires manual intervention (for example, issuing a `cask install`
  command when you have updated your `Cask` file). However, both
  `straight.el` and Cask can be considered declarative package
  managers.
* `straight.el` supports 100% reproducibility for your Emacs packages
  with version lockfiles. Cask can theoretically provide some measure
  of reproducibility, but this requires significant manual effort
  since all packages are not associated with specific revisions by
  default, nor is the revision of Cask saved anywhere.
* `straight.el` allows you to make arbitrary changes to your packages
  locally. While it is possible to make local changes to Cask
  packages, these will not be version-controlled and they will be
  silently overwritten or shadowed when Cask performs an update.
* `straight.el` allows you to perform arbitrary version-control
  operations on your package's Git repositories, including
  contributing changes upstream. `straight.el` has explicit support
  for specifying both an upstream and a fork for a package.
  Contributing changes upstream with Cask is impossible.
* `straight.el` is designed with `emacs -Q` bug reports in mind. Cask
  appears to be unsuitable for minimal bug reproductions, since there
  does not appear to be a straightforward way to load a single
  package, without loading all other packages configured in your
  `Cask` file.
* `straight.el` operates quietly when all is going well. Since Cask is
  based on `package.el`, it displays all messages, errors, and
  warnings that come from byte-compilation and autoload generation.
* `straight.el` has a profile system that allows users of someone
  else's Emacs configuration to manage an additional subset of
  packages, or to overriding upstream package configuration, without
  forking the upstream. Cask has no such concept.

#### Advantages of Cask

* Cask provides a useful toolbox of operations for project management,
  which are completely absent from `straight.el`.
* Since Cask is based on `package.el`, it does not require that you
  have Git installed. (It does require Python, however.) `straight.el`
  is mostly unusable without Git.
* Since Cask is based on `package.el`, it can perform bulk package
  updates more quickly than `straight.el`.
* Since Cask is based on `package.el`, it inherits a user interface
  for package management that also displays package metadata.
* Since Cask is based on `package.el`, you can install packages
  without editing a file manually, although this rather defeats the
  entire purpose of using Cask instead of `package.el`. `straight.el`
  absolutely refuses to permanently install a package without an
  explicit reference to it in your init-file (although this may be
  considered an advantage, depending on your perspective).
* Using MELPA Stable, Cask can install only stable versions of
  packages. By default, Cask also installs only stable versions of
  packages from GNU ELPA. These modes of operation are unsupported by
  `straight.el` at this time, although this is
  a [planned feature][tag-only-issue].
* Cask supports more version-control systems than `straight.el` (which
  only supports Git).

### Comparison to el-get

I have not used el-get extensively, so please feel especially free to
offer corrections for this section.

* Both el-get and `straight.el` implement their own package management
  abstractions instead of delegating to `package.el`. However:
    * el-get goes the route of adding as many package sources as
      possible (e.g. `package.el`, many different version-control
      systems, various specific websites, and even system package
      managers) so that packages can be used very easily
    * `straight.el` only supports Git and in doing so is able to
      provide more advanced package management features.

#### Advantages of `straight.el`

* `straight.el` has integrated support for selecting particular Git
  revisions of packages. This process is more manual in el-get, as it
  requires placing the commit hash into the recipe, which disables
  updates.
* `straight.el` uses your init-file as the sole source of truth for
  package operations. el-get has additional metadata stored outside
  the init-file, although specifying all packages in your init-file is
  a supported mode of operation.
* `straight.el` supports 100% reproducibility for your Emacs packages
  with version lockfiles. el-get can theoretically provide some
  measure of reproducibility, but this requires significant manual
  effort since all packages are not associated with specific revisions
  by default, nor is the revision of el-get saved anywhere.
* `straight.el` allows you to make arbitrary changes to your packages
  locally, and conflicts during updates are presented to the user and
  resolved interactively. While it is possible to make local changes
  to el-get packages, the el-get manual warns that such changes may
  break the update mechanism.
* `straight.el` has explicit support for configuring both an upstream
  repository and a fork for the same package. el-get does not have
  such a concept.
* `straight.el` allows you to perform arbitrary version-control
  operartions on your package's Git repositories. el-get allows this,
  but local changes will be overwritten when el-get performs an
  update.
* `straight.el` provides a suite of powerful interactive workflows for
  performing bulk operations on your package's Git repositories.
  el-get only allows you to install, uninstall, and update packages.
* `straight.el` operates quietly when all is going well. el-get
  reports its progress verbosely.
* `straight.el` has a profile system that allows users of someone
  else's Emacs configuration to manage an additional subset of
  packages, or to overriding upstream package configuration, without
  forking the upstream. el-get has no such concept.

#### Advantages of el-get

* el-get supports virtually all known version-control systems, as well
  as system package managers, EmacsWiki, arbitrary HTTP, and even `go
  get`. `straight.el` supports only Git, although it does allow you to
  manage your local repositories manually if you would like.
* el-get has been around since 2010 and is on its fifth major version,
  whereas `straight.el` was created in January 2017 and is only now
  approaching a 1.0 release. Clearly, el-get is more stable, although
  despite its recency `straight.el` is already almost 50% of the size
  of el-get, by the line count. Both package managers are actively
  maintained.
* el-get has a recipe format which is several orders of magnitude more
  powerful than that of `straight.el`, since it supports many more
  package sources that can be configured and since it allows for a
  more complex build process.
* el-get provides a number of features for running per-package
  initialization and setup code, including pulling that code from
  arbitrary sources. `straight.el` does not support this and expects
  you to use a dedicated tool like [`use-package`][use-package] (with
  which integration is built in) for that purpose.
* el-get has a user interface for package management that also
  displays package metadata, similarly to `package.el`. `straight.el`
  has no user interface for package management; any UI is provided by
  the user's `completing-read` framework.

### Comparison to Borg

* Borg and `straight.el` are perhaps the two most similar package
  managers on this list. The difference is that Borg is very minimal
  and expects you to complement it with other tools such as [Magit],
  [epkg], [`use-package`][use-package], and [auto-compile]. On the
  other hand, `straight.el` aspires to be a one-stop package
  management solution, although it does not try to replace dedicated
  version-control packages (Magit) or dedicated package
  *configuration* packages (`use-package`).
* Borg uses Git submodules, while `straight.el` uses independently
  managed Git repositories.

#### Advantages of `straight.el`

* `straight.el` supports MELPA, EmacsMirror, and custom recipe
  sources. Borg only supports EmacsMirror and custom recipe sources.
  However, as the EmacsMirror is a complete superset of MELPA, this
  does not mean you have access to more packages: it just means you
  benefit from the recipe maintenance efforts of the MELPA team and
  the EmacsMirror team, rather than only the latter.
* Borg, even when combined with related tools, do not allow for the
  kind of massive interactive repository management provided by
  `straight.el`.
* `straight.el` supports deferred and conditional installation. This
  is not supported by Borg, although it could in principle be
  implemented via lazy cloning of submodules.
* `straight.el` provides an API designed for other version-control
  backends to be added in future. Borg is inextricably tied to Git.
* The interface for Git submodules has a number of sharp edges.
* `straight.el` provides dependency management. This is a manual
  process in Borg.
* `straight.el` provides mechanisms for updating your packages. This
  is a manual process in Borg.
* `straight.el` is configured solely by how you use in your init-file.
  Configuring Borg requires customizing `~/.emacs.d/.gitmodules`,
  which means (for example) that you cannot generate recipes
  dynamically. (However, the handling of configuration
  is [planned][borg-improvements] to be improved in a future release.)
* `straight.el` has a profile system that allows users of someone
  else's Emacs configuration to manage an additional subset of
  packages, or to overriding upstream package configuration, without
  forking the upstream. Borg has no such concept.

#### Advantages of Borg

* Borg does a heck of a lot less magic, so if you want a solution with
  simple implementation details, `straight.el` may not be for you.
  (But see the developer manual and docstrings, first.)
* Borg supports arbitrary build commands; `straight.el` does not
  (although this is a [planned feature][build-command-issue]).

### Comparison to the manual approach

* The manual approach is to download packages yourself and put them on
  your `load-path`. `straight.el` is more or less what you get when
  you take the manual approach, think very hard about the best way to
  do everything, and then automate all of it.

#### Advantages of `straight.el`

* `straight.el` figures out where to clone your packages from for you.
* `straight.el` byte-compiles your packages for you and generates
  their autoloads automatically.
* `straight.el` frees you from needing to manually recompile and
  regenerate autoloads.
* `straight.el` keeps track of dependencies for you.
* `straight.el` provides tools to manage all your packages in bulk,
  which would otherwise be a long, tedious process.
* `straight.el` allows you to get reproducibility for your
  configuration without needing to keep all of your packages under
  version control.
* `straight.el` (when used with [`use-package`][use-package])
  automates the complex process of deferred installation.
* `straight.el` links packages into a separate build directories.
  Running packages directly from their repositories has a number of
  problems, including:
    * making it impossible to run only one package, if others are
      provided in the same repository.
    * making your working directory dirty when the package author
      forgot to add their build artifacts like `*.elc` and autoload
      files to the `.gitignore`.
    * instantly losing compatibility with MELPA recipes.
* `straight.el` offers you a single entry point to install only a
  single package in isolation, for a minimal bug reproduction. With
  the manual approach this would be more complicated, especially if
  the package has dependencies.
* `straight.el` frees you from needing to think about package
  management, since I already did all the thinking to figure how best
  to design everything.

#### Advantages of the manual approach

* No dependencies.
* You learn a lot, if you don't give up first.
* You might end up writing a package manager (case in point).
* This is the only way to deal with packages that have non-Git
  upstreams which you need to contribute changes to. (However, you can
  always use the manual approach for one package and `straight.el` for
  the rest. Or you can just eschew `straight.el`'s version-control
  support for that package, and use it only for building the package.)
