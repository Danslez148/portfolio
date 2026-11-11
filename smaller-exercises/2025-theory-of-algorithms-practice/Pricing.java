import java.util.Scanner;
public class Pricing {
   public static long availableMoney;
   public static long maxGemsBuyable;

   public static long getCostOfGems(long numGems){
      long totalCost = 0;
      for (int i=1; i<numGems; i++){        
         totalCost += i*(numGems/i);
      }
      return totalCost;
   }
   
   public static void bs(long start, long end){
      if (start>end){ 
         return; 
      }
      long mid = start+(end-start)/2;
      long currCost = getCostOfGems(mid);
      if (currCost == availableMoney){
         maxGemsBuyable = mid;
         return;
      }
      else if (currCost > availableMoney){
         bs(start, mid-1);
      }
      else if (currCost < availableMoney){
         maxGemsBuyable = mid;
         bs(mid+1, end);
      }
   }
 
   public static void main(String[] args){
      Scanner sc = new Scanner(System.in);
      availableMoney = sc.nextLong();
      bs(0, 1000000);
      System.out.println(maxGemsBuyable);
   }
}