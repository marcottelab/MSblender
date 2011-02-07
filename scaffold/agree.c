#include "agree.h"

int nrow(FILE *fp) {
  char buf[10000];
  int n = 0;
  while(fgets(buf, sizeof(buf), fp) != NULL) n++;
  return n;
}

int newlinechar(char *buf, int k) {
  int i;
  int found = 0;
  for(i=0;i<k;i++) {
    if(buf[i] == '\n') {
      found = 1;
      break;
    }
  }
  return found;
}

int ncol(FILE *fp) {
  char buf[10000];
  int i,cont = 0;
  fgets(buf, sizeof(buf), fp);
  for(i=0;i<10000;i++) {
    if(buf[i] == '\t') cont++;
    else if(buf[i] == '\0') break;
  }
  return cont;
}

int main(int argc, char **argv) {

  /* Data */
  int p, n;
  DATA data;   /* all data */
  PAR par;
  char newName[256];        

  const gsl_rng_type *T;
  gsl_rng *r;
  gsl_rng_env_setup();
  T = gsl_rng_default;
  r = gsl_rng_alloc(T);

  if (argc != 2) {
    fprintf(stderr, "usage: agreementScore [data]\n");
    return 1;
  }
  FILE *fp = fopen(argv[1], "r");
  if(fp == NULL) { 
    fprintf(stderr, "Data file %s does not exist.\n", argv[1]);
    return 1; 
  }

  p = nrow(fp) - 1;
  rewind(fp);
  n = ncol(fp) - 1;  
  rewind(fp);

  /* Read complete data */
  read_data(fp, &data, &p, &n);
  init_par(&par, &data, r);

  /* Estimation */
  agreeScore(&par, &data, r);

  /* Output */
  strcpy(newName, argv[1]);
  strcat(newName, "_agreement");
  FILE *fpout = fopen(newName, "w");
  writeResult(fpout, &par, &data); 

  free_data(&data);

  fclose(fp);
  fclose(fpout);

  return 0;
}


