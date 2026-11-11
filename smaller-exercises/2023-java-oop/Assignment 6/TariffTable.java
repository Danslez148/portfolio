// Class to record parking tariffs ina  parking garage
// Daniel Schlesinger
// SCHDAN066
// 3 Sep 2023

public class TariffTable {
   private ParkingTariff[] parkingTariffs;
   private int nextFree;
   
   public TariffTable(int maxSize) {
      parkingTariffs = new ParkingTariff[maxSize];
      nextFree = 0;
   }
   
   public void addTariff(TimePeriod period, Money tariff) {
      ParkingTariff currentTariff = new ParkingTariff(period, tariff);
      if (nextFree==0) {
         parkingTariffs[nextFree] = currentTariff;
         nextFree++;
      } else {
         if ((parkingTariffs[nextFree-1].getPeriod().precedes(period)) && (parkingTariffs[nextFree-1].getPeriod().adjacent(period))) {
            parkingTariffs[nextFree] = currentTariff;
            nextFree++;
         } else {
            throw new IllegalArgumentException("Tariff periods must be adjacent.");
         }
      }
   }
   
   public Money getTariff(Duration lengthOfStay) {
      Currency rand = new Currency("R", "ZAR", 100);
      Money tariffReturned = new Money("R0", rand);
      for (int i=0; i<nextFree; i++) {
         if (parkingTariffs[i].getPeriod().includes(lengthOfStay)) {
            tariffReturned = parkingTariffs[i].getRate();
         }
      }
      return tariffReturned;
   }
   
   public String toString() {
      String result = "";
      int i = 0;
      for (i=0; i<nextFree; i++) {
         if (i==nextFree-1) {
            result += (parkingTariffs[i].getPeriod().toString() + " : " + parkingTariffs[i].getRate().toString());
         } else {
            result += (parkingTariffs[i].getPeriod().toString() + " : " + parkingTariffs[i].getRate().toString() + "\n");
         }
      }
      return result;   
   }
}