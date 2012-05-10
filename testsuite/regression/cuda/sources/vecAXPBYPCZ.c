void VecAXPBYPCZ(int n, double a, double *x, double b, double *y, double c, double *z) {

  register int i;

  /*@ begin Loop(transform CUDA(threadCount=32, blockCount=14, streamCount=2, cacheBlocks=True, preferL1Size=16)

  for (i=0; i<=n-1; i++)
    y[i]=a*x[i]+b*y[i]+c*z[i];

  ) @*/

  for (i=0; i<=n-1; i++)
    y[i]=a*x[i]+b*y[i]+c*z[i];

  /*@ end @*/
}
