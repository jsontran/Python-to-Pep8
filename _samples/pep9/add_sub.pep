         BR      program
value:   .BLOCK 2
_UNIV:   .WORD 42
result:  .BLOCK 2
variable:.WORD 3
program: DECI value, d
         LDWA _UNIV, d
         ADDA value, d
         STWA result, d
         LDWA result, d
         SUBA variable, d
         STWA result, d
         LDWA result, d
         SUBA 1, i
         STWA result, d
         DECO result, d
         .END 