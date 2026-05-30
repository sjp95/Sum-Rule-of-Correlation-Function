#!/bin/bash
mkdir -p build

cmake -S . -B build
cmake --build build -j$(nproc)
#!/bin/bash

export OMP_NUM_THREADS=8

for N in 30 #60 90 120
do
  for hz in 0 #400.0
  do
    for eta in 2 #3 4 5
    do
      for A in 1
      do
        ./build/h $N 0 0 100 100 100 100 $eta $A $hz
      done
    done
  done
done
#=========================================================================================#
#=========================================================================================#
# for t0 in 100 
#  do
#   for t1 in 10 20 30 40 50
#     do
#     for A in {0..3}
#      do
#       for kpp in {0..11}
#        do
#           #====================================================================
#           echo "#PBS  -N  RIXS_t-J"$kpp                        > $sub
#           echo "#PBS -l nodes=1:ppn=1"                        >> $sub
#           echo "#PBS -j oe "                                  >> $sub
#           echo "#PBS -o out.log"                              >> $sub
#           echo "#PBS -e err.log"                              >> $sub
#           echo "cd"    \$PBS_O_WORKDIR                        >> $sub
#           echo "date"                                         >> $sub
#           echo "./h $kpp"                                     >> $sub
#           echo "date"                                         >> $sub
#           #====================================================================
#           chmod 777 job.sge
#           qsub  job.sge
#        done
#      done
#     done
#   done
#   ./h $A $kpp $t0 $t1
#=========================================================================================#
#=========================================================================================#
