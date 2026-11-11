public class ParallelFJ1 { //extends RecursiveTask<Integer>  
	  int lo, hi;
	  int[] arr;
	  static final int CUT=5000;
	
	  ParallelFJ1(int[] a, int l, int h) { lo=l; hi=h; arr=a;}

	  protected Integer compute(){
		  if((hi-lo) < CUT) {
			  int ans = arr[lo];
			  for(int i=(lo+1); i < hi; i++) {
				  if (ans < arr[i]) ans=arr[i];
			  }
			  return ans;
		  }
		    else {
		    	ParallelFJ1 left = new ParallelFJ1(arr,lo,(hi+lo)/2);
		    	ParallelFJ1 right= new ParallelFJ1(arr,(hi+lo)/2,hi);
		    	left.fork(); 
		    	int leftAns  = left.join();   
		    	int rightAns = right.compute(); 
		    	if (leftAns < rightAns)
		    		return rightAns;
		    	return leftAns;     
		    }
		  }
	  
	  public static void main(String[] args) throws Exception {
		  Random rand = new Random();  //the random number generator
	    	
			int max =10000000;
			int [] arr = new int[max];
			for (int i=0;i<max;i++) { arr[i]=rand.nextInt(5000); }
			final ForkJoinPool fjPool = ForkJoinPool.commonPool();
			int ans = fjPool.invoke(new ParallelFJ1(arr,0,arr.length));
			System.out.println(ans);
	  }
}