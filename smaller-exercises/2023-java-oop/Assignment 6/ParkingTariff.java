// Class describing the parking tariffs for a parking garage
// Daniel Schlesinger
// SCHDAN066
// 3 Sep 2023

public class ParkingTariff {
   
   private TimePeriod period;
   private Money rate;
   
   public ParkingTariff(TimePeriod periodOfTime, Money rateOfPay) {
      this.period = periodOfTime;
      this.rate = rateOfPay;
   }
   
   public Money getRate() {
      return this.rate;
   }
   
   public TimePeriod getPeriod() {
      return this.period;
   }
   
   public void changeRate(Money newAmount) {
      this.rate = newAmount;
   }
   
   
}