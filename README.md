# Arguably The greatest simulator for RISC-V Superscalar processors that you can find.

ISA: RV-32I

## Instructions to run:
- cd to src directory
- write your assembly code in text_input.txt
- run the Assembler.py to convert it to binary_input.json
- run the Convertor.py to convert it to json_input.json
- run the main.py to run the simulator

### Contributors (same for all dates):
- 1. Prathamesh Vijay Deshpande
- 2. Sarang Mittal

### Note: Prathamesh and Sarang are good friends and sometimes we discuss and switch from academics to fun stuff knowingly/unknowingly during chit-chating so we don't remember everything that we discussed and excat dates and time of when we meet and chatted about project so the given data is bound to some errors wrt date, but its completely honest and not AI generated and we have tried our best cover as much formal information we remember discussing :) 


## Date-8/2/2026

#### Discussion:
- We decide that we won't be following the exact way for SB and J type instructions where the immediate value is of 13 and 21 bits respectively in RISC-V which is very confusing where they are ignoring the end 0, and considering values from 12-1 so instead we made our immediate of 12 and 20 bits respectively and we are considering all the bits from 11 to 0 of the offset value. Fixed one more critical bug in branch switching.
- we got another critical bug in the immediates of the branch and jump instruction caused due to solving the previous critical bug, so needed to fix that, it was  
- config file is yet to be made and it seems difficult, weather it would be completed by today
- integration of the Assembler with the rest of the pipeline 
- creating this MOM file :)
- documentation is yet to be done code is tuff to understand for outside person, 
- And so on much more...

## Date- 27/2/2026

 Discussion: 
- something imp, cool stuff which I forgot while making this MOM :( 

## Date- 22/2/2026 

#### Discussion: 
- Machine is BIG ENDIAN 

## Date- 16/2/2026

#### Discussion: 
- We split our work and decided who will work on what, earlier we decided that Prathaemsh will take care of Assembler, IF, WB and Sarang will take care of ID/RF, EXE, ME, but later sarang proposed that he wants to take IF and WB himself, Prathamesh was ok with it but he always told sarang if he is overwhelmed by the work he can always give some more work to Prathamesh to which he used to reply my main work will come in phase 2...

