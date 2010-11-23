
#include "msblender.h"

void alloc_par(PAR *par, DATA *data) {
  int i;
  par->N = data->N;
  par->P = data->P;
  par->P0 = data->P0;
  // par->ncomp = pow(2, par->N);
  par->ncomp = 2;
  par->ncomp0 = 2;  /* each engine */

  par->pi = 0.1;
  assert(par->piT = (double *) calloc(par->ncomp, sizeof(double)));
  assert(par->piF = (double **) calloc(par->N, sizeof(double *)));
  for(i=0;i<par->N;i++) assert(par->piF[i] = (double *) calloc(par->ncomp0, sizeof(double)));
  par->MuT = (gsl_vector **) calloc(par->ncomp, sizeof(gsl_vector *));
  par->SigmaT = (gsl_matrix **) calloc(par->ncomp, sizeof(gsl_matrix *));
  assert(par->MuF = (double **) calloc(par->N, sizeof(double *)));
  assert(par->SigmaF = (double **) calloc(par->N, sizeof(double *)));
  for(i=0;i<par->ncomp;i++) {
    par->MuT[i] = gsl_vector_alloc(par->N);
    par->SigmaT[i] = gsl_matrix_alloc(par->N, par->N);
  }
  for(i=0;i<par->N;i++) {
    assert(par->MuF[i] = (double *) calloc(par->ncomp0, sizeof(double)));
    assert(par->SigmaF[i] = (double *) calloc(par->ncomp0, sizeof(double)));
  }
  assert(par->detT = (double *) calloc(par->ncomp, sizeof(double)));
  assert(par->detF = (double *) calloc(par->ncomp0, sizeof(double)));

  assert(par->z = (double *) calloc(par->P, sizeof(double)));
  assert(par->zTsum = (double *) calloc(par->ncomp, sizeof(double)));
  assert(par->zFsum = (double *) calloc(par->ncomp0, sizeof(double)));
}

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

double determSigma(const gsl_matrix *Cov, gsl_matrix *iCov, int M) {
  int s, err;
  double determ;
  if(M == 1) {
    determ = gsl_matrix_get(Cov, 0, 0);
    gsl_matrix_set(iCov, 0, 0, 1.0/determ);
  }
  else {
    gsl_permutation *p = gsl_permutation_alloc(M);
    gsl_permutation_init(p);
    gsl_matrix *LU = gsl_matrix_alloc(M, M);
    err = gsl_matrix_memcpy(LU, Cov);
    gsl_linalg_LU_decomp(LU, p, &s);  /* LU is now L and U */
    gsl_linalg_LU_invert(LU, p, iCov);
    determ = gsl_linalg_LU_det(LU, s);
    gsl_matrix_free(LU);
    gsl_permutation_free(p);
  }
  return determ;
}

double determ(const gsl_matrix *Cov, int M) {
  int s, err;
  double determ;
  if(M == 1) {
    determ = gsl_matrix_get(Cov, 0, 0);
  }
  else {
    gsl_permutation *p = gsl_permutation_alloc(M);
    gsl_permutation_init(p);
    gsl_matrix *LU = gsl_matrix_alloc(M, M);
    err = gsl_matrix_memcpy(LU, Cov);
    gsl_linalg_LU_decomp(LU, p, &s);  /* LU is now L and U */
    determ = gsl_linalg_LU_det(LU, s);
    gsl_matrix_free(LU);
    gsl_permutation_free(p);
  }
  return determ;
}

double quad_form(double *X, const gsl_vector *Mu, const gsl_matrix *iCov, int n) {
  int i,j;
  double x[n];
  double res[n];
  double qf = 0.0;
  for(i=0;i<n;i++) x[i] = X[i] - gsl_vector_get(Mu,i);
  for(i=0;i<n;i++) {
    res[i] = 0.0;
    for(j=0;j<n;j++) res[i] += x[i] * gsl_matrix_get(iCov,j,i);
  }
  for(i=0;i<n;i++) qf += res[i] * x[i];  
  return qf;
}

