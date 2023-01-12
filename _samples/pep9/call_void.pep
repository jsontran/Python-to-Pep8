         BR      program
_UNIV:   .EQUATE 42
value:   .EQUATE 2
result:  .EQUATE 0
my_func: SUBSP 4,i
         DECI value, s 
         LDWA _UNIV, i
         ADDA value, s
         STWA result, s
         DECO result, s
         ADDSP 4, i
         RET
program: CALL my_func
         .END      
