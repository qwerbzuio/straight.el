`straight.el` is a next-generation, purely functional package manager
for the [Emacs] hacker.

* [GitHub][github]
* [Gitter chat][gitter]
* [Travis CI][travis]

Refer to the table of contents on the left to navigate the
documentation.

## Features

* Install Emacs packages from [MELPA], [EmacsMirror], or manually
  specified sources.
* Clone and manage packages as [Git] (or other) repositories, not as
  opaque tarballs.
* Make changes to a package simply by editing its source code, no
  additional steps required. Contribute upstream just by pushing your
  changes.
* Powerful interactive workflows (with popups à la Magit) for
  performing bulk maintenance on the Git repositories for your
  packages.
* Save and load version lockfiles that ensure 100% reproducibility for
  your Emacs configuration. Package state is defined entirely by your
  init-file and (optional) lockfile, with no extra persistent data
  floating around.
* Specify package descriptions using a powerful recipe format that
  supports everything from [MELPA recipes][melpa-recipe-format] and
  more.
* [`use-package`][use-package] integration.
* Modular: you can install your packages manually and straight.el will
  load them for you. Or you can also have straight.el install your
  packages, while you provide the recipes explicitly. Or straight.el
  can also fetch recipes, if you want. Bulk repository management and
  package updates are also optional.
* Extensible APIs to add new recipe sources and version-control
  backends.
* The cleanest source code you've ever
  seen. [45%][comments-and-docstrings] of `straight.el` is comments
  and docstrings.

## Guiding principles

* Init-file and version lockfiles as the sole source of truth. No
  persistent state kept elsewhere.
* 100% reproducible package management, accounting for changes in
  packages, recipe repositories, configuration, and the package
  manager itself.
* No support whatsoever for `package.el`.
* Edit packages by editing their code, no extra steps required. Allow
  for manual version control operations.
* Compatibility with MELPA and EmacsMirror.
* Trivial to quickly try out a package without permanently installing
  it.
* Good for reproducing an issue with `emacs -Q`.

## FAQ

* *I get errors/warnings/the wrong version when installing Org.*

  This is a combination of two problems: firstly, Org isn't designed
  to be used without running `make` first, and `straight.el` doesn't
  yet have support for running custom commands while building a
  package ([#72]); secondly, Emacs ships an obsolete version of Org
  and there's no way to prevent that version from being made
  available. Here is how to work around these problems:

      (require 'subr-x)
      (straight-use-package 'git)

      (defun org-git-version ()
        "The Git version of org-mode.
      Inserted by installing org-mode or when a release is made."
        (require 'git)
        (let ((git-repo (expand-file-name
                         "straight/repos/org/" user-emacs-directory)))
          (string-trim
           (git-run "describe"
                    "--match=release\*"
                    "--abbrev=6"
                    "HEAD"))))

      (defun org-release ()
        "The release version of org-mode.
      Inserted by installing org-mode or when a release is made."
        (require 'git)
        (let ((git-repo (expand-file-name
                         "straight/repos/org/" user-emacs-directory)))
          (string-trim
           (string-remove-prefix
            "release_"
            (git-run "describe"
                     "--match=release\*"
                     "--abbrev=0"
                     "HEAD")))))

      (provide 'org-version)

      (straight-use-package 'org) ;; or org-plus-contrib if desired

* *My init-time is slower since switching to `straight.el`.*

  Unlike other package managers, `straight.el` automatically detects
  changes to packages and rebuilds them when needed. This takes a bit
  of time. If you'd like to speed up Emacs initialization by disabling
  this feature, customize the user option
  `straight-check-for-modifications`. (Further work is pending on
  improving the user experience for non-default settings of this
  variable; see [#180].)

  Performance could also be improved by optimizing the evaluation of
  autoloads beyond the approach taken in `package.el` ([#119]),
  optimizing the saving of `straight.el`'s build cache
  ([#9][#9-comment]), and eliminating unnecessary disk operations
  during recipe lookup ([#227][#227-comment]).

* *How can I use stable versions of packages?*

  Check out the tags you want in your packages' Git repositories. See
  also [#31].

## News

* 2017-12-12: Due to major updates upstream, the interface for
  `straight.el`'s `use-package` integration has changed significantly.
  You should now use `:straight` instead of `:ensure` and `:recipe`,
  and use `straight-use-package-by-default` instead of
  `use-package-always-ensure`. You can recover the old behavior (for
  now) by customizing the variable `straight-use-package-version`.
* 2017-12-08: You can now install `org` and `org-plus-contrib` using
  `straight.el` just like you could from Org ELPA, with no extra
  effort required.
* 2017-11-10: `straight.el` now has out-of-the-box support for
  Microsoft Windows.
* 2017-11-06: You can now save about 500ms per 100 packages at Emacs
  init if you customize `straight-check-for-modifications` to `live`,
  which causes `straight.el` to detect package modifications as they
  are made instead of using `find(1)` at init time.
* 2017-10-30: `straight.el` now has a much more usable "package
  update" operation because `straight-pull-all` has been separated
  into `straight-fetch-all` and `straight-merge-all`.
* 2017-10-27: `straight.el` now supports texinfo manuals.
* 2017-10-22: `straight.el` now supports Emacs 24.5 and Emacs 24.4.

[comments-and-docstrings]: /misc#comments-and-docstrings

[#9-comment]: https://github.com/raxod502/straight.el/issues/9#issuecomment-318550998
[#31]: https://github.com/raxod502/straight.el/issues/31
[#72]: https://github.com/raxod502/straight.el/issues/72
[#119]: https://github.com/raxod502/straight.el/issues/119
[#180]: https://github.com/raxod502/straight.el/issues/180
[#227-comment]: https://github.com/raxod502/straight.el/pull/227#issuecomment-362932049

[git]: https://git-scm.com/
[github]: https://github.com/raxod502/straight.el
[gitter]: https://gitter.im/raxod502/straight.el
[travis]: https://travis-ci.org/raxod502/straight.el
[melpa-recipe-format]: https://github.com/melpa/melpa#recipe-format
[melpa]: http://melpa.org/#/
[emacsmirror]: https://emacsmirror.net/
[emacs]: https://www.gnu.org/software/emacs/
[use-package]: https://github.com/jwiegley/use-package