double log_mgaussian_pdf(double *X, const gsl_vector *Mu, const gsl_matrix *Sigma, int n) {
  gsl_matrix *iCov = gsl_matrix_alloc(n,n);
  double quadf;
  double determ = determSigma(Sigma, iCov, n);
  double res = 0.0;
  if(determ <= 0.0) {
    // fprintf(stderr, "covariance problem\n");
    res = GSL_NEGINF;
  }
  else {
    quadf = quad_form(X, Mu, iCov, n);
    res = .5 * ((double) n) * log(2.0 * M_PI) - .5 * log(determ) - .5 * quadf;
  }
  gsl_matrix_free(iCov);
  return res;
}

double log_gaussian_pdf(double x, double mu, double sigma) {
  double tmp = log(2.0) + log(M_PI) + log(sigma);
  if(sigma <= 0.0) {
    // fprintf(stderr, "covariance problem\n");
    tmp = GSL_NEGINF;
  }
  else {
    tmp *= -.5;
    tmp -= .5 * pow(x - mu, 2.0) / sigma;
  }
  return tmp;
}

double log_mgaussian_marginal_pdf(double *X, const gsl_vector *Mu, const gsl_matrix *Sigma, int n) {
  int i,j,nn;
  int p[n];
  double x[n];
  double loglik;
  nn = 0;
  for(i=0;i<n;i++) {
    if(X[i] != _missval_) { 
      p[nn] = i;
      nn++;
    }
  } 
  gsl_vector *mu = gsl_vector_alloc(nn);
  gsl_matrix *sigma = gsl_matrix_alloc(nn, nn);
  for(i=0;i<nn;i++) {
    x[i] = X[p[i]];
    gsl_vector_set(mu, i, gsl_vector_get(Mu, p[i]));
    for(j=0;j<nn;j++) gsl_matrix_set(sigma, i, j, gsl_matrix_get(Sigma, p[i], p[j]));
  }
  if(nn == 1) {
    loglik = log_gaussian_pdf(x[0], gsl_vector_get(mu,0), gsl_matrix_get(sigma,0,0));
  }
  else {
    loglik = log_mgaussian_pdf(x, mu, sigma, nn);
  }
  gsl_vector_free(mu);
  gsl_matrix_free(sigma);
  return loglik;
}


double log_mgaussian_marginal0_pdf(double *X, const gsl_vector *Mu, const gsl_matrix *Sigma, int n) {
  int i,j,nn;
  int p[n];
  double x[n];
  double loglik;
  nn = 0;
  for(i=0;i<n;i++) {
    if(X[i] != _missval_) { 
      p[nn] = i;
      nn++;
    }
  } 
  gsl_vector *mu = gsl_vector_alloc(nn);
  gsl_matrix *sigma = gsl_matrix_alloc(nn, nn);
  for(i=0;i<nn;i++) {
    x[i] = X[p[i]];
    gsl_vector_set(mu, i, gsl_vector_get(Mu, p[i]));
    for(j=0;j<nn;j++) gsl_matrix_set(sigma, i, j, gsl_matrix_get(Sigma, p[i], p[j]));
  }
  if(nn == 1) {
    loglik = log_gaussian_pdf(x[0], gsl_vector_get(mu,0), gsl_matrix_get(sigma,0,0));
  }
  else {
    loglik = 0.0;
    for(i=0;i<nn;i++) loglik += log_gaussian_pdf(x[i], gsl_vector_get(mu,i), gsl_matrix_get(sigma,i,i)); 
  }
  gsl_vector_free(mu);
  gsl_matrix_free(sigma);
  return loglik;
}


