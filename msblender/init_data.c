#include "msblender.h"


void free_data(DATA *data) {
  int i,j;
  for(i=0;i<data->P;i++) free(data->peptide[i]);
  free(data->peptide);
  for(j=0;j<data->N;j++) free(data->engine[j]);
  free(data->engine);
  gsl_matrix_free(data->X);
  free(data->is_complete);
  free(data->is_decoy);
}

void fill_tab(int **tab, int n) {
  int i, j, k, ncase;
  int div, res;
  int pos, neg;
  ncase = pow(2,n);
  int use[ncase][n];
  for(i=0;i<ncase;i++) {
    for(j=0;j<ncase;j++) {
      tab[i][j] = 0;
    }
    for(j=0;j<n;j++) {
      use[i][j] = 0;
    }
  }

  for(i=1;i<ncase;i++) {
    res = i;
    for(j=(n-1);j>=0;j--) {
      div = res / pow(2,j);
      use[i][j] = div;
      res -= div * pow(2,j);
    }  
  }

  for(i=1;i<ncase;i++) {
    for(j=1;j<ncase;j++) {
      pos = 0;
      for(k=0;k<n;k++) { 
        if(use[i][k] == 1 && use[j][k] == 1) pos++;
      }
      neg = 0;
      for(k=0;k<n;k++) { 
        if(use[i][k] == 0 && use[j][k] == 1) neg++;
      }
      if(pos > 0 && neg == 0) tab[i][j] = 1; /* for pi_i, use j-th case */ 
    }
  }
}

void read_data(FILE *fp, DATA *data, int *p, int *n) {
  int i,j;
  char buf[_MAX_BUF_];
  int ct_decoy;
  int tmp, ncase;
  data->N = *n;
  ncase = pow(2, *n);
  data->ncase = ncase;

  assert(data->is_decoy = (int *) calloc(*p, sizeof(int)));
  assert(data->is_complete = (int *) calloc(*p, sizeof(int)));
  assert(data->app = (int *) calloc(*p, sizeof(int)));
  assert(data->tab = (int **) calloc(ncase, sizeof(int *)));
  for(i=0;i<ncase;i++) assert(data->tab[i] = (int *) calloc(ncase, sizeof(int)));
  fill_tab(data->tab, *n);

  ct_decoy = 0;
  for(j=0;j<(data->N+2);j++) fscanf(fp, "%s",buf);
  for(i=0;i<*p;i++) {
    data->is_complete[i] = 1;
    fscanf(fp, "%s",buf);
    fscanf(fp, "%s",buf);
    data->is_decoy[i] = atoi(buf);
    if(data->is_decoy[i]) ct_decoy++;
    tmp = 0;
    for(j=0;j<data->N;j++) {
      fscanf(fp, "%s",buf);
      if(strcmp(buf, "NA") == 0) {
        data->is_complete[i] = 0;
      }
      else tmp += pow(2, j);
    }
    data->app[i] = tmp;
  }

  rewind(fp); 
  data->P = *p;
  data->P0 = ct_decoy;

  assert(data->engine = (char **) calloc(data->N, sizeof(char *)));
  for(j=0;j<data->N;j++ ) assert(data->engine[j] = (char *) calloc(_MAX_NAME_, sizeof(char)));

  assert(data->peptide = (char **) calloc(*p, sizeof(char *)));
  for(i=0;i<data->P;i++) assert(data->peptide[i] = (char *) calloc(_MAX_NAME_, sizeof(char))); 

  data->X = gsl_matrix_alloc(data->P, data->N);

  fscanf(fp,"%s",buf);
  fscanf(fp,"%s",buf);
  for(j=0;j<data->N;j++) {
    fscanf(fp,"%s",buf);
    strcpy(data->engine[j], buf);
  }

  for(i=0;i<*p;i++) {
    fscanf(fp,"%s",buf);
    strcpy(data->peptide[i], buf);
    fscanf(fp,"%s",buf);
    for(j=0;j<data->N;j++) {
      fscanf(fp,"%s",buf);
      if(strcmp(buf, "NA") == 0) {
        gsl_matrix_set(data->X,i,j,_missval_);
      }
      else {
        gsl_matrix_set(data->X,i,j,atof(buf));
      }
    }
  }


}






