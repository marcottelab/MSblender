#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdarg.h>
#include <math.h>
#include <float.h>
#include <ctype.h>
#include <assert.h>

#include <gsl/gsl_math.h>
#include <gsl/gsl_rng.h>
#include <gsl/gsl_cdf.h>
#include <gsl/gsl_sf_gamma.h>
#include <gsl/gsl_randist.h>
#include <gsl/gsl_sort.h>
#include <gsl/gsl_sort_vector.h>

#include <gsl/gsl_matrix.h>
#include <gsl/gsl_vector.h>
#include <gsl/gsl_linalg.h>

#define _PRINT_FREQ_		10
#define _MAX_BUF_		10000
#define _MAX_NAME_		1000
#define _MAXITER_	100
#define _missval_	GSL_NEGINF
#define _tiny_	1e-10
#define _thres_ 0.01
#define _large_ 1e6

typedef struct tagDATA {
  int N;
  int P;
  int P0;
  char **engine;
  char **peptide;
  gsl_matrix *X;
  gsl_matrix *adjX;
  gsl_matrix *A;
  int *is_decoy;
  int *is_complete;
} DATA;

typedef struct tagPAR {
  int N;  /* number of search engines */
  int P;  /* number of peptides - forward */
  int P0; /* number of peptides - decoy */

  /* key parameters */
  double *AbPlus;
  double *AbMinus;
  double *score;
} PAR;


/*************/
/* functions */
/*************/

int nrow(FILE *fp);
int newlinechar(char *buf, int k);
int ncol(FILE *fp);

void read_data(FILE *fp, DATA *data, int *p, int *n);
void free_data(DATA *data);

void init_par(PAR *par, DATA *data, const gsl_rng *r);

void computeAscore(PAR *par, DATA *data);
int computeAb(PAR *par, DATA *data);        
void adjustProb(PAR *par, DATA *data);
void finalScore(PAR *par, DATA *data);

void agreeScore(PAR *par, DATA *cdata, const gsl_rng *r);

void printMatrix(const gsl_matrix *M, int m);
void printVector(const gsl_vector *V, int m);

void writeResult(FILE *fp, PAR *par, DATA *data);


double minimum(const double x1, const double x2);
double maximum(const double x1, const double x2);
void normalize(double *x, int len);
double log_sum(double *x, int len);
double vec_partial_sum(const double *vec, const int *m, int match, int len);
double vec_sum(const double *vec, int len);
double vec_max(const double *vec, int len);
double vec_min(const double *vec, int len);
double vec_mean(const double *vec, int len);
double vec_var(const double *vec, int len);
int vec_min_index(const double *vec, int len);
int vec_max_index(const double *vec, int len);

double vec_cond_max(const double *vec, const double *cond, int len);
double vec_cond_min(const double *vec, const double *cond, int len);
double vec_cond_sum(const double *vec, const double *cond, int len);