void find_loc(double *mean, double *stdev, DATA *data) {
  int i,j,ct;
  double m, sd, tmp;
  for(j=0;j<data->N;j++) {
    m = 0.0;
    sd = 0.0;
    for(i=0;i<data->P;i++) {
      tmp = gsl_matrix_get(data->X,i,j);
      if(tmp != _missval_) {
        m += tmp;
        ct++;
      }
    }
    m /= ((double) ct);
    for(i=0;i<data->P;i++) {
      tmp = gsl_matrix_get(data->X,i,j);
      if(tmp != _missval_) {
        sd += pow(tmp - m, 2.0);
      }
    }
    sd /= ((double) ct);
    sd = sqrt(sd);
    mean[j] = m;
    stdev[j] = sd;
  }
}

void find_mode(int i, int *mode, int n) {
  int k,val;
  val = i;
  for(k=(n-1);k>=0;k--) {
    mode[k] = val / pow(2,k);    
    val -= mode[k] * pow(2,k);
  }
  if(val != 0) fprintf(stderr, "mode finding problem\n");
}

void init_MuSigma(double *mean, double *stdev, PAR *par, DATA *data, const gsl_rng *r) {
  int i,j;
  for(i=0;i<par->ncomp;i++) {
    for(j=0;j<data->N;j++) {
      gsl_vector_set(par->MuT[i], j, mean[j] + stdev[j] * gsl_ran_flat(r, 0.0, 4.0));
    }
    gsl_matrix_set_zero(par->SigmaT[i]);
    for(j=0;j<data->N;j++) {
      gsl_matrix_set(par->SigmaT[i], j, j, pow(stdev[j],2.0) * 0.5);
    }
  }
  for(j=0;j<par->N;j++) {
    for(i=0;i<par->ncomp0;i++) {
      par->MuF[j][i] = mean[j] + stdev[j] * gsl_ran_flat(r, 0.0, 0.5);
      par->SigmaF[j][i] = pow(stdev[j],2.0) * 0.5;
    }
  }
}

void init_par(PAR *par, DATA *data, const gsl_rng *r) {
  int i,j;
  double eq;
  double mean[data->N];
  double stdev[data->N];

  /* initial values */
  eq = 1.0 / ((double) par->ncomp);
  for(i=0;i<par->ncomp;i++) par->piT[i] = eq;
  eq = 1.0 / ((double) par->ncomp0);
  for(j=0;j<par->N;j++) {
    for(i=0;i<par->ncomp0;i++) par->piF[j][i] = eq;
  }

  /* Mu; Sigma */
  find_loc(mean, stdev, data);
  init_MuSigma(mean, stdev, par,data, r);

  /* Latent Varialbes */
  for(i=0;i<data->P;i++) {
    if(data->is_decoy[i]) par->z[i] = 0.0;
    else par->z[i] = 0.5;
  }
}

