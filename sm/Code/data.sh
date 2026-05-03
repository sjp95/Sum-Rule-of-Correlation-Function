#!/bin/bash
#sub=job.sge
#module load gcc-7.5.0
#module load compilers/gcc/9.2.0
OMP_NUM_THREADS=4
export OMP_NUM_THREADS

#g++ -std=c++11 D.cpp -lfftw3 -o h -fopenmp
g++ -std=c++11 D.cpp -o h -I/usr/local/opt/libomp/include -L/usr/local/opt/libomp/lib -Xpreprocessor -fopenmp -lomp
# //./h 12 5 5 -100 -10 100 10 c 
for N in 30 60 90 120
do
for hz in 50
do
for eta in 1 2 3 4 5
do
  for A in 0 # 1 2
  do
    ./h $N 0 0 100 100 100 100 $eta $A $hz
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
