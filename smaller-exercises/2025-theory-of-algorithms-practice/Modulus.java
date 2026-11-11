import java.util.Scanner;
public class Modulus {
    public static void main(String[] args){
      Scanner sc = new Scanner(System.in);
      int N = sc.nextInt();
      int Z = sc.nextInt();
      int countPairs = 0;
      
      for (int X=1; X<N; X++){
         for (int Y=1; Y<N; Y++) {
            if ((X*Y)%N==Z) { countPairs++; }
         }
      }
      
      System.out.println(countPairs);
    }
}
