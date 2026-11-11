import java.util.Scanner;
import java.util.ArrayList;
public class Scoring {
   public static int maxScore;
   public static int numTerms;
   public static int[] arrTerms;
   //public static ArrayList<Integer> finalScores = new ArrayList();
   
   public static void calcMaxScore(int index, int currScore, int targetScore) {
         if (index == numTerms) { 
            if ((currScore < targetScore) && (currScore > maxScore)) {
               maxScore = currScore;
               // finalScores.add(currScore);
            }
            return; 
         }
         calcMaxScore(index+1, currScore + arrTerms[index], targetScore);
         calcMaxScore(index+1, currScore * arrTerms[index], targetScore);
      }

   public static void main(String[] args) {
      maxScore = 1;
      int targetScore;
      
      Scanner sc = new Scanner(System.in);
      numTerms = sc.nextInt();
      arrTerms = new int[numTerms];     
      for (int i=0; i<numTerms; i++) {
         arrTerms[i]=sc.nextInt();
      }
      targetScore = sc.nextInt();
      
      calcMaxScore(0, 1, targetScore);
  /*    
      int maxHelp=1;
      for (int j=0; j<finalScores.size(); j++) {
         maxHelp=Math.max(finalScores.get(j), maxHelp);
      }
   */   
     // System.out.println(maxHelp);
      System.out.println(maxScore);
   }
}