void EM1(PAR *par, DATA *data) {
  /* pi, piT, piF, z */
  int i,j,k;    
  double maxp, sump;
  double pos_sum, neg_sum;
  double lik[par->ncomp];
  double likT[par->ncomp];
  double likF[data->N][par->ncomp0];
  double x[data->N];  
  double y[data->N];  
  double condT[par->ncomp];
  double condF[data->N][par->ncomp0];

  for(i=0;i<par->ncomp;i++) par->detT[i] = determ(par->SigmaT[i], data->N);
  for(i=0;i<par->ncomp;i++) condT[i] = par->detT[i] * par->piT[i];

  for(j=0;j<data->N;j++) {
    for(i=0;i<par->ncomp0;i++) condF[j][i] = par->piF[j][i] * par->SigmaF[j][i] > 0.0 ? 1.0 : 0.0;
  }

  for(i=0;i<par->ncomp;i++) par->zTsum[i] = 0.0;
  for(i=0;i<data->P;i++) {
    for(j=0;j<data->N;j++) x[j] = gsl_matrix_get(data->X, i, j);    

    /* positive */
    if(data->is_complete[i]) {
      for(k=0;k<par->ncomp && condT[k] > 0.0;k++) lik[k] = 0.0;
      for(k=0;k<par->ncomp && condT[k] > 0.0;k++) lik[k] = log_mgaussian_pdf(x, par->MuT[k], par->SigmaT[k], data->N);    
      maxp = vec_cond_max(lik, condT, par->ncomp);
      for(k=0;k<par->ncomp && condT[k] > 0.0;k++) lik[k] -= maxp;
      for(k=0;k<par->ncomp && condT[k] > 0.0;k++) lik[k] = exp(lik[k]);
      sump = vec_cond_sum(lik, condT, par->ncomp);
      for(k=0;k<par->ncomp && condT[k] > 0.0;k++) lik[k] /= sump;
      for(k=0;k<par->ncomp && condT[k] > 0.0;k++) par->zTsum[k] += lik[k] * par->z[i];    
    }
  }
  sump = vec_cond_sum(par->zTsum, condT, par->ncomp);
  for(k=0;k<par->ncomp;k++) par->piT[k] = par->zTsum[k] / sump;

  /* negative */
  for(j=0;j<par->N;j++) {
    for(k=0;k<par->ncomp0;k++) par->zFsum[k] = 0.0;
    for(i=0;i<data->P;i++) {    
      x[j] = gsl_matrix_get(data->X, i, j);    
      if(x[j] != _missval_) {
        for(k=0;k<par->ncomp0 && condF[j][k];k++) lik[k] = 0.0;
        for(k=0;k<par->ncomp0 && condF[j][k];k++) lik[k] = log_gaussian_pdf(x[j], par->MuF[j][k], par->SigmaF[j][k]);    
        maxp = vec_cond_max(lik, condF[j], par->ncomp0);
        for(k=0;k<par->ncomp0 && condF[j][k];k++) lik[k] -= maxp;
        for(k=0;k<par->ncomp0 && condF[j][k];k++) lik[k] = exp(lik[k]);
        sump = vec_cond_sum(lik, condF[j], par->ncomp0);
        for(k=0;k<par->ncomp0 && condF[j][k];k++) lik[k] /= sump;
        for(k=0;k<par->ncomp0 && condF[j][k];k++) par->zFsum[k] += lik[k] * (1.0 - par->z[i]);    
      }
    }
    sump = vec_cond_sum(par->zFsum, condF[j], par->ncomp0);
    for(k=0;k<par->ncomp0 && sump > 0.0 ;k++) {
       par->piF[j][k] = condF[j][k] ? par->zFsum[k] / sump : 0.0;
    }
  }


  for(i=0;i<data->P;i++) {
    for(j=0;j<data->N;j++) x[j] = gsl_matrix_get(data->X, i, j);    
    for(j=0;j<data->N;j++) {
      if(x[j] != _missval_) y[j] = GSL_MAX( x[j], vec_cond_min(par->MuF[j], condF[j], par->ncomp0));    
      else y[j] = x[j];
    }
    for(k=0;k<par->ncomp && condT[k] > 0.0;k++) likT[k] = log_mgaussian_marginal_pdf(x, par->MuT[k], par->SigmaT[k], data->N);    

    for(j=0;j<data->N;j++) {
      if(y[j] != _missval_) {
        for(k=0;k<par->ncomp0 && condF[j][k];k++) likF[j][k] = log_gaussian_pdf(y[j], par->MuF[j][k], par->SigmaF[j][k]);
      }
    } 
    neg_sum = 0.0;
    for(j=0;j<data->N;j++) {
      if(y[j] != _missval_) {
        maxp = vec_cond_max(likF[j], condF[j], par->ncomp0);
        for(k=0;k<par->ncomp0 && condF[j][k];k++) {
          likF[j][k] -= maxp;
          likF[j][k] = par->piF[j][k] * exp(likF[j][k]);
        }
        neg_sum += maxp + log(vec_cond_sum(likF[j], condF[j], par->ncomp0));
      }
    }
    maxp = GSL_MAX(vec_cond_max(likT, condT, par->ncomp), neg_sum);
        
    for(k=0;k<par->ncomp && condT[k] > 0.0;k++) {
      likT[k] -= maxp;
      likT[k] = exp(likT[k]);
    }
    pos_sum = 0.0;
    for(k=0;k<par->ncomp && condT[k] > 0.0;k++) pos_sum += par->piT[k] * likT[k];

    neg_sum = exp(neg_sum - maxp);

    par->z[i] = par->pi * pos_sum / (par->pi * pos_sum + (1.0 - par->pi) * neg_sum);    
    if(data->is_decoy[i]) par->z[i] = 0.0;
  }

  par->pi = 0.0;
  k = 0;
  for(i=0;i<data->P;i++) {
    if(data->is_decoy[i]) {}
    else {
      par->pi += par->z[i];
      k++;
    }
  }
  par->pi /= ((double) k);
}


