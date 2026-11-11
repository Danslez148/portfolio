//Program to create different time periods
//Daniel Schlesinger
//SCHDAN066
//3 Sep 2023

public class TimePeriod {
   private Duration lowerBound;
   private Duration upperBound;
   
   public TimePeriod(Duration lowerBound, Duration upperBound) {
      this.lowerBound = lowerBound;
      this.upperBound = upperBound;
   }
   
   public Duration lowerBound() {
      return this.lowerBound;
   }
   
   public Duration upperBound() {
      return this.upperBound;
   }
   
   public boolean includes(Duration duration) {
      return ((duration.compareTo(lowerBound)>=0) && (duration.compareTo(upperBound) <0));
   }
   
   public boolean precedes(TimePeriod other) {
      return (this.upperBound().compareTo(other.lowerBound())<=0);
   }
   
   public boolean adjacent(TimePeriod other) {
      return ((this.upperBound().compareTo(other.lowerBound())==0) || (this.lowerBound().compareTo(other.upperBound())==0));
   }
   
   public String toString() {
      return ("[" + Duration.format(lowerBound, "minutes") + " .. " + Duration.format(upperBound, "minutes") + "]");
   }
}