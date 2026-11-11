// describing work shifts
// SCHDAN066
// Daniel Schlesinger
// 15 September

public class Shift {
   private CalendarTime start;
   private CalendarTime finish;
   
   public Shift(CalendarTime start, CalendarTime finish) {
      this.start = start;
      this.finish = finish;
   }
   
   public CalendarTime start() {
      return this.start;
   }
   
   public CalendarTime finish() {
      return this.finish;
   }
   
   public boolean inWeek(Week w) {
      if (w.includes(start.date()) && w.includes(finish.date())) {
         return true;
      }
      return false;
   }
   
   public boolean includesDate(Date date) {
      if (date.equals(start.date()) || date.equals(finish.date())) {
         return true;
      }
      return false;
   }
   
   public Duration length() {
      return finish.subtract(start);
   }
   
   public String toString() {
      return start.date().toString() + "%" + start.time().toString() + " - " + finish.date().toString() + "%" + finish.time().toString();
   }
}