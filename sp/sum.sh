for N in 30 60 90 120
do
for i in 50
do
for eta in 10 20 30 40 50
do
  python3 integrate_qw_v2.py $N 100 100 100 100 $i 0 $eta
  #python3 integrate_qw.py $N 100 100 100 100 $i 0 $eta
done
done
done