void EM2(PAR *par, DATA *data) {
  int i,j,k, s, t;    
  double maxp, sump, tmp, tmpprod;
  double lik[par->ncomp];
  double liksum[par->ncomp];
  double x[data->N];  

  double condT[par->ncomp];

  for(i=0;i<par->ncomp;i++) par->detT[i] = determ(par->SigmaT[i], data->N);
  for(i=0;i<par->ncomp;i++) condT[i] = par->detT[i] * par->piT[i];

  gsl_vector **Mu;
  gsl_matrix **Sigma;
  assert(Mu = (gsl_vector **) calloc(par->ncomp, sizeof(gsl_vector *)));
  assert(Sigma = (gsl_matrix **) calloc(par->ncomp, sizeof(gsl_matrix *)));

  for(i=0;i<par->ncomp;i++) {
    Mu[i] = gsl_vector_alloc(par->N);
    Sigma[i] = gsl_matrix_alloc(par->N, par->N);
  }

  for(i=0;i<par->ncomp;i++) {
    gsl_vector_set_zero(Mu[i]);
    liksum[i] = 0.0;
  }
  for(i=0;i<data->P;i++) {
    if(data->is_complete[i]) {
      for(j=0;j<data->N;j++) x[j] = gsl_matrix_get(data->X, i, j);    
      for(k=0;k<par->ncomp && condT[k] > 0.0;k++) lik[k] = log_mgaussian_pdf(x, par->MuT[k], par->SigmaT[k], data->N);    
      maxp = vec_cond_max(lik, condT, par->ncomp);
      for(k=0;k<par->ncomp && condT[k] > 0.0;k++) lik[k] -= maxp;
      for(k=0;k<par->ncomp && condT[k] > 0.0;k++) lik[k] = exp(lik[k]);
      sump = vec_cond_sum(lik, condT, par->ncomp);
      for(k=0;k<par->ncomp && condT[k] > 0.0;k++) lik[k] /= sump;
      for(k=0;k<par->ncomp && condT[k] > 0.0;k++) {
        liksum[k] += lik[k] * par->z[i];    
        for(j=0;j<data->N;j++) {
          tmp = gsl_vector_get(Mu[k], j);
          gsl_vector_set(Mu[k], j, tmp + lik[k] * par->z[i] * x[j]);
        }
      }
    }
  }
  for(k=0;k<par->ncomp && condT[k] > 0.0;k++) {
    for(j=0;j<data->N;j++) {
      tmp = gsl_vector_get(Mu[k], j);
      gsl_vector_set(par->MuT[k], j, tmp / liksum[k]);
    }
  }    

  for(i=0;i<par->ncomp;i++) {
    gsl_matrix_set_zero(Sigma[i]);
    liksum[i] = 0.0;
  }
  for(i=0;i<data->P;i++) {
    if(data->is_complete[i]) {
      for(j=0;j<data->N;j++) x[j] = gsl_matrix_get(data->X, i, j);    
      for(k=0;k<par->ncomp && condT[k] > 0.0;k++) lik[k] = log_mgaussian_pdf(x, par->MuT[k], par->SigmaT[k], data->N);    
      maxp = vec_cond_max(lik, condT, par->ncomp);
      for(k=0;k<par->ncomp && condT[k] > 0.0;k++) lik[k] -= maxp;
      for(k=0;k<par->ncomp && condT[k] > 0.0;k++) lik[k] = exp(lik[k]);
      sump = vec_cond_sum(lik, condT, par->ncomp);
      for(k=0;k<par->ncomp && condT[k] > 0.0;k++) lik[k] /= sump;
      for(k=0;k<par->ncomp && condT[k] > 0.0;k++) {
        liksum[k] += lik[k] * par->z[i];    
        for(s=0;s<data->N;s++) {
          for(t=0;t<data->N;t++) {
            tmp = gsl_matrix_get(Sigma[k], s, t);
            tmpprod = (x[s] - gsl_vector_get(par->MuT[k],s)) * (x[t] - gsl_vector_get(par->MuT[k],t));
            gsl_matrix_set(Sigma[k], s, t, tmp + lik[k] * par->z[i] * tmpprod);
          }
        }
      }
    }
  }
  for(k=0;k<par->ncomp && condT[k] > 0.0;k++) {
    for(s=0;s<data->N;s++) {
      for(t=0;t<data->N;t++) {
        tmp = gsl_matrix_get(Sigma[k], s, t);
        gsl_matrix_set(par->SigmaT[k], s, t, tmp / liksum[k]);
      }
    }
  }    

  /* temporary memory */
  for(i=0;i<par->ncomp;i++) gsl_vector_free(Mu[i]);
  for(i=0;i<par->ncomp;i++) gsl_matrix_free(Sigma[i]);
  free(Mu);
  free(Sigma);
}


