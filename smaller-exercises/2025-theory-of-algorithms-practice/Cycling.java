import java.util.Scanner;

public class Cycling{
   public static void main(String[] args) {
      Scanner sc = new Scanner(System.in);
      int N = sc.nextInt();
      int[] P = new int[N];
      for (int i=0; i<N; i++){
         P[i] = sc.nextInt();
      }
      int[] preSum = new int[N+1];
      preSum[0] = 0;
      preSum[1] = P[0];
      for (int i=1; i<N; i++){
         preSum[i+1] = preSum[i] + P[i];
      }
      int maxPoints = 0;
      for (int j=0; j<N+1; j++){
         for (int k=j; k<N+1; k++){
            int points = preSum[k]-preSum[j];
            if (points>maxPoints) { maxPoints = points; }
         }
      }
      System.out.println(maxPoints);
   }
}