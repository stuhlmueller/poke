#!r6rs

(import (rnrs)
        (church compiler)
        (scheme-tools hash)
        (scheme-tools py-pickle)
        (scheme-tools srfi-compat :1)
        (scheme-tools)
        (settings))

(define CHURCH-HEADER
  (read-source CHURCH-HEADER-FILE))

(define (local expr)
   `((lambda () ,expr)))

(define (read-source pathname)
 (call-with-input-file pathname
  (lambda (port)
   (let loop ((forms '()))
    (let ((form (read port)))
     (if (eof-object? form)
	 (reverse forms)
	 (loop (cons form forms))))))))

(define (define? expr)
  (tagged-list? expr 'define))

(define define->var second)

(define (defined-variables code)
  (if (not (list? code))
      '()
      (filter-map (lambda (expr)
                    (if (and (define? expr)
                             (not (list? (define->var expr))))
                        `(list ',(define->var expr) ,(define->var expr))
                        #f))
                  code)))

(define (transform code)
  (if (or (null? code)
          (not (list? code)))
      code
      `((repeat ,SAMPLES-PER-RUN
                (lambda ()
                  (begin
                    ,@(append (drop-right code 1)
                              (list `(define poke-result ,(last code)))
                              (list `(list ,@(defined-variables code)
                                           (list 'poke-result poke-result))))))))))

(define (expr->body expr)
   (filter (lambda (e) (not (tagged-list? e 'import)))
           expr))

(define (expr->environment expr)
  (let ([imports (find (lambda (e) (tagged-list? e 'import)) expr)])
    (apply environment (rest imports))))

(define (remove-procedures obj)
  (finitize obj))

(define (make-thunk compiled-expr)
  (lambda () (eval (local (append '(begin)
                             (expr->body CHURCH-HEADER)
                             compiled-expr
                             CHURCH-TRAILER))
              (expr->environment CHURCH-HEADER))))

(define (main)
  (display "church-loop started.\n")
  (let* ([compiled-expr (compile (transform (read-source CHURCH-INPUT-FILE)) '())]
         [thunk (make-thunk compiled-expr)])
    (display "church code compiled.\n")
    (let ([py-port (open-py-port "./receiver.py")])
      (display "py-port opened.\n")
      (let loop ([i 0])
        (let ([results (thunk)])
          (when (= i 0)
                (display "got first samples.\n"))
          (for-each (lambda (result)
                      (py-pickle py-port (remove-procedures result)))
                    results)
          (loop (+ i 1)))))))

(main)