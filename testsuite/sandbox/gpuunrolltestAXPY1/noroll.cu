#include "book.h"

__global__ void orcu_kernel11(int n, int orcu_var8, double a1, double* y, double* x1) {
  int tid=blockIdx.x*blockDim.x+threadIdx.x+orcu_var8;
  if (tid<=n-1) {
    //printf("jack %d\n", tid);
    y[tid]=y[tid]+a1*x1[tid];
  }
}


void axpy1(int n, double *y, double a1, double *x1)
{
register int i;


/*@ begin Loop(
  transform Composite(
    cuda = (16,False, False, 1)
    ,scalarreplace = (False, 'int')
, unrolljam = (['i'], [2])
  )
   {
    for (i=0; i<=n-1; i++) {
    	y[i]=y[i]+a1*x1[i];
    }
    
   }


   
  
) @*/

cudaEvent_t start, stop;
HANDLE_ERROR(cudaEventCreate(&start));
HANDLE_ERROR(cudaEventCreate(&stop));


{
  {
    int orio_lbound2=0;
    {
      printf("hello???\n");
      /*declare variables*/
      double *dev_y, *dev_x1;
      int nthreads=TC;
      /*calculate device dimensions*/
      dim3 dimGrid, dimBlock;
      dimBlock.x=nthreads;
      dimGrid.x=(n+nthreads-1)/nthreads;
      /*allocate device memory*/
      int nbytes=n*sizeof(double);
      HANDLE_ERROR(cudaMalloc((void**)&dev_y,nbytes));
      HANDLE_ERROR(cudaMalloc((void**)&dev_x1,nbytes));
      /*copy data from host to device*/
      HANDLE_ERROR(cudaMemcpy(dev_y,y,nbytes,cudaMemcpyHostToDevice));
      HANDLE_ERROR(cudaMemcpy(dev_x1,x1,nbytes,cudaMemcpyHostToDevice));
      /*invoke device kernel*/
      int orcu_var8=orio_lbound2;
      HANDLE_ERROR(cudaEventRecord(start, 0));
      orcu_kernel11<<<dimGrid,dimBlock>>>(n,orcu_var8,a1,dev_y,dev_x1);
      HANDLE_ERROR(cudaEventRecord(stop, 0));
      HANDLE_ERROR(cudaEventSynchronize(stop));
      /*copy data from device to host*/
      HANDLE_ERROR(cudaMemcpy(y,dev_y,nbytes,cudaMemcpyDeviceToHost));
      /*free allocated memory*/
      HANDLE_ERROR(cudaFree(dev_y));
      HANDLE_ERROR(cudaFree(dev_x1));
    }
  }
}
/*@ end @*/

//HANDLE_ERROR(cudaEventSynchronize(stop));
float passedTime;
HANDLE_ERROR(cudaEventElapsedTime(&passedTime, start, stop));
HANDLE_ERROR(cudaEventDestroy(start));
HANDLE_ERROR(cudaEventDestroy(stop));
printf("timePassed: %f ms\n", passedTime);
}

int main(){
	double* y = (double*) malloc(sizeof(double)*NN);
	double* x1 = (double*) malloc(sizeof(double)*NN);
	double a1 = AA;
	int i;
	for(i=0; i<NN; i++){
		y[i] = i;
		x1[i] = i;
	}
	axpy1(NN, y, a1, x1);
	for(i=0; i<13; i++)
		printf("%f\n", y[i]);
        for(i=NN-9; i<NN; i++)
                printf("%f\n", y[i]);

	return 0;
}
