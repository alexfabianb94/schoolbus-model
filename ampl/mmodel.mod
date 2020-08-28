param NumUsua;
param NumCole;
param n;
param NumFurgo := 2;


set nodos := 0 .. NumCole + NumUsua + 1;

set U := 1..NumUsua;
set E := NumUsua + 1 .. NumCole + NumUsua;
set N := U union E;
param depo := 0;
param nk1 := NumCole + NumUsua + 1 ;

set arcos := {i in N, j in N: i != j} union {i in {depo}, j in U} union {i in E, j in {nk1}} union {i in {depo}, j in {nk1}};
#set arcos := {i in nodos, j in nodos: i != j};

param xcoord{nodos};
param ycoord{nodos};
param color{E} symbolic;

param P {nodos};

set K := 1..NumFurgo;

param D {nodos};
param S {nodos};
# param T {(i,j) in arcos} := sqrt((xcoord[i]- xcoord[j])**2 + (ycoord[i]- ycoord[j])**2) ;
param T {(i,j) in arcos} := round(sqrt((xcoord[i]- xcoord[j])**2 + (ycoord[i]- ycoord[j])**2));
param Q;
param M;
param c{(i,j) in arcos} := T[i,j];
param TE {E};

var x{arcos, K} binary; 
var t {nodos, K} >= 0;  
var f {arcos, K, U} >= 0;
var y {E, K} binary;

#minimize z: sum{i in E} t[i];
#maximize z: t[0]+0.01*sum{i in E} t[i];
#maximize z: sum{i in E union U, k in K} t[i,k];
#maximize z: t[0];
minimize z: sum{i in N, j in N, k in K: (i,j) in arcos} (T[i,j]+S[j])*x[i,j,k];
#minimize z: sum{i in N, j in N: (i,j) in arcos} (T[i,j]+S[j])*x[i,j] -t[0];
#minimize z: sum{i in U} (t[P[i]]-t[i]);

s.t.
llegada {k in K}: sum {j in U union {nk1}} x[depo,j,k] = 1;
salida  {j in U}: sum {i in {depo} union N, k in K: (i,j) in arcos} x[i,j,k] = 1;

balance {j in N, k in K}: sum {i in {depo} union N: (i,j) in arcos} x[i,j,k] = sum {h in {nk1} union N: (j,h) in arcos} x[j,h,k];

Rest3  {j in E, k in K}: sum {i in N: (i,j) in arcos} x[i,j,k] = y[j,k];
Rest4 {k in K}: sum {i in E union {depo}} x[i,nk1,k] = 1;
#Rest5 {i in U}: sum {j in N, k in K: (i,j) in arcos} x[i,j,k] = 1;
#Rest6 {i in E, k in K}: sum {j in N union {nk1}: (i,j) in arcos} x[i,j,k] = y[i,k];

MTZ1{i in N, j in N, k in K: (i,j) in arcos}: t[j,k]>= t[i,k]+(T[i,j]+S[j])*x[i,j,k]+ M*(x[i,j,k]-1); 
MTZ10 {j in U, k in K}: t[j,k] >= t[depo,k] + M*(x[depo,j,k]-1);

MTZ2{i in U, k in K}: t[i,k]<=t[P[i],k];
MTZ9{e in E, k in K}:t[e,k] <= TE[e]*y[e,k];

Multi1 {u in U}: sum{j in N, k in K: (u,j) in arcos} f[u,j,k,u] = 1;
Multi2 {u in U}: sum{i in N, k in K: (i,P[u]) in arcos} f[i,P[u],k,u] = 1;
Multi3 {j in N, k in K, u in U: j != u and j != P[u]}: sum{i in N: (i,j) in arcos} f[i,j,k,u] = sum{h in N: (j,h) in arcos} f[j,h,k,u];
Multi4 {i in N, j in N, k in K, u in U: (i,j) in arcos}: f[i,j,k,u] <= x[i,j,k];
Multi5 {i in N, j in N, k in K: (i,j) in arcos} : sum{u in U} f[i,j,k,u] <= Q;

