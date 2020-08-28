param NumUsua;
param NumCole;
param n;

set nodos := 0 .. NumCole + NumUsua + 1;
set arcos := {i in nodos, j in nodos: i != j};

set U := 1..NumUsua;
set E := NumUsua + 1 .. NumCole + NumUsua;
set N := U union E;

param depo := 0;
param nk1 := NumCole + NumUsua + 1 ;

param xcoord{nodos};
param color{E} symbolic;
param ycoord{nodos};

param P {nodos};
param D {nodos};
param S {nodos};
# param T {(i,j) in arcos} := sqrt((xcoord[i]- xcoord[j])**2 + (ycoord[i]- ycoord[j])**2) ;
param T {(i,j) in arcos} := round(sqrt((xcoord[i]- xcoord[j])**2 + (ycoord[i]- ycoord[j])**2));
param Q;
param M;
param c{(i,j) in arcos} := T[i,j];
param TE {E};

var x{arcos} binary; 
var t {nodos} >= 0;  
var r {nodos} >= 0;

#minimize z: sum{i in E} t[i];
#maximize z: t[0]+0.01*sum{i in E} t[i];
#maximize z: sum{i in E union U} t[i];
#maximize z: t[0];
minimize z: sum{i in N, j in N: (i,j) in arcos} (T[i,j]+S[j])*x[i,j];
#minimize z: sum{i in N, j in N: (i,j) in arcos} (T[i,j]+S[j])*x[i,j] -t[0];
#minimize z: sum{i in U} (t[P[i]]-t[i]);

s.t.
llegada: sum {j in U} x[depo,j] = 1;
salida  {j in U}: sum {i in {depo} union N: (i,j) in arcos} x[i,j] = 1;

Rest3  {j in E}: sum {i in N: (i,j) in arcos} x[i,j] = 1;
Rest4 : sum {i in E} x[i,nk1] = 1;
Rest5 {i in U}: sum {j in N: (i,j) in arcos} x[i,j] = 1;
Rest6 {i in E}: sum {j in N union {nk1}: (i,j) in arcos} x[i,j] = 1;

MTZ1{i in N, j in N: (i,j) in arcos}: t[j]>= t[i]+(T[i,j]+S[j])*x[i,j]+ M*(x[i,j]-1); 
MTZ2{i in U}: t[i]<=t[P[i]];
MTZ3{i in N, j in U: (i,j) in arcos}: r[j]>= r[i]+D[j]*x[i,j]+Q*(x[i,j]-1);  
MTZ4{i in N, j in E: (i,j) in arcos}: r[j]>= r[i]-D[j]*x[i,j]+Q*(x[i,j]-1);    

MTZ5: r[depo] = 0;
#MTZ6: t[depo] = 0;
MTZ7: r[nk1] = 0;
MTZ8 {e in E}: r[e]<=Q;

#MTZ9{i in U}: TE[P[i]] <= t[i];
MTZ9{e in E}:t[e] <= TE[e];

MTZ10 {j in U}: t[j] >= t[depo] + M*(x[depo,j]-1);
MTZ11 {j in U}: r[j] >= r[depo] + D[j] * x[depo,j];
