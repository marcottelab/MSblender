#include "agree.h"


void free_data(DATA *data) {
  int i,j;
  for(i=0;i<data->P;i++) free(data->peptide[i]);
  free(data->peptide);
  for(j=0;j<data->N;j++) free(data->engine[j]);
  free(data->engine);
  gsl_matrix_free(data->X);
  gsl_matrix_free(data->adjX);
  gsl_matrix_free(data->A);
  free(data->is_complete);
  free(data->is_decoy);
}

void read_data(FILE *fp, DATA *data, int *p, int *n) {
  int i,j;
  char buf[_MAX_BUF_];
  int ct_decoy;

  data->N = *n;

  assert(data->is_decoy = (int *) calloc(*p, sizeof(int)));
  assert(data->is_complete = (int *) calloc(*p, sizeof(int)));

  ct_decoy = 0;
  for(j=0;j<(data->N+2);j++) fscanf(fp, "%s",buf);
  for(i=0;i<*p;i++) {
    data->is_complete[i] = 1;
    fscanf(fp, "%s",buf);
    fscanf(fp, "%s",buf);
    data->is_decoy[i] = atoi(buf);
    if(data->is_decoy[i]) ct_decoy++;
    for(j=0;j<data->N;j++) {
      fscanf(fp, "%s",buf);
      if(strcmp(buf, "NA") == 0) data->is_complete[i] = 0;
    }
  }
  rewind(fp); 
  data->P = *p;
  data->P0 = ct_decoy;



  assert(data->engine = (char **) calloc(data->N, sizeof(char *)));
  for(j=0;j<data->N;j++) assert(data->engine[j] = (char *) calloc(_MAX_NAME_, sizeof(char)));

  assert(data->peptide = (char **) calloc(*p, sizeof(char *)));
  for(i=0;i<data->P;i++) assert(data->peptide[i] = (char *) calloc(_MAX_NAME_, sizeof(char))); 

  data->X = gsl_matrix_alloc(data->P, data->N);
  data->adjX = gsl_matrix_alloc(data->P, data->N);
  data->A = gsl_matrix_alloc(data->P, data->N);

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
    data->is_decoy[i] = atoi(buf);
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




