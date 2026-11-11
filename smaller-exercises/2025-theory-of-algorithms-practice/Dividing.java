import java.util.Scanner;
public class Dividing {
   public static int N;
   public static long[] planks;
   public static long K;
   public static long M;
   
   public static long getMaxPlanks(long[] arr, long lengthOfPlank){
      long count = 0;
      for (int j=0; j<arr.length; j++){
         count+=arr[j]/lengthOfPlank;
      }
      return count;
   }
   
   public static void bs(long start, long end){
      if (start>end) { return; }
      long mid = start + (end - start)/2;
      
      long currMaxPlanks = getMaxPlanks(planks, mid);
      
      if (currMaxPlanks < K) {
         bs(start, mid-1);
      }
      
      else if (currMaxPlanks >= K) { 
         M = mid;
         bs(mid+1, end); 
      }
      
   }
   
   public static void main(String[] args){
      Scanner sc = new Scanner(System.in);
      N = sc.nextInt();
      planks = new long[N];
      for (int i=0; i<N; i++){
         planks[i]=sc.nextLong();
      }
      K = sc.nextLong();
      
      bs(1, 1000000000);
      
      System.out.println(M);
      
   }
}