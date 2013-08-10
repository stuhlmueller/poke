#!r6rs

(library

 (settings)

 (export CHURCH-HEADER-FILE
         CHURCH-TRAILER
         SAMPLES-PER-RUN
         CHURCH-INPUT-FILE)

 (import (rnrs))

 (define CHURCH-HEADER-FILE
   "/Users/andreas/code/bher/scheme-compilers/header-vicare.sc")

 (define CHURCH-TRAILER
   '( (randomize-rng)
      (lambda () (church-main '(top) (make-empty-store))) ))

 (define SAMPLES-PER-RUN 10)

 (define CHURCH-INPUT-FILE "./input.church")

 )