void EM3(PAR *par, DATA *data) {
  int i,j,k;    
  double maxp, sump;
  double lik[par->ncomp0];
  double liksum[par->ncomp0];
  double x;  
  double Mu[par->ncomp0];
  double Sigma[par->ncomp0];

  double condF[data->N][par->ncomp0];

  for(j=0;j<data->N;j++) {
    for(i=0;i<par->ncomp0;i++) condF[j][i] = par->piF[j][i] * par->SigmaF[j][i] > 0.0 ? 1.0 : 0.0;
  }

  for(j=0;j<data->N;j++) {
    for(k=0;k<par->ncomp0 && condF[j][k];k++) {
      liksum[k] = 0.0;
      Mu[k] = 0.0;
    }
    for(i=0;i<data->P;i++) {
      x = gsl_matrix_get(data->X, i, j);
      if(x != _missval_) {
        for(k=0;k<par->ncomp0 && condF[j][k];k++) lik[k] = log_gaussian_pdf(x, par->MuF[j][k], par->SigmaF[j][k]);    
        maxp = vec_cond_max(lik, condF[j], par->ncomp0);
        for(k=0;k<par->ncomp0 && condF[j][k];k++) lik[k] -= maxp;
        for(k=0;k<par->ncomp0 && condF[j][k];k++) lik[k] = exp(lik[k]);
        sump = vec_cond_sum(lik, condF[j], par->ncomp0);
        for(k=0;k<par->ncomp0 && condF[j][k];k++) lik[k] /= sump;
        for(k=0;k<par->ncomp0 && condF[j][k];k++) {
          liksum[k] += lik[k] * (1.0 - par->z[i]);   
          Mu[k] += lik[k] * (1.0 - par->z[i]) * x; 
        }
      }
    }
    for(k=0;k<par->ncomp0 && condF[j][k];k++) {
      par->MuF[j][k] = Mu[k] / liksum[k];
    }    
  }

  for(j=0;j<data->N;j++) {
    for(k=0;k<par->ncomp0 && condF[j][k];k++) {
      Sigma[k] = 0.0;
    }
    for(i=0;i<data->P;i++) {
      x = gsl_matrix_get(data->X, i, j);
      if(x != _missval_) {
        for(k=0;k<par->ncomp0 && condF[j][k];k++) lik[k] = log_gaussian_pdf(x, par->MuF[j][k], par->SigmaF[j][k]);    
        maxp = vec_cond_max(lik, condF[j], par->ncomp0);
        for(k=0;k<par->ncomp0 && condF[j][k];k++) lik[k] -= maxp;
        for(k=0;k<par->ncomp0 && condF[j][k];k++) lik[k] = exp(lik[k]);
        sump = vec_cond_sum(lik, condF[j], par->ncomp0);
        for(k=0;k<par->ncomp0 && condF[j][k];k++) lik[k] /= sump;
        for(k=0;k<par->ncomp0 && condF[j][k];k++) {
          Sigma[k] += lik[k] * (1.0 - par->z[i]) * pow(x - par->MuF[j][k], 2.0); 
        }
      }
    }
    for(k=0;k<par->ncomp0 && condF[j][k];k++) {
      par->SigmaF[j][k] = Sigma[k] / liksum[k];
    }    
  }
}



