         BR      program
_UNIV:   .EQUATE 42
x:       .BLOCK 2
; *** my_func(value) -> void
result:  .EQUATE 0 ; local variable:
value:   .EQUATE 4 ; para
my_func: SUBSP 2, i
         LDWA value, s
         ADDA _UNIV, i
         STWA result, s 
         DECO result, s
         ADDSP 2, i
         RET
program: DECI x, d
         SUBSP 2, i
         LDWA x, d
         STWA 0, s  
         CALL my_func
         ADDSP 2, i
         .END