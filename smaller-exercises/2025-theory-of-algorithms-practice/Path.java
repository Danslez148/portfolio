import java.util.Scanner;

public class Path{
   public static void main(String[] args){
      Scanner sc = new Scanner(System.in);
      int N = sc.nextInt();
      int K = sc.nextInt();
      long[][] grid = new long[N+1][N+1];
      for (int i=0; i<K; i++){
         int c = sc.nextInt();
         int r = sc.nextInt();
         grid[N-r][c] = -1;
      }
      /*
      for (int l=0; l<N+1; l++){
         System.out.println("");
         for (int m=0; m<N+1; m++){
            System.out.print(grid[l][m]);
         }
      }
      System.out.println("");
      System.out.println("---");
      */
      grid[N-1][0] = 1;
      for (int j=N-1; j>=0; j--){
         for (int k=1; k<N+1; k++){
            if (grid[j][k]==-1) { continue; }
            long inLeft = grid[j][k-1];
            long inBottom = grid[j+1][k];
            inLeft = Math.max(inLeft, 0);
            inBottom = Math.max(inBottom, 0);
            grid[j][k] = inLeft+inBottom;
         }
      }
      /*
      for (int l=0; l<N+1; l++){
         System.out.println("");
         for (int m=0; m<N+1; m++){
            System.out.print(grid[l][m]);
         }
      }
      System.out.println("");
      System.out.println("---");
      */
      System.out.println(grid[0][N]);
   }
}