void SCORE(PAR *par, DATA *data) {
  /* pi, piT, piF, z */
  int i,j,k;    
  double maxp;
  double pos_sum, neg_sum;
  double likT[par->ncomp];
  double likF[data->N][par->ncomp0];
  double x[data->N];  
  double y[data->N];  
  double condT[par->ncomp];
  double condF[data->N][par->ncomp0];

  for(i=0;i<par->ncomp;i++) par->detT[i] = determ(par->SigmaT[i], data->N);
  for(i=0;i<par->ncomp;i++) condT[i] = par->detT[i] * par->piT[i];

  for(j=0;j<data->N;j++) {
    for(i=0;i<par->ncomp0;i++) condF[j][i] = par->piF[j][i] * par->SigmaF[j][i] > 0.0 ? 1.0 : 0.0;
  }

  for(i=0;i<data->P;i++) {
    for(j=0;j<data->N;j++) x[j] = gsl_matrix_get(data->X, i, j);    
    for(j=0;j<data->N;j++) {
      if(x[j] != _missval_) y[j] = GSL_MAX( x[j], vec_cond_min(par->MuF[j], condF[j], par->ncomp0));    
      else y[j] = x[j];
    }
    for(k=0;k<par->ncomp && condT[k] > 0.0;k++) likT[k] = log_mgaussian_marginal_pdf(x, par->MuT[k], par->SigmaT[k], data->N);    

    for(j=0;j<data->N;j++) {
      if(y[j] != _missval_) {
        for(k=0;k<par->ncomp0 && condF[j][k];k++) likF[j][k] = log_gaussian_pdf(y[j], par->MuF[j][k], par->SigmaF[j][k]);
      }
    } 
    neg_sum = 0.0;
    for(j=0;j<data->N;j++) {
      if(y[j] != _missval_) {
        maxp = vec_cond_max(likF[j], condF[j], par->ncomp0);
        for(k=0;k<par->ncomp0 && condF[j][k];k++) {
          likF[j][k] -= maxp;
          likF[j][k] = par->piF[j][k] * exp(likF[j][k]);
        }
        neg_sum += maxp + log(vec_cond_sum(likF[j], condF[j], par->ncomp0));
      }
    }
    maxp = GSL_MAX(vec_cond_max(likT, condT, par->ncomp), neg_sum);
        
    for(k=0;k<par->ncomp && condT[k] > 0.0;k++) {
      likT[k] -= maxp;
      likT[k] = exp(likT[k]);
    }
    pos_sum = 0.0;
    for(k=0;k<par->ncomp && condT[k] > 0.0;k++) pos_sum += par->piT[k] * likT[k];

    neg_sum = exp(neg_sum - maxp);

    par->z[i] = par->pi * pos_sum / (par->pi * pos_sum + (1.0 - par->pi) * neg_sum);    
  }
}


