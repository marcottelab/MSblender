#include "agree.h"

void printVector(const gsl_vector *V, int m) {
  int i;
  for(i=0;i<m;i++) {
    fprintf(stdout, "%.3f\t", gsl_vector_get(V,i));
  }
  fprintf(stdout, "\n");
}


void printMatrix(const gsl_matrix *M, int m) {
  int i,j;
  for(i=0;i<m;i++) {
    for(j=0;j<m;j++) fprintf(stdout, "%.3f\t", gsl_matrix_get(M,i,j));
    fprintf(stdout, "\n");
  }
}


void init_par(PAR *par, DATA *data, const gsl_rng *r) {
  int i;
  int N = data->N;
  par->N = data->N;
  par->P = data->P;
  par->P0 = data->P0;

  assert(par->AbPlus = (double *) calloc(2*N-1, sizeof(double)));
  assert(par->AbMinus = (double *) calloc(2*N-1, sizeof(double)));
  assert(par->score = (double *) calloc(par->P, sizeof(double)));

  for(i=0;i<(2*N-1);i++) {
    par->AbPlus[i] = 0.5 + ((double) (i-N+1)) / ((double) N) * 0.4;
    par->AbMinus[i] = 0.5 - ((double) (i-N+1)) / ((double) N) * 0.4;
  }
}


void agreeScore(PAR *par, DATA *data, const gsl_rng *r) {
  int ct;
  computeAscore(par, data);
  ct = computeAb(par, data);        
  adjustProb(par, data);
  finalScore(par, data);
}

void computeAscore(PAR *par, DATA *data) {
  int i,j,k;
  double x, tmp;
  for(i=0;i<data->P;i++) {
    for(j=0;j<data->N;j++) {
      tmp = 0.0;
      for(k=0;k<data->N;k++) {
        if(k != j) {
          x = gsl_matrix_get(data->X, i, k); 
          if(x == _missval_ || x < 0.05) tmp += 0.0;
          else if(x >= 0.05 && x < 0.5) tmp += 0.5;
          else tmp += 1.0;
        }
      }
      if(x != _missval_) gsl_matrix_set(data->A, i, j, tmp);
    }
  }
}

int computeAb(PAR *par, DATA *data) {
  int i,j,id;
  double sum[2*data->N-1];
  double x, totalSum;
  double old_ratio, ratio;

  /* AbPlus */
  for(i=0;i<(2*data->N-1);i++) sum[i] = 0.0;
  for(i=0;i<data->P;i++) {
    for(j=0;j<data->N;j++) {
      id = ((int) (gsl_matrix_get(data->A,i,j) * 2.0));
      x = gsl_matrix_get(data->X,i,j);
      if(x != _missval_) sum[id] += x;
    }
  }  
  totalSum = vec_sum(sum, 2*data->N-1);
  for(i=0;i<(2*data->N-1);i++) par->AbPlus[i] = sum[i] / totalSum;

  /* AbMinus */
  for(i=0;i<(2*data->N-1);i++) sum[i] = 0.0;
  for(i=0;i<data->P;i++) {
    for(j=0;j<data->N;j++) {
      id = ((int) (gsl_matrix_get(data->A,i,j) * 2.0));
      x = gsl_matrix_get(data->X,i,j);
      if(x != _missval_) sum[id] += (1.0-x);
    }
  }  
  totalSum = vec_sum(sum, 2*data->N-1);
  for(i=0;i<(2*data->N-1);i++) par->AbMinus[i] = sum[i] / totalSum;

  /* monotone increasing */
  old_ratio = par->AbPlus[0] / par->AbMinus[0];
  for(i=1;i<(2*data->N-1);i++) {
    ratio = par->AbPlus[i] / par->AbMinus[i];
    if(ratio < old_ratio) {
      par->AbPlus[i] = par->AbPlus[i-1];
      par->AbMinus[i] = par->AbMinus[i-1];
    }
  }

  fprintf(stderr, "AbPlus:\t");
  for(i=0;i<(2*data->N-1);i++) {
    fprintf(stderr, "%.3f\t", par->AbPlus[i]);
  }
  fprintf(stderr, "\n");
  fprintf(stderr, "AbMinus:\t");
  for(i=0;i<(2*data->N-1);i++) {
    fprintf(stderr, "%.3f\t", par->AbMinus[i]);
  }
  fprintf(stderr, "\n");

  return 1; //for now one iteration 
}


void adjustProb(PAR *par, DATA *data) {
  int i,j,id;
  double x, tmp, tmpaplus, tmpaminus, tmpratio;
  for(i=0;i<data->P;i++) {
    for(j=0;j<data->N;j++) {
      x = gsl_matrix_get(data->X,i,j);
      if(x == _missval_ || x == 0.0) gsl_matrix_set(data->adjX,i,j,0.0);
      else {
        id = ((int) (gsl_matrix_get(data->A,i,j) * 2.0));
        tmpaplus = par->AbPlus[id];
        tmpaminus = par->AbMinus[id];
        tmpaplus = GSL_MAX(GSL_MIN(tmpaplus, 0.95), 0.05);
        tmpaminus = GSL_MAX(GSL_MIN(tmpaminus, 0.95), 0.05);
        tmpratio = tmpaminus / tmpaplus;
        tmp = (1.0 - x) / x * tmpratio;
        tmp = 1.0 / (1.0 + tmp);
        gsl_matrix_set(data->adjX,i,j,tmp);
      }
    }
  }
}

void finalScore(PAR *par, DATA *data) {
  int i, j;
  double tmp;
  for(i=0;i<data->P;i++) {
    par->score[i] = gsl_matrix_get(data->adjX,i,0);
    for(j=1;j<data->N;j++) {
      tmp = gsl_matrix_get(data->adjX,i,j);
      if(tmp > par->score[i]) par->score[i] = tmp;
    }
  }
}









