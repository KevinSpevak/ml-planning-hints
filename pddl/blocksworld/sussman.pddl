(define (problem sussman)
        (:domain blocksworld)
        (:objects A B C)
        (:init (clear B) (clear C) (ontable A)
               (ontable B) (on C A) (handempty))
        (:goal (and (on A B) (on B C))))
