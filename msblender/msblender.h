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
  int *is_decoy;
  int *is_complete;
  int *is_solo;
} DATA;

typedef struct tagPAR {
  int N;  /* number of search engines */
  int P;  /* number of peptides - forward */
  int P0; /* number of peptides - decoy */
  int ncomp;  
  int ncomp0;

  /* key parameters */
  double *pi_solo;
  double pi; /* proportion of true */
  double *piT;
  double **piF; /* per engine */
  gsl_vector **MuT;
  gsl_matrix **SigmaT;
  double *detT;
  double **MuF;
  double **SigmaF;  /* diagonal matrix for all components  */
  double *detF;

  /* latent variables */
  double *z;  /* true/false indicator for all data; only for non-decoys */
  double *zTsum;  /* length ncomp */
  double *zFsum;  /* length ncomp */
} PAR;


/*************/
/* functions */
/*************/

int nrow(FILE *fp);
int newlinechar(char *buf, int k);
int ncol(FILE *fp);


void read_data(FILE *fp, DATA *data, int *p, int *n);
void free_data(DATA *data);


void alloc_par(PAR *par, DATA *data);
void init_par(PAR *par, DATA *data, const gsl_rng *r);

double determSigma(const gsl_matrix *Cov, gsl_matrix *iCov, int M);
double determ(const gsl_matrix *Cov, int M);
double quad_form(double *X, const gsl_vector *Mu, const gsl_matrix *iCov, int n);
double log_mgaussian_pdf(double *X, const gsl_vector *Mu, const gsl_matrix *Sigma, int n);
double log_gaussian_pdf(double x, double mu, double sigma);

double log_mgaussian_marginal_pdf(double *X, const gsl_vector *Mu, const gsl_matrix *Sigma, int n);
double log_mgaussian_marginal0_pdf(double *X, const gsl_vector *Mu, const gsl_matrix *Sigma, int n);

void find_loc(double *mean, double *stdev, DATA *cdata);
void init_MuSigma(double *mean, double *stdev, PAR *par, DATA *cdata, const gsl_rng *r);
void init_par(PAR *par, DATA *cdata, const gsl_rng *r);
void EM1(PAR *par, DATA *cdata);
void EM2(PAR *par, DATA *cdata);
void EM3(PAR *par, DATA *cdata);
void mvEM(PAR *par, DATA *cdata, int niter, const gsl_rng *r);
void SCORE(PAR *par, DATA *cdata);

double logLik(PAR *par, DATA *data);

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
int vec_cond_max_id(const double *vec, const double *cond, int len);
int vec_cond_min_id(const double *vec, const double *cond, int len);