double logLik(PAR *par, DATA *data) {
  int i,j,k;
  double maxp, tsum, fsum, tmp;
  double x[data->N];
  double likT[par->ncomp];
  double likF[par->N][par->ncomp0];
  double loglik;
  double condT[par->ncomp];
  double condF[data->N][par->ncomp0];

  for(i=0;i<par->ncomp;i++) par->detT[i] = determ(par->SigmaT[i], data->N);
  for(i=0;i<par->ncomp;i++) condT[i] = par->detT[i] * par->piT[i] > 0.0 ? 1.0 : 0.0;

  for(j=0;j<data->N;j++) {
    for(i=0;i<par->ncomp0;i++) condF[j][i] = par->piF[j][i] * par->SigmaF[j][i] > 0.0 ? 1.0 : 0.0;
  }

  loglik = 0.0;
  for(i=0;i<data->P;i++) {
    if(!(data->is_decoy[i])) {

    for(j=0;j<data->N;j++) x[j] = gsl_matrix_get(data->X, i, j);    
    for(k=0;k<par->ncomp && condT[k] > 0.0;k++) likT[k] = log_mgaussian_marginal_pdf(x, par->MuT[k], par->SigmaT[k], data->N);
    fsum = 0.0;
    for(j=0;j<par->N;j++) {
      if(x[j] != _missval_) {
        for(k=0;k<par->ncomp0 && condF[j][k];k++) likF[j][k] = log_gaussian_pdf(x[j], par->MuF[j][k], par->SigmaF[j][k]);
        maxp = vec_cond_max(likF[j], condF[j], par->ncomp0);
        for(k=0;k<par->ncomp0 && condF[j][k];k++) {
          likF[j][k] -= maxp;
          likF[j][k] = par->piF[j][k] * exp(likF[j][k]);
        }
        fsum += maxp + log(vec_cond_sum(likF[j], condF[j], par->ncomp0));
      }
    }
    maxp = GSL_MAX(vec_cond_max(likT, condT, par->ncomp), fsum);
    fsum -= maxp;
    fsum = (1.0 - par->pi) * exp(fsum);
    for(k=0;k<par->ncomp && condT[k] > 0.0;k++) {
      likT[k] -= maxp;
      likT[k] = par->pi * par->piT[k] * exp(likT[k]);
    }
    tsum = vec_cond_sum(likT, condT, par->ncomp);
    tmp = maxp + log(tsum + fsum);
    if(gsl_finite(tmp)) loglik += tmp;

    }
  }  
  return loglik;
}


void mvEM(PAR *par, DATA *data, int niter, const gsl_rng *r) {
  int i;
  double oldlik, newlik;
  double oldpi, newpi;

  oldpi = 0.0;
  newpi = 0.0;
  for(i=0;i<niter;i++) {
    if(i==0) oldlik = GSL_NEGINF;
    else oldlik = newlik;

    oldpi = newpi;

    EM1(par, data);
    EM2(par, data);
    EM3(par, data);
    
    newpi = par->pi;
    newlik = logLik(par, data);

    fprintf(stdout, "%d\t%.6f\t%.4f\n", i+1, newlik, par->pi);
   
    /*
    int k,j;
    fprintf(stdout, "TRUE\n");
    for(k=0;k<par->ncomp;k++) {
      fprintf(stdout, "%.3f\n", par->piT[k]);
      printVector(par->MuT[k], par->N);
      fprintf(stdout, "\n");
      printMatrix(par->SigmaT[k], par->N);
      fprintf(stdout, "\n");
    }
    fprintf(stdout, "FALSE\n");
    for(j=0;j<par->N;j++) {
      for(k=0;k<par->ncomp0;k++) {
        fprintf(stdout, "%.3f\t%.3f\t%.3f\n", par->piF[j][k], par->MuF[j][k], par->SigmaF[j][k]);
      } 
      fprintf(stdout, "\n");
    }
    fprintf(stdout, "\n");
    */
    if(fabs(newpi - oldpi) <= 0.0001) {
      break;
    }            
  }
  
  SCORE(par, data);
}



