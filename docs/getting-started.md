## Getting started

> **Note: `straight.el` supports a minimum version of Emacs 24.4, and
> works on macOS, Windows, and most flavors of Linux.**

First, place the following bootstrap code in your init-file:

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

Even if you want to use a particular version or branch of
`straight.el`, or even your own fork, this code does not need to be
modified. To learn more, see the documentation
on [configuring the installation of straight.el][straight.el-recipe].

### Install packages

Out of the box, you can install any package from [MELPA] or
[EmacsMirror], which is to say any package in existence. To install a
package temporarily (until you restart Emacs), run `M-x
straight-use-package` and select the package you want. To install a
package permanently, place a call to `straight-use-package` in your
init-file, like:

    (straight-use-package 'el-patch)

Note that installing a package will activate all of its autoloads, but
it will not actually `require` the features provided by the package.
This means that you might need to use `require` or `autoload` for some
antiquated packages that do not properly declare their autoloads.

To learn more, see the documentation
on [the package lifecycle][package-lifecycle].

### But what about my fork of (obscure .el package)?

Instead of passing just a package name to `straight-use-package`, you
can pass a list ("recipe"). You can see the default recipe for any
given package by running `M-x straight-get-recipe`. For example, the
recipe for `el-patch` is:

    (el-patch :type git :host github :repo "raxod502/el-patch")

So, if you have forked `el-patch` and you want to use your fork
instead of the upstream, do:

    (straight-use-package
     '(el-patch :type git :host github :repo "your-name/el-patch"))

In fact, `straight.el` has explicit support for using a forked
package, since this is so common:

    (straight-use-package
     '(el-patch :type git :host github :repo "your-name/el-patch"
                :upstream (:host github
                           :repo "raxod502/el-patch")))

You may also omit the `:type git` if you leave `straight-default-vc`
at its default value of `git`.

To learn more, see the documentation
on [the recipe format][recipe-format].

### Integration with `use-package`

[`use-package`][use-package] is a macro that provides convenient
syntactic sugar for many common tasks related to installing and
configuring Emacs packages. Of course, it does not actually install
the packages, but instead defers to a package manager, like
`straight.el` (which comes with `use-package` integration by default).

To use `use-package`, first install it with `straight.el`:

    (straight-use-package 'use-package)

Now `use-package` will use `straight.el` to automatically install
missing packages if you provide `:straight t`:

    (use-package el-patch
      :straight t)

You can still provide a custom recipe for the package:

    (use-package el-patch
      :straight (el-patch :type git :host github :repo "your-name/el-patch"
                          :upstream (:host github
                                     :repo "raxod502/el-patch")))

Specifying `:straight t` is unnecessary if you set
`straight-use-package-by-default` to a non-nil value.

To learn more, see the documentation
on
[`straight.el`'s `use-package` integration][use-package-integration].

### Edit packages locally

One of the biggest strengths of `straight.el` is that editing packages
locally is trivial. You literally just edit the files (`find-function`
and friends all work as you would expect). Packages will be
automatically rebuilt if necessary when Emacs next starts up.

You can even commit your changes and push or pull to various remotes
using Git. You have complete control over your packages' Git
repositories.

To learn more, see the documentation
on [the package lifecycle][package-lifecycle].

### Automatic repository management

While being able to make arbitrary changes to your packages is very
powerful, it can also get tiring to keep track of the all those
changes. For this reason, `straight.el` provides a suite of powerful
interactive workflows to perform bulk operations on your packages.

* To restore each package to its canonical state (a clean working
  directory with the main branch checked out, and the remotes set
  correctly), run `M-x straight-normalize-package` or `M-x
  straight-normalize-all`.

* To fetch from each package's configured remote, run `M-x
  straight-fetch-package` or `M-x straight-fetch-all`; to also fetch
  from the upstream (if any), supply a prefix argument.

* To merge changes from each package's configured remote, run `M-x
  straight-merge-package` or `M-x straight-merge-all`; to also merge
  from the upstream (if any), supply a prefix argument.

* To push all local changes to each package's configured remote, run
  `M-x straight-push-package` or `M-x straight-push-all`.

All of these commands are highly interactive and ask you before making
any changes. At any point, you can stop and perform manual operations
with Magit or other tools in a recursive edit.

To learn more, see the documentation
on [bulk repository management][repository-management].

### Configuration reproducibility

To save the currently checked out revisions of all of your packages,
run `M-x straight-freeze-versions`. The resulting file
(`~/.emacs.d/straight/versions/default.el`), together with your
init-file, perfectly define your package configuration. Keep your
version lockfile checked into version control; when you install your
Emacs configuration on another machine, the versions of packages
specified in your lockfile will automatically be checked out after the
packages are installed. You can manually revert all packages to the
revisions specified in the lockfile by running `M-x
straight-thaw-versions`.

To learn more, see the documentation
on [version lockfiles][lockfiles].

### Installing Org

There are [some complications][org] with installing Org at the moment.
However, they are not hard to work around.

[straight.el-recipe]: /user-manual#overriding-the-recipe-for-straightel
