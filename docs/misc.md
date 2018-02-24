## Trivia

This section has random, (possibly) interesting tidbits about
`straight.el` that don't fit in the other sections.

### Comments and docstrings

How did I get that statistic about the percentage of `straight.el`
that is comments and docstrings? Simple: by abusing the syntax
highlighting.

    (let ((lines (make-hash-table :test #'equal)))
      (goto-char (point-min))
      (while (< (point) (point-max))
        (when (memq (face-at-point)
                    '(font-lock-comment-face
                      font-lock-doc-face))
          (puthash (line-number-at-pos) t lines))
        (forward-char))
      (* (/ (float (length (hash-table-keys lines)))
            (line-number-at-pos))
         100))

Note that you will have to scroll through the entire buffer first,
since `font-lock-mode` computes syntax highlighting lazily.
