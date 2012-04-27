#include "agree.h"

double minimum(const double x1, const double x2) {
  return x1 > x2 ? x2 : x1;
}

double maximum(const double x1, const double x2) {
  return x1 > x2 ? x1 : x2;
}

void normalize(double *x, int len) {
  int i;
  double sum;
  sum = vec_sum(x, len);
  if(sum <= 0.0) fprintf(stderr, "sum not positive\n");
  for(i=0;i<len;i++) x[i] /= sum;
}

double log_sum(double *x, int len) {
  int i;
  double res, sum;
  sum = vec_max(x, len);
  for(i=0;i<len;i++) x[i] -= sum;
  for(i=0;i<len;i++) x[i] = exp(x[i]);
  res = vec_sum(x, len);
  return res;  
}



double vec_partial_sum(const double *vec, const int *m, int match, int len) {
  int i;
  double res;
  res=0.0;
  for(i=0;i<len;i++) {
    if(m[i] == match) res+=vec[i];
  }
  return res;
}


double vec_sum(const double *vec, int len) {
  int i;
  double res;
  res=vec[0];
  for(i=1;i<len;i++) res+=vec[i];
  return res;
}

double vec_max(const double *vec, int len) {
  int i;
  double res;
  res=vec[0];
  for(i=1;i<len;i++) {
    if(res<vec[i]) res=vec[i];
  }
  return res;
}

double vec_cond_sum(const double *vec, const double *cond, int len) {
  int i;
  double res = 0.0;
  for(i=0;i<len;i++) if(cond[i] > 0.0) res+=vec[i];
  return res;
}

double vec_cond_max(const double *vec, const double *cond, int len) {
  int i;
  double res = GSL_NEGINF;
  for(i=0;i<len;i++) {
    if(res<vec[i] && cond[i] > 0.0) res=vec[i];
  }
  return res;
}

double vec_cond_min(const double *vec, const double *cond, int len) {
  int i;
  double res;
  res=vec[0];
  for(i=1;i<len;i++) {
    if(res>vec[i] && cond[i]) res=vec[i];
  }
  return res;
}


double vec_min(const double *vec, int len) {
  int i;
  double res;
  res=vec[0];
  for(i=1;i<len;i++) {
    if(res>vec[i]) res=vec[i];
  }
  return res;
}

double vec_mean(const double *vec, int len) {
  double tmp=0.0;
  int i;
  for(i=0;i<len;i++) tmp+=vec[i];
  tmp=tmp/((double) len);
  return tmp;
}

double vec_var(const double *vec, int len) {
  double mean=0.0;
  double var=0.0;
  int i;
  for(i=0;i<len;i++) mean+=vec[i];
  mean=mean/((double) len);
  for(i=0;i<len;i++) var+=pow((vec[i]-mean),2);
  var/=((double) (len-1));
  var=sqrt(var);
  return var;
}


int vec_min_index(const double *vec, int len) {
  int i,index;
  double res;
  if(len == 1) return 0;
  else {
    res=vec[0];
    index = 0;
    for(i=1;i<len;i++) {
      if(res>vec[i]) {
        index = i;
      }
    }
  }
  return index;
}

int vec_max_index(const double *vec, int len) {
  int i,index;
  double res;
  if(len == 1) return 0;
  else {
    res=vec[0];
    index = 0;
    for(i=1;i<len;i++) {
      if(res<vec[i]) {
        index = i;
      }
    }
  }
  return index;
}

