## List of commands of GAMMA software for InSAR training course#
################################################################

### Maurizio Santoro ####

# Last update: 6 June 2018#


################
# DISP commands#
################


disSLC 05721.slc 2500  
dispwr 05721.mli 2500  

# Same command but different syntax
raspwr 05721.mli 2500 
disras 05721.mli.ras

disSLC 05721.slc 2500
dispwr 05721.mli 2500
dispwr 05721_2_10.mli 1250
dispwr 05721_4_20.mli 625 

dismph 05721_25394.int 2500  
dismph_pwr 05721_25394.int - 2500 
dismph_pwr 05721_25394.int 05721.mli 2500

dismph 05721_25394.flt_sm 2500
dismph_pwr 05721_25394.flt_sm 05721.mli 2500

discc 05721_25394.cc - 2500  
discc 05721_25394.cc 05721.mli 2500

disrmg 05721_25394.flt_sm.unw 05721.mli 2500 
disrmg 05721_25394.flt_sm.unw 05721.mli 2500 - - - 2

vispwr.py 05721.mli 2500 
visdt_pwr 05721_25394.flt_sm.unw 05721.mli 2500 -m hls.cm -c 6.28 -b
vismph.py 05721_25394.int 05721.mli 2500 -b -p 05721_25394.int.png


# END OF FILE #

