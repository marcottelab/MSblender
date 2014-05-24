#include "msblender.h"

void writeResult(FILE *fp, PAR *par, DATA *data) {
  int i,j;
  double tmp;
  fprintf(fp, "Spectrum\tDecoy\t");
  for(j=0;j<data->N;j++) {
    fprintf(fp, "%s\t", data->engine[j]);
  }
  fprintf(fp, "mvScore\n");
  for(i=0;i<data->P;i++) {
    fprintf(fp, "%s\t", data->peptide[i]);
    fprintf(fp, data->is_decoy[i] ? "D\t" : "F\t");
    for(j=0;j<data->N;j++) {
      tmp = gsl_matrix_get(data->X, i, j);
      if(tmp != _missval_) fprintf(fp, "%.2f", tmp);
      fprintf(fp, "\t");
    }    
    fprintf(fp, "%.6f\n", par->z[i]);
  